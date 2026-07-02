"""Publication figures for cited vs uncited churn contrast."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from artifact_lab.execution.atomic_io import atomic_replace


def _save(fig, path: Path) -> None:
    tmp = path.with_name(path.name + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(tmp, format="pdf", bbox_inches="tight", dpi=300)
    atomic_replace(tmp, path)


def render_figure_cited_uncited_churn(
    *,
    cited_values: list[float],
    uncited_values: list[float],
    path: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(7, 5))
    data = [cited_values, uncited_values]
    positions = [1, 2]
    parts = ax.violinplot(data, positions=positions, showmeans=True, showmedians=True)
    for body in parts["bodies"]:
        body.set_alpha(0.7)
    ax.boxplot(data, positions=positions, widths=0.15, patch_artist=True)
    ax.set_xticks(positions, ["Cited paths", "Matched uncited controls"])
    ax.set_ylabel("Git commits touching path in panel window")
    ax.set_title("Cited vs uncited path churn contrast")
    ax.grid(True, axis="y", alpha=0.3)
    _save(fig, path)
    plt.close(fig)


def render_figure_churn_difference_hist(differences: list[float], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.hist(differences, bins=30, color="#3498DB", edgecolor="white", alpha=0.85)
    ax.axvline(0.0, color="#C0392B", linestyle="--", linewidth=1.5, label="No difference")
    ax.set_xlabel("Cited churn − uncited churn (commits)")
    ax.set_ylabel("Matched path pairs")
    ax.set_title("Paired churn difference (negative = cited more stable)")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    _save(fig, path)
    plt.close(fig)
