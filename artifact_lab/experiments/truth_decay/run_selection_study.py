"""Run matched observational study for the selection hypothesis."""

from __future__ import annotations

import csv
from dataclasses import asdict
from io import StringIO
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.truth_decay.selection_figures import (
    render_figure_selection_churn,
    render_figure_selection_matched_effect,
    render_figure_selection_survival,
)
from artifact_lab.experiments.truth_decay.selection_study import (
    METRIC_LABELS,
    SelectionMatchPair,
    SelectionStudyStatistics,
    build_selection_pairs,
    compute_selection_statistics,
)
from artifact_lab.experiments.truth_pilots.gates_common import DEFAULT_RQ1_LONGITUDINAL

DEFAULT_EXPORT = Path("exports/truth_decay_pilot")


def _write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        atomic_write_text(path, "")
        return
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    atomic_write_text(path, buffer.getvalue())


def _format_metric_row(effect) -> list[str]:
    label = METRIC_LABELS.get(effect.metric, effect.metric)
    ci_crosses_zero = effect.mean_difference_ci_low <= 0 <= effect.mean_difference_ci_high
    sig = effect.permutation_p_value < 0.05
    return [
        f"### {label}",
        "",
        f"- Referenced mean: **{effect.referenced_mean:.4f}**",
        f"- Control mean: **{effect.control_mean:.4f}**",
        f"- Paired difference (referenced − control): **{effect.mean_difference:.4f}**",
        f"  (95% bootstrap CI: {effect.mean_difference_ci_low:.4f}–{effect.mean_difference_ci_high:.4f})",
        f"- Standardized mean difference (Cohen's d): **{effect.cohens_d:.4f}**",
        f"- Permutation p-value ({effect.alternative}-tailed): **{effect.permutation_p_value:.6f}**",
        f"- Fraction favoring referenced stability: **{100 * effect.referenced_favorable_fraction:.1f}%**",
        f"  (95% bootstrap CI: {100 * effect.referenced_favorable_ci_low:.1f}%–"
        f"{100 * effect.referenced_favorable_ci_high:.1f}%)",
        f"- Bootstrap CI crosses zero: **{'yes' if ci_crosses_zero else 'no'}**",
        f"- Permutation significant at α=0.05: **{'yes' if sig else 'no'}**",
        "",
    ]


def _summary_markdown(*, stats: SelectionStudyStatistics, seed: int) -> str:
    lines = [
        "# Selection Hypothesis — Matched Observational Study",
        "",
        "## Research question",
        "",
        "Are files referenced by machine-consumable instruction files intrinsically more stable",
        "than comparable files inside the same repository?",
        "",
        "## Design",
        "",
        "Observational matched-pair study. For each file-level reference in the longitudinal panel:",
        "",
        "1. **Treatment:** referenced path (`path`, `script_name`).",
        "2. **Control:** never-referenced path in the same repository at panel start, matched on:",
        "   - file extension",
        "   - directory depth (±1 level)",
        "   - creation period (first-commit timestamp, when available)",
        "   - file size at panel start (when available)",
        "3. **Outcomes (panel window):** active lifetime, commit churn, rename frequency,",
        "   deletion before panel end, survival until panel end.",
        "4. **Inference:** paired differences, bootstrap 95% CIs, Cohen's d, sign-flip permutation tests.",
        "",
        f"- Random seed: **{seed}**",
        f"- Matched pairs: **{stats.n_pairs}**",
        f"- Repositories: **{stats.n_repos}**",
        "",
        "## Results",
        "",
    ]
    for effect in stats.metrics:
        lines.extend(_format_metric_row(effect))

    lines.extend(
        [
            "## Interpretation",
            "",
            "Negative paired differences on churn, rename, and deletion (and positive on lifetime",
            "and survival) support the **selection hypothesis**: instruction files disproportionately",
            "reference intrinsically stable repository paths rather than volatile ones.",
            "",
            "This study does not modify prior RQ outputs (`cited_uncited_*`, RQ1–RQ4).",
            "",
            "## Outputs",
            "",
            "- `rq_selection_dataset.csv`",
            "- `figure_selection_churn.pdf`",
            "- `figure_selection_survival.pdf`",
            "- `figure_selection_matched_effect.pdf`",
            "",
        ]
    )
    return "\n".join(lines)


def run_selection_study(
    *,
    longitudinal_csv: Path = DEFAULT_RQ1_LONGITUDINAL,
    scratch_dir: Path = Path("scratch"),
    output_dir: Path = DEFAULT_EXPORT,
    max_referenced_per_repo: int | None = None,
    seed: int = 42,
    clone_timeout: int = 600,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "dataset_csv": output_dir / "rq_selection_dataset.csv",
        "summary_md": output_dir / "rq_selection_summary.md",
        "figure_churn": output_dir / "figure_selection_churn.pdf",
        "figure_survival": output_dir / "figure_selection_survival.pdf",
        "figure_effect": output_dir / "figure_selection_matched_effect.pdf",
    }

    print("selection study: building matched pairs (git clones required)", flush=True)
    pairs = build_selection_pairs(
        longitudinal_csv=longitudinal_csv,
        scratch_dir=scratch_dir,
        max_referenced_per_repo=max_referenced_per_repo,
        seed=seed,
        clone_timeout=clone_timeout,
    )
    stats = compute_selection_statistics(pairs, seed=seed)

    _write_csv([asdict(p) for p in pairs], paths["dataset_csv"])
    atomic_write_text(paths["summary_md"], _summary_markdown(stats=stats, seed=seed))

    render_figure_selection_churn(pairs, paths["figure_churn"])
    render_figure_selection_survival(pairs, paths["figure_survival"])
    render_figure_selection_matched_effect(stats.metrics, paths["figure_effect"])

    print(
        f"selection study complete: pairs={stats.n_pairs}, repos={stats.n_repos}",
        flush=True,
    )
    return paths
