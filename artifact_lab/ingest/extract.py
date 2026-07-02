"""L1 extraction: ephemeral clone → file event log + blob store."""

from __future__ import annotations

import csv
import json
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pyarrow as pa

from artifact_lab.contracts.datasets import L1_DATASET_VERSION
from artifact_lab.contracts.paths import EXTRACTION_PROFILE_PATH
from artifact_lab.contracts.repo_id import normalize_repo_url, repo_id_from_url
from artifact_lab.contracts.schemas import (
    FILE_EVENT_LOG_COLUMNS,
    file_event_log_schema,
    hash_email,
)
from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.execution.checkpoint import RepoCheckpoint
from artifact_lab.execution.execution_log import ExecutionLog
from artifact_lab.execution.paths import (
    execution_log_path,
    receipt_path,
    repo_events_path,
    repo_manifest_path,
)
from artifact_lab.execution.recover import cleanup_scratch, rebuild_global_events
from artifact_lab.execution.verify import verify_repo_completion
from artifact_lab.ingest.git_activity import track_git_activity
from artifact_lab.ingest.git_utils import (
    blob_at_commit,
    clone_bare,
    deletion_commits,
    log_follow,
    remove_clone,
    ts_to_datetime,
)
from artifact_lab.ingest.profiling import (
    ExtractionLiveState,
    ExtractionProfile,
    PhaseTimings,
    ResourceMetrics,
    assign_batch_write_shares,
    format_extraction_summary,
    format_progress_log,
    load_profiles,
    merge_profiles,
    slow_repo_warning,
    write_profiles,
)
from artifact_lab.protocol.detector import is_matched_path, is_text_candidate, safe_normalize_path
from artifact_lab.protocol.loader import family_version, load_family
from artifact_lab.store.blobs import BlobStore
from artifact_lab.store.job_queue import JobQueue
from artifact_lab.store.manifest import write_manifest
from artifact_lab.store.parquet import read_parquet, write_parquet


DEFAULT_CLONE_TIMEOUT = 300
DEFAULT_REPO_TIMEOUT = 600
SKIP_SLOW_CLONE_TIMEOUT = 120
SKIP_SLOW_REPO_TIMEOUT = 120

INSPECTION_MODE_HEAD_ONLY = "head-only"
INSPECTION_MODE_FULL_HISTORY = "full-history"
DEFAULT_INSPECTION_MODE = INSPECTION_MODE_HEAD_ONLY
INSPECTION_MODES: tuple[str, ...] = (INSPECTION_MODE_HEAD_ONLY, INSPECTION_MODE_FULL_HISTORY)

# Test hook: raise when phase name matches (e.g. "clone", "parquet", "manifest", "receipt").
FAULT_INJECTION_HOOK: Callable[[str], None] | None = None


def _inject_fault(phase: str) -> None:
    if FAULT_INJECTION_HOOK is not None:
        FAULT_INJECTION_HOOK(phase)


@dataclass
class ExtractConfig:
    registry_path: Path
    family: str
    scratch_dir: Path
    events_dir: Path
    blobs_dir: Path
    receipts_dir: Path
    queue_path: Path
    extraction_wave: str = "pilot_v1"
    dataset_version: str = L1_DATASET_VERSION
    registry_version: str | None = None
    clone_timeout: int = 300
    repo_timeout: int = 600
    max_clone_bytes: int = 500_000_000
    force: bool = False
    retry_failed: bool = False
    limit: int | None = None
    profile_path: Path = EXTRACTION_PROFILE_PATH
    inspection_mode: str = DEFAULT_INSPECTION_MODE


class CloneTooLargeError(RuntimeError):
    pass


class RepoTimeoutError(RuntimeError):
    pass


def read_registry(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        return []
    if "repo_url" not in rows[0]:
        raise ValueError("registry must include repo_url column")
    for row in rows:
        row["repo_url"] = row["repo_url"].strip()
        row["repo_id"] = repo_id_from_url(row["repo_url"])
        row["normalized_repo_url"] = normalize_repo_url(row["repo_url"])
    return rows


def registry_skip_reason(row: dict[str, str]) -> str | None:
    archived = (row.get("archived") or "").strip().lower()
    if archived in {"1", "true", "yes"}:
        return "archived"
    skip = (row.get("skip_reason") or "").strip()
    if skip:
        return f"skip:{skip}"
    too_large = (row.get("too_large") or "").strip().lower()
    if too_large in {"1", "true", "yes"}:
        return "too_large"
    return None


def clone_size_bytes(repo_dir: Path) -> int:
    total = 0
    for path in repo_dir.rglob("*"):
        if path.is_file():
            total += path.stat().st_size
    return total


def write_receipt(receipts_dir: Path, repo_id: str, receipt: dict) -> Path:
    receipts_dir.mkdir(parents=True, exist_ok=True)
    path = receipt_path(receipts_dir, repo_id)
    serializable = {k: v for k, v in receipt.items() if k not in {"events", "profile"}}
    _inject_fault("receipt")
    atomic_write_text(path, json.dumps(serializable, indent=2) + "\n")
    return path


def write_repo_l1_events(events_dir: Path, repo_id: str, events: list[dict]) -> Path:
    out_path = repo_events_path(events_dir, repo_id)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    _inject_fault("parquet")
    if events:
        table = pa.Table.from_pylist(events, schema=file_event_log_schema())
    else:
        table = pa.table(
            {col: pa.array([], type=file_event_log_schema().field(col).type) for col in FILE_EVENT_LOG_COLUMNS}
        )
    from artifact_lab.store.parquet import write_parquet

    write_parquet(table, out_path, expected_columns=FILE_EVENT_LOG_COLUMNS)
    return out_path


def write_repo_l1_manifest(
    events_dir: Path,
    repo_id: str,
    *,
    row_count: int,
    family: str,
    extraction_wave: str,
    registry_version: str | None,
    dataset_version: str,
    detector_version: str,
) -> Path:
    _inject_fault("manifest")
    path = repo_manifest_path(events_dir, repo_id)
    write_manifest(
        path,
        dataset_name="file_event_log_repo",
        version=extraction_wave,
        input_datasets=[repo_id],
        protocol_version=detector_version,
        row_count=row_count,
        columns=FILE_EVENT_LOG_COLUMNS,
        extra={
            "repo_id": repo_id,
            "family": family,
            "dataset_version": dataset_version,
            "extraction_wave": extraction_wave,
            "registry_version": registry_version,
            "detector_version": detector_version,
        },
    )
    return path


def discover_matched_paths(
    repo_dir: Path,
    family: str,
    *,
    git_timeout: int,
    timings: PhaseTimings,
    inspection_mode: str = DEFAULT_INSPECTION_MODE,
    live: ExtractionLiveState | None = None,
) -> set[str]:
    from artifact_lab.ingest.git_utils import list_all_paths, list_head_paths

    if live:
        live.enter_phase("inspection")
    t0 = time.perf_counter()
    try:
        if inspection_mode == INSPECTION_MODE_HEAD_ONLY:
            raw_paths = list_head_paths(repo_dir, timeout=git_timeout)
        else:
            raw_paths = list_all_paths(repo_dir, timeout=git_timeout)
    finally:
        if live is None or live.should_record_timing():
            timings.inspection_s += time.perf_counter() - t0

    if live:
        live.enter_phase("detector")
    t0 = time.perf_counter()
    try:
        matched: set[str] = set()
        for raw in raw_paths:
            norm = safe_normalize_path(raw)
            if norm and is_matched_path(norm, family):
                matched.add(norm)
    finally:
        if live is None or live.should_record_timing():
            timings.detector_s += time.perf_counter() - t0
    return matched


def extract_repo_events(
    repo_dir: Path,
    *,
    repo_id: str,
    repo_url: str,
    family: str,
    extraction_wave: str,
    detector_version: str,
    blob_store: BlobStore,
    git_timeout: int,
    timings: PhaseTimings,
    resources: ResourceMetrics,
    inspection_mode: str = DEFAULT_INSPECTION_MODE,
    live: ExtractionLiveState | None = None,
) -> list[dict]:
    paths = discover_matched_paths(
        repo_dir,
        family,
        git_timeout=git_timeout,
        timings=timings,
        inspection_mode=inspection_mode,
        live=live,
    )
    events: list[dict] = []
    for path in sorted(paths):
        if live:
            live.enter_phase("history")
        t0 = time.perf_counter()
        try:
            history = log_follow(repo_dir, path, timeout=git_timeout)
            deletes = deletion_commits(repo_dir, path, timeout=git_timeout)
        finally:
            if live is None or live.should_record_timing():
                timings.history_s += time.perf_counter() - t0

        for idx, touch in enumerate(history):
            change_type = "add" if idx == 0 else "modify"
            if touch["commit_sha"] in deletes:
                change_type = "delete"
            blob_sha = ""
            if change_type != "delete" and is_text_candidate(path, family):
                if live:
                    live.enter_phase("blobs")
                t0 = time.perf_counter()
                try:
                    _inject_fault("blob")
                    content = blob_at_commit(repo_dir, touch["commit_sha"], path, timeout=git_timeout)
                    if content is not None and b"\x00" not in content:
                        t_blob = time.perf_counter()
                        blob_sha = blob_store.put_text(content)
                        resources.local_cpu_s += time.perf_counter() - t_blob
                finally:
                    if live is None or live.should_record_timing():
                        timings.blobs_s += time.perf_counter() - t0
            events.append(
                {
                    "repo_id": repo_id,
                    "repo_url": repo_url,
                    "family": family,
                    "path": path,
                    "commit_sha": touch["commit_sha"],
                    "commit_time": ts_to_datetime(touch["commit_ts"]),
                    "author_name": touch["author_name"],
                    "author_email_hash": hash_email(touch["author_email"]),
                    "change_type": change_type,
                    "blob_sha": blob_sha,
                    "extraction_wave": extraction_wave,
                    "detector_version": detector_version,
                }
            )
    return events


def _extract_repo_body(
    cfg: ExtractConfig,
    row: dict[str, str],
    blob_store: BlobStore,
    live: ExtractionLiveState,
    checkpoint: RepoCheckpoint | None = None,
) -> dict:
    repo_id = row["repo_id"]
    repo_url = row["normalized_repo_url"]
    clone_path = cfg.scratch_dir / repo_id
    wall_start = time.perf_counter()
    started = datetime.now(timezone.utc)
    timings = PhaseTimings()
    profile = live.profile
    profile.timings = timings
    profile.inspection_mode = cfg.inspection_mode
    receipt: dict = {
        "repo_id": repo_id,
        "repo_url": repo_url,
        "family": cfg.family,
        "extraction_wave": cfg.extraction_wave,
        "started_at": started.isoformat(),
        "status": "failed",
        "n_events": 0,
        "matched_paths": [],
        "error": None,
        "skip_reason": None,
    }
    try:
        skip = registry_skip_reason(row)
        if skip:
            receipt["status"] = "skipped"
            receipt["skip_reason"] = skip
            receipt["error"] = skip
            receipt["events"] = []
            profile.status = "skipped"
            profile.failure_reason = skip
            return receipt

        with track_git_activity() as git_stats:
            live.enter_phase("clone")
            t0 = time.perf_counter()
            try:
                _inject_fault("clone")
                clone_bare(row["repo_url"], clone_path, timeout=cfg.clone_timeout)
            finally:
                if live.should_record_timing():
                    timings.clone_s = time.perf_counter() - t0

            if checkpoint is not None:
                checkpoint.start_extracting()

            size = clone_size_bytes(clone_path)
            receipt["clone_bytes"] = size
            profile.clone_bytes = size
            if size > cfg.max_clone_bytes:
                raise CloneTooLargeError(f"clone size {size} exceeds limit {cfg.max_clone_bytes}")

            git_timeout = min(cfg.repo_timeout, cfg.clone_timeout)
            events = extract_repo_events(
                clone_path,
                repo_id=repo_id,
                repo_url=repo_url,
                family=cfg.family,
                extraction_wave=cfg.extraction_wave,
                detector_version=family_version(cfg.family),
                blob_store=blob_store,
                git_timeout=git_timeout,
                timings=timings,
                resources=profile.resources,
                inspection_mode=cfg.inspection_mode,
                live=live,
            )
            profile.resources.local_cpu_s += timings.detector_s
            profile.resources.git_network_wait_s = git_stats.git_network_wait_s
            profile.resources.git_local_wait_s = git_stats.git_local_wait_s
            profile.resources.n_git_subprocesses = git_stats.n_git_subprocesses
            profile.resources.n_lazy_blob_fetches = git_stats.n_lazy_blob_fetches
            profile.resources.bytes_downloaded = size + git_stats.bytes_from_git

            receipt["matched_paths"] = sorted({e["path"] for e in events})
            receipt["n_events"] = len(events)
            receipt["status"] = "ok" if events else "no_matches"
            receipt["events"] = events
            profile.status = receipt["status"]
            profile.n_events = len(events)
            profile.n_matched_paths = len(receipt["matched_paths"])
    except Exception as exc:  # noqa: BLE001 — record and continue pilot
        receipt["error"] = f"{exc.__class__.__name__}: {exc}"
        receipt["events"] = []
        profile.status = "failed"
        profile.failure_reason = normalize_failure_reason(receipt.get("error"))
    finally:
        live.enter_phase("cleanup")
        t0 = time.perf_counter()
        _inject_fault("cleanup")
        remove_clone(clone_path)
        if live.should_record_timing():
            timings.cleanup_s = time.perf_counter() - t0
            timings.wall_s = time.perf_counter() - wall_start
        receipt["clone_removed"] = not clone_path.exists()
        receipt["finished_at"] = datetime.now(timezone.utc).isoformat()
        profile.recorded_at = receipt["finished_at"]
        receipt["profile"] = profile
    return receipt


def normalize_failure_reason(error: str | None) -> str:
    if not error:
        return "unknown_failure"
    if error.startswith("timeout:"):
        return error
    if "RepoTimeoutError" in error or error == "timeout":
        return "timeout"
    return error


def extract_one_repo(
    cfg: ExtractConfig,
    row: dict[str, str],
    blob_store: BlobStore,
    checkpoint: RepoCheckpoint | None = None,
) -> dict:
    started = datetime.now(timezone.utc)
    profile = ExtractionProfile(
        repo_id=row["repo_id"],
        repo_url=row["normalized_repo_url"],
        extraction_wave=cfg.extraction_wave,
        status="failed",
        timings=PhaseTimings(),
        resources=ResourceMetrics(),
        recorded_at=started.isoformat(),
        inspection_mode=cfg.inspection_mode,
    )
    live = ExtractionLiveState(profile=profile)
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(_extract_repo_body, cfg, row, blob_store, live, checkpoint)
        try:
            return future.result(timeout=cfg.repo_timeout)
        except FuturesTimeout:
            clone_path = cfg.scratch_dir / row["repo_id"]
            remove_clone(clone_path)
            finished = datetime.now(timezone.utc).isoformat()
            profile = live.build_timeout_profile()
            profile.recorded_at = finished
            return {
                "repo_id": row["repo_id"],
                "repo_url": row["normalized_repo_url"],
                "family": cfg.family,
                "extraction_wave": cfg.extraction_wave,
                "started_at": started.isoformat(),
                "finished_at": finished,
                "status": "failed",
                "n_events": 0,
                "matched_paths": [],
                "error": profile.failure_reason,
                "skip_reason": None,
                "clone_removed": not clone_path.exists(),
                "events": [],
                "profile": profile,
            }


def _load_existing_events(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return read_parquet(path).to_pylist()


def _merge_events(
    existing: list[dict],
    fresh: list[dict],
    *,
    replaced_repo_ids: set[str],
) -> list[dict]:
    kept = [e for e in existing if e["repo_id"] not in replaced_repo_ids]
    return kept + fresh


def _record_profile(cfg: ExtractConfig, receipt: dict, run_profiles: list[ExtractionProfile]) -> ExtractionProfile | None:
    profile = receipt.get("profile")
    if not isinstance(profile, ExtractionProfile):
        return None
    status = receipt["status"]
    if status == "skipped":
        profile.failure_reason = receipt.get("skip_reason") or "skipped"
    elif status not in {"ok", "no_matches"}:
        profile.failure_reason = normalize_failure_reason(profile.failure_reason or receipt.get("error"))
    run_profiles.append(profile)
    existing_rows = [p.to_row() for p in load_profiles(cfg.profile_path)]
    merged = merge_profiles(existing_rows, [profile])
    write_profiles(merged, cfg.profile_path, csv_path=cfg.profile_path.with_suffix(".csv"))
    return profile


def _finalize_successful_repo(
    cfg: ExtractConfig,
    checkpoint: RepoCheckpoint,
    repo_id: str,
    receipt: dict,
    blob_store: BlobStore,
    queue: JobQueue,
) -> bool:
    events = receipt.get("events") or []
    n_events = len(events)
    detector_version = family_version(cfg.family)

    checkpoint.start_writing_l1()
    write_repo_l1_events(cfg.events_dir, repo_id, events)
    write_repo_l1_manifest(
        cfg.events_dir,
        repo_id,
        row_count=n_events,
        family=cfg.family,
        extraction_wave=cfg.extraction_wave,
        registry_version=cfg.registry_version,
        dataset_version=cfg.dataset_version,
        detector_version=detector_version,
    )
    write_receipt(cfg.receipts_dir, repo_id, receipt)

    checkpoint.start_verifying()
    failures = verify_repo_completion(
        repo_id=repo_id,
        events_dir=cfg.events_dir,
        receipts_dir=cfg.receipts_dir,
        blob_store=blob_store,
    )
    if failures:
        checkpoint.fail(reason=f"verification_failed: {'; '.join(failures)}")
        return False

    checkpoint.complete(n_events=n_events)
    rebuild_global_events(
        events_dir=cfg.events_dir,
        queue_path=cfg.queue_path,
        family=cfg.family,
        wave=cfg.extraction_wave,
        registry_path=cfg.registry_path,
        protocol_version=detector_version,
        extraction_wave=cfg.extraction_wave,
        registry_version=cfg.registry_version,
        dataset_version=cfg.dataset_version,
    )
    return True


def run_extract(cfg: ExtractConfig) -> Path:
    load_family(cfg.family)
    registry = read_registry(cfg.registry_path)
    if cfg.limit is not None:
        registry = registry[: cfg.limit]
    blob_store = BlobStore(cfg.blobs_dir)
    cfg.events_dir.mkdir(parents=True, exist_ok=True)
    out_path = cfg.events_dir / "events.parquet"
    detector_version = family_version(cfg.family)

    run_profiles: list[ExtractionProfile] = []
    stale_recovered = 0
    queue_counts: dict[str, int] = {}
    execution_log = ExecutionLog(execution_log_path(cfg.events_dir))

    scratch_removed = cleanup_scratch(cfg.scratch_dir)
    if scratch_removed:
        print(f"removed {len(scratch_removed)} abandoned scratch dir(s)", flush=True)

    with JobQueue(cfg.queue_path) as queue:
        stale_recovered = queue.reset_stale_in_progress()
        if stale_recovered:
            print(f"recovered {stale_recovered} stale in-progress job(s) -> pending", flush=True)
        for row in registry:
            queue.upsert_pending(row["repo_id"], row["normalized_repo_url"], cfg.family, cfg.extraction_wave)

        total = len(registry)
        for index, row in enumerate(registry, start=1):
            repo_id = row["repo_id"]
            repo_url = row["normalized_repo_url"]
            if not queue.should_process(
                repo_id,
                cfg.family,
                cfg.extraction_wave,
                force=cfg.force,
                retry_failed=cfg.retry_failed,
            ):
                job = queue.get(repo_id, cfg.family, cfg.extraction_wave)
                state = job.state if job else "unknown"
                print(f"[{index}/{total}] skip {repo_url} (state={state})", flush=True)
                continue

            checkpoint = RepoCheckpoint(
                queue=queue,
                log=execution_log,
                repo_id=repo_id,
                family=cfg.family,
                wave=cfg.extraction_wave,
            )
            checkpoint.start_cloning()
            receipt = extract_one_repo(cfg, row, blob_store, checkpoint)
            profile = _record_profile(cfg, receipt, run_profiles)
            if profile is not None:
                print(format_progress_log(index=index, total=total, profile=profile), flush=True)
                warning = slow_repo_warning(profile)
                if warning:
                    print(warning, flush=True)

            status = receipt["status"]
            if status in {"ok", "no_matches"}:
                _finalize_successful_repo(cfg, checkpoint, repo_id, receipt, blob_store, queue)
            elif status == "skipped":
                reason = receipt.get("skip_reason") or "skipped"
                write_receipt(cfg.receipts_dir, repo_id, receipt)
                checkpoint.fail(reason=reason)
            else:
                reason = (
                    profile.failure_reason
                    if isinstance(profile, ExtractionProfile) and profile.failure_reason
                    else normalize_failure_reason(receipt.get("error"))
                )
                write_receipt(cfg.receipts_dir, repo_id, receipt)
                checkpoint.fail(reason=reason)

        queue_counts = queue.counts_by_state()

    if not out_path.exists():
        rebuild_global_events(
            events_dir=cfg.events_dir,
            queue_path=cfg.queue_path,
            family=cfg.family,
            wave=cfg.extraction_wave,
            registry_path=cfg.registry_path,
            protocol_version=detector_version,
            extraction_wave=cfg.extraction_wave,
            registry_version=cfg.registry_version,
            dataset_version=cfg.dataset_version,
        )

    print(
        format_extraction_summary(
            queue_counts=queue_counts,
            run_profiles=run_profiles,
            stale_recovered=stale_recovered,
            registry_limit=cfg.limit,
        ),
        flush=True,
    )

    return out_path
