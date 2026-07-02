"""Run cited vs uncited path churn contrast audit."""

from __future__ import annotations

import csv
from dataclasses import asdict
from io import StringIO
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.truth_decay.cited_uncited_churn import (
    PathChurnPair,
    build_cited_uncited_pairs,
    compute_churn_contrast_statistics,
)
from artifact_lab.experiments.truth_decay.cited_uncited_figures import (
    render_figure_churn_difference_hist,
    render_figure_cited_uncited_churn,
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


def _summary_markdown(*, stats, pairs: list[PathChurnPair]) -> str:
    stable_pct = 100 * stats.cited_more_stable_fraction
    stable_lo = 100 * stats.cited_more_stable_ci_low
    stable_hi = 100 * stats.cited_more_stable_ci_high
    if stats.mean_difference_ci_low <= 0 <= stats.mean_difference_ci_high:
        mean_claim = "Mean git churn is **not significantly different** between groups (bootstrap CI crosses zero)."
    elif stats.mean_difference < 0:
        mean_claim = "Mean git churn is **lower for cited paths** than matched uncited controls."
    else:
        mean_claim = "Mean git churn is **higher for cited paths** than matched uncited controls."

    if stats.cited_more_stable_ci_low >= 0.5:
        stability_claim = (
            f"In **{stable_pct:.1f}%** of matched pairs, cited paths churn less than or equal to "
            "their uncited controls — evidence that instruction files disproportionately reference "
            "intrinsically stable paths (selection effect)."
        )
    else:
        stability_claim = "No strong evidence that cited paths are intrinsically more stable than matched controls."

    lines = [
        "# Cited vs Uncited Path Churn Contrast",
        "",
        "## Purpose",
        "",
        "Test whether paths referenced in AI instruction files are intrinsically more stable",
        "than comparable non-referenced paths in the same repositories.",
        "",
        "## Design",
        "",
        "- **Cited paths:** file-level references (`path`, `script_name`) from the longitudinal panel.",
        "- **Controls:** same-extension, depth-matched paths present in the repo tree at panel start,",
        "  never cited in instruction files for that repository.",
        "- **Churn metric:** count of git commits touching the path between panel start and end commits.",
        "- **Matching:** up to 40 cited paths sampled per repository (fixed seed).",
        "",
        "## Sample",
        "",
        f"- Matched pairs analyzed: **{stats.n_pairs}**",
        f"- Repositories represented: **{stats.n_repos}**",
        f"- Mean cited verification rate (longitudinal): **{100 * stats.cited_mean_verified_rate:.1f}%**",
        "",
        "## Results",
        "",
        f"- Mean cited churn: **{stats.cited_mean_churn:.2f}** commits",
        f"  (95% bootstrap CI: {stats.cited_mean_churn_ci_low:.2f}–{stats.cited_mean_churn_ci_high:.2f})",
        f"- Mean uncited churn: **{stats.uncited_mean_churn:.2f}** commits",
        f"  (95% bootstrap CI: {stats.uncited_mean_churn_ci_low:.2f}–{stats.uncited_mean_churn_ci_high:.2f})",
        f"- Mean paired difference (cited − uncited): **{stats.mean_difference:.2f}**",
        f"  (95% bootstrap CI: {stats.mean_difference_ci_low:.2f}–{stats.mean_difference_ci_high:.2f})",
        f"- Fraction of pairs where cited churn ≤ uncited churn: **{stable_pct:.1f}%**",
        f"  (95% bootstrap CI: {stable_lo:.1f}%–{stable_hi:.1f}%)",
        "",
        "## Interpretation",
        "",
        mean_claim,
        "",
        stability_claim,
        "",
        "Mean and paired analyses can diverge when a minority of pairs have extreme churn; ",
        "the paired stability fraction is the primary test of intrinsic stability.",
        "",
        "## Limitations",
        "",
        "- Matching uses extension and directory depth only (not LOC or team ownership).",
        "- Churn counts depend on git history availability in bare clones.",
        "- Does not modify prior RQ outputs.",
        "",
        "## Outputs",
        "",
        "- `cited_uncited_comparison.csv`",
        "- `figure_cited_uncited_churn.pdf`",
        "- `figure_churn_difference_hist.pdf`",
        "",
    ]
    return "\n".join(lines)


def run_cited_uncited_audit(
    *,
    longitudinal_csv: Path = DEFAULT_RQ1_LONGITUDINAL,
    scratch_dir: Path = Path("scratch"),
    output_dir: Path = DEFAULT_EXPORT,
    max_cited_per_repo: int = 40,
    seed: int = 42,
    clone_timeout: int = 180,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "comparison_csv": output_dir / "cited_uncited_comparison.csv",
        "summary_md": output_dir / "cited_uncited_summary.md",
        "figure_violin": output_dir / "figure_cited_uncited_churn.pdf",
        "figure_hist": output_dir / "figure_churn_difference_hist.pdf",
    }

    print("cited-vs-uncited audit: building matched pairs (git clones required)", flush=True)
    pairs = build_cited_uncited_pairs(
        longitudinal_csv=longitudinal_csv,
        scratch_dir=scratch_dir,
        max_cited_per_repo=max_cited_per_repo,
        seed=seed,
        clone_timeout=clone_timeout,
    )
    stats = compute_churn_contrast_statistics(pairs)

    rows = [asdict(p) for p in pairs]
    _write_csv(rows, paths["comparison_csv"])
    atomic_write_text(paths["summary_md"], _summary_markdown(stats=stats, pairs=pairs))

    cited_vals = [float(p.cited_churn_commits) for p in pairs]
    uncited_vals = [float(p.uncited_churn_commits) for p in pairs]
    diffs = [c - u for c, u in zip(cited_vals, uncited_vals)]
    render_figure_cited_uncited_churn(
        cited_values=cited_vals,
        uncited_values=uncited_vals,
        path=paths["figure_violin"],
    )
    render_figure_churn_difference_hist(diffs, paths["figure_hist"])

    print(
        f"cited-vs-uncited complete: pairs={stats.n_pairs}, "
        f"mean_diff={stats.mean_difference}, stable_fraction={stats.cited_more_stable_fraction}",
        flush=True,
    )
    return paths
