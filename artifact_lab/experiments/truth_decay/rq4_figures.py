"""Publication figures for RQ4 multi-state lifecycle analysis."""

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


def render_figure_lifecycle_diagram(transition_rows: list[dict], path: Path) -> None:
    """Conceptual lifecycle diagram with empirical first-transition and key edge weights."""
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    nodes = {
        "birth": (1.0, 3.0),
        "operational": (3.5, 4.5),
        "integrity_loss": (6.0, 3.0),
        "repair": (6.0, 1.0),
        "deletion": (9.0, 3.0),
        "unverifiable": (3.5, 1.0),
    }
    labels = {
        "birth": "Birth",
        "operational": "Operational",
        "integrity_loss": "Integrity\nloss",
        "repair": "Repair",
        "deletion": "Deletion",
        "unverifiable": "Unverifiable",
    }

    first_probs = {
        r["to_phase"]: r["probability"]
        for r in transition_rows
        if r.get("section") == "first_transition_probability"
    }
    trans_probs = {
        (r["from_phase"], r["to_phase"]): r["probability"]
        for r in transition_rows
        if r.get("section") == "transition_probability"
    }

    for name, (x, y) in nodes.items():
        ax.add_patch(plt.Circle((x, y), 0.55, fill=True, color="#ECF0F1", ec="#2C3E50", lw=1.5))
        ax.text(x, y, labels[name], ha="center", va="center", fontsize=9, fontweight="bold")

    def edge(a: str, b: str, rad: float = 0.0, label: str | None = None) -> None:
        x1, y1 = nodes[a]
        x2, y2 = nodes[b]
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(arrowstyle="->", color="#34495E", lw=1.2, connectionstyle=f"arc3,rad={rad}"),
        )
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + rad
            ax.text(mx, my, label, fontsize=7, ha="center", color="#7F8C8D")

    edge("birth", "operational", label=f"{first_probs.get('operational', 0):.1%}")
    edge("birth", "integrity_loss", rad=-0.15, label=f"{first_probs.get('integrity_loss', 0):.1%}")
    edge("birth", "unverifiable", rad=0.15, label=f"{first_probs.get('unverifiable', 0):.1%}")
    edge("operational", "integrity_loss", label=f"{trans_probs.get(('operational', 'integrity_loss'), 0):.1%}")
    edge("integrity_loss", "repair", rad=-0.2, label=f"{trans_probs.get(('integrity_loss', 'repair'), 0):.1%}")
    edge("repair", "operational", rad=0.2, label=f"{trans_probs.get(('repair', 'operational'), 0):.1%}")
    edge("integrity_loss", "deletion", label=f"{trans_probs.get(('integrity_loss', 'deletion'), 0):.1%}")
    edge("operational", "deletion", rad=0.15, label=f"{trans_probs.get(('operational', 'deletion'), 0):.1%}")

    ax.set_title("RQ4 — Multi-state reference lifecycle (empirical transition weights)", fontsize=12)
    _save(fig, path)
    plt.close(fig)


def render_figure_transition_matrix(transition_rows: list[dict], path: Path) -> None:
    phases = ["birth", "operational", "integrity_loss", "repair", "deletion", "unverifiable"]
    matrix = np.zeros((len(phases), len(phases)))
    for r in transition_rows:
        if r.get("section") != "transition_probability":
            continue
        i = phases.index(r["from_phase"])
        j = phases.index(r["to_phase"])
        matrix[i, j] = r["probability"]

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(matrix, cmap="YlOrRd", vmin=0, vmax=max(0.01, matrix.max()))
    ax.set_xticks(range(len(phases)), [p.replace("_", "\n") for p in phases], fontsize=8)
    ax.set_yticks(range(len(phases)), [p.replace("_", "\n") for p in phases], fontsize=8)
    ax.set_xlabel("To phase")
    ax.set_ylabel("From phase")
    ax.set_title("RQ4 — Lifecycle transition probability matrix")
    fig.colorbar(im, ax=ax, fraction=0.046, label="P(to | from)")
    _save(fig, path)
    plt.close(fig)


def render_figure_state_occupancy(occupancy_rows: list[dict], path: Path) -> None:
    phases = [r["lifecycle_phase"] for r in occupancy_rows]
    props = [r["occupancy_proportion"] for r in occupancy_rows]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    colors = ["#27AE60", "#E74C3C", "#3498DB", "#95A5A6", "#F39C12"]
    ax.bar(range(len(phases)), props, color=colors[: len(phases)])
    ax.set_xticks(range(len(phases)), [p.replace("_", "\n") for p in phases], fontsize=9)
    ax.set_ylim(0, max(props) * 1.15 if props else 1)
    ax.set_ylabel("Occupancy proportion (person-time)")
    ax.set_title("RQ4 — State occupancy in longitudinal panel")
    ax.grid(True, axis="y", alpha=0.3)
    _save(fig, path)
    plt.close(fig)


def _latency_histogram(values: list[float], path: Path, *, title: str, xlabel: str) -> None:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    if not values:
        ax.text(0.5, 0.5, "No events observed", ha="center", va="center")
        ax.set_axis_off()
    else:
        capped = [min(v, 365 * 3) for v in values]
        ax.hist(capped, bins=30, color="#8E44AD", edgecolor="white", alpha=0.85)
        ax.axvline(float(np.median(values)), color="#E74C3C", linestyle="--", label=f"Median = {np.median(values):.0f}d")
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Count")
        ax.legend()
        ax.grid(True, axis="y", alpha=0.3)
    ax.set_title(title)
    _save(fig, path)
    plt.close(fig)


def render_figure_repair_latency(records: list, path: Path) -> None:
    values = [r.repair_latency_days for r in records if r.repair_latency_days is not None]
    _latency_histogram(
        values,
        path,
        title="RQ4 — Repair latency (integrity loss → repair)",
        xlabel="Days (capped at 3 years for display)",
    )


def render_figure_deletion_latency(records: list, path: Path) -> None:
    values = [r.deletion_latency_days for r in records if r.deletion_latency_days is not None]
    _latency_histogram(
        values,
        path,
        title="RQ4 — Deletion latency (birth → deletion)",
        xlabel="Days (capped at 3 years for display)",
    )
