"""TOSEM go/no-go report from P1 and P2 pilot outputs."""

from __future__ import annotations

import csv
import statistics
from collections import Counter
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text


def _read_summary_csv(path: Path) -> list[dict]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _read_metric_rows(path: Path) -> dict[str, float]:
    rows = _read_summary_csv(path)
    out: dict[str, float] = {}
    for row in rows:
        metric = row.get("metric", "")
        try:
            out[metric] = float(row.get("value", 0))
        except ValueError:
            continue
    return out


def _p1_stats(summary_csv: Path) -> dict:
    rows = _read_summary_csv(summary_csv)
    if not rows:
        return {}
    n_files = len(rows)
    with_verifiable = sum(1 for r in rows if int(r.get("verifiable_references", 0)) > 0)
    refs = [int(r["total_references"]) for r in rows]
    verifiable = [int(r["verifiable_references"]) for r in rows]
    extraction_failures = sum(1 for r in rows if r.get("extraction_ok") == "false")
    return {
        "n_files": n_files,
        "with_verifiable_pct": 100 * with_verifiable / n_files if n_files else 0,
        "median_refs": statistics.median(refs) if refs else 0,
        "median_verifiable": statistics.median(verifiable) if verifiable else 0,
        "extraction_failures": extraction_failures,
        "group_counts": Counter(r.get("family_group", "") for r in rows),
    }


def run_go_no_go_report(*, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "go_no_go.md"

    p1_summary = output_dir / "reference_summary.csv"
    p2_summary = output_dir / "agent_attribution_summary.csv"
    p1 = _p1_stats(p1_summary)
    p2 = _read_metric_rows(p2_summary)

    p1_density_ok = (
        p1.get("with_verifiable_pct", 0) >= 40
        and p1.get("median_verifiable", 0) >= 1
        and p1.get("extraction_failures", 0) <= max(1, p1.get("n_files", 1)) * 0.05
    )
    p2_signal_rate = p2.get("signal_rate_pct", 0)
    p2_files_signal = p2.get("files_with_agent_signal", 0)
    p2_files_total = max(1, p2.get("instruction_files_touched", 1))
    p2_attribution_ok = p2_signal_rate >= 5 and (p2_files_signal / p2_files_total * 100) >= 10

    if p1_density_ok and p2_attribution_ok:
        overall = "GO"
    elif p1_density_ok or p2_attribution_ok:
        overall = "CONDITIONAL GO"
    else:
        overall = "NO-GO"

    lines = [
        "# TOSEM Go/No-Go — Half-Life of Truth",
        "",
        f"**Overall recommendation:** **{overall}**",
        "",
        "## P1 — Reference density",
        "",
        f"- Files sampled: **{int(p1.get('n_files', 0))}**",
        f"- Files with ≥1 verifiable reference: **{p1.get('with_verifiable_pct', 0):.1f}%**",
        f"- Median verifiable references per file: **{p1.get('median_verifiable', 0):.1f}**",
        f"- Extraction failures: **{int(p1.get('extraction_failures', 0))}**",
        f"- Density sufficient for truth-decay study? **{'Yes' if p1_density_ok else 'Marginal / needs refinement'}**",
        "",
        "### RQs supported by P1",
        "- **RQ_truth_decay:** Do machine-consumed instruction files encode verifiable claims that go stale?",
        "- **RQ_reference_half_life:** What fraction of path/directory/script/dependency references fail at HEAD?",
        "",
        "### RQs to drop or defer (P1)",
        "- Adoption prevalence at ecosystem scale (original E1 census) — defer unless reframed as covariate.",
        "- Semantic truth / LLM-judged correctness — not validated here; defer to L5.",
        "",
        "## P2 — Agent attribution",
        "",
        f"- Commits scanned: **{int(p2.get('commits_scanned', 0))}**",
        f"- Candidate agent-authored: **{int(p2.get('candidate_agent_authored', 0))}**",
        f"- Candidate agent-co-authored: **{int(p2.get('candidate_agent_coauthored', 0))}**",
        f"- Signal rate: **{p2_signal_rate:.1f}%**",
        f"- Files with agent signal: **{int(p2_files_signal)}** ({p2_files_signal / p2_files_total * 100:.1f}%)",
        f"- Attribution sufficient for self-maintenance RQ? **{'Yes' if p2_attribution_ok else 'Marginal / needs refinement'}**",
        "",
        "### RQs supported by P2",
        "- **RQ_self_maintenance:** Are instruction-file changes disproportionately agent-co-authored?",
        "- **RQ_agent_vs_human_decay:** Do agent-maintained files show different reference staleness?",
        "",
        "### RQs to drop or defer (P2)",
        "- Binary agent/human without attribution metadata — signal too weak alone.",
        "",
        "## Recommended next step",
    ]

    if overall == "GO":
        lines.append(
            "1. Design longitudinal protocol: resample instruction files at T+Δ, remeasure reference verification."
        )
        lines.append("2. Join P1 audit rows with P2 attribution on (repo_id, instruction_path).")
        lines.append("3. Keep E1-1000 frozen; extend only via targeted re-extraction for longitudinal panel.")
    elif overall == "CONDITIONAL GO":
        if not p1_density_ok:
            lines.append("1. Improve reference extraction (script names, dependency manifests) before scaling.")
        if not p2_attribution_ok:
            lines.append("2. Expand attribution patterns or add commit-trailer mining before self-maintenance RQ.")
        lines.append("3. Re-run go/no-go pilot after refinements; do not scale E1-1000 yet.")
    else:
        lines.append("1. Do not pivot TOSEM paper to truth-decay yet.")
        lines.append("2. Revisit detector families or instruction-file corpus quality.")
        lines.append("3. Keep laboratory; retain E1 engineering cohort for alternative framing.")

    lines.append("")
    atomic_write_text(report_path, "\n".join(lines))
    return report_path
