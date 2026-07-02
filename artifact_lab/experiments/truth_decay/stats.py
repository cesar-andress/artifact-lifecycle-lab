"""Deterministic exploratory statistics for RQ1 feasibility."""

from __future__ import annotations

import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RQ1ExploratoryStats:
    instruction_files: int
    total_observations: int
    references_per_file_median: float
    references_per_file_mean: float
    verified_ratio: float
    missing_ratio: float
    repaired_ratio: float
    unverifiable_ratio: float
    deleted_ratio: float
    state_counts: dict[str, int]
    transition_counts: dict[str, int]
    first_failure_count: int
    repair_event_count: int
    reference_additions: int
    reference_removals: int
    median_time_to_first_missing_days: float | None
    median_repair_latency_days: float | None
    files_with_decay: int
    files_with_repair: int


def _parse_time(value: str) -> datetime:
    text = value.replace("Z", "+00:00")
    return datetime.fromisoformat(text)


def _days_between(start: str, end: str) -> float:
    delta = _parse_time(end) - _parse_time(start)
    return delta.total_seconds() / 86400.0


def compute_exploratory_stats(rows: list[dict]) -> RQ1ExploratoryStats:
    if not rows:
        return RQ1ExploratoryStats(
            instruction_files=0,
            total_observations=0,
            references_per_file_median=0.0,
            references_per_file_mean=0.0,
            verified_ratio=0.0,
            missing_ratio=0.0,
            repaired_ratio=0.0,
            unverifiable_ratio=0.0,
            deleted_ratio=0.0,
            state_counts={},
            transition_counts={},
            first_failure_count=0,
            repair_event_count=0,
            reference_additions=0,
            reference_removals=0,
            median_time_to_first_missing_days=None,
            median_repair_latency_days=None,
            files_with_decay=0,
            files_with_repair=0,
        )

    file_keys = {(r["repo_id"], r["instruction_path"]) for r in rows}
    refs_per_file: Counter[tuple[str, str]] = Counter()
    state_counts: Counter[str] = Counter()
    transition_counts: Counter[str] = Counter()

    for row in rows:
        if not row.get("reference_removed"):
            file_key = (row["repo_id"], row["instruction_path"])
            refs_per_file[file_key] += 1
        state_counts[row["state"]] += 1
        transition_counts[row["transition"]] += 1

    total_state_rows = sum(state_counts.values())
    ratios = {
        s: state_counts.get(s, 0) / total_state_rows if total_state_rows else 0.0
        for s in ("VERIFIED", "MISSING", "REPAIRED", "UNVERIFIABLE", "DELETED")
    }

    per_file_values = list(refs_per_file.values()) if refs_per_file else [0]

    # Time to first missing per reference trajectory
    trajectories: dict[tuple[str, str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        if row.get("reference_removed"):
            continue
        key = (row["repo_id"], row["instruction_path"], row["reference_type"], row["reference"])
        trajectories[key].append(row)

    time_to_missing: list[float] = []
    repair_latencies: list[float] = []
    files_with_decay: set[tuple[str, str]] = set()
    files_with_repair: set[tuple[str, str]] = set()

    for key, events in trajectories.items():
        events.sort(key=lambda r: r["commit_time"])
        first_verified_time: str | None = None
        first_missing_time: str | None = None
        missing_start: str | None = None

        for ev in events:
            file_key = (ev["repo_id"], ev["instruction_path"])
            if ev["state"] == "VERIFIED" and first_verified_time is None:
                first_verified_time = ev["commit_time"]
            if ev["state"] == "MISSING":
                files_with_decay.add(file_key)
                if first_missing_time is None:
                    first_missing_time = ev["commit_time"]
                if missing_start is None:
                    missing_start = ev["commit_time"]
            if ev["state"] == "REPAIRED" and missing_start:
                files_with_repair.add(file_key)
                repair_latencies.append(_days_between(missing_start, ev["commit_time"]))
                missing_start = None

        if first_verified_time and first_missing_time:
            time_to_missing.append(_days_between(first_verified_time, first_missing_time))

    return RQ1ExploratoryStats(
        instruction_files=len(file_keys),
        total_observations=len(rows),
        references_per_file_median=float(statistics.median(per_file_values)),
        references_per_file_mean=float(statistics.mean(per_file_values)),
        verified_ratio=ratios["VERIFIED"],
        missing_ratio=ratios["MISSING"],
        repaired_ratio=ratios["REPAIRED"],
        unverifiable_ratio=ratios["UNVERIFIABLE"],
        deleted_ratio=ratios["DELETED"],
        state_counts=dict(state_counts),
        transition_counts=dict(transition_counts),
        first_failure_count=sum(1 for r in rows if r.get("first_failure")),
        repair_event_count=sum(1 for r in rows if r.get("repair_event")),
        reference_additions=sum(1 for r in rows if r.get("reference_added")),
        reference_removals=sum(1 for r in rows if r.get("reference_removed")),
        median_time_to_first_missing_days=(
            float(statistics.median(time_to_missing)) if time_to_missing else None
        ),
        median_repair_latency_days=(
            float(statistics.median(repair_latencies)) if repair_latencies else None
        ),
        files_with_decay=len(files_with_decay),
        files_with_repair=len(files_with_repair),
    )


def stats_to_summary_rows(stats: RQ1ExploratoryStats) -> list[dict]:
    rows = [
        {"metric": "instruction_files", "value": stats.instruction_files},
        {"metric": "total_observations", "value": stats.total_observations},
        {"metric": "references_per_file_median", "value": round(stats.references_per_file_median, 3)},
        {"metric": "references_per_file_mean", "value": round(stats.references_per_file_mean, 3)},
        {"metric": "verified_ratio", "value": round(stats.verified_ratio, 4)},
        {"metric": "missing_ratio", "value": round(stats.missing_ratio, 4)},
        {"metric": "repaired_ratio", "value": round(stats.repaired_ratio, 4)},
        {"metric": "unverifiable_ratio", "value": round(stats.unverifiable_ratio, 4)},
        {"metric": "deleted_ratio", "value": round(stats.deleted_ratio, 4)},
        {"metric": "first_failure_count", "value": stats.first_failure_count},
        {"metric": "repair_event_count", "value": stats.repair_event_count},
        {"metric": "reference_additions", "value": stats.reference_additions},
        {"metric": "reference_removals", "value": stats.reference_removals},
        {"metric": "files_with_decay", "value": stats.files_with_decay},
        {"metric": "files_with_repair", "value": stats.files_with_repair},
    ]
    if stats.median_time_to_first_missing_days is not None:
        rows.append(
            {
                "metric": "median_time_to_first_missing_days",
                "value": round(stats.median_time_to_first_missing_days, 2),
            }
        )
    if stats.median_repair_latency_days is not None:
        rows.append(
            {"metric": "median_repair_latency_days", "value": round(stats.median_repair_latency_days, 2)}
        )
    for state, count in sorted(stats.state_counts.items()):
        rows.append({"metric": f"state_{state}", "value": count})
    return rows
