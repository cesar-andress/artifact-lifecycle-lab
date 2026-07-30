"""Lightweight read-only monitoring for in-progress Phase 0 calibration."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean, median

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.rq5_v2.phase0_analysis import classify_failure
from artifact_lab.experiments.rq5_v2.phase0_run import DEFAULT_OUTPUT_DIR, PHASE0_EXPECTED_RUNS

PHASE0_EXPECTED_CASES = 20
MIN_RUNS_FOR_RATE_WARNINGS = 15
MAX_CONSECUTIVE_INFRA = 3


@dataclass(frozen=True)
class Phase0StatusSnapshot:
    completed_runs: int
    completed_cases: int
    success_rate: float
    instruction_read_rate: float
    anchor_attempt_rate: float
    timeout_rate: float
    infra_toolchain_rate: float
    median_files_modified: float
    mean_cost_per_run: float
    cumulative_cost: float
    estimated_remaining_cost: float
    mean_runtime_seconds: float
    estimated_eta_utc: str | None
    last_run_id: str
    last_case_id: str
    last_failure_reason: str
    warnings: list[str]
    provisional: bool
    log_tail: str


def _bool(value: object) -> bool:
    return str(value).lower() in ("true", "1", "yes")


def _float(value: object, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def load_results_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_log_tail(path: Path, *, max_lines: int = 5) -> str:
    if not path.exists():
        return "(log not found)"
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return "(log unreadable)"
    tail = [ln.strip() for ln in lines if ln.strip()][-max_lines:]
    return "\n".join(tail) if tail else "(log empty)"


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _max_consecutive_infrastructure(rows: list[dict]) -> int:
    streak = 0
    best = 0
    for row in rows:
        if _bool(row.get("success")):
            streak = 0
            continue
        if classify_failure(row) == "Infrastructure":
            streak += 1
            best = max(best, streak)
        else:
            streak = 0
    return best


def compute_warnings(*, rows: list[dict], snapshot_metrics: dict[str, float]) -> list[str]:
    warnings: list[str] = []
    n = len(rows)

    consec = _max_consecutive_infrastructure(rows)
    if consec > MAX_CONSECUTIVE_INFRA:
        warnings.append(
            f"WARN: {consec} consecutive infrastructure failures (threshold >{MAX_CONSECUTIVE_INFRA})"
        )

    if n < MIN_RUNS_FOR_RATE_WARNINGS:
        return warnings

    sr = snapshot_metrics["success_rate"]
    if sr < 0.30 or sr > 0.85:
        warnings.append(f"WARN: success rate {sr:.3f} outside [0.30, 0.85] (n={n})")

    aa = snapshot_metrics["anchor_attempt_rate"]
    if aa < 0.60:
        warnings.append(f"WARN: anchor_attempt rate {aa:.3f} < 0.60 (n={n})")

    ir = snapshot_metrics["instruction_read_rate"]
    if ir < 0.90:
        warnings.append(f"WARN: instruction_read rate {ir:.3f} < 0.90 (n={n})")

    infra_rate = snapshot_metrics["infra_toolchain_rate"]
    if infra_rate > 0.20:
        warnings.append(
            f"WARN: infrastructure/toolchain failure rate {infra_rate:.3f} > 0.20 (n={n})"
        )

    med_files = snapshot_metrics["median_files_modified"]
    if med_files > 20:
        warnings.append(f"WARN: median files_modified {med_files:.1f} > 20 (n={n})")

    return warnings


def build_status_snapshot(
    *,
    rows: list[dict],
    log_tail: str = "",
) -> Phase0StatusSnapshot:
    n = len(rows)
    cases = {r.get("case_id", "") for r in rows if r.get("case_id")}
    successes = sum(_bool(r.get("success")) for r in rows)
    read_hits = sum(_bool(r.get("instruction_read")) for r in rows)
    anchor_hits = sum(_bool(r.get("anchor_attempted")) for r in rows)
    timeouts = sum(
        _bool(r.get("timed_out")) or "timeout" in str(r.get("error_message", "")).lower()
        for r in rows
    )
    infra_tool = sum(
        1
        for r in rows
        if not _bool(r.get("success"))
        and classify_failure(r) in {"Infrastructure", "Toolchain"}
    )
    files = [_float(r.get("files_modified")) for r in rows]
    costs = [_float(r.get("cost_usd")) for r in rows if r.get("cost_usd") not in (None, "")]
    durs = [_float(r.get("execution_time_seconds")) for r in rows]

    success_rate = _rate(successes, n)
    instruction_read_rate = _rate(read_hits, n)
    anchor_attempt_rate = _rate(anchor_hits, n)
    timeout_rate = _rate(timeouts, n)
    infra_toolchain_rate = _rate(infra_tool, n)
    median_files = median(files) if files else 0.0
    mean_cost = mean(costs) if costs else 0.0
    cumulative = sum(costs)
    mean_runtime = mean(durs) if durs else 0.0
    remaining = max(PHASE0_EXPECTED_RUNS - n, 0)
    est_remaining_cost = mean_cost * remaining

    eta: str | None = None
    if mean_runtime > 0 and remaining > 0:
        eta_dt = datetime.now(timezone.utc) + timedelta(seconds=mean_runtime * remaining)
        eta = eta_dt.isoformat()

    last_run_id = ""
    last_case_id = ""
    last_failure = ""
    if rows:
        last = rows[-1]
        last_run_id = str(last.get("run_id", ""))
        last_case_id = str(last.get("case_id", ""))
        if not _bool(last.get("success")):
            last_failure = (last.get("error_message") or "").strip()[:300]
        else:
            for row in reversed(rows):
                if not _bool(row.get("success")):
                    last_failure = (row.get("error_message") or "").strip()[:300]
                    break

    metrics = {
        "success_rate": success_rate,
        "anchor_attempt_rate": anchor_attempt_rate,
        "instruction_read_rate": instruction_read_rate,
        "infra_toolchain_rate": infra_toolchain_rate,
        "median_files_modified": median_files,
    }
    warnings = compute_warnings(rows=rows, snapshot_metrics=metrics)

    return Phase0StatusSnapshot(
        completed_runs=n,
        completed_cases=len(cases),
        success_rate=success_rate,
        instruction_read_rate=instruction_read_rate,
        anchor_attempt_rate=anchor_attempt_rate,
        timeout_rate=timeout_rate,
        infra_toolchain_rate=infra_toolchain_rate,
        median_files_modified=median_files,
        mean_cost_per_run=mean_cost,
        cumulative_cost=cumulative,
        estimated_remaining_cost=est_remaining_cost,
        mean_runtime_seconds=mean_runtime,
        estimated_eta_utc=eta,
        last_run_id=last_run_id,
        last_case_id=last_case_id,
        last_failure_reason=last_failure,
        warnings=warnings,
        provisional=n < PHASE0_EXPECTED_RUNS,
        log_tail=log_tail,
    )


def render_status_markdown(snapshot: Phase0StatusSnapshot) -> str:
    ts = datetime.now(timezone.utc).isoformat()
    lines = [
        "# RQ5 v2 Phase 0 — Live Status",
        "",
        f"**Updated (UTC):** {ts}",
        "",
    ]
    if snapshot.provisional:
        lines.extend(
            [
                "> **Provisional:** fewer than 60 runs complete — do not treat metrics as final calibration.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "> **Run count complete (60/60).** Use `make rq5-v2-phase0-analysis` for final gate evaluation.",
                "",
            ]
        )

    lines.extend(
        [
            "## Progress",
            "",
            f"- Completed runs: **{snapshot.completed_runs} / {PHASE0_EXPECTED_RUNS}**",
            f"- Completed cases: **{snapshot.completed_cases} / {PHASE0_EXPECTED_CASES}**",
            "",
            "## Current metrics",
            "",
            f"- Success rate: **{snapshot.success_rate:.3f}**",
            f"- Instruction read rate: **{snapshot.instruction_read_rate:.3f}**",
            f"- Anchor attempt rate: **{snapshot.anchor_attempt_rate:.3f}**",
            f"- Timeout rate: **{snapshot.timeout_rate:.3f}**",
            f"- Infrastructure/toolchain failure rate: **{snapshot.infra_toolchain_rate:.3f}**",
            f"- Median files modified: **{snapshot.median_files_modified:.1f}**",
            "",
            "## Cost & runtime",
            "",
            f"- Mean cost per run: **${snapshot.mean_cost_per_run:.4f}**",
            f"- Cumulative cost: **${snapshot.cumulative_cost:.4f}**",
            f"- Estimated remaining cost: **${snapshot.estimated_remaining_cost:.4f}**",
            f"- Mean runtime: **{snapshot.mean_runtime_seconds:.1f} s**",
        ]
    )
    if snapshot.estimated_eta_utc:
        lines.append(f"- Estimated ETA (UTC): **{snapshot.estimated_eta_utc}**")
    else:
        lines.append("- Estimated ETA: **—** (insufficient runtime data)")

    lines.extend(
        [
            "",
            "## Last completed run",
            "",
            f"- Run ID: `{snapshot.last_run_id or '—'}`",
            f"- Case ID: `{snapshot.last_case_id or '—'}`",
        ]
    )
    if snapshot.last_failure_reason:
        lines.extend(
            [
                "",
                "## Last failure reason",
                "",
                f"```",
                snapshot.last_failure_reason,
                "```",
            ]
        )

    lines.extend(["", "## Warning flags", ""])
    if snapshot.warnings:
        for w in snapshot.warnings:
            lines.append(f"- {w}")
    else:
        lines.append("- None")

    lines.extend(["", "## Recent log tail", "", "```", snapshot.log_tail, "```", ""])
    return "\n".join(lines)


def run_phase0_status(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> Path:
    """Read ledger exports and write phase0_status.md (read-only)."""
    results_csv = output_dir / "phase0_results.csv"
    run_log = output_dir / "phase0_run.log"
    trace_audit_csv = output_dir / "phase0_trace_audit.csv"
    trace_audit_rows = load_results_csv(trace_audit_csv) if trace_audit_csv.exists() else []

    rows = load_results_csv(results_csv)
    log_tail = read_log_tail(run_log)
    if trace_audit_csv.exists():
        log_tail = (
            f"{log_tail}\n(trace_audit rows: {len(trace_audit_rows)}, "
            f"results rows: {len(rows)})"
        ).strip()
    snapshot = build_status_snapshot(rows=rows, log_tail=log_tail)
    out_path = output_dir / "phase0_status.md"
    atomic_write_text(out_path, render_status_markdown(snapshot))
    return out_path


def main() -> int:
    path = run_phase0_status()
    print(f"status -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
