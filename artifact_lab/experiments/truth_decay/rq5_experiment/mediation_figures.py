"""Figures for RQ5 mediation audit."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from artifact_lab.execution.atomic_io import atomic_replace
from artifact_lab.experiments.truth_decay.rq5_experiment.mediation_analysis import (
    CAUSAL_ROLES_B,
    MediationClassification,
    mediation_flow_counts,
)


def _save(fig, path: Path) -> None:
    tmp = path.with_name(path.name + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(tmp, format="pdf", bbox_inches="tight", dpi=300)
    atomic_replace(tmp, path)


def render_figure_rq5_mediation_flow(classifications: list[MediationClassification], path: Path) -> None:
    flow = mediation_flow_counts(classifications)
    b_rows = [r for r in classifications if r.condition == "B"]
    n_b = len(b_rows) or 1

    stages = [
        ("present", "present"),
        ("read", "read"),
        ("quoted", "quoted"),
        ("used", "used in tool"),
        ("obstacle", "obstacle"),
        ("corrected", "corrected"),
        ("failed_because", "failed due\nto claim"),
        ("succeeded_despite", "succeeded\ndespite"),
    ]
    labels = [label for _, label in stages]
    rates = [flow[key] / n_b for key, _ in stages]

    role_counts = Counter(r.causal_role for r in b_rows)
    role_labels = [r.replace("_", "\n") for r in CAUSAL_ROLES_B if role_counts.get(r, 0) > 0]
    role_values = [role_counts[r] for r in CAUSAL_ROLES_B if role_counts.get(r, 0) > 0]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].bar(range(len(labels)), rates, color="#8E44AD")
    axes[0].set_xticks(range(len(labels)), labels, fontsize=8)
    axes[0].set_ylim(0, 1.05)
    axes[0].set_ylabel("Fraction of B runs")
    axes[0].set_title("False-claim mediation funnel (B)")
    axes[0].grid(True, axis="y", alpha=0.3)

    axes[1].barh(role_labels, role_values, color="#C0392B")
    axes[1].set_xlabel("Run count")
    axes[1].set_title("B causal_role distribution")
    axes[1].grid(True, axis="x", alpha=0.3)

    fig.suptitle("RQ5 null-result mediation audit", fontsize=12)
    fig.tight_layout()
    _save(fig, path)
    plt.close(fig)
