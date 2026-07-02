"""Publication figures for RQ2 survival analysis."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from artifact_lab.execution.atomic_io import atomic_replace
from artifact_lab.experiments.truth_decay.survival_estimators import RepairPoint, SurvivalPoint


def _save(fig, path: Path) -> None:
    tmp = path.with_name(path.name + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(tmp, format="pdf", bbox_inches="tight", dpi=300)
    atomic_replace(tmp, path)


def render_figure_survival(points: list[SurvivalPoint], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    if not points:
        ax.text(0.5, 0.5, "No survival data", ha="center", va="center")
        ax.set_axis_off()
        _save(fig, path)
        plt.close(fig)
        return

    times = [0.0] + [p.time_days for p in points]
    surv = [1.0] + [p.survival for p in points]
    lower = [1.0] + [p.survival_lower for p in points]
    upper = [1.0] + [p.survival_upper for p in points]

    ax.step(times, surv, where="post", color="#2C3E50", linewidth=2, label="Kaplan–Meier")
    ax.fill_between(times, lower, upper, step="post", alpha=0.2, color="#3498DB", label="95% CI")
    ax.axhline(0.5, color="#E74C3C", linestyle="--", linewidth=1, alpha=0.7, label="Median threshold")
    ax.set_xlabel("Days since first verified observation")
    ax.set_ylabel("Survival probability (reference still true)")
    ax.set_title("RQ2 — Reference truth survival (verifiable references)")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="upper right", frameon=True)
    ax.grid(True, alpha=0.3)
    _save(fig, path)
    plt.close(fig)


def render_figure_cumulative_hazard(points: list[SurvivalPoint], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    if not points:
        ax.text(0.5, 0.5, "No hazard data", ha="center", va="center")
        ax.set_axis_off()
        _save(fig, path)
        plt.close(fig)
        return

    times = [p.time_days for p in points]
    hazard = [p.cumulative_hazard for p in points]
    lower = [p.cumulative_hazard_lower for p in points]
    upper = [p.cumulative_hazard_upper for p in points]

    ax.step(times, hazard, where="post", color="#8E44AD", linewidth=2, label="Nelson–Aalen")
    ax.fill_between(times, lower, upper, step="post", alpha=0.2, color="#9B59B6")
    ax.set_xlabel("Days since first verified observation")
    ax.set_ylabel("Cumulative hazard")
    ax.set_title("RQ2 — Cumulative hazard of reference failure")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)
    _save(fig, path)
    plt.close(fig)


def render_figure_censoring(outcome_counts: dict[str, int], path: Path) -> None:
    labels = []
    values = []
    mapping = [
        ("first_missing", "First missing (event)"),
        ("right_censored", "Right-censored"),
        ("deleted", "Instruction file deleted"),
    ]
    for key, label in mapping:
        if outcome_counts.get(key, 0) > 0:
            labels.append(label)
            values.append(outcome_counts[key])

    fig, ax = plt.subplots(figsize=(6.5, 4))
    if not values:
        ax.text(0.5, 0.5, "No censoring data", ha="center", va="center")
        ax.set_axis_off()
        _save(fig, path)
        plt.close(fig)
        return

    colors = ["#E74C3C", "#95A5A6", "#34495E"]
    ax.barh(labels, values, color=colors[: len(values)])
    ax.set_xlabel("Reference count")
    ax.set_title("RQ2 — Outcome distribution (censoring vs events)")
    ax.grid(True, axis="x", alpha=0.3)
    _save(fig, path)
    plt.close(fig)


def render_figure_repair_incidence(points: list[RepairPoint], path: Path) -> None:
    """Optional fourth figure — repair CIF stored separately if needed."""
    fig, ax = plt.subplots(figsize=(6.5, 4))
    if not points:
        ax.text(0.5, 0.5, "No repair events", ha="center", va="center")
        ax.set_axis_off()
        _save(fig, path)
        plt.close(fig)
        return
    times = [p.time_days for p in points]
    inc = [p.cumulative_incidence for p in points]
    ax.step(times, inc, where="post", color="#27AE60", linewidth=2)
    ax.set_xlabel("Days since first missing")
    ax.set_ylabel("Cumulative repair incidence")
    ax.set_title("RQ2 — Repair cumulative incidence (post-failure)")
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)
    _save(fig, path)
    plt.close(fig)
