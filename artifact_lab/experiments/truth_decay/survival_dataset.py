"""Build RQ2 survival dataset from RQ1 longitudinal observations."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime

from artifact_lab.experiments.truth_pilots.gates_common import (
    VERIFIABLE_REFERENCE_TYPES,
    _csv_bool,
)

OUTCOME_FIRST_MISSING = "first_missing"
OUTCOME_DELETED = "deleted"
OUTCOME_RIGHT_CENSORED = "right_censored"


@dataclass(frozen=True)
class ReferenceSurvivalRecord:
    repo_id: str
    instruction_path: str
    reference_type: str
    reference: str
    time_origin: str
    time_end: str
    duration_days: float
    outcome: str
    ever_repaired: bool
    repair_lag_days: float | None
    post_failure_followup_days: float | None
    n_observations: int


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _days_between(start: datetime, end: datetime) -> float:
    return max(0.0, (end - start).total_seconds() / 86400.0)


def _trajectory_key(row: dict) -> tuple[str, str, str, str]:
    return (row["repo_id"], row["instruction_path"], row["reference_type"], row["reference"])


def build_survival_dataset(rows: list[dict]) -> tuple[list[ReferenceSurvivalRecord], dict]:
    """One record per verifiable reference that reaches VERIFIED at least once.

    RQ2 estimand (protocol): time from first VERIFIED to first MISSING,
    right-censored at end of follow-up or instruction-file DELETED.
    """
    grouped: dict[tuple[str, str, str, str], list[dict]] = defaultdict(list)
    removal_times: dict[tuple[str, str, str, str], datetime] = {}

    for row in rows:
        if row["reference_type"] not in VERIFIABLE_REFERENCE_TYPES:
            continue
        key = _trajectory_key(row)
        if _csv_bool(row.get("reference_removed")):
            removal_times[key] = _parse_time(row["commit_time"])
            continue
        grouped[key].append(row)

    records: list[ReferenceSurvivalRecord] = []
    excluded_never_verified = 0

    for key, events in grouped.items():
        events.sort(key=lambda r: r["commit_time"])
        repo_id, instruction_path, ref_type, reference = key

        first_verified: datetime | None = None
        for ev in events:
            if ev["state"] == "VERIFIED":
                first_verified = _parse_time(ev["commit_time"])
                break

        if first_verified is None:
            excluded_never_verified += 1
            continue

        first_missing: datetime | None = None
        deleted_time: datetime | None = None
        repair_time: datetime | None = None

        for ev in events:
            ts = _parse_time(ev["commit_time"])
            if ts < first_verified:
                continue
            if ev["state"] == "MISSING" and first_missing is None:
                first_missing = ts
            if ev["state"] == "DELETED":
                deleted_time = ts
                break
            if first_missing and ev["state"] == "REPAIRED" and repair_time is None:
                repair_time = ts

        removed = removal_times.get(key)
        last_ts = _parse_time(events[-1]["commit_time"])

        if first_missing is not None and (deleted_time is None or first_missing <= deleted_time):
            if removed and removed < first_missing:
                end_time = removed
                outcome = OUTCOME_RIGHT_CENSORED
            else:
                end_time = first_missing
                outcome = OUTCOME_FIRST_MISSING
        elif deleted_time is not None:
            end_time = deleted_time
            outcome = OUTCOME_DELETED
        elif removed is not None:
            end_time = removed
            outcome = OUTCOME_RIGHT_CENSORED
        else:
            end_time = last_ts
            outcome = OUTCOME_RIGHT_CENSORED

        repair_lag: float | None = None
        ever_repaired = repair_time is not None and first_missing is not None
        if ever_repaired and repair_time and first_missing:
            repair_lag = _days_between(first_missing, repair_time)

        post_failure_followup: float | None = None
        if first_missing is not None:
            followup_end = last_ts
            if deleted_time is not None and deleted_time > first_missing:
                followup_end = deleted_time
            if removed is not None and removed > first_missing:
                followup_end = max(followup_end, removed)
            post_failure_followup = _days_between(first_missing, followup_end)

        records.append(
            ReferenceSurvivalRecord(
                repo_id=repo_id,
                instruction_path=instruction_path,
                reference_type=ref_type,
                reference=reference,
                time_origin=first_verified.isoformat(),
                time_end=end_time.isoformat(),
                duration_days=_days_between(first_verified, end_time),
                outcome=outcome,
                ever_repaired=ever_repaired,
                repair_lag_days=repair_lag,
                post_failure_followup_days=post_failure_followup,
                n_observations=len(events),
            )
        )

    meta = {
        "excluded_never_verified": excluded_never_verified,
        "cohort_size": len(records),
    }
    return records, meta


def records_to_rows(records: list[ReferenceSurvivalRecord]) -> list[dict]:
    return [asdict(r) for r in records]
