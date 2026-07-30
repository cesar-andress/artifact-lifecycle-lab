"""Figures for task difficulty calibration exports."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from artifact_lab.execution.atomic_io import atomic_replace
from artifact_lab.experiments.task_calibration.model import TARGET_SUCCESS_HIGH, TARGET_SUCCESS_LOW


def _save(fig: plt.Figure, path: Path) -> None:
    tmp = path.with_name(path.name + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(tmp, format="pdf", bbox_inches="tight", dpi=300)
    atomic_replace(tmp, path)


def render_difficulty_distribution(
    *,
    rows: list[dict],
    path: Path,
    historical_success: list[float] | None = None,
) -> None:
    """
    Multi-panel PDF: dimension boxplots, composite histogram, calibrated success histogram.
    """
    if not rows:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "No calibration rows", ha="center", va="center")
        ax.axis("off")
        _save(fig, path)
        return

    dim_keys = [
        ("compilation_complexity", "Compilation"),
        ("edited_files_estimate", "Edited files"),
        ("test_complexity", "Tests"),
        ("dependency_depth", "Dependency depth"),
        ("historical_failure_rate", "Historical failures"),
    ]
    composites = [float(r["composite_difficulty"]) for r in rows]
    calibrated = [float(r["calibrated_expected_success"]) for r in rows]
    tiers = [r.get("calibration_tier", "") for r in rows]
    n_target = sum(1 for t in tiers if t == "target_band")

    fig = plt.figure(figsize=(12, 9))
    gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.28)

    # Panel A: dimension scores (boxplot)
    ax_a = fig.add_subplot(gs[0, 0])
    data = [[float(r[k]) for r in rows] for k, _ in dim_keys]
    labels = [label for _, label in dim_keys]
    bp = ax_a.boxplot(data, tick_labels=labels, patch_artist=True, showfliers=False)
    for patch in bp["boxes"]:
        patch.set_facecolor("#c6dbef")
    ax_a.set_ylabel("Score (0 = easy, 1 = hard)")
    ax_a.set_title("A. Difficulty dimensions")
    ax_a.set_ylim(0, 1.05)
    ax_a.tick_params(axis="x", rotation=25)

    # Panel B: composite difficulty
    ax_b = fig.add_subplot(gs[0, 1])
    ax_b.hist(composites, bins=20, color="#6baed6", edgecolor="white", alpha=0.9)
    ax_b.axvline(np.median(composites), color="#08519c", linestyle="--", linewidth=1.2, label="Median")
    ax_b.set_xlabel("Composite difficulty")
    ax_b.set_ylabel("Task count")
    ax_b.set_title("B. Composite difficulty distribution")
    ax_b.legend(fontsize=8)

    # Panel C: calibrated expected success
    ax_c = fig.add_subplot(gs[1, 0])
    ax_c.hist(
        calibrated,
        bins=20,
        color="#74c476",
        edgecolor="white",
        alpha=0.9,
        label="Candidates",
    )
    if historical_success:
        ax_c.hist(
            historical_success,
            bins=8,
            color="#fd8d3c",
            edgecolor="white",
            alpha=0.55,
            label="RQ5 v1 cases (observed)",
        )
    ax_c.axvspan(TARGET_SUCCESS_LOW, TARGET_SUCCESS_HIGH, color="#fee391", alpha=0.45, label="Target 40–60%")
    ax_c.axvline(np.median(calibrated), color="#238b45", linestyle="--", linewidth=1.2)
    ax_c.set_xlabel("Expected success rate")
    ax_c.set_ylabel("Count")
    ax_c.set_title(f"C. Calibrated success (target band: {n_target}/{len(rows)})")
    ax_c.set_xlim(0, 1)
    ax_c.legend(fontsize=7, loc="upper right")

    # Panel D: composite vs calibrated scatter
    ax_d = fig.add_subplot(gs[1, 1])
    colors = {"target_band": "#31a354", "too_hard": "#de2d26", "too_easy": "#756bb1"}
    for tier in ("target_band", "too_hard", "too_easy"):
        xs = [float(r["composite_difficulty"]) for r in rows if r.get("calibration_tier") == tier]
        ys = [float(r["calibrated_expected_success"]) for r in rows if r.get("calibration_tier") == tier]
        if xs:
            ax_d.scatter(xs, ys, s=12, alpha=0.55, c=colors[tier], label=tier.replace("_", " "))
    comp_grid = np.linspace(0, 1, 50)
    if rows and "raw_logistic_success" in rows[0]:
        # Show monotonic curve from first row's params if stored in summary — skip
        pass
    ax_d.axhspan(TARGET_SUCCESS_LOW, TARGET_SUCCESS_HIGH, color="#fee391", alpha=0.35)
    ax_d.set_xlabel("Composite difficulty")
    ax_d.set_ylabel("Calibrated expected success")
    ax_d.set_title("D. Inclusion tiers")
    ax_d.set_xlim(0, 1)
    ax_d.set_ylim(0, 1)
    ax_d.legend(fontsize=7, loc="upper right")

    fig.suptitle("Task difficulty calibration — pre-inclusion scoring", fontsize=12, y=0.98)
    _save(fig, path)
