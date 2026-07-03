"""Extended figures for RQ5 causal evidence outputs."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from artifact_lab.execution.atomic_io import atomic_replace
from artifact_lab.experiments.truth_decay.rq5_experiment.causal_statistics import CausalStatisticsRow
from artifact_lab.experiments.truth_decay.rq5_experiment.models import AgentRunResult


def _save(fig, path: Path) -> None:
    tmp = path.with_name(path.name + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(tmp, format="pdf", bbox_inches="tight", dpi=300)
    atomic_replace(tmp, path)


def render_figure_success(results: list[AgentRunResult], path: Path) -> None:
    grouped: dict[tuple[str, str], list[AgentRunResult]] = defaultdict(list)
    for result in results:
        grouped[(result.agent_id, result.condition)].append(result)
    agents = sorted({result.agent_id for result in results})
    x = range(len(agents))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    for i, condition in enumerate(["A", "B"]):
        rates = []
        for agent in agents:
            bucket = grouped.get((agent, condition), [])
            rates.append(sum(1 for r in bucket if r.success) / len(bucket) if bucket else 0.0)
        offset = -width / 2 if condition == "A" else width / 2
        ax.bar([xi + offset for xi in x], rates, width=width, label=f"Condition {condition}")
    ax.set_xticks(list(x), agents, rotation=15, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Success rate")
    ax.set_title("RQ5 causal evidence — success rate")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    _save(fig, path)
    plt.close(fig)


def render_figure_failure_modes(failure_rows: list[dict], path: Path) -> None:
    counts = Counter(row.get("failure_mode", "unknown") for row in failure_rows)
    labels = list(counts.keys())
    values = [counts[k] for k in labels]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(labels, values, color="#C0392B")
    ax.set_ylabel("Run count")
    ax.set_title("RQ5 causal evidence — failure modes")
    ax.tick_params(axis="x", rotation=20)
    ax.grid(True, axis="y", alpha=0.3)
    _save(fig, path)
    plt.close(fig)


def render_figure_effect_sizes(stats_rows: list[CausalStatisticsRow], path: Path) -> None:
    deltas = [
        row
        for row in stats_rows
        if row.estimand == "paired_success_difference_a_minus_b"
    ]
    if not deltas:
        return
    agents = [row.agent_id for row in deltas]
    values = [row.value for row in deltas]
    lo = [row.ci_low for row in deltas]
    hi = [row.ci_high for row in deltas]
    err = [[v - l for v, l in zip(values, lo)], [h - v for v, h in zip(values, hi)]]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(agents, values, yerr=err, capsize=4, color="#3498DB")
    ax.axhline(0.0, color="#7F8C8D", linestyle="--")
    ax.set_ylabel("Paired success difference (A − B)")
    ax.set_title("RQ5 causal evidence — effect sizes")
    ax.grid(True, axis="y", alpha=0.3)
    _save(fig, path)
    plt.close(fig)


def render_figure_trace_flow(trace_rows: list[dict], path: Path) -> None:
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for row in trace_rows:
        key = f"{row['condition']}|{row['agent_id']}"
        grouped[key][row["trace_class"]] += row["count"]
    labels = sorted(grouped.keys())
    classes = sorted({row["trace_class"] for row in trace_rows})
    fig, ax = plt.subplots(figsize=(10, 5))
    bottom = [0] * len(labels)
    x = range(len(labels))
    cmap = plt.cm.tab10
    for i, cls in enumerate(classes):
        vals = [grouped[label].get(cls, 0) for label in labels]
        ax.bar(x, vals, bottom=bottom, label=cls.replace("_", " "), color=cmap(i % 10))
        bottom = [b + v for b, v in zip(bottom, vals)]
    ax.set_xticks(list(x), [label.replace("|", "\n") for label in labels], rotation=0, fontsize=8)
    ax.set_ylabel("Run count")
    ax.set_title("RQ5 causal evidence — trace classifications")
    ax.legend(fontsize=7, loc="upper right")
    _save(fig, path)
    plt.close(fig)
