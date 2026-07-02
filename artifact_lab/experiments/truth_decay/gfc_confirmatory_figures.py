"""Publication figures for genuine_false_claim confirmatory audit."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from artifact_lab.execution.atomic_io import atomic_replace
from artifact_lab.experiments.truth_decay.gfc_confirmatory import CONFIRMATORY_CATEGORIES


def _save(fig, path: Path) -> None:
    tmp = path.with_name(path.name + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(tmp, format="pdf", bbox_inches="tight", dpi=300)
    atomic_replace(tmp, path)


def render_figure_gfc_confirmatory(category_counts: Counter[str], path: Path) -> None:
    labels = [c.replace("_", "\n") for c in CONFIRMATORY_CATEGORIES]
    values = [category_counts.get(c, 0) for c in CONFIRMATORY_CATEGORIES]
    colors = ["#C0392B", "#E74C3C", "#9B59B6", "#34495E", "#F39C12", "#95A5A6"]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(labels, values, color=colors)
    ax.set_xlabel("Count among prior genuine_false_claim cohort")
    ax.set_title("Confirmatory audit — genuine_false_claim decomposition")
    ax.grid(True, axis="x", alpha=0.3)
    _save(fig, path)
    plt.close(fig)
