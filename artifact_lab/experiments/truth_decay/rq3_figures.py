"""Publication figures for RQ3 observational analysis."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from artifact_lab.execution.atomic_io import atomic_replace


def _save(fig, path: Path) -> None:
    tmp = path.with_name(path.name + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(tmp, format="pdf", bbox_inches="tight", dpi=300)
    atomic_replace(tmp, path)


def render_figure_birth_integrity(metrics_rows: list[dict], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    regimes = [r["maintenance_regime"] for r in metrics_rows]
    verified = [r["p_verified_birth"] for r in metrics_rows]
    stale = [r["p_born_stale"] for r in metrics_rows]
    x = np.arange(len(regimes))
    w = 0.35
    ax.bar(x - w / 2, verified, w, label="P(verified birth)", color="#27AE60")
    ax.bar(x + w / 2, stale, w, label="P(born-stale)", color="#E74C3C")
    ax.set_xticks(x, [r.replace("_", "\n") for r in regimes], fontsize=9)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Observational proportion (verifiable refs)")
    ax.set_title("RQ3 — Birth integrity by maintenance regime")
    ax.legend(loc="upper right")
    ax.grid(True, axis="y", alpha=0.3)
    _save(fig, path)
    plt.close(fig)


def render_figure_repair_probability(metrics_rows: list[dict], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    regimes = [r["maintenance_regime"] for r in metrics_rows]
    decay = [r["p_decay_given_verified"] for r in metrics_rows]
    repair = [r["p_repair_given_decay"] for r in metrics_rows]
    x = np.arange(len(regimes))
    w = 0.35
    ax.bar(x - w / 2, decay, w, label="P(decay | ever verified)", color="#8E44AD")
    ax.bar(x + w / 2, repair, w, label="P(repair | decay)", color="#3498DB")
    ax.set_xticks(x, [r.replace("_", "\n") for r in regimes], fontsize=9)
    ax.set_ylim(0, max(max(decay + repair, default=0) * 1.2, 0.1))
    ax.set_ylabel("Observational proportion")
    ax.set_title("RQ3 — Decay and repair by maintenance regime")
    ax.legend(loc="upper right")
    ax.grid(True, axis="y", alpha=0.3)
    _save(fig, path)
    plt.close(fig)


def render_figure_transition_matrix(transition_rows: list[dict], path: Path) -> None:
    regimes = ["human_only", "agent_assisted", "agent_dominated", "unknown"]
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    axes_flat = axes.flatten()

    for ax, regime in zip(axes_flat, regimes):
        subset = [r for r in transition_rows if r["maintenance_regime"] == regime]
        if not subset:
            ax.set_axis_off()
            continue
        from_states = sorted({r["from_state"] for r in subset})
        to_states = sorted({r["to_state"] for r in subset})
        matrix = np.zeros((len(from_states), len(to_states)))
        for r in subset:
            i = from_states.index(r["from_state"])
            j = to_states.index(r["to_state"])
            matrix[i, j] = r["count"]
        im = ax.imshow(matrix, aspect="auto", cmap="Blues")
        ax.set_xticks(range(len(to_states)), to_states, rotation=45, ha="right", fontsize=7)
        ax.set_yticks(range(len(from_states)), from_states, fontsize=7)
        ax.set_title(regime.replace("_", " "), fontsize=10)
        fig.colorbar(im, ax=ax, fraction=0.046)

    fig.suptitle("RQ3 — State transition counts by maintenance regime", fontsize=12)
    fig.tight_layout()
    _save(fig, path)
    plt.close(fig)
