"""RQ3 observational metrics — specification integrity by maintenance regime."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass

from artifact_lab.experiments.truth_decay.rq3_attribution import is_agent_maintenance
from artifact_lab.experiments.truth_pilots.gates_common import VERIFIABLE_REFERENCE_TYPES

BirthIntegrity = str  # verified_birth | born_stale | unverifiable_birth | other


@dataclass(frozen=True)
class ReferenceTrajectoryRecord:
    repo_id: str
    instruction_path: str
    reference_type: str
    reference: str
    maintenance_regime: str
    birth_commit: str
    birth_attribution_class: str
    birth_agent_maintenance: bool
    birth_state: str
    birth_integrity: str
    ever_verified: bool
    ever_born_stale: bool
    ever_decay: bool
    ever_repaired: bool
    n_observations: int
    n_transitions: int


def _birth_integrity(reference_type: str, ever_verified: bool) -> BirthIntegrity:
    if reference_type not in VERIFIABLE_REFERENCE_TYPES:
        return "unverifiable_birth"
    if ever_verified:
        return "verified_birth"
    return "born_stale"


def _ever_decay(events: list[dict]) -> bool:
    first_verified_idx: int | None = None
    for i, ev in enumerate(events):
        if ev["state"] == "VERIFIED" and first_verified_idx is None:
            first_verified_idx = i
        if first_verified_idx is not None and i > first_verified_idx and ev["state"] == "MISSING":
            return True
    return False


def build_reference_trajectories(
    longitudinal_rows: list[dict],
    file_regimes: dict[tuple[str, str], str],
    attribution_index: dict[tuple[str, str, str], dict],
) -> list[ReferenceTrajectoryRecord]:
    grouped: dict[tuple[str, str, str, str], list[dict]] = defaultdict(list)
    for row in longitudinal_rows:
        if row.get("reference_removed"):
            continue
        key = (row["repo_id"], row["instruction_path"], row["reference_type"], row["reference"])
        grouped[key].append(row)

    records: list[ReferenceTrajectoryRecord] = []
    for key, events in grouped.items():
        events.sort(key=lambda r: r["commit_time"])
        repo_id, instruction_path, ref_type, reference = key
        first = events[0]
        regime = file_regimes.get((repo_id, instruction_path), "unknown")
        att = attribution_index.get((repo_id, instruction_path, first["commit"]))
        att_class = att.get("attribution_class", "") if att else ""
        agent_flag = is_agent_maintenance(att) if att else False

        ever_verified = any(e["state"] == "VERIFIED" for e in events)
        ever_repaired = any(e.get("repair_event") or e["state"] == "REPAIRED" for e in events)
        ever_stale = ref_type in VERIFIABLE_REFERENCE_TYPES and not ever_verified
        decay = _ever_decay(events) if ever_verified else False
        transitions = sum(1 for e in events if e.get("transition") and "->" in e["transition"])

        records.append(
            ReferenceTrajectoryRecord(
                repo_id=repo_id,
                instruction_path=instruction_path,
                reference_type=ref_type,
                reference=reference,
                maintenance_regime=regime,
                birth_commit=first["commit"],
                birth_attribution_class=att_class or "unknown",
                birth_agent_maintenance=agent_flag,
                birth_state=first["state"],
                birth_integrity=_birth_integrity(ref_type, ever_verified),
                ever_verified=ever_verified,
                ever_born_stale=ever_stale,
                ever_decay=decay,
                ever_repaired=ever_repaired,
                n_observations=len(events),
                n_transitions=transitions,
            )
        )
    return records


def compute_regime_metrics(records: list[ReferenceTrajectoryRecord]) -> list[dict]:
    """Observational proportions by maintenance regime (verifiable references for birth metrics)."""
    by_regime: dict[str, list[ReferenceTrajectoryRecord]] = defaultdict(list)
    for r in records:
        by_regime[r.maintenance_regime].append(r)

    rows: list[dict] = []
    for regime in ("human_only", "agent_assisted", "agent_dominated", "unknown"):
        subset = by_regime.get(regime, [])
        verifiable = [r for r in subset if r.reference_type in VERIFIABLE_REFERENCE_TYPES]
        n_all = len(subset)
        n_v = len(verifiable) or 1
        verified_birth = sum(1 for r in verifiable if r.birth_integrity == "verified_birth")
        born_stale = sum(1 for r in verifiable if r.birth_integrity == "born_stale")
        verified_ever = [r for r in verifiable if r.ever_verified]
        decay_n = sum(1 for r in verified_ever if r.ever_decay)
        decay_denom = len(verified_ever) or 1
        decayed = [r for r in verified_ever if r.ever_decay]
        repair_n = sum(1 for r in decayed if r.ever_repaired)
        repair_denom = len(decayed) or 1

        rows.append(
            {
                "maintenance_regime": regime,
                "n_reference_trajectories": n_all,
                "n_verifiable_trajectories": len(verifiable),
                "p_verified_birth": round(verified_birth / n_v, 4),
                "p_born_stale": round(born_stale / n_v, 4),
                "birth_integrity_index": round(verified_birth / n_v, 4),
                "p_decay_given_verified": round(decay_n / decay_denom, 4),
                "p_repair_given_decay": round(repair_n / repair_denom, 4) if decayed else 0.0,
                "n_decay_events": decay_n,
                "n_repair_after_decay": repair_n,
            }
        )
    return rows


def compute_transition_matrix(
    longitudinal_rows: list[dict],
    file_regimes: dict[tuple[str, str], str],
) -> list[dict]:
    """Count state transitions by maintenance regime (observational panel)."""
    counts: Counter[tuple[str, str, str]] = Counter()
    for row in longitudinal_rows:
        if row.get("reference_removed"):
            continue
        regime = file_regimes.get((row["repo_id"], row["instruction_path"]), "unknown")
        prev = row.get("previous_state") or "INIT"
        state = row["state"]
        if prev == state and prev == "":
            continue
        from_state = prev if prev else "INIT"
        counts[(regime, from_state, state)] += 1

    rows = []
    for (regime, from_state, to_state), n in sorted(counts.items()):
        rows.append(
            {
                "maintenance_regime": regime,
                "from_state": from_state,
                "to_state": to_state,
                "count": n,
            }
        )
    return rows


def trajectory_records_to_rows(records: list[ReferenceTrajectoryRecord]) -> list[dict]:
    return [asdict(r) for r in records]
