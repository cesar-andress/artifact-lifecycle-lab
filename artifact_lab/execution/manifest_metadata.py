"""Standard metadata fields for dataset manifests."""

from __future__ import annotations

import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

from artifact_lab.execution.session import touch_wave, wave_execution_finish, wave_execution_start
from artifact_lab.execution.states import COMPLETED, FAILED, normalize_state
from artifact_lab.store.job_queue import JobQueue
from artifact_lab.store.manifest import git_sha


def registry_hash_sha256(registry_path: Path) -> str:
    digest = hashlib.sha256(registry_path.read_bytes()).hexdigest()
    return digest


def queue_outcome_counts(
    queue_path: Path,
    *,
    family: str,
    wave: str,
) -> tuple[int, int]:
    if not queue_path.exists():
        return 0, 0
    with JobQueue(queue_path) as queue:
        completed = 0
        failed = 0
        for job in queue.list_jobs(family=family, wave=wave):
            state = normalize_state(job.state)
            if state == COMPLETED:
                completed += 1
            elif state == FAILED:
                failed += 1
    return completed, failed


def build_dataset_manifest_extra(
    *,
    registry_path: Path,
    registry_version: str | None,
    wave_id: str,
    protocol_version: str,
    detector_version: str,
    queue_path: Path,
    family: str,
    wave: str,
    dataset_version: str | None = None,
    mark_activity: bool = True,
) -> dict:
    if mark_activity:
        touch_wave(wave_id)
    completed, failed = queue_outcome_counts(queue_path, family=family, wave=wave)
    execution_start = wave_execution_start(wave_id)
    execution_finish = wave_execution_finish(wave_id)
    extra: dict = {
        "registry_version": registry_version,
        "registry_hash": registry_hash_sha256(registry_path) if registry_path.exists() else None,
        "wave_id": wave_id,
        "protocol_version": protocol_version,
        "detector_version": detector_version,
        "git_commit": git_sha(),
        "python_version": sys.version.split()[0],
        "execution_start": execution_start,
        "execution_finish": execution_finish or datetime.now(timezone.utc).isoformat(),
        "completed_repositories": completed,
        "failed_repositories": failed,
    }
    if dataset_version is not None:
        extra["dataset_version"] = dataset_version
    return extra
