"""Exploratory figures for RQ1 feasibility study."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from artifact_lab.execution.atomic_io import atomic_replace
from artifact_lab.experiments.truth_decay.stats import RQ1ExploratoryStats


def _save_fig(fig, path: Path, **kwargs) -> None:
    tmp = path.with_name(path.name + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(tmp, **kwargs)
    atomic_replace(tmp, path)


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _file_age_days(rows: list[dict]) -> dict[tuple[str, str], datetime]:
    intro: dict[tuple[str, str], datetime] = {}
    for row in rows:
        key = (row["repo_id"], row["instruction_path"])
        ts = _parse_time(row["commit_time"])
        if key not in intro or ts < intro[key]:
            intro[key] = ts
    return intro


def render_figure_a_reference_density(rows: list[dict], path: Path) -> None:
    """Figure A — distribution of reference observations per instruction file."""
    per_file: Counter[tuple[str, str]] = Counter()
    for row in rows:
        if row.get("reference_removed"):
            continue
        per_file[(row["repo_id"], row["instruction_path"])] += 1

    values = list(per_file.values()) if per_file else [0]
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.hist(values, bins=min(30, max(5, len(set(values)))), color="#4C72B0", edgecolor="white")
    ax.set_xlabel("Reference observations per instruction file")
    ax.set_ylabel("File count")
    ax.set_title("Figure A — Reference density distribution")
    _save_fig(fig, path, format="pdf", bbox_inches="tight")
    plt.close(fig)


def render_figure_b_verified_vs_missing_by_age(rows: list[dict], path: Path) -> None:
    """Figure B — verified vs missing share by instruction-file age (months)."""
    intro = _file_age_days(rows)
    age_buckets: dict[int, Counter[str]] = defaultdict(Counter)

    for row in rows:
        if row.get("reference_removed"):
            continue
        if row["state"] not in ("VERIFIED", "MISSING", "REPAIRED"):
            continue
        key = (row["repo_id"], row["instruction_path"])
        age_days = (_parse_time(row["commit_time"]) - intro[key]).days
        bucket = min(age_days // 30, 24)
        state = "MISSING" if row["state"] == "MISSING" else "VERIFIED"
        if row["state"] == "REPAIRED":
            state = "VERIFIED"
        age_buckets[bucket][state] += 1

    buckets = sorted(age_buckets)
    if not buckets:
        fig, ax = plt.subplots(figsize=(6.5, 4))
        ax.text(0.5, 0.5, "No verified/missing observations", ha="center", va="center")
        ax.set_axis_off()
        _save_fig(fig, path, format="pdf", bbox_inches="tight")
        plt.close(fig)
        return

    verified = []
    missing = []
    labels = []
    for b in buckets:
        counts = age_buckets[b]
        total = counts["VERIFIED"] + counts["MISSING"]
        verified.append(counts["VERIFIED"] / total if total else 0)
        missing.append(counts["MISSING"] / total if total else 0)
        labels.append(str(b))

    x = range(len(buckets))
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(x, verified, label="Verified share", color="#55A868")
    ax.bar(x, missing, bottom=verified, label="Missing share", color="#C44E52")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_xlabel("Instruction-file age (months since first touch)")
    ax.set_ylabel("Share of observations")
    ax.set_title("Figure B — Verified vs Missing by file age")
    ax.legend(loc="upper right")
    _save_fig(fig, path, format="pdf", bbox_inches="tight")
    plt.close(fig)


def render_figure_c_repair_latency(rows: list[dict], path: Path) -> None:
    """Figure C — repair latency histogram (days from missing to repaired)."""
    from artifact_lab.experiments.truth_decay.stats import compute_exploratory_stats

    stats = compute_exploratory_stats(rows)
    trajectories: dict[tuple[str, str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        if row.get("reference_removed"):
            continue
        key = (row["repo_id"], row["instruction_path"], row["reference_type"], row["reference"])
        trajectories[key].append(row)

    latencies: list[float] = []
    for events in trajectories.values():
        events.sort(key=lambda r: r["commit_time"])
        missing_start: str | None = None
        for ev in events:
            if ev["state"] == "MISSING" and missing_start is None:
                missing_start = ev["commit_time"]
            if ev["state"] == "REPAIRED" and missing_start:
                delta = (_parse_time(ev["commit_time"]) - _parse_time(missing_start)).days
                latencies.append(float(delta))
                missing_start = None

    fig, ax = plt.subplots(figsize=(6.5, 4))
    if latencies:
        ax.hist(latencies, bins=min(25, max(5, len(set(latencies)))), color="#8172B3", edgecolor="white")
        ax.set_xlabel("Repair latency (days)")
    else:
        ax.text(0.5, 0.5, "No repair events observed", ha="center", va="center")
        ax.set_axis_off()
    ax.set_ylabel("Repair count")
    ax.set_title("Figure C — Repair latency histogram")
    _save_fig(fig, path, format="pdf", bbox_inches="tight")
    plt.close(fig)


def render_figure_d_transition_diagram(stats: RQ1ExploratoryStats, path: Path) -> None:
    """Figure D — state transition diagram (counts on edges)."""
    edges: Counter[tuple[str, str]] = Counter()
    for transition, count in stats.transition_counts.items():
        if "->" not in transition or transition.endswith("->REMOVED"):
            continue
        src, dst = transition.split("->", 1)
        if src in ("INIT", "UNKNOWN") or src == dst:
            continue
        edges[(src, dst)] += count

    states = sorted({s for pair in edges for s in pair})
    if not states:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.text(0.5, 0.5, "No state transitions", ha="center", va="center")
        ax.set_axis_off()
        _save_fig(fig, path, format="pdf", bbox_inches="tight")
        plt.close(fig)
        return

    positions = {state: (i, 0) for i, state in enumerate(states)}
    fig, ax = plt.subplots(figsize=(8, 3.5))
    for state, (x, y) in positions.items():
        ax.scatter([x], [y], s=800, c="#DD8452", zorder=2)
        ax.text(x, y, state, ha="center", va="center", fontsize=8, fontweight="bold")

    for (src, dst), count in edges.most_common(12):
        if src not in positions or dst not in positions:
            continue
        x0, y0 = positions[src]
        x1, y1 = positions[dst]
        ax.annotate(
            "",
            xy=(x1, y1),
            xytext=(x0, y0),
            arrowprops=dict(arrowstyle="->", color="#333333", lw=1.2),
        )
        ax.text((x0 + x1) / 2, 0.15, str(count), ha="center", fontsize=7, color="#333333")

    ax.set_xlim(-0.5, len(states) - 0.5)
    ax.set_ylim(-0.5, 0.6)
    ax.set_axis_off()
    ax.set_title("Figure D — State transition diagram (top transitions)")
    _save_fig(fig, path, format="pdf", bbox_inches="tight")
    plt.close(fig)


def render_all_figures(rows: list[dict], stats: RQ1ExploratoryStats, output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "figure_a": output_dir / "figure_a_reference_density.pdf",
        "figure_b": output_dir / "figure_b_verified_vs_missing_by_age.pdf",
        "figure_c": output_dir / "figure_c_repair_latency.pdf",
        "figure_d": output_dir / "figure_d_state_transitions.pdf",
    }
    render_figure_a_reference_density(rows, paths["figure_a"])
    render_figure_b_verified_vs_missing_by_age(rows, paths["figure_b"])
    render_figure_c_repair_latency(rows, paths["figure_c"])
    render_figure_d_transition_diagram(stats, paths["figure_d"])
    return paths
