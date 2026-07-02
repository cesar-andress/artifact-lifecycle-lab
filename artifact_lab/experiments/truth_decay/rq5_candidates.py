"""RQ5 experimental corpus preparation — natural snapshot identification."""

from __future__ import annotations

import hashlib
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime

from artifact_lab.experiments.truth_decay.rq5_availability import (
    assess_issue_availability,
    assess_task_availability,
)
from artifact_lab.experiments.truth_pilots.gates_common import VERIFIABLE_REFERENCE_TYPES, _csv_bool
from artifact_lab.store.blobs import BlobStore

SnapshotType = str  # truthful | born_stale | repaired | degraded


@dataclass(frozen=True)
class CommitSpecState:
    repo_id: str
    instruction_path: str
    commit: str
    commit_time: str
    references: dict[tuple[str, str], str]  # (type, ref) -> state
    transitions: dict[tuple[str, str], str]  # (type, ref) -> transition label


@dataclass(frozen=True)
class RQ5CandidateSnapshot:
    spec_id: str
    snapshot_id: str
    repo_id: str
    repo_url: str
    instruction_path: str
    family_group: str
    snapshot_type: SnapshotType
    commit_sha: str
    commit_time: str
    task_commit_sha: str
    blob_sha: str
    blob_available: bool
    n_refs_total: int
    n_verifiable: int
    n_verified_verifiable: int
    n_missing_verifiable: int
    n_unverifiable: int
    n_repaired: int
    verified_ratio_verifiable: float
    anchor_reference: str
    anchor_reference_type: str
    paired_truthful_commit_sha: str
    paired_truthful_blob_sha: str
    issue_availability: bool
    issue_availability_reason: str
    task_availability: bool
    task_availability_reason: str
    experimental_eligible: bool
    exclusion_reason: str
    protocol_condition: str
    p1_sample: bool


def stable_id(*parts: str) -> str:
    payload = "|".join(parts).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _ref_key(row: dict) -> tuple[str, str]:
    return (row["reference_type"], row["reference"])


def build_commit_spec_states(rows: list[dict]) -> dict[tuple[str, str], list[CommitSpecState]]:
    """Aggregate longitudinal rows to per-spec commit snapshots."""
    grouped: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        if _csv_bool(row.get("reference_removed")):
            continue
        grouped[(row["repo_id"], row["instruction_path"], row["commit"])].append(row)

    by_spec: dict[tuple[str, str], list[CommitSpecState]] = defaultdict(list)
    for (repo_id, instruction_path, commit), events in grouped.items():
        events.sort(key=lambda r: r["reference"])
        refs = { _ref_key(e): e["state"] for e in events }
        transitions = { _ref_key(e): e.get("transition", "") for e in events }
        by_spec[(repo_id, instruction_path)].append(
            CommitSpecState(
                repo_id=repo_id,
                instruction_path=instruction_path,
                commit=commit,
                commit_time=events[0]["commit_time"],
                references=refs,
                transitions=transitions,
            )
        )

    for key in by_spec:
        by_spec[key].sort(key=lambda s: _parse_time(s.commit_time))
    return by_spec


def _counts(state: CommitSpecState) -> dict[str, int]:
    n_verifiable = n_verified = n_missing = n_unverifiable = n_repaired = 0
    for (ref_type, _), st in state.references.items():
        if st == "REPAIRED":
            n_repaired += 1
        if ref_type in VERIFIABLE_REFERENCE_TYPES:
            n_verifiable += 1
            if st == "VERIFIED":
                n_verified += 1
            elif st == "MISSING":
                n_missing += 1
        elif st == "UNVERIFIABLE":
            n_unverifiable += 1
    return {
        "n_refs_total": len(state.references),
        "n_verifiable": n_verifiable,
        "n_verified_verifiable": n_verified,
        "n_missing_verifiable": n_missing,
        "n_unverifiable": n_unverifiable,
        "n_repaired": n_repaired,
    }


def _verified_refs(state: CommitSpecState) -> list[str]:
    return [
        ref
        for (ref_type, ref), st in state.references.items()
        if st == "VERIFIED" and ref_type in VERIFIABLE_REFERENCE_TYPES
    ]


def _ref_ever_verified(
    spec_rows: list[dict],
    ref_key: tuple[str, str],
) -> bool:
    for row in spec_rows:
        if _csv_bool(row.get("reference_removed")):
            continue
        if _ref_key(row) == ref_key and row["state"] == "VERIFIED":
            return True
    return False


def _select_truthful(states: list[CommitSpecState]) -> tuple[CommitSpecState, str, str] | None:
    candidates: list[tuple[float, datetime, CommitSpecState]] = []
    for state in states:
        counts = _counts(state)
        if counts["n_verifiable"] == 0:
            continue
        ratio = counts["n_verified_verifiable"] / counts["n_verifiable"]
        if ratio <= 0:
            continue
        candidates.append((ratio, _parse_time(state.commit_time), state))
    if not candidates:
        return None
    candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
    best = candidates[0][2]
    anchor = _verified_refs(best)[0] if _verified_refs(best) else ""
    anchor_type = "path"
    for (t, r), _ in best.references.items():
        if r == anchor:
            anchor_type = t
            break
    return best, anchor, anchor_type


def _select_born_stale(
    states: list[CommitSpecState],
    spec_rows: list[dict],
) -> tuple[CommitSpecState, str, str] | None:
    for state in states:
        for (ref_type, ref), st in state.references.items():
            if ref_type not in VERIFIABLE_REFERENCE_TYPES:
                continue
            if st != "MISSING":
                continue
            if not _ref_ever_verified(spec_rows, (ref_type, ref)):
                return state, ref, ref_type
    return None


def _select_repaired(states: list[CommitSpecState]) -> tuple[CommitSpecState, str, str] | None:
    for state in states:
        for (ref_type, ref), st in state.references.items():
            if st == "REPAIRED":
                return state, ref, ref_type
            if state.transitions.get((ref_type, ref), "").endswith("->REPAIRED"):
                return state, ref, ref_type
    return None


def _select_degraded(states: list[CommitSpecState]) -> tuple[CommitSpecState, str, str] | None:
    for state in states:
        for (ref_type, ref), transition in state.transitions.items():
            if transition == "VERIFIED->MISSING":
                return state, ref, ref_type
    return None


def _last_verified_commit_for_ref(
    spec_rows: list[dict],
    ref_type: str,
    reference: str,
    before_time: datetime,
) -> str:
    verified: list[tuple[datetime, str]] = []
    for row in spec_rows:
        if _csv_bool(row.get("reference_removed")):
            continue
        if row["reference_type"] != ref_type or row["reference"] != reference:
            continue
        if row["state"] != "VERIFIED":
            continue
        t = _parse_time(row["commit_time"])
        if t <= before_time:
            verified.append((t, row["commit"]))
    if not verified:
        return ""
    verified.sort(key=lambda x: x[0])
    return verified[-1][1]


def _protocol_condition(snapshot_type: SnapshotType) -> str:
    return {
        "truthful": "A_truthful",
        "born_stale": "B_observed_integrity_loss",
        "degraded": "B_observed_integrity_loss",
        "repaired": "post_repair_observational",
    }[snapshot_type]


def _eligibility(
    *,
    snapshot_type: SnapshotType,
    blob_available: bool,
    counts: dict[str, int],
    issue_available: bool,
    task_available: bool,
) -> tuple[bool, str]:
    if not blob_available:
        return False, "instruction_blob_missing"
    if counts["n_verifiable"] == 0:
        return False, "no_verifiable_references"
    if snapshot_type == "truthful" and counts["n_verified_verifiable"] == 0:
        return False, "no_verified_verifiable_at_snapshot"
    if snapshot_type == "born_stale" and counts["n_missing_verifiable"] == 0:
        return False, "no_born_stale_references"
    if snapshot_type == "degraded" and counts["n_missing_verifiable"] == 0:
        return False, "no_degraded_references_at_snapshot"
    if snapshot_type == "repaired" and counts["n_repaired"] == 0:
        return False, "no_repaired_state_at_snapshot"
    if not task_available:
        return False, "task_availability_heuristic_failed"
    if snapshot_type in ("born_stale", "degraded") and not issue_available:
        return False, "issue_availability_heuristic_failed"
    return True, ""


def _load_instruction_text(
    blob_sha: str,
    blob_store: BlobStore | None,
    cache: dict[str, str],
) -> str:
    if not blob_sha:
        return ""
    if blob_sha in cache:
        return cache[blob_sha]
    text = ""
    if blob_store is not None:
        try:
            text = blob_store.get_text(blob_sha).decode("utf-8", errors="replace")
        except OSError:
            text = ""
    cache[blob_sha] = text
    return text


def build_rq5_candidate_snapshots(
    *,
    rows: list[dict],
    repo_urls: dict[str, str],
    blob_index: dict[tuple[str, str, str], str],
    blob_store: BlobStore | None,
    family_by_spec: dict[tuple[str, str], str],
    p1_keys: set[tuple[str, str]],
) -> list[RQ5CandidateSnapshot]:
    by_spec = build_commit_spec_states(rows)
    spec_rows_map: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        if _csv_bool(row.get("reference_removed")):
            continue
        spec_rows_map[(row["repo_id"], row["instruction_path"])].append(row)

    snapshots: list[RQ5CandidateSnapshot] = []
    text_cache: dict[str, str] = {}

    for (repo_id, instruction_path), states in sorted(by_spec.items()):
        if not states:
            continue
        spec_id = stable_id(repo_id, instruction_path)
        spec_rows = spec_rows_map[(repo_id, instruction_path)]
        repo_url = repo_urls.get(repo_id, "")
        family = family_by_spec.get((repo_id, instruction_path), "")

        truthful_state = _select_truthful(states)
        truthful_commit = truthful_state[0].commit if truthful_state else ""
        truthful_blob = blob_index.get((repo_id, instruction_path, truthful_commit), "") if truthful_commit else ""

        for snapshot_type in ("truthful", "born_stale", "repaired", "degraded"):
            if snapshot_type == "truthful":
                picked = _select_truthful(states)
            elif snapshot_type == "born_stale":
                picked = _select_born_stale(states, spec_rows)
            elif snapshot_type == "repaired":
                picked = _select_repaired(states)
            else:
                picked = _select_degraded(states)

            if picked is None:
                continue

            state, anchor_ref, anchor_type = picked
            counts = _counts(state)
            ratio = (
                counts["n_verified_verifiable"] / counts["n_verifiable"]
                if counts["n_verifiable"]
                else 0.0
            )
            blob_sha = blob_index.get((repo_id, instruction_path, state.commit), "")
            blob_available = bool(blob_sha)
            instruction_text = _load_instruction_text(blob_sha, blob_store, text_cache)

            issue_ok, issue_reason = assess_issue_availability(
                snapshot_type=snapshot_type,
                instruction_text=instruction_text,
                n_missing_verifiable=counts["n_missing_verifiable"],
                n_verifiable=counts["n_verifiable"],
            )
            task_ok, task_reason = assess_task_availability(
                instruction_text=instruction_text,
                verified_refs=_verified_refs(state),
            )
            eligible, exclusion = _eligibility(
                snapshot_type=snapshot_type,
                blob_available=blob_available,
                counts=counts,
                issue_available=issue_ok,
                task_available=task_ok,
            )

            paired_truthful_commit = ""
            paired_truthful_blob = ""
            if snapshot_type in ("degraded", "repaired", "born_stale"):
                if snapshot_type == "degraded":
                    paired_truthful_commit = _last_verified_commit_for_ref(
                        spec_rows,
                        anchor_type,
                        anchor_ref,
                        _parse_time(state.commit_time),
                    )
                else:
                    paired_truthful_commit = truthful_commit
                if paired_truthful_commit:
                    paired_truthful_blob = blob_index.get(
                        (repo_id, instruction_path, paired_truthful_commit), ""
                    )

            snapshot_id = stable_id(spec_id, snapshot_type, state.commit)
            snapshots.append(
                RQ5CandidateSnapshot(
                    spec_id=spec_id,
                    snapshot_id=snapshot_id,
                    repo_id=repo_id,
                    repo_url=repo_url,
                    instruction_path=instruction_path,
                    family_group=family,
                    snapshot_type=snapshot_type,
                    commit_sha=state.commit,
                    commit_time=state.commit_time,
                    task_commit_sha=state.commit,
                    blob_sha=blob_sha,
                    blob_available=blob_available,
                    n_refs_total=counts["n_refs_total"],
                    n_verifiable=counts["n_verifiable"],
                    n_verified_verifiable=counts["n_verified_verifiable"],
                    n_missing_verifiable=counts["n_missing_verifiable"],
                    n_unverifiable=counts["n_unverifiable"],
                    n_repaired=counts["n_repaired"],
                    verified_ratio_verifiable=round(ratio, 4),
                    anchor_reference=anchor_ref,
                    anchor_reference_type=anchor_type,
                    paired_truthful_commit_sha=paired_truthful_commit,
                    paired_truthful_blob_sha=paired_truthful_blob,
                    issue_availability=issue_ok,
                    issue_availability_reason=issue_reason,
                    task_availability=task_ok,
                    task_availability_reason=task_reason,
                    experimental_eligible=eligible,
                    exclusion_reason=exclusion,
                    protocol_condition=_protocol_condition(snapshot_type),
                    p1_sample=(repo_id, instruction_path) in p1_keys,
                )
            )

    return snapshots


def snapshots_to_rows(snapshots: list[RQ5CandidateSnapshot]) -> list[dict]:
    return [asdict(s) for s in snapshots]
