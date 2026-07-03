"""Figures for RQ5 uptake analysis."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from artifact_lab.execution.atomic_io import atomic_replace
from artifact_lab.experiments.truth_decay.rq5_experiment.uptake_analysis import (
    UptakeClassification,
    uptake_flow_counts,
)


def _save(fig, path: Path) -> None:
    tmp = path.with_name(path.name + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(tmp, format="pdf", bbox_inches="tight", dpi=300)
    atomic_replace(tmp, path)


def render_figure_uptake_flow(classifications: list[UptakeClassification], path: Path) -> None:
    flow = uptake_flow_counts(classifications)
    stages = [
        "instruction_present",
        "instruction_read",
        "instruction_quoted",
        "instruction_followed",
        "task_success",
    ]
    labels = [s.replace("_", "\n") for s in stages]
    x = range(len(stages))
    width = 0.35

    n_a = sum(1 for r in classifications if r.condition == "A") or 1
    n_b = sum(1 for r in classifications if r.condition == "B") or 1
    rates_a = [flow["A"][stage] / n_a for stage in stages]
    rates_b = [flow["B"][stage] / n_b for stage in stages]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar([xi - width / 2 for xi in x], rates_a, width=width, label="Condition A (truthful)", color="#2E86AB")
    ax.bar([xi + width / 2 for xi in x], rates_b, width=width, label="Condition B (false claim)", color="#C0392B")
    ax.set_xticks(list(x), labels, fontsize=9)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Fraction of runs reaching stage")
    ax.set_title("RQ5 uptake funnel — instruction causal path")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    _save(fig, path)
    plt.close(fig)
