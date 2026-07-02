"""RQ3 — observational specification integrity by maintenance regime."""

from __future__ import annotations

import csv
from collections import Counter
from io import StringIO
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.truth_decay.rq3_analysis import (
    build_reference_trajectories,
    compute_regime_metrics,
    compute_transition_matrix,
    trajectory_records_to_rows,
)
from artifact_lab.experiments.truth_decay.rq3_attribution import (
    AGENT_DOMINATED_THRESHOLD,
    build_file_regimes,
    load_attribution_index,
)
from artifact_lab.experiments.truth_decay.rq3_figures import (
    render_figure_birth_integrity,
    render_figure_repair_probability,
    render_figure_transition_matrix,
)
from artifact_lab.experiments.truth_pilots.gates_common import (
    DEFAULT_PILOT_EXPORT,
    DEFAULT_RQ1_LONGITUDINAL,
    load_longitudinal_rows,
)

DEFAULT_EXPORT = Path("exports/truth_decay_pilot")
DEFAULT_ATTRIBUTION = DEFAULT_PILOT_EXPORT / "agent_commit_candidates.csv"


def _write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        atomic_write_text(path, "")
        return
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    atomic_write_text(path, buffer.getvalue())


def _summary_markdown(
    *,
    metrics: list[dict],
    file_regime_counts: Counter[str],
    n_trajectories: int,
    join_rate: float,
) -> str:
    lines = [
        "# RQ3 — Specification Integrity by Maintenance Regime",
        "",
        "## Research question (observational)",
        "",
        "**RQ3:** How does specification integrity differ between human-maintained and",
        "agent-maintained machine-consumable specifications?",
        "",
        "> **No causal claims.** This analysis reports **associations** between git-derived",
        "> maintenance regimes and mechanical reference integrity in the longitudinal panel.",
        "> Regime labels describe **observed commit attribution patterns**, not interventions.",
        "",
        "## Join specification",
        "",
        "- Longitudinal panel: `reference_longitudinal.csv`",
        "- Attribution: `agent_commit_candidates.csv`",
        "- Join key: `(repo_id, instruction_path, commit_sha)`",
        f"- Commit–attribution match rate (unique file commits): **{join_rate:.1%}**",
        "",
        "## Maintenance regime definitions",
        "",
        "File-level regime from commits touching each instruction file (P4 agent-maintenance rules;",
        "Dependabot/Renovate/security bots excluded from agent tally):",
        "",
        f"- **human_only:** 0% agent-maintenance commits among labeled commits",
        f"- **agent_assisted:** 0% < agent share < {AGENT_DOMINATED_THRESHOLD:.0%}",
        f"- **agent_dominated:** agent share ≥ {AGENT_DOMINATED_THRESHOLD:.0%}",
        "- **unknown:** no attribution label for any commit in the file panel",
        "",
        "## File counts by regime",
        "",
    ]
    for regime in ("human_only", "agent_assisted", "agent_dominated", "unknown"):
        lines.append(f"- **{regime}:** {file_regime_counts.get(regime, 0)} instruction files")

    lines.extend(
        [
            "",
            f"- Reference trajectories analyzed: **{n_trajectories}**",
            "",
            "## Estimands (observational proportions)",
            "",
            "| Regime | N (verifiable) | P(verified birth) | P(born-stale) | P(decay\\|verified) | P(repair\\|decay) |",
            "|--------|---------------:|------------------:|--------------:|-------------------:|------------------:|",
        ]
    )
    for m in metrics:
        lines.append(
            f"| {m['maintenance_regime']} | {m['n_verifiable_trajectories']} | "
            f"{m['p_verified_birth']:.3f} | {m['p_born_stale']:.3f} | "
            f"{m['p_decay_given_verified']:.3f} | {m['p_repair_given_decay']:.3f} |"
        )

    lines.extend(
        [
            "",
            "### Construct definitions",
            "",
            "- **Birth integrity index:** P(reference ever reaches VERIFIED | verifiable type)",
            "- **Born-stale:** verifiable reference never VERIFIED in panel (see born-stale autopsy)",
            "- **Decay:** VERIFIED observed, then later MISSING (post-verification)",
            "- **Repair:** decay trajectory with ≥1 repair event or REPAIRED state",
            "",
            "## Threats to validity",
            "",
            "1. **Attribution precision unvalidated (P4 pending):** regime labels inherit heuristic",
            "   git-metadata errors (missing Co-Authored-By, false signatures).",
            "2. **Ecological confounding:** agent-dominated files may differ in project type,",
            "   template reuse, and team maturity — not controlled observationally.",
            "3. **File-level regime aggregation:** birth and decay events may occur under different",
            "   commits than the dominant regime label.",
            "4. **Mechanical integrity ≠ semantic correctness:** VERIFIED is tree membership only.",
            "5. **Born-stale heterogeneity:** stale-at-birth mixes extraction artifacts, templates,",
            "   and genuine false claims (see born-stale autopsy).",
            "6. **Selection bias:** pilot + E1-100 engineering cohort; not population representative.",
            "7. **Repo clustering:** multiple references within repos are not independent;",
            "   proportions are unadjusted for clustering.",
            "8. **Unknown regime mass:** commits without attribution candidates inflate unknown stratum.",
            "9. **No temporal ordering claim:** higher born-stale in agent-dominated files does not",
            "   imply agents *cause* stale references without experimental design (RQ5).",
            "",
            "## Interpretation guardrails",
            "",
            "- Report **differences in observed integrity**, not agent *effects*.",
            "- Stratify future work by born-stale taxonomy before comparing maintenance regimes.",
            "- Do not merge born-stale prevalence with post-verification decay rates.",
            "",
            "## Outputs",
            "",
            "- `rq3_dataset.csv` — per-reference trajectory with regime and integrity flags",
            "- `rq3_tables.csv` — regime metrics + transition counts",
            "- `figure_rq3_birth_integrity.pdf`",
            "- `figure_rq3_repair_probability.pdf`",
            "- `figure_rq3_transition_matrix.pdf`",
            "",
        ]
    )
    return "\n".join(lines)


def run_rq3_observational_analysis(
    *,
    longitudinal_csv: Path = DEFAULT_RQ1_LONGITUDINAL,
    attribution_csv: Path = DEFAULT_ATTRIBUTION,
    output_dir: Path = DEFAULT_EXPORT,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "dataset_csv": output_dir / "rq3_dataset.csv",
        "summary_md": output_dir / "rq3_summary.md",
        "tables_csv": output_dir / "rq3_tables.csv",
        "fig_birth": output_dir / "figure_rq3_birth_integrity.pdf",
        "fig_repair": output_dir / "figure_rq3_repair_probability.pdf",
        "fig_transitions": output_dir / "figure_rq3_transition_matrix.pdf",
    }

    rows = load_longitudinal_rows(longitudinal_csv)
    attribution_index = load_attribution_index(attribution_csv)
    file_regimes = build_file_regimes(rows, attribution_index)

    unique_commits = {
        (r["repo_id"], r["instruction_path"], r["commit"])
        for r in rows
        if not r.get("reference_removed")
    }
    matched = sum(1 for c in unique_commits if c in attribution_index)
    join_rate = matched / len(unique_commits) if unique_commits else 0.0

    records = build_reference_trajectories(rows, file_regimes, attribution_index)
    metrics = compute_regime_metrics(records)
    transitions = compute_transition_matrix(rows, file_regimes)

    combined_tables: list[dict] = []
    for m in metrics:
        combined_tables.append({"section": "regime_metrics", **m})
    for t in transitions:
        combined_tables.append({"section": "state_transition", **t})

    _write_csv(trajectory_records_to_rows(records), paths["dataset_csv"])
    _write_csv(combined_tables, paths["tables_csv"])
    atomic_write_text(
        paths["summary_md"],
        _summary_markdown(
            metrics=metrics,
            file_regime_counts=Counter(file_regimes.values()),
            n_trajectories=len(records),
            join_rate=join_rate,
        ),
    )

    render_figure_birth_integrity(metrics, paths["fig_birth"])
    render_figure_repair_probability(metrics, paths["fig_repair"])
    render_figure_transition_matrix(transitions, paths["fig_transitions"])

    return paths
