"""Publication figures for RQ5 causal experiment."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from artifact_lab.execution.atomic_io import atomic_replace
from artifact_lab.experiments.truth_decay.rq5_experiment.models import AgentRunResult


def _save(fig, path: Path) -> None:
    tmp = path.with_name(path.name + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(tmp, format="pdf", bbox_inches="tight", dpi=300)
    atomic_replace(tmp, path)


def render_figure_success_rate(results: list[AgentRunResult], path: Path) -> None:
    grouped: dict[tuple[str, str], list[AgentRunResult]] = defaultdict(list)
    for result in results:
        grouped[(result.agent_id, result.condition)].append(result)

    agents = sorted({result.agent_id for result in results})
    conditions = ["A", "B"]
    x = range(len(agents))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    for i, condition in enumerate(conditions):
        rates = []
        for agent in agents:
            bucket = grouped.get((agent, condition), [])
            rates.append(sum(1 for r in bucket if r.success) / len(bucket) if bucket else 0.0)
        offset = -width / 2 if condition == "A" else width / 2
        ax.bar([xi + offset for xi in x], rates, width=width, label=f"Condition {condition}")
    ax.set_xticks(list(x), agents, rotation=20, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Success rate")
    ax.set_title("RQ5 — Success rate by condition")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    _save(fig, path)
    plt.close(fig)


def render_figure_failure_modes(results: list[AgentRunResult], path: Path) -> None:
    modes = Counter()
    for result in results:
        if result.success:
            modes["success"] += 1
        elif not result.tests_passing:
            modes["tests_failed"] += 1
        elif not result.compilation_success:
            modes["compile_failed"] += 1
        elif result.tool_failures:
            modes["tool_failure"] += 1
        else:
            modes["other_failure"] += 1

    labels = list(modes.keys())
    values = [modes[k] for k in labels]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(labels, values, color="#E74C3C")
    ax.set_ylabel("Run count")
    ax.set_title("RQ5 — Failure mode counts")
    ax.grid(True, axis="y", alpha=0.3)
    _save(fig, path)
    plt.close(fig)


def render_figure_trace_flow(results: list[AgentRunResult], path: Path) -> None:
    flags = (
        "read_instruction",
        "followed_reference",
        "ignored_reference",
        "detected_inconsistency",
        "repaired_reference",
    )
    grouped: dict[str, list[AgentRunResult]] = defaultdict(list)
    for result in results:
        grouped[result.condition].append(result)

    conditions = ["A", "B"]
    fig, ax = plt.subplots(figsize=(8, 5))
    x = range(len(flags))
    width = 0.35
    for i, condition in enumerate(conditions):
        rates = []
        bucket = grouped.get(condition, [])
        for flag in flags:
            rates.append(sum(1 for r in bucket if getattr(r, flag)) / len(bucket) if bucket else 0.0)
        offset = -width / 2 if condition == "A" else width / 2
        ax.bar([xi + offset for xi in x], rates, width=width, label=f"Condition {condition}")
    ax.set_xticks(list(x), [f.replace("_", "\n") for f in flags], rotation=0)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Trace-coded rate")
    ax.set_title("RQ5 — Trace behavior by condition")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    _save(fig, path)
    plt.close(fig)
