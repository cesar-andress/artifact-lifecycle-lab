"""Trace aggregation for RQ5 experiment."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass

from artifact_lab.experiments.truth_decay.rq5_experiment.models import AgentRunResult


@dataclass(frozen=True)
class TraceStatisticsRow:
    metric: str
    condition: str
    agent_id: str
    value: float
    n_runs: int


def compute_trace_statistics(results: list[AgentRunResult]) -> list[TraceStatisticsRow]:
    grouped: dict[tuple[str, str], list[AgentRunResult]] = defaultdict(list)
    for result in results:
        grouped[(result.condition, result.agent_id)].append(result)

    rows: list[TraceStatisticsRow] = []
    flags = (
        "read_instruction",
        "followed_reference",
        "ignored_reference",
        "detected_inconsistency",
        "repaired_reference",
    )
    for (condition, agent_id), bucket in sorted(grouped.items()):
        n = len(bucket)
        for flag in flags:
            rate = sum(1 for r in bucket if getattr(r, flag)) / n if n else 0.0
            rows.append(
                TraceStatisticsRow(
                    metric=f"rate_{flag}",
                    condition=condition,
                    agent_id=agent_id,
                    value=round(rate, 6),
                    n_runs=n,
                )
            )
        event_counts = Counter()
        for result in bucket:
            for event in result.trace_events:
                event_counts[event.event_type] += 1
        for event_type, count in sorted(event_counts.items()):
            rows.append(
                TraceStatisticsRow(
                    metric=f"event_count_{event_type}",
                    condition=condition,
                    agent_id=agent_id,
                    value=float(count),
                    n_runs=n,
                )
            )
    return rows


def trace_statistics_to_rows(rows: list[TraceStatisticsRow]) -> list[dict]:
    return [asdict(row) for row in rows]
