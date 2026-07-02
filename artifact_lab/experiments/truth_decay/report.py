"""RQ1 feasibility report generation."""

from __future__ import annotations

from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.truth_decay.stats import RQ1ExploratoryStats


def assess_tosem_viability(stats: RQ1ExploratoryStats) -> tuple[str, str]:
    """Return (verdict, justification) for TOSEM RQ1 support."""
    has_decay = stats.missing_ratio >= 0.05 and stats.first_failure_count >= 10
    has_repair = stats.repair_event_count >= 5
    has_longitudinal = stats.instruction_files >= 50 and stats.total_observations >= 500
    has_density = stats.references_per_file_median >= 1.0

    if has_decay and has_longitudinal and has_density and stats.files_with_decay >= 20:
        if has_repair:
            return (
                "YES",
                "Longitudinal panel shows measurable decay (missing references over time), "
                "non-trivial repair events, and sufficient file/observation density across the cohort.",
            )
        return (
            "PROBABLY",
            "Decay signal is present across many instruction files, but repair dynamics are sparse; "
            "RQ1 is viable with careful framing around staleness rather than self-healing.",
        )

    if has_decay or (stats.missing_ratio >= 0.02 and stats.first_failure_count >= 5):
        return (
            "UNCLEAR",
            "Some decay signal exists, but effect size or cohort coverage may be insufficient for a "
            "standalone TOSEM claim without extending the observation window or cohort.",
        )

    return (
        "NO",
        "Insufficient missing-reference transitions or observation density to support a truth-decay study.",
    )


def generate_rq1_feasibility_report(
    *,
    stats: RQ1ExploratoryStats,
    output_path: Path,
    figure_paths: dict[str, Path],
) -> Path:
    verdict, justification = assess_tosem_viability(stats)

    top_transitions = sorted(
        ((k, v) for k, v in stats.transition_counts.items() if "->" in k and not k.endswith("->REMOVED")),
        key=lambda item: item[1],
        reverse=True,
    )[:8]

    unexpected: list[str] = []
    if stats.repaired_ratio > stats.missing_ratio:
        unexpected.append("Repaired observations exceed missing observations — repairs may be over-counted or decay under-detected.")
    if stats.unverifiable_ratio > 0.5:
        unexpected.append("Majority of observations are UNVERIFIABLE (mostly commands); verifiable decay is concentrated in path-like references.")
    if stats.reference_removals > stats.reference_additions:
        unexpected.append("Reference removals exceed additions — instruction files shed claims faster than they add them.")
    if stats.deleted_ratio > 0.05:
        unexpected.append("Non-trivial DELETED rate — instruction-file death is part of the lifecycle signal.")
    if not unexpected:
        unexpected.append("No major anomalies relative to pilot expectations; decay and repair patterns align with protocol assumptions.")

    lines = [
        "# RQ1 Feasibility Study — Truth Decay",
        "",
        "## 1. Research question",
        "",
        "**RQ1:** How does the truth of machine-consumed documentation evolve over time?",
        "",
        "This milestone reconstructs longitudinal reference states from L1/L1b instruction-file events,",
        "verifies references at each commit snapshot, and reports exploratory decay/repair signals.",
        "",
        "## 2. Observed signals",
        "",
        f"- Instruction files analyzed: **{stats.instruction_files}**",
        f"- Longitudinal observations: **{stats.total_observations}**",
        f"- Median reference observations per file: **{stats.references_per_file_median:.1f}**",
        f"- Verified ratio: **{stats.verified_ratio:.1%}**",
        f"- Missing ratio: **{stats.missing_ratio:.1%}**",
        f"- Repaired ratio: **{stats.repaired_ratio:.1%}**",
        f"- Unverifiable ratio: **{stats.unverifiable_ratio:.1%}**",
        f"- First-failure events: **{stats.first_failure_count}**",
        f"- Repair events: **{stats.repair_event_count}**",
        f"- Files with decay (≥1 missing): **{stats.files_with_decay}**",
        f"- Files with repair: **{stats.files_with_repair}**",
    ]
    if stats.median_time_to_first_missing_days is not None:
        lines.append(
            f"- Median time to first missing reference: **{stats.median_time_to_first_missing_days:.1f} days**"
        )
    if stats.median_repair_latency_days is not None:
        lines.append(f"- Median repair latency: **{stats.median_repair_latency_days:.1f} days**")

    lines.extend(
        [
            "",
            "### Top transitions",
            "",
        ]
    )
    for transition, count in top_transitions:
        lines.append(f"- `{transition}`: {count}")

    lines.extend(
        [
            "",
            "### Figures",
            "",
        ]
    )
    for label, fig_path in figure_paths.items():
        lines.append(f"- {label}: `{fig_path}`")

    lines.extend(
        [
            "",
            "## 3. Unexpected observations",
            "",
        ]
    )
    for item in unexpected:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## 4. Threats to validity",
            "",
            "- Mechanical verification ≠ semantic truth; UNVERIFIABLE commands dominate many files.",
            "- Cohort is pilot + E1-100 engineering frame, not E1-1000 scientific strata.",
            "- Reference extraction recall is regex-bound; false MISSING may reflect extraction noise.",
            "- Repair detection requires a prior MISSING at the same reference key; repo-side fixes without instruction edits are invisible.",
            "- Commit-time tree checks depend on ephemeral bare clones and L1 event completeness.",
            "",
            "## 5. Can RQ1 support a TOSEM paper?",
            "",
            f"**Answer: {verdict}**",
            "",
            justification,
            "",
        ]
    )

    atomic_write_text(output_path, "\n".join(lines))
    return output_path
