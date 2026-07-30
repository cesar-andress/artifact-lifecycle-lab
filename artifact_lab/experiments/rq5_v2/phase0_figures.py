"""Publication-quality Phase 0 figures (vector PDF, minimal styling)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from artifact_lab.execution.atomic_io import atomic_replace


def _save(fig: plt.Figure, path: Path) -> None:
    tmp = path.with_name(path.name + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(tmp, format="pdf", bbox_inches="tight", dpi=300)
    atomic_replace(tmp, path)


def render_success_rate(
    *,
    success_rate: float,
    wilson_low: float,
    wilson_high: float,
    path: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(4.5, 4))
    ax.bar(["T+L"], [success_rate], color="#2C3E50", width=0.5)
    ax.errorbar(
        [0],
        [success_rate],
        yerr=[[success_rate - wilson_low], [wilson_high - success_rate]],
        fmt="none",
        color="#000000",
        capsize=6,
        linewidth=1.2,
    )
    ax.axhspan(0.45, 0.75, color="#27AE60", alpha=0.12, label="Calibration band")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Success rate")
    ax.set_title("Phase 0 — T+L success rate")
    ax.legend(loc="upper right", frameon=False)
    ax.grid(True, axis="y", alpha=0.25, linewidth=0.5)
    _save(fig, path)
    plt.close(fig)


def render_distribution(
    *,
    values: list[float],
    path: Path,
    title: str,
    xlabel: str,
) -> None:
    fig, ax = plt.subplots(figsize=(5, 4))
    if values:
        ax.hist(values, bins=min(15, max(5, len(values) // 3)), color="#34495E", edgecolor="white")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Run count")
    ax.set_title(title)
    ax.grid(True, axis="y", alpha=0.25, linewidth=0.5)
    _save(fig, path)
    plt.close(fig)


def render_funnel(
    *,
    stages: list[tuple[str, int]],
    path: Path,
    title: str,
) -> None:
    labels = [s[0] for s in stages]
    counts = [s[1] for s in stages]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(labels, counts, color="#5D6D7E")
    ax.set_ylabel("Run count")
    ax.set_title(title)
    ax.tick_params(axis="x", rotation=15)
    ax.grid(True, axis="y", alpha=0.25, linewidth=0.5)
    _save(fig, path)
    plt.close(fig)
