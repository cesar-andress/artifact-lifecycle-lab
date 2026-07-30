"""Publication figures for RQ4 multi-state lifecycle analysis."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch

from artifact_lab.execution.atomic_io import atomic_replace

NODE_RADIUS = 0.68


def _save(fig, path: Path) -> None:
    tmp = path.with_name(path.name + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(tmp, format="pdf", bbox_inches="tight", dpi=300)
    atomic_replace(tmp, path)


def _boundary_point(cx: float, cy: float, tx: float, ty: float, *, radius: float = NODE_RADIUS) -> tuple[float, float]:
    """Point on circle edge toward target (tx, ty)."""
    dx, dy = tx - cx, ty - cy
    dist = math.hypot(dx, dy)
    if dist < 1e-9:
        return cx, cy
    return cx + radius * dx / dist, cy + radius * dy / dist


def _arc_midpoint(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    rad: float,
) -> tuple[float, float]:
    """Approximate label anchor along a curved arc3 connection."""
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy) or 1.0
    px, py = -dy / length, dx / length
    offset = rad * length * 0.45
    return mx + px * offset, my + py * offset


def render_figure_lifecycle_diagram(transition_rows: list[dict], path: Path) -> None:
    """Conceptual lifecycle diagram with empirical first-transition and key edge weights."""
    fig, ax = plt.subplots(figsize=(10.5, 7.5))
    ax.set_xlim(-0.2, 10.2)
    ax.set_ylim(-0.25, 7.35)
    ax.axis("off")
    ax.set_aspect("equal")

    # Layered layout: operational center, integrity_loss directly above, repair below,
    # birth left, deletion right, unverifiable bottom-left.  Edges follow natural flow
    # top-to-bottom / left-to-right with minimal crossings.
    nodes = {
        "operational": (5.0, 3.6),
        "integrity_loss": (5.0, 6.15),
        "birth": (1.4, 3.6),
        "deletion": (8.6, 3.6),
        "unverifiable": (1.4, 0.85),
        "repair": (5.0, 0.85),
    }
    labels = {
        "birth": "Birth",
        "operational": "Operational",
        "integrity_loss": "Integrity loss",
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

    for _name, (x, y) in nodes.items():
        ax.add_patch(
            plt.Circle((x, y), NODE_RADIUS, fill=True, color="#ECF0F1", ec="#2C3E50", lw=1.6, zorder=3)
        )

    for name, (x, y) in nodes.items():
        label = labels[name]
        fontsize = 9 if len(label) <= 12 else 8.5
        ax.text(x, y, label, ha="center", va="center", fontsize=fontsize, fontweight="bold", zorder=4)

    def edge(
        a: str,
        b: str,
        *,
        rad: float = 0.0,
        label: str | None = None,
        label_offset: tuple[float, float] = (0.0, 0.0),
        label_xy: tuple[float, float] | None = None,
    ) -> None:
        x1, y1 = nodes[a]
        x2, y2 = nodes[b]
        sx, sy = _boundary_point(x1, y1, x2, y2)
        ex, ey = _boundary_point(x2, y2, x1, y1)
        style = f"arc3,rad={rad}"
        arrow = FancyArrowPatch(
            (sx, sy),
            (ex, ey),
            arrowstyle="-|>",
            mutation_scale=13,
            color="#34495E",
            linewidth=1.25,
            connectionstyle=style,
            shrinkA=0,
            shrinkB=0,
            zorder=1,
        )
        ax.add_patch(arrow)
        if label:
            if label_xy is not None:
                lx, ly = label_xy
            else:
                lx, ly = _arc_midpoint(sx, sy, ex, ey, rad=rad)
                lx += label_offset[0]
                ly += label_offset[1]
            ax.text(
                lx,
                ly,
                label,
                fontsize=7.5,
                ha="center",
                va="center",
                color="#5D6D7E",
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.9),
                zorder=2,
            )

    # Birth fan-out (left column).
    edge(
        "birth",
        "operational",
        rad=0.0,
        label=f"{first_probs.get('operational', 0):.1%}",
        label_xy=(3.0, 4.05),
    )
    edge(
        "birth",
        "unverifiable",
        rad=0.0,
        label=f"{first_probs.get('unverifiable', 0):.1%}",
        label_xy=(0.55, 2.1),
    )
    edge(
        "birth",
        "integrity_loss",
        rad=0.28,
        label=f"{first_probs.get('integrity_loss', 0):.1%}",
        label_xy=(2.35, 5.55),
    )

    # Vertical spine through operational.
    edge(
        "operational",
        "integrity_loss",
        rad=0.0,
        label=f"{trans_probs.get(('operational', 'integrity_loss'), 0):.1%}",
        label_xy=(4.2, 4.95),
    )
    edge(
        "repair",
        "operational",
        rad=0.0,
        label=f"{trans_probs.get(('repair', 'operational'), 0):.1%}",
        label_xy=(4.2, 2.35),
    )

    # Horizontal exits at operational and integrity_loss rows.
    edge(
        "operational",
        "deletion",
        rad=0.0,
        label=f"{trans_probs.get(('operational', 'deletion'), 0):.1%}",
        label_xy=(6.9, 3.95),
    )
    edge(
        "integrity_loss",
        "deletion",
        rad=-0.22,
        label=f"{trans_probs.get(('integrity_loss', 'deletion'), 0):.1%}",
        label_xy=(7.55, 5.25),
    )

    # Downward branch to repair.
    edge(
        "integrity_loss",
        "repair",
        rad=0.22,
        label=f"{trans_probs.get(('integrity_loss', 'repair'), 0):.1%}",
        label_xy=(6.0, 2.55),
    )

    ax.set_title("RQ4: Multi-state reference lifecycle (empirical transition weights)", fontsize=12)
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
