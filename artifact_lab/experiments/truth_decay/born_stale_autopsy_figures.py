"""Publication figures for born-stale autopsy."""

from __future__ import annotations

from collections import Counter, defaultdict
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


def render_figure_taxonomy(category_counts: Counter[str], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    labels = [
        "extraction\nartifact",
        "template\nplaceholder",
        "normative\nprescriptive",
        "pre-observation\nevolution",
        "external\nreference",
        "verification\nanchor mismatch",
        "genuine false\nclaim",
        "unresolved\ndisagreement",
    ]
    keys = [
        "extraction_artifact",
        "template_placeholder",
        "normative_prescriptive",
        "pre_observation_evolution",
        "external_reference",
        "verification_anchor_mismatch",
        "genuine_false_claim",
        "unresolved_disagreement",
    ]
    values = [category_counts.get(k, 0) for k in keys]
    colors = ["#E74C3C", "#F39C12", "#9B59B6", "#3498DB", "#1ABC9C", "#34495E", "#C0392B", "#95A5A6"]
    ax.barh(labels, values, color=colors)
    ax.set_xlabel("Born-stale reference count")
    ax.set_title("Born-Stale Autopsy — Inferred failure taxonomy")
    ax.grid(True, axis="x", alpha=0.3)
    _save(fig, path)
    plt.close(fig)


def render_figure_by_reference_type(rows: list[dict], path: Path) -> None:
    by_type: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        by_type[row["reference_type"]][row.get("final_category") or "unresolved_disagreement"] += 1

    types = ["path", "directory", "script_name", "dependency"]
    categories = sorted({c for ctr in by_type.values() for c in ctr})
    fig, ax = plt.subplots(figsize=(9, 5))
    bottom = [0] * len(types)
    x = range(len(types))
    cmap = plt.cm.tab10
    for i, cat in enumerate(categories):
        vals = [by_type[t].get(cat, 0) for t in types]
        ax.bar(x, vals, bottom=bottom, label=cat.replace("_", " "), color=cmap(i % 10))
        bottom = [b + v for b, v in zip(bottom, vals)]
    ax.set_xticks(list(x), types)
    ax.set_ylabel("Count")
    ax.set_title("Born-Stale taxonomy by reference type")
    ax.legend(loc="upper right", fontsize=7, frameon=True)
    _save(fig, path)
    plt.close(fig)


def render_figure_by_repository(rows: list[dict], path: Path, *, top_n: int = 15) -> None:
    repo_counts = Counter(r["repo_id"] for r in rows)
    top = repo_counts.most_common(top_n)
    fig, ax = plt.subplots(figsize=(9, 5))
    labels = [f"{rid[:8]}… ({cnt})" for rid, cnt in top]
    values = [cnt for _, cnt in top]
    ax.barh(labels[::-1], values[::-1], color="#2C3E50")
    ax.set_xlabel("Born-stale references")
    ax.set_title(f"Top {top_n} repositories by born-stale mass")
    ax.grid(True, axis="x", alpha=0.3)
    _save(fig, path)
    plt.close(fig)
