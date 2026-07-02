"""Recovery repairs for interrupted extraction runs."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path

import pyarrow as pa

from artifact_lab.contracts.schemas import FILE_EVENT_LOG_COLUMNS, file_event_log_schema
from artifact_lab.execution.atomic_io import atomic_write_parquet, remove_tmp_siblings
from artifact_lab.execution.paths import (
    global_events_path,
    global_manifest_path,
    repo_events_path,
)
from artifact_lab.execution.states import COMPLETED, FAILED, normalize_state
from artifact_lab.execution.verify import verify_repo_completion
from artifact_lab.store.blobs import BlobStore
from artifact_lab.store.job_queue import JobQueue
from artifact_lab.store.manifest import write_manifest
from artifact_lab.store.parquet import read_parquet


@dataclass
class RecoverAction:
    category: str
    detail: str


@dataclass
class RecoverReport:
    stale_reset: int = 0
    scratch_removed: list[str] = field(default_factory=list)
    tmp_removed: list[str] = field(default_factory=list)
    reverted_to_failed: list[str] = field(default_factory=list)
    inconsistent: list[str] = field(default_factory=list)
    actions: list[RecoverAction] = field(default_factory=list)
    global_events_rebuilt: bool = False

    @property
    def ok(self) -> bool:
        return True


def cleanup_scratch(scratch_dir: Path) -> list[str]:
    """Remove all scratch clones — never trust scratch after restart."""
    removed: list[str] = []
    if not scratch_dir.exists():
        return removed
    for child in scratch_dir.iterdir():
        if child.is_dir():
            shutil.rmtree(child, ignore_errors=True)
            removed.append(child.name)
    return removed


def rebuild_global_events(
    *,
    events_dir: Path,
    queue_path: Path,
    family: str,
    wave: str,
    registry_path: Path,
    protocol_version: str,
    extraction_wave: str,
    registry_version: str | None,
    dataset_version: str,
) -> bool:
    """Rebuild global events.parquet from verified per-repo artifacts only."""
    events_dir.mkdir(parents=True, exist_ok=True)
    out_path = global_events_path(events_dir)

    with JobQueue(queue_path) as queue:
        completed_ids = sorted(
            job.repo_id
            for job in queue.list_jobs(family=family, wave=wave)
            if normalize_state(job.state) == COMPLETED
        )

    merged: list[dict] = []
    for repo_id in completed_ids:
        path = repo_events_path(events_dir, repo_id)
        if path.exists():
            merged.extend(read_parquet(path).to_pylist())

    if merged:
        table = pa.Table.from_pylist(merged, schema=file_event_log_schema())
    else:
        table = pa.table(
            {col: pa.array([], type=file_event_log_schema().field(col).type) for col in FILE_EVENT_LOG_COLUMNS}
        )
    row_count = atomic_write_parquet(table, out_path, expected_columns=FILE_EVENT_LOG_COLUMNS)

    write_manifest(
        global_manifest_path(events_dir),
        dataset_name="file_event_log",
        version=extraction_wave,
        input_datasets=[str(registry_path)],
        protocol_version=protocol_version,
        row_count=row_count,
        columns=FILE_EVENT_LOG_COLUMNS,
        extra={
            "family": family,
            "dataset_version": dataset_version,
            "extraction_wave": extraction_wave,
            "registry_version": registry_version,
            "detector_version": protocol_version,
        },
    )
    return True


def run_recover(
    *,
    registry_path: Path,
    events_dir: Path,
    receipts_dir: Path,
    blobs_dir: Path,
    queue_path: Path,
    scratch_dir: Path,
    family: str,
    wave: str,
    protocol_version: str,
    extraction_wave: str,
    registry_version: str | None = None,
    dataset_version: str = "v1",
    stale_timeout_seconds: int | None = None,
) -> RecoverReport:
    report = RecoverReport()
    blob_store = BlobStore(blobs_dir)

    with JobQueue(queue_path) as queue:
        report.stale_reset = queue.reset_stale_in_progress(max_age_seconds=stale_timeout_seconds)
        if report.stale_reset:
            report.actions.append(
                RecoverAction("stale_reset", f"reset {report.stale_reset} in-progress job(s) -> pending")
            )

        for job in queue.list_jobs(family=family, wave=wave):
            if normalize_state(job.state) != COMPLETED:
                continue
            failures = verify_repo_completion(
                repo_id=job.repo_id,
                events_dir=events_dir,
                receipts_dir=receipts_dir,
                blob_store=blob_store,
            )
            if failures:
                queue.mark_failed(
                    job.repo_id,
                    family,
                    wave,
                    reason=f"recovery_revert: {'; '.join(failures)}",
                    n_events=0,
                )
                report.reverted_to_failed.append(job.repo_id)
                report.inconsistent.append(job.repo_id)
                report.actions.append(
                    RecoverAction(
                        "revert_completed",
                        f"{job.repo_id}: completed -> failed ({'; '.join(failures)})",
                    )
                )

    report.scratch_removed = cleanup_scratch(scratch_dir)
    if report.scratch_removed:
        report.actions.append(
            RecoverAction("scratch_cleanup", f"removed {len(report.scratch_removed)} scratch dir(s)")
        )

    for tmp in remove_tmp_siblings(events_dir):
        report.tmp_removed.append(str(tmp))
    if receipts_dir.exists():
        for tmp in remove_tmp_siblings(receipts_dir):
            report.tmp_removed.append(str(tmp))
    if report.tmp_removed:
        report.actions.append(RecoverAction("tmp_cleanup", f"removed {len(report.tmp_removed)} tmp file(s)"))

    # Receipts without matching queue completed state
    if receipts_dir.exists():
        with JobQueue(queue_path) as queue:
            for receipt_file in receipts_dir.glob("*.json"):
                repo_id = receipt_file.stem
                job = queue.get(repo_id, family, wave)
                if job is None:
                    report.inconsistent.append(repo_id)
                    report.actions.append(
                        RecoverAction("orphan_receipt", f"{repo_id}: receipt without queue job")
                    )
                elif normalize_state(job.state) != COMPLETED:
                    try:
                        data = json.loads(receipt_file.read_text(encoding="utf-8"))
                        status = data.get("status")
                        if status in {"ok", "no_matches"}:
                            report.inconsistent.append(repo_id)
                            report.actions.append(
                                RecoverAction(
                                    "receipt_queue_mismatch",
                                    f"{repo_id}: receipt status={status} but queue state={job.state}",
                                )
                            )
                    except json.JSONDecodeError:
                        report.inconsistent.append(repo_id)

    rebuild_global_events(
        events_dir=events_dir,
        queue_path=queue_path,
        family=family,
        wave=wave,
        registry_path=registry_path,
        protocol_version=protocol_version,
        extraction_wave=extraction_wave,
        registry_version=registry_version,
        dataset_version=dataset_version,
    )
    report.global_events_rebuilt = True
    report.actions.append(RecoverAction("global_rebuild", "rebuilt events.parquet from completed per-repo L1"))

    return report
