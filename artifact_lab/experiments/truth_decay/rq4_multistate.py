"""RQ4 multi-state lifecycle analysis from longitudinal reference panel."""

from __future__ import annotations

import statistics
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime

from artifact_lab.experiments.truth_pilots.gates_common import VERIFIABLE_REFERENCE_TYPES, _csv_bool

LIFECYCLE_PHASES = (
    "birth",
    "operational",
    "integrity_loss",
    "repair",
    "deletion",
    "unverifiable",
)

MECHANICAL_TO_LIFECYCLE = {
    "VERIFIED": "operational",
    "MISSING": "integrity_loss",
    "REPAIRED": "repair",
    "DELETED": "deletion",
    "UNVERIFIABLE": "unverifiable",
}


@dataclass(frozen=True)
class ReferenceLifecycleRecord:
    repo_id: str
    instruction_path: str
    reference_type: str
    reference: str
    birth_time: str
    birth_phase: str
    final_phase: str
    ever_operational: bool
    ever_integrity_loss: bool
    ever_repair: bool
    ever_deleted: bool
    repair_latency_days: float | None
    deletion_latency_days: float | None
    operational_to_deletion_days: float | None
    n_observations: int
    n_phase_transitions: int


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _days_between(start: datetime, end: datetime) -> float:
    return max(0.0, (end - start).total_seconds() / 86400.0)


def mechanical_to_lifecycle(state: str) -> str:
    return MECHANICAL_TO_LIFECYCLE.get(state, "unverifiable")


def _trajectory_key(row: dict) -> tuple[str, str, str, str]:
    return (row["repo_id"], row["instruction_path"], row["reference_type"], row["reference"])


def build_reference_lifecycle_records(rows: list[dict]) -> list[ReferenceLifecycleRecord]:
    grouped: dict[tuple[str, str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        if _csv_bool(row.get("reference_removed")):
            continue
        grouped[_trajectory_key(row)].append(row)

    records: list[ReferenceLifecycleRecord] = []
    for key, events in grouped.items():
        events.sort(key=lambda r: r["commit_time"])
        repo_id, instruction_path, ref_type, reference = key

        phases = [mechanical_to_lifecycle(e["state"]) for e in events]
        birth_phase = phases[0]
        final_phase = phases[-1]
        birth_time = _parse_time(events[0]["commit_time"])

        first_loss_time: datetime | None = None
        first_repair_time: datetime | None = None
        first_deleted_time: datetime | None = None
        first_operational_time: datetime | None = None
        ever_operational = False
        ever_integrity_loss = False
        ever_repair = False
        ever_deleted = False
        n_phase_transitions = 0
        prev_phase: str | None = None

        for ev, phase in zip(events, phases):
            t = _parse_time(ev["commit_time"])
            if phase == "operational":
                ever_operational = True
                if first_operational_time is None:
                    first_operational_time = t
            if phase == "integrity_loss":
                ever_integrity_loss = True
                if first_loss_time is None:
                    first_loss_time = t
            if phase == "repair":
                ever_repair = True
                if first_repair_time is None:
                    first_repair_time = t
            if phase == "deletion":
                ever_deleted = True
                if first_deleted_time is None:
                    first_deleted_time = t

            if prev_phase is None:
                prev_phase = phase
                continue
            if phase != prev_phase:
                n_phase_transitions += 1
                prev_phase = phase

        repair_latency: float | None = None
        if first_loss_time and first_repair_time and first_repair_time >= first_loss_time:
            repair_latency = _days_between(first_loss_time, first_repair_time)

        deletion_latency: float | None = None
        if first_deleted_time:
            deletion_latency = _days_between(birth_time, first_deleted_time)

        operational_to_deletion: float | None = None
        if first_operational_time and first_deleted_time and first_deleted_time >= first_operational_time:
            operational_to_deletion = _days_between(first_operational_time, first_deleted_time)

        records.append(
            ReferenceLifecycleRecord(
                repo_id=repo_id,
                instruction_path=instruction_path,
                reference_type=ref_type,
                reference=reference,
                birth_time=events[0]["commit_time"],
                birth_phase=birth_phase,
                final_phase=final_phase,
                ever_operational=ever_operational,
                ever_integrity_loss=ever_integrity_loss,
                ever_repair=ever_repair,
                ever_deleted=ever_deleted,
                repair_latency_days=repair_latency,
                deletion_latency_days=deletion_latency,
                operational_to_deletion_days=operational_to_deletion,
                n_observations=len(events),
                n_phase_transitions=n_phase_transitions,
            )
        )
    return records


def compute_phase_transitions(rows: list[dict]) -> Counter[tuple[str, str]]:
    """Count lifecycle phase transitions (collapse consecutive same-phase observations)."""
    grouped: dict[tuple[str, str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        if _csv_bool(row.get("reference_removed")):
            continue
        grouped[_trajectory_key(row)].append(row)

    counts: Counter[tuple[str, str]] = Counter()
    for events in grouped.values():
        events.sort(key=lambda r: r["commit_time"])
        prev: str | None = None
        for ev in events:
            phase = mechanical_to_lifecycle(ev["state"])
            if prev is None:
                counts[("birth", phase)] += 1
                prev = phase
                continue
            if phase != prev:
                counts[(prev, phase)] += 1
                prev = phase
    return counts


def transition_probability_rows(counts: Counter[tuple[str, str]]) -> list[dict]:
    by_from: dict[str, Counter[str]] = defaultdict(Counter)
    for (from_phase, to_phase), n in counts.items():
        by_from[from_phase][to_phase] += n

    rows: list[dict] = []
    for from_phase in sorted(by_from):
        total = sum(by_from[from_phase].values())
        for to_phase in sorted(by_from[from_phase]):
            n = by_from[from_phase][to_phase]
            rows.append(
                {
                    "section": "transition_probability",
                    "from_phase": from_phase,
                    "to_phase": to_phase,
                    "count": n,
                    "probability": round(n / total, 6) if total else 0.0,
                    "from_total": total,
                }
            )
    return rows


def first_transition_probability_rows(counts: Counter[tuple[str, str]]) -> list[dict]:
    birth_counts = Counter({to_phase: n for (from_phase, to_phase), n in counts.items() if from_phase == "birth"})
    total = sum(birth_counts.values()) or 1
    rows: list[dict] = []
    for to_phase in ("operational", "integrity_loss", "unverifiable", "repair", "deletion"):
        n = birth_counts.get(to_phase, 0)
        rows.append(
            {
                "section": "first_transition_probability",
                "from_phase": "birth",
                "to_phase": to_phase,
                "count": n,
                "probability": round(n / total, 6),
                "from_total": total,
            }
        )
    return rows


def compute_state_occupancy(rows: list[dict]) -> list[dict]:
    """Person-time in each lifecycle phase (commit-interval weighted)."""
    grouped: dict[tuple[str, str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        if _csv_bool(row.get("reference_removed")):
            continue
        grouped[_trajectory_key(row)].append(row)

    dwell: Counter[str] = Counter()
    for events in grouped.values():
        events.sort(key=lambda r: r["commit_time"])
        for i, ev in enumerate(events):
            phase = mechanical_to_lifecycle(ev["state"])
            if i + 1 < len(events):
                dt = _days_between(_parse_time(ev["commit_time"]), _parse_time(events[i + 1]["commit_time"]))
            else:
                dt = 0.0
            dwell[phase] += dt

    total = sum(dwell.values()) or 1.0
    rows_out: list[dict] = []
    for phase in ("operational", "integrity_loss", "repair", "deletion", "unverifiable"):
        days = dwell.get(phase, 0.0)
        rows_out.append(
            {
                "section": "state_occupancy",
                "lifecycle_phase": phase,
                "person_days": round(days, 2),
                "occupancy_proportion": round(days / total, 6),
                "total_person_days": round(total, 2),
            }
        )
    return rows_out


def _latency_summary(values: list[float], *, section: str, latency_type: str) -> list[dict]:
    if not values:
        return [
            {
                "section": section,
                "latency_type": latency_type,
                "statistic": "n",
                "value_days": 0,
                "n": 0,
            }
        ]
    sorted_vals = sorted(values)
    n = len(sorted_vals)

    def pct(p: float) -> float:
        idx = min(n - 1, max(0, int(p * (n - 1))))
        return sorted_vals[idx]

    stats = [
        ("n", float(n)),
        ("mean", statistics.mean(sorted_vals)),
        ("median", statistics.median(sorted_vals)),
        ("p25", pct(0.25)),
        ("p75", pct(0.75)),
        ("p90", pct(0.90)),
    ]
    return [
        {
            "section": section,
            "latency_type": latency_type,
            "statistic": name,
            "value_days": round(val, 2),
            "n": n,
        }
        for name, val in stats
    ]


def latency_rows(records: list[ReferenceLifecycleRecord]) -> list[dict]:
    repair = [r.repair_latency_days for r in records if r.repair_latency_days is not None]
    deletion = [r.deletion_latency_days for r in records if r.deletion_latency_days is not None]
    op_to_del = [r.operational_to_deletion_days for r in records if r.operational_to_deletion_days is not None]

    rows: list[dict] = []
    rows.extend(_latency_summary(repair, section="repair_latency", latency_type="integrity_loss_to_repair"))
    rows.extend(_latency_summary(deletion, section="deletion_latency", latency_type="birth_to_deletion"))
    rows.extend(
        _latency_summary(op_to_del, section="deletion_latency", latency_type="operational_to_deletion")
    )
    return rows


def verifiable_subset_metrics(records: list[ReferenceLifecycleRecord]) -> list[dict]:
    """Observational proportions for verifiable reference types only."""
    verifiable = [r for r in records if r.reference_type in VERIFIABLE_REFERENCE_TYPES]
    n = len(verifiable) or 1
    rows = [
        {
            "section": "verifiable_cohort",
            "metric": "n_trajectories",
            "value": len(verifiable),
        },
        {
            "section": "verifiable_cohort",
            "metric": "p_birth_operational",
            "value": round(sum(1 for r in verifiable if r.birth_phase == "operational") / n, 4),
        },
        {
            "section": "verifiable_cohort",
            "metric": "p_birth_integrity_loss",
            "value": round(sum(1 for r in verifiable if r.birth_phase == "integrity_loss") / n, 4),
        },
        {
            "section": "verifiable_cohort",
            "metric": "p_ever_operational",
            "value": round(sum(1 for r in verifiable if r.ever_operational) / n, 4),
        },
        {
            "section": "verifiable_cohort",
            "metric": "p_ever_integrity_loss",
            "value": round(sum(1 for r in verifiable if r.ever_integrity_loss) / n, 4),
        },
        {
            "section": "verifiable_cohort",
            "metric": "p_ever_repair",
            "value": round(sum(1 for r in verifiable if r.ever_repair) / n, 4),
        },
        {
            "section": "verifiable_cohort",
            "metric": "p_ever_deleted",
            "value": round(sum(1 for r in verifiable if r.ever_deleted) / n, 4),
        },
    ]
    return rows


def build_multistate_table(
    rows: list[dict],
    records: list[ReferenceLifecycleRecord],
) -> list[dict]:
    counts = compute_phase_transitions(rows)
    table: list[dict] = []
    table.extend(transition_probability_rows(counts))
    table.extend(first_transition_probability_rows(counts))
    table.extend(compute_state_occupancy(rows))
    table.extend(latency_rows(records))
    table.extend(verifiable_subset_metrics(records))
    return table


def lifecycle_records_to_rows(records: list[ReferenceLifecycleRecord]) -> list[dict]:
    out: list[dict] = []
    for r in records:
        row = asdict(r)
        row["section"] = "trajectory"
        out.append(row)
    return out
