"""Longitudinal reconstruction of reference states from L1 instruction-file events."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from artifact_lab.experiments.truth_pilots.references import extract_references
from artifact_lab.experiments.truth_pilots.sample import _parse_commit_time
from artifact_lab.experiments.truth_decay.states import (
    reference_key,
    resolve_observation_state,
    transition_label,
)
from artifact_lab.experiments.truth_decay.verify_at_commit import CommitTreeCache, verify_reference_at_commit
from artifact_lab.ingest.git_utils import clone_bare, remove_clone
from artifact_lab.protocol.detector import is_matched_path
from artifact_lab.store.blobs import BlobStore

import pyarrow.parquet as pq


@dataclass(frozen=True)
class LongitudinalObservation:
    repo_id: str
    repo_url: str
    instruction_path: str
    commit: str
    commit_time: str
    reference: str
    reference_type: str
    state: str
    previous_state: str
    transition: str
    change_type: str
    reference_added: bool
    reference_removed: bool
    first_failure: bool
    repair_event: bool


def load_instruction_file_events(
    l1_paths: list[Path],
    *,
    family: str = "ai_conventions_v1",
) -> dict[tuple[str, str], list[dict]]:
    """Group L1 rows by (repo_id, instruction_path), sorted by commit_time."""
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for l1_path in l1_paths:
        path = l1_path.resolve()
        if path.is_dir():
            parquet = path / "events.parquet"
            if not parquet.exists():
                continue
            table = pq.read_table(parquet)
        elif path.exists() and path.stat().st_size > 100:
            table = pq.read_table(path)
        else:
            continue
        for row in table.to_pylist():
            if not is_matched_path(row["path"], family):
                continue
            key = (row["repo_id"], row["path"])
            grouped[key].append(row)

    for key in grouped:
        grouped[key].sort(key=lambda r: _parse_commit_time(r["commit_time"]))
    return grouped


def reconstruct_longitudinal_table(
    *,
    l1_paths: list[Path],
    blobs_dir: Path,
    scratch_dir: Path,
    clone_timeout: int = 180,
    max_files: int | None = None,
    file_filter: set[tuple[str, str]] | None = None,
) -> list[LongitudinalObservation]:
    grouped = load_instruction_file_events(l1_paths)
    file_keys = sorted(grouped.keys())
    if file_filter is not None:
        file_keys = [k for k in file_keys if k in file_filter]
    if max_files is not None:
        file_keys = file_keys[:max_files]

    blob_store = BlobStore(blobs_dir)
    observations: list[LongitudinalObservation] = []
    clone_cache: dict[str, Path] = {}
    tree_caches: dict[str, CommitTreeCache] = {}

    try:
        for repo_id, instruction_path in file_keys:
            events = grouped[(repo_id, instruction_path)]
            if not events:
                continue
            repo_url = events[0]["repo_url"]

            if repo_id not in clone_cache:
                clone_path = scratch_dir / f"rq1_{repo_id}"
                clone_bare(repo_url, clone_path, timeout=clone_timeout)
                clone_cache[repo_id] = clone_path
                tree_caches[repo_id] = CommitTreeCache(clone_path, timeout=clone_timeout)

            repo_dir = clone_cache[repo_id]
            tree_cache = tree_caches[repo_id]

            previous_refs: set[tuple[str, str]] = set()
            previous_states: dict[tuple[str, str], str] = {}
            seen_failure: set[tuple[str, str]] = set()

            for event in events:
                commit_sha = event["commit_sha"]
                commit_time = _parse_commit_time(event["commit_time"])
                change_type = event.get("change_type") or ""
                commit_time_iso = commit_time.isoformat()

                if change_type == "delete" or not (event.get("blob_sha") or "").strip():
                    for ref_type, ref_text in sorted(previous_refs):
                        prev = previous_states.get((ref_type, ref_text), "")
                        observations.append(
                            LongitudinalObservation(
                                repo_id=repo_id,
                                repo_url=repo_url,
                                instruction_path=instruction_path,
                                commit=commit_sha,
                                commit_time=commit_time_iso,
                                reference=ref_text,
                                reference_type=ref_type,
                                state="DELETED",
                                previous_state=prev,
                                transition=transition_label(prev or None, "DELETED"),
                                change_type=change_type or "delete",
                                reference_added=False,
                                reference_removed=False,
                                first_failure=False,
                                repair_event=False,
                            )
                        )
                        previous_states[(ref_type, ref_text)] = "DELETED"
                    previous_refs.clear()
                    continue

                try:
                    text = blob_store.get_text(event["blob_sha"]).decode("utf-8", errors="replace")
                except FileNotFoundError:
                    continue

                extracted = extract_references(text)
                current_refs = {reference_key(r.reference_type, r.reference_text) for r in extracted}
                added_refs = current_refs - previous_refs
                removed_refs = previous_refs - current_refs

                for ref in extracted:
                    key = reference_key(ref.reference_type, ref.reference_text)
                    verify_status, _ = verify_reference_at_commit(
                        ref,
                        repo_dir=repo_dir,
                        commit_sha=commit_sha,
                        tree_cache=tree_cache,
                        timeout=clone_timeout,
                    )
                    prev = previous_states.get(key, "")
                    state = resolve_observation_state(
                        verify_status=verify_status,
                        previous_state=prev or None,
                        file_deleted=False,
                    )
                    first_failure = state == "MISSING" and key not in seen_failure
                    if first_failure:
                        seen_failure.add(key)
                    repair_event = state == "REPAIRED"

                    observations.append(
                        LongitudinalObservation(
                            repo_id=repo_id,
                            repo_url=repo_url,
                            instruction_path=instruction_path,
                            commit=commit_sha,
                            commit_time=commit_time_iso,
                            reference=ref.reference_text,
                            reference_type=ref.reference_type,
                            state=state,
                            previous_state=prev,
                            transition=transition_label(prev or None, state),
                            change_type=change_type,
                            reference_added=key in added_refs,
                            reference_removed=False,
                            first_failure=first_failure,
                            repair_event=repair_event,
                        )
                    )
                    previous_states[key] = state

                for ref_type, ref_text in sorted(removed_refs):
                    prev = previous_states.get((ref_type, ref_text), "")
                    observations.append(
                        LongitudinalObservation(
                            repo_id=repo_id,
                            repo_url=repo_url,
                            instruction_path=instruction_path,
                            commit=commit_sha,
                            commit_time=commit_time_iso,
                            reference=ref_text,
                            reference_type=ref_type,
                            state=prev or "UNVERIFIABLE",
                            previous_state=prev,
                            transition=f"{prev or 'UNKNOWN'}->REMOVED",
                            change_type=change_type,
                            reference_added=False,
                            reference_removed=True,
                            first_failure=False,
                            repair_event=False,
                        )
                    )

                previous_refs = current_refs

    finally:
        for clone_path in clone_cache.values():
            remove_clone(clone_path)

    return observations


def observations_to_rows(observations: list[LongitudinalObservation]) -> list[dict]:
    return [asdict(row) for row in observations]
