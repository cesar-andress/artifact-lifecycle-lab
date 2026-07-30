"""Post-processing pipeline for RQ5 v2 Phase 0 calibration (analysis only)."""

from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from statistics import mean, median, pstdev

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.rq5_v2.manifest import load_case_manifest
from artifact_lab.experiments.rq5_v2.phase0_figures import (
    render_distribution,
    render_funnel,
    render_success_rate,
)
from artifact_lab.experiments.rq5_v2.phase0_provenance import (
    collect_provenance,
    provenance_block,
    provenance_json,
)
from artifact_lab.experiments.rq5_v2.phase0_run import (
    DEFAULT_OUTPUT_DIR,
    PHASE0_CELL,
    PHASE0_EXPECTED_RUNS,
    compute_phase0_metrics,
    wilson_ci,
)
from artifact_lab.experiments.rq5_v2.phase0_trace import enrich_result_from_trace, parse_trace_events

ANALYSIS_SCRIPTS = [
    Path(__file__),
    Path(__file__).with_name("phase0_figures.py"),
    Path(__file__).with_name("phase0_provenance.py"),
    Path(__file__).with_name("phase0_trace.py"),
]

FAILURE_CATEGORIES = (
    "Infrastructure",
    "Toolchain",
    "Compilation",
    "Tests",
    "Wrong edit",
    "Timeout",
    "No grounding",
    "No instruction uptake",
    "Unknown",
)


@dataclass(frozen=True)
class GateRow:
    gate: str
    target: str
    observed: str
    status: str


def _bool(value: object) -> bool:
    return str(value).lower() in ("true", "1", "yes")


def _float(value: object, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def _int(value: object, default: int = 0) -> int:
    if value in (None, ""):
        return default
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def load_results(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_audit(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    return {row["case_id"]: row for row in csv.DictReader(path.open(encoding="utf-8"))}


def load_trace_audit(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def enrich_rows(
    *,
    rows: list[dict],
    manifest_path: Path,
    traces_dir: Path,
) -> list[dict]:
    cases = {c.case_id: c for c in load_case_manifest(manifest_path)}
    enriched: list[dict] = []
    for row in rows:
        case = cases.get(row.get("case_id", ""))
        trace_path = Path(row.get("trace_path") or "")
        if not trace_path.is_absolute():
            candidate = Path.cwd() / trace_path
            trace_path = candidate if candidate.exists() else traces_dir / f"{row.get('run_id', '')}.jsonl"
        if case is not None:
            out = enrich_result_from_trace(
                case=case,
                cell_code=row.get("cell_code", PHASE0_CELL),
                result_row=dict(row),
                trace_path=trace_path,
            )
            out["instruction_self_repair"] = _detect_instruction_self_repair(
                case.instruction_path,
                trace_path,
            )
            enriched.append(out)
        else:
            row = dict(row)
            row["instruction_self_repair"] = False
            enriched.append(row)
    return enriched


def _detect_instruction_self_repair(instruction_path: str, trace_path: Path) -> bool:
    events, _ = parse_trace_events(trace_path)
    base = instruction_path.rstrip("/").split("/")[-1]
    for event in events:
        blob = json.dumps(event.payload)
        if event.event_type.lower() in {"edit", "write", "notebookedit"} and (
            instruction_path in blob or base in blob
        ):
            return True
    return False


def classify_failure(row: dict) -> str:
    if _bool(row.get("success")):
        return ""
    err = (row.get("error_message") or "").lower()
    if _bool(row.get("timed_out")) or "timeout" in err:
        return "Timeout"
    if any(
        token in err
        for token in (
            "invalid api key",
            "authentication",
            "not logged in",
            "clone",
            "network",
            "connection refused",
            "no space left",
        )
    ):
        return "Infrastructure"
    if not _bool(row.get("instruction_read")):
        return "No instruction uptake"
    if not _bool(row.get("anchor_attempted")):
        return "No grounding"
    if not _bool(row.get("compilation_success", True)):
        return "Compilation"
    if any(
        token in err
        for token in (
            "not found",
            "command not found",
            "no such file",
            "npm err",
            "cargo:",
            "go:",
            "vitest",
            "pytest",
            "jest",
            "mvn",
            "gradle",
        )
    ):
        return "Toolchain"
    if _bool(row.get("decoy_path_touched")) and not _bool(row.get("anchor_path_touched")):
        return "Wrong edit"
    if not _bool(row.get("tests_passing")):
        return "Tests"
    return "Unknown"


def _gate_status_pass_warn_fail(
    *,
    observed: float,
    pass_low: float | None = None,
    pass_high: float | None = None,
    warn_low: float | None = None,
    warn_high: float | None = None,
    higher_is_better: bool = True,
) -> str:
    if higher_is_better:
        if pass_low is not None and observed >= pass_low:
            if pass_high is None or observed <= pass_high:
                return "PASS"
        if warn_low is not None and observed >= warn_low:
            if warn_high is None or observed <= warn_high:
                return "WARN"
        return "FAIL"
    # lower is better (timeout rate)
    if pass_high is not None and observed <= pass_high:
        return "PASS"
    if warn_high is not None and observed <= warn_high:
        return "WARN"
    return "FAIL"


def evaluate_gates(
    *,
    rows: list[dict],
    metrics,
    audit: dict[str, dict],
    manifest_path: Path,
) -> list[GateRow]:
    gates: list[GateRow] = []

    n = len(rows)
    completion = n / PHASE0_EXPECTED_RUNS if PHASE0_EXPECTED_RUNS else 0.0
    gates.append(
        GateRow(
            "Run completion",
            f"{PHASE0_EXPECTED_RUNS}/{PHASE0_EXPECTED_RUNS}",
            f"{n}/{PHASE0_EXPECTED_RUNS}",
            "PASS" if n >= PHASE0_EXPECTED_RUNS else ("WARN" if n >= PHASE0_EXPECTED_RUNS * 0.5 else "FAIL"),
        )
    )

    sr = metrics.success_rate
    gates.append(
        GateRow(
            "Calibration success (T+L)",
            "0.45–0.75",
            f"{sr:.3f}",
            _gate_status_pass_warn_fail(
                observed=sr,
                pass_low=0.45,
                pass_high=0.75,
                warn_low=0.30,
                warn_high=0.85,
            ),
        )
    )

    ir = metrics.instruction_read_rate
    gates.append(
        GateRow(
            "Instruction read (present)",
            ">0.90",
            f"{ir:.3f}",
            "PASS" if ir >= 0.90 else ("WARN" if ir >= 0.80 else "FAIL"),
        )
    )

    aa = metrics.anchor_attempt_rate
    gates.append(
        GateRow(
            "Anchor attempt (M1)",
            ">0.60",
            f"{aa:.3f}",
            _gate_status_pass_warn_fail(observed=aa, pass_low=0.60, warn_low=0.40),
        )
    )

    tr = metrics.timeout_rate
    gates.append(
        GateRow(
            "Timeout rate",
            "≤0.15",
            f"{tr:.3f}",
            _gate_status_pass_warn_fail(
                observed=tr,
                pass_high=0.15,
                warn_high=0.30,
                higher_is_better=False,
            ),
        )
    )

    fm = metrics.files_modified_median
    gates.append(
        GateRow(
            "Median files modified",
            "≤10",
            f"{fm:.1f}",
            "PASS" if fm <= 10 else ("WARN" if fm <= 20 else "FAIL"),
        )
    )

    # Mechanical truth — all Phase 0 cases T+L cell mechanical_truth=True
    cases = load_case_manifest(manifest_path)
    mech_fail = [
        c.case_id
        for c in cases
        if c.case_id in audit and not c.get_cell(PHASE0_CELL).mechanical_truth
    ]
    mech_rate = 1.0 - (len(mech_fail) / len(cases)) if cases else 0.0
    gates.append(
        GateRow(
            "Mechanical truth (design)",
            "100%",
            f"{100 * mech_rate:.1f}%",
            "PASS" if not mech_fail else "FAIL",
        )
    )

    # Per-case operational LB (≥60% anchor attempt per case, 3 replicates)
    by_case: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_case[row.get("case_id", "")].append(row)
    failing_lb = []
    for case_id, case_rows in by_case.items():
        if not case_rows:
            continue
        rate = sum(_bool(r.get("anchor_attempted")) for r in case_rows) / len(case_rows)
        if rate < 0.60:
            failing_lb.append(case_id)
    lb_case_rate = 1.0 - len(failing_lb) / max(len(by_case), 1)
    gates.append(
        GateRow(
            "Per-case anchor attempt",
            "≥0.60 each case",
            f"{100 * lb_case_rate:.1f}% cases pass",
            "PASS" if not failing_lb else ("WARN" if len(failing_lb) <= 2 else "FAIL"),
        )
    )

    dry = sum(_bool(r.get("dry_run")) for r in rows)
    gates.append(
        GateRow(
            "No dry-run contamination",
            "0 dry runs",
            str(dry),
            "PASS" if dry == 0 else "FAIL",
        )
    )

    return gates


def compute_funnel(rows: list[dict]) -> dict[str, int]:
    n = len(rows)
    m1 = sum(_bool(r.get("anchor_attempted")) for r in rows)
    m2 = sum(_bool(r.get("bind_failure_detected")) and _bool(r.get("anchor_attempted")) for r in rows)
    m3 = sum(_bool(r.get("grounding_action")) and _bool(r.get("bind_failure_detected")) for r in rows)
    m4 = sum(_bool(r.get("repair_success")) and _bool(r.get("grounding_action")) for r in rows)
    read = sum(_bool(r.get("instruction_read")) for r in rows)
    return {
        "all_runs": n,
        "instruction_read": read,
        "M1_anchor_attempted": m1,
        "M2_bind_failure": m2,
        "M3_grounding_action": m3,
        "M4_repair_success": m4,
    }


def funnel_transitions(rows: list[dict]) -> dict[str, int]:
    """Confusion-style counts for sequential M1→M2→M3→M4 path."""
    counts: Counter[str] = Counter()
    for row in rows:
        stages = []
        if _bool(row.get("instruction_read")):
            stages.append("read")
        if _bool(row.get("anchor_attempted")):
            stages.append("M1")
        if _bool(row.get("bind_failure_detected")):
            stages.append("M2")
        if _bool(row.get("grounding_action")):
            stages.append("M3")
        if _bool(row.get("repair_success")):
            stages.append("M4")
        if not stages:
            counts["none"] += 1
        else:
            counts["→".join(stages)] += 1
    return dict(counts)


def repairability_distribution(audit: dict[str, dict], rows: list[dict]) -> Counter[float]:
    case_ids = {r.get("case_id") for r in rows}
    scores: Counter[float] = Counter()
    for case_id in case_ids:
        row = audit.get(case_id or "")
        if row:
            scores[_float(row.get("repairability_score"))] += 1
    return scores


def grounding_distribution(rows: list[dict]) -> Counter[str]:
    dist: Counter[str] = Counter()
    for row in rows:
        if _bool(row.get("repair_success")):
            dist["repair_success"] += 1
        elif _bool(row.get("grounding_action")):
            dist["grounding_only"] += 1
        elif _bool(row.get("anchor_attempted")):
            dist["anchor_only"] += 1
        elif _bool(row.get("instruction_read")):
            dist["read_only"] += 1
        else:
            dist["no_uptake"] += 1
    return dist


def power_update(*, rows: list[dict], metrics) -> str:
    """Sample-size update from observed Phase 0 variance (no planning assumptions)."""
    n0 = len(rows)
    p = metrics.success_rate if n0 else 0.0
    if n0 <= 1:
        var_run = 0.0
    else:
        successes = [1.0 if _bool(r.get("success")) else 0.0 for r in rows]
        var_run = pstdev(successes) ** 2

    # Per-case success rates (3 replicates)
    by_case: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        by_case[row.get("case_id", "")].append(1.0 if _bool(row.get("success")) else 0.0)
    case_rates = [mean(v) for v in by_case.values() if v]
    var_case = pstdev(case_rates) ** 2 if len(case_rates) > 1 else var_run

    z = 1.96
    targets = (0.05, 0.08, 0.10)
    lines = [
        "# Phase 1 Power Update (observed Phase 0 variance)",
        "",
        "All estimates use **observed** Phase 0 data only.",
        "",
        "## Observed variance",
        "",
        f"- Runs (Phase 0): **{n0}**",
        f"- Observed success rate: **{p:.3f}**",
        f"- Per-run variance (Bernoulli sample): **{var_run:.4f}**",
        f"- Per-case variance (mean of 3 replicates): **{var_case:.4f}**",
        f"- Cases with data: **{len(case_rates)}**",
        "",
        "## Required runs for T+L success-rate precision (Wilson-normal approx.)",
        "",
        "| Target half-width (95%) | Required runs (p̂={:.3f}) |".format(p),
        "|---|---|",
    ]
    for hw in targets:
        if p > 0 and p < 1:
            n_req = math.ceil((z**2) * p * (1 - p) / (hw**2))
        else:
            n_req = 0
        lines.append(f"| ±{hw:.2f} | {n_req} |")

    lines.extend(
        [
            "",
            "## Phase 1a (40 cases × 5 cells × 3 replicates = 600 runs planned)",
            "",
        ]
    )
    hw_1a = z * math.sqrt(var_case / 40) if var_case > 0 else 0.0
    lines.append(
        f"- With **observed per-case variance** and **N=40 cases**, expected 95% CI half-width on case-mean success: **±{hw_1a:.3f}**."
    )
    if hw_1a > 0.10:
        extra = math.ceil(var_case * (z / 0.10) ** 2) - 40
        lines.append(
            f"- To tighten half-width to ±0.10 at same variance: need **~{max(40, 40 + extra)} cases** (+{max(0, extra)} vs plan)."
        )
    else:
        lines.append("- Planned N=40 cases is **consistent** with ±0.10 precision at observed variance.")

    lines.extend(
        [
            "",
            "## Phase 1b (120 cases × 5 cells × 3 replicates = 1,800 runs planned)",
            "",
        ]
    )
    hw_1b = z * math.sqrt(var_case / 120) if var_case > 0 else 0.0
    lines.append(
        f"- Expected 95% CI half-width on case-mean success at N=120: **±{hw_1b:.3f}**."
    )

    # Anchor attempt rate precision
    aa = metrics.anchor_attempt_rate
    if aa > 0 and aa < 1 and n0:
        n_anchor = math.ceil((z**2) * aa * (1 - aa) / (0.08**2))
        lines.extend(
            [
                "",
                "## Operational LB gate (anchor attempt) precision",
                "",
                f"- Observed anchor rate: **{aa:.3f}**",
                f"- Runs needed for ±0.08 precision at 95%: **{n_anchor}**",
            ]
        )

    lines.append("")
    return "\n".join(lines)


def editorial_decision(
    *,
    gates: list[GateRow],
    metrics,
    rows: list[dict],
    failure_counts: Counter[str],
) -> str:
    fail_gates = [g for g in gates if g.status == "FAIL"]
    warn_gates = [g for g in gates if g.status == "WARN"]
    n = len(rows)
    infra = failure_counts.get("Infrastructure", 0)

    proceed = "No"
    if not fail_gates and not warn_gates and n >= PHASE0_EXPECTED_RUNS:
        proceed = "Conditional yes — human gate still required"
    elif warn_gates and not fail_gates:
        proceed = "No — resolve WARN gates first"
    else:
        proceed = "No"

    lines = [
        "# Phase 0 Editorial Decision",
        "",
        "## Associate Editor recommendation",
        "",
        f"**Proceed to Phase 1a?** **{proceed}**",
        "",
        "### Manipulation validity",
        "",
    ]
    if metrics.instruction_read_rate >= 0.90:
        lines.append("- Instruction uptake: **adequate** for present-cell manipulation check.")
    else:
        lines.append(
            f"- Instruction uptake (**{metrics.instruction_read_rate:.3f}**) **below preregistered 0.90** — manipulation check not established."
        )

    if metrics.anchor_attempt_rate >= 0.60:
        lines.append("- Operational load-bearing (M1): **adequate** at pooled level.")
    else:
        lines.append(
            f"- Operational LB (**{metrics.anchor_attempt_rate:.3f}**) **fails** the ≥0.60 gate — tasks may not be coupled to cited anchors."
        )

    lines.extend(["", "### Calibration validity", ""])
    if 0.45 <= metrics.success_rate <= 0.75:
        lines.append(
            f"- T+L success (**{metrics.success_rate:.3f}**) is inside the calibration band — difficulty target met."
        )
    else:
        lines.append(
            f"- T+L success (**{metrics.success_rate:.3f}**) is **outside** [0.45, 0.75] — calibration not validated."
        )

    lines.extend(["", "### Causal validity", ""])
    lines.append(
        "- Phase 0 does not estimate H4. Causal identifiability for Phase 1 depends on passing operational LB and instruction-read gates."
    )
    if fail_gates:
        lines.append(f"- **{len(fail_gates)} gate(s) FAIL** — causal runway not cleared.")

    lines.extend(["", "### Statistical validity", ""])
    if n < PHASE0_EXPECTED_RUNS:
        lines.append(f"- **Incomplete execution** ({n}/{PHASE0_EXPECTED_RUNS} runs) — inferential summaries are provisional.")
    else:
        lines.append(f"- Full Phase 0 battery completed ({n} runs).")

    lines.extend(["", "### Protocol deviations", ""])
    if infra:
        lines.append(f"- **{infra} infrastructure failures** detected — not part of preregistered failure taxonomy for task difficulty.")
    if dry := sum(_bool(r.get("dry_run")) for r in rows):
        lines.append(f"- **{dry} dry-run rows** — protocol violation if present in results ledger.")
    if not infra and not dry:
        lines.append("- No major protocol deviations detected in completed runs.")

    lines.extend(["", "### Risks", ""])
    top_fail = failure_counts.most_common(3)
    for cat, count in top_fail:
        if cat:
            pct = 100 * count / max(sum(1 for r in rows if not _bool(r.get("success"))), 1)
            lines.append(f"- **{cat}**: {count} failures ({pct:.0f}% of failed runs).")

    lines.extend(["", "### Required fixes before Phase 1a", ""])
    if fail_gates:
        for g in fail_gates:
            lines.append(f"- Fix **{g.gate}** (observed {g.observed}, target {g.target}).")
    elif warn_gates:
        for g in warn_gates:
            lines.append(f"- Review **{g.gate}** (observed {g.observed}, target {g.target}).")
    else:
        lines.append("- None blocking at Phase 0 level; proceed only after human review of this report.")

    lines.append("")
    return "\n".join(lines)


def _md_table(headers: list[str], table_rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in table_rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def write_dashboard(
    *,
    rows: list[dict],
    metrics,
    audit: dict[str, dict],
    provenance: dict,
    path: Path,
) -> None:
    tokens = [_float(r.get("token_usage")) for r in rows if r.get("token_usage") not in (None, "")]
    costs = [_float(r.get("cost_usd")) for r in rows if r.get("cost_usd") not in (None, "")]
    durs = [_float(r.get("execution_time_seconds")) for r in rows]
    rep_dist = repairability_distribution(audit, rows)
    ground_dist = grounding_distribution(rows)

    summary_rows = [
        ["Completed runs", f"{metrics.n_runs} / {PHASE0_EXPECTED_RUNS}"],
        ["Success rate", f"{metrics.success_rate:.3f} [{metrics.success_wilson_low:.3f}, {metrics.success_wilson_high:.3f}]"],
        ["Mean runtime (s)", f"{mean(durs):.1f}" if durs else "—"],
        ["Median runtime (s)", f"{median(durs):.1f}" if durs else "—"],
        ["Mean cost (USD)", f"{mean(costs):.4f}" if costs else "—"],
        ["Mean tokens", f"{mean(tokens):.0f}" if tokens else "—"],
        ["Instruction read rate", f"{metrics.instruction_read_rate:.3f}"],
        ["Anchor attempt rate", f"{metrics.anchor_attempt_rate:.3f}"],
        ["Mean files modified", f"{metrics.files_modified_mean:.2f}"],
        ["Median files modified", f"{metrics.files_modified_median:.1f}"],
    ]

    rep_rows = [[str(int(k)), str(v)] for k, v in sorted(rep_dist.items())]
    ground_rows = [[k, str(v), f"{100 * v / max(len(rows), 1):.1f}%"] for k, v in ground_dist.most_common()]

    body = "\n".join(
        [
            "# RQ5 v2 Phase 0 Dashboard",
            "",
            "Compact summary for TOSEM supplementary reporting.",
            "",
            provenance_block(provenance),
            "",
            "## Summary",
            "",
            _md_table(["Metric", "Value"], summary_rows),
            "",
            "## Repairability distribution (cases)",
            "",
            _md_table(["Score", "Cases"], rep_rows or [["—", "0"]]),
            "",
            "## Grounding distribution (runs)",
            "",
            _md_table(["Category", "Count", "Share"], ground_rows or [["—", "0", "—"]]),
            "",
        ]
    )
    atomic_write_text(path, body)


def write_gate_report(*, gates: list[GateRow], provenance: dict, path: Path) -> None:
    table = [[g.gate, g.target, g.observed, g.status] for g in gates]
    overall = "FAIL" if any(g.status == "FAIL" for g in gates) else (
        "WARN" if any(g.status == "WARN" for g in gates) else "PASS"
    )
    body = "\n".join(
        [
            "# Phase 0 Gate Report",
            "",
            f"**Overall verdict:** **{overall}**",
            "",
            provenance_block(provenance),
            "",
            _md_table(["Gate", "Target", "Observed", "Status"], table),
            "",
        ]
    )
    atomic_write_text(path, body)


def write_failure_taxonomy(*, rows: list[dict], output_dir: Path) -> Counter[str]:
    taxonomy_rows: list[dict] = []
    counts: Counter[str] = Counter()
    for row in rows:
        category = classify_failure(row) if not _bool(row.get("success")) else "Success"
        if category:
            counts[category] += 1
        taxonomy_rows.append(
            {
                "run_id": row.get("run_id", ""),
                "case_id": row.get("case_id", ""),
                "success": row.get("success", ""),
                "failure_category": category or "Success",
                "error_message": (row.get("error_message") or "")[:200],
                "timed_out": row.get("timed_out", ""),
                "instruction_read": row.get("instruction_read", ""),
                "anchor_attempted": row.get("anchor_attempted", ""),
            }
        )

    csv_path = output_dir / "phase0_failure_taxonomy.csv"
    if taxonomy_rows:
        buf = StringIO()
        writer = csv.DictWriter(buf, fieldnames=list(taxonomy_rows[0].keys()))
        writer.writeheader()
        writer.writerows(taxonomy_rows)
        atomic_write_text(csv_path, buf.getvalue())

    failed = sum(1 for r in rows if not _bool(r.get("success")))
    summary_lines = [
        "# Phase 0 Failure Taxonomy Summary",
        "",
        f"Failed runs: **{failed}** / {len(rows)}",
        "",
    ]
    for cat in FAILURE_CATEGORIES:
        c = counts.get(cat, 0)
        pct = 100 * c / failed if failed else 0.0
        summary_lines.append(f"- **{cat}**: {c} ({pct:.1f}% of failures)")
    if counts.get("Success"):
        summary_lines.append(f"- **Success**: {counts['Success']}")
    summary_lines.append("")
    atomic_write_text(output_dir / "phase0_failure_summary.md", "\n".join(summary_lines))
    return counts


def write_trace_quality(*, rows: list[dict], provenance: dict, path: Path) -> None:
    funnel = compute_funnel(rows)
    transitions = funnel_transitions(rows)
    n = max(funnel["all_runs"], 1)

    trace_rows = [
        ["instruction_read", str(funnel["instruction_read"]), f"{100 * funnel['instruction_read'] / n:.1f}%"],
        ["M1 anchor_attempted", str(funnel["M1_anchor_attempted"]), f"{100 * funnel['M1_anchor_attempted'] / n:.1f}%"],
        ["M2 bind_failure", str(funnel["M2_bind_failure"]), f"{100 * funnel['M2_bind_failure'] / n:.1f}%"],
        ["M3 grounding_action", str(funnel["M3_grounding_action"]), f"{100 * funnel['M3_grounding_action'] / n:.1f}%"],
        ["M4 repair_success", str(funnel["M4_repair_success"]), f"{100 * funnel['M4_repair_success'] / n:.1f}%"],
    ]
    self_repair = sum(_bool(r.get("instruction_self_repair")) for r in rows)

    trans_rows = [[k, str(v)] for k, v in sorted(transitions.items(), key=lambda x: -x[1])]

    body = "\n".join(
        [
            "# Phase 0 Trace Quality Report",
            "",
            provenance_block(provenance),
            "",
            "## M1→M2→M3→M4 funnel",
            "",
            _md_table(["Stage", "Count", "Share"], trace_rows),
            "",
            f"- **instruction_self_repair** (runs): {self_repair} ({100 * self_repair / n:.1f}%)",
            "",
            "## Path confusion table (sequential trace flags)",
            "",
            _md_table(["Path", "Runs"], trans_rows[:15]),
            "",
        ]
    )
    atomic_write_text(path, body)


def run_phase0_analysis(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    manifest_path: Path | None = None,
    repo_root: Path | None = None,
) -> dict[str, Path]:
    """Run full Phase 0 post-processing pipeline (no agent execution)."""
    output_dir = Path(output_dir)
    manifest_path = manifest_path or output_dir / "factorial_case_manifest.json"
    repo_root = repo_root or Path.cwd()
    results_csv = output_dir / "phase0_results.csv"
    trace_audit_csv = output_dir / "phase0_trace_audit.csv"
    traces_dir = output_dir / "phase0_traces"
    audit_csv = output_dir / "phase0_case_audit.csv"

    provenance = collect_provenance(
        manifest_path=manifest_path,
        script_paths=ANALYSIS_SCRIPTS,
        cwd=repo_root,
    )

    raw_rows = load_results(results_csv)
    rows = enrich_rows(rows=raw_rows, manifest_path=manifest_path, traces_dir=traces_dir)
    audit = load_audit(audit_csv)
    metrics = compute_phase0_metrics(rows)
    gates = evaluate_gates(rows=rows, metrics=metrics, audit=audit, manifest_path=manifest_path)

    paths: dict[str, Path] = {}

    paths["dashboard"] = output_dir / "phase0_dashboard.md"
    write_dashboard(rows=rows, metrics=metrics, audit=audit, provenance=provenance, path=paths["dashboard"])

    paths["gate_report"] = output_dir / "phase0_gate_report.md"
    write_gate_report(gates=gates, provenance=provenance, path=paths["gate_report"])

    failure_counts = write_failure_taxonomy(rows=rows, output_dir=output_dir)
    paths["failure_taxonomy"] = output_dir / "phase0_failure_taxonomy.csv"
    paths["failure_summary"] = output_dir / "phase0_failure_summary.md"

    paths["trace_quality"] = output_dir / "phase0_trace_quality.md"
    write_trace_quality(rows=rows, provenance=provenance, path=paths["trace_quality"])

    power_body = power_update(rows=rows, metrics=metrics)
    paths["power_update"] = output_dir / "phase1_power_update.md"
    atomic_write_text(
        paths["power_update"],
        power_body + "\n" + provenance_block(provenance) + "\n",
    )

    editor_body = editorial_decision(
        gates=gates, metrics=metrics, rows=rows, failure_counts=failure_counts
    )
    paths["editorial_decision"] = output_dir / "phase0_editorial_decision.md"
    atomic_write_text(
        paths["editorial_decision"],
        editor_body + provenance_block(provenance) + "\n",
    )

    # Figures
    paths["fig_success"] = output_dir / "success_rate.pdf"
    render_success_rate(
        success_rate=metrics.success_rate,
        wilson_low=metrics.success_wilson_low,
        wilson_high=metrics.success_wilson_high,
        path=paths["fig_success"],
    )
    durs = [_float(r.get("execution_time_seconds")) for r in rows]
    costs = [_float(r.get("cost_usd")) for r in rows if r.get("cost_usd") not in (None, "")]
    paths["fig_runtime"] = output_dir / "runtime_distribution.pdf"
    render_distribution(
        values=durs,
        path=paths["fig_runtime"],
        title="Phase 0 — runtime distribution",
        xlabel="Execution time (s)",
    )
    paths["fig_cost"] = output_dir / "cost_distribution.pdf"
    render_distribution(
        values=costs,
        path=paths["fig_cost"],
        title="Phase 0 — cost distribution",
        xlabel="Cost (USD)",
    )
    funnel = compute_funnel(rows)
    paths["fig_grounding"] = output_dir / "grounding_funnel.pdf"
    render_funnel(
        stages=[
            ("Read", funnel["instruction_read"]),
            ("M1", funnel["M1_anchor_attempted"]),
            ("M2", funnel["M2_bind_failure"]),
            ("M3", funnel["M3_grounding_action"]),
            ("M4", funnel["M4_repair_success"]),
        ],
        path=paths["fig_grounding"],
        title="Phase 0 — grounding funnel",
    )
    paths["fig_repair"] = output_dir / "repair_funnel.pdf"
    render_funnel(
        stages=[
            ("M2 bind fail", funnel["M2_bind_failure"]),
            ("M3 grounding", funnel["M3_grounding_action"]),
            ("M4 repair", funnel["M4_repair_success"]),
            ("Success", sum(_bool(r.get("success")) for r in rows)),
        ],
        path=paths["fig_repair"],
        title="Phase 0 — repair funnel",
    )

    paths["provenance"] = output_dir / "phase0_analysis_provenance.json"
    atomic_write_text(paths["provenance"], provenance_json(provenance))

    return paths


def main() -> int:
    paths = run_phase0_analysis()
    for label, path in sorted(paths.items()):
        print(f"{label} -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
