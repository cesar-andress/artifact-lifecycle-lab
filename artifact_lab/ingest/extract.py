"""L1 extraction: ephemeral clone → file event log + blob store."""

from __future__ import annotations

import csv
import json
import time
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
    clone_timeout: int = 300
    repo_timeout: int = 600
    max_clone_bytes: int = 500_000_000
    force: bool = False
    limit: int | None = None
    profile_path: Path = EXTRACTION_PROFILE_PATH


DEFAULT_CLONE_TIMEOUT = 300
DEFAULT_REPO_TIMEOUT = 600
SKIP_SLOW_CLONE_TIMEOUT = 120
SKIP_SLOW_REPO_TIMEOUT = 120


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
    path = receipts_dir / f"{repo_id}.json"
    serializable = {k: v for k, v in receipt.items() if k not in {"events", "profile"}}
    path.write_text(json.dumps(serializable, indent=2) + "\n", encoding="utf-8")
    return path


def discover_matched_paths(
    repo_dir: Path,
    family: str,
    *,
    git_timeout: int,
    timings: PhaseTimings,
) -> set[str]:
    from artifact_lab.ingest.git_utils import list_all_paths

    t0 = time.perf_counter()
    try:
        raw_paths = list_all_paths(repo_dir, timeout=git_timeout)
    finally:
        timings.inspection_s += time.perf_counter() - t0

    t0 = time.perf_counter()
    try:
        matched: set[str] = set()
        for raw in raw_paths:
            norm = safe_normalize_path(raw)
            if norm and is_matched_path(norm, family):
                matched.add(norm)
    finally:
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
) -> list[dict]:
    paths = discover_matched_paths(repo_dir, family, git_timeout=git_timeout, timings=timings)
    events: list[dict] = []
    for path in sorted(paths):
        t0 = time.perf_counter()
        try:
            history = log_follow(repo_dir, path, timeout=git_timeout)
            deletes = deletion_commits(repo_dir, path, timeout=git_timeout)
        finally:
            timings.history_s += time.perf_counter() - t0

        for idx, touch in enumerate(history):
            change_type = "add" if idx == 0 else "modify"
            if touch["commit_sha"] in deletes:
                change_type = "delete"
            blob_sha = ""
            if change_type != "delete" and is_text_candidate(path, family):
                t0 = time.perf_counter()
                try:
                    content = blob_at_commit(repo_dir, touch["commit_sha"], path, timeout=git_timeout)
                    if content is not None and b"\x00" not in content:
                        t_blob = time.perf_counter()
                        blob_sha = blob_store.put_text(content)
                        resources.local_cpu_s += time.perf_counter() - t_blob
                finally:
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
) -> dict:
    repo_id = row["repo_id"]
    repo_url = row["normalized_repo_url"]
    clone_path = cfg.scratch_dir / repo_id
    wall_start = time.perf_counter()
    started = datetime.now(timezone.utc)
    timings = PhaseTimings()
    profile = ExtractionProfile(
        repo_id=repo_id,
        repo_url=repo_url,
        extraction_wave=cfg.extraction_wave,
        status="failed",
        timings=timings,
        resources=ResourceMetrics(),
        recorded_at=started.isoformat(),
    )
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
            t0 = time.perf_counter()
            try:
                clone_bare(row["repo_url"], clone_path, timeout=cfg.clone_timeout)
            finally:
                timings.clone_s = time.perf_counter() - t0

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
        t0 = time.perf_counter()
        remove_clone(clone_path)
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
    if "RepoTimeoutError" in error or error == "timeout":
        return "timeout"
    return error


def extract_one_repo(cfg: ExtractConfig, row: dict[str, str], blob_store: BlobStore) -> dict:
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(_extract_repo_body, cfg, row, blob_store)
        try:
            return future.result(timeout=cfg.repo_timeout)
        except FuturesTimeout:
            clone_path = cfg.scratch_dir / row["repo_id"]
            remove_clone(clone_path)
            finished = datetime.now(timezone.utc).isoformat()
            profile = ExtractionProfile(
                repo_id=row["repo_id"],
                repo_url=row["normalized_repo_url"],
                extraction_wave=cfg.extraction_wave,
                status="failed",
                timings=PhaseTimings(wall_s=float(cfg.repo_timeout)),
                recorded_at=finished,
                failure_reason="timeout",
            )
            return {
                "repo_id": row["repo_id"],
                "repo_url": row["normalized_repo_url"],
                "family": cfg.family,
                "extraction_wave": cfg.extraction_wave,
                "started_at": finished,
                "finished_at": finished,
                "status": "failed",
                "n_events": 0,
                "matched_paths": [],
                "error": "timeout",
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


def run_extract(cfg: ExtractConfig) -> Path:
    load_family(cfg.family)
    registry = read_registry(cfg.registry_path)
    if cfg.limit is not None:
        registry = registry[: cfg.limit]
    blob_store = BlobStore(cfg.blobs_dir)
    cfg.events_dir.mkdir(parents=True, exist_ok=True)
    out_path = cfg.events_dir / "events.parquet"

    existing_events = _load_existing_events(out_path)
    new_events: list[dict] = []
    processed_repo_ids: set[str] = set()
    run_profiles: list[ExtractionProfile] = []
    stale_recovered = 0
    queue_counts: dict[str, int] = {}

    with JobQueue(cfg.queue_path) as queue:
        stale_recovered = queue.reset_stale_running()
        if stale_recovered:
            print(f"recovered {stale_recovered} stale running job(s) -> pending", flush=True)
        for row in registry:
            queue.upsert_pending(row["repo_id"], row["normalized_repo_url"], cfg.family, cfg.extraction_wave)

        total = len(registry)
        for index, row in enumerate(registry, start=1):
            repo_id = row["repo_id"]
            repo_url = row["normalized_repo_url"]
            if not queue.should_process(repo_id, cfg.family, cfg.extraction_wave, force=cfg.force):
                job = queue.get(repo_id, cfg.family, cfg.extraction_wave)
                state = job.state if job else "unknown"
                print(f"[{index}/{total}] skip {repo_url} (state={state})", flush=True)
                continue

            queue.mark_running(repo_id, cfg.family, cfg.extraction_wave)
            receipt = extract_one_repo(cfg, row, blob_store)
            profile = receipt.get("profile")
            if isinstance(profile, ExtractionProfile):
                status = receipt["status"]
                if status == "skipped":
                    profile.failure_reason = receipt.get("skip_reason") or "skipped"
                elif status not in {"ok", "no_matches"}:
                    profile.failure_reason = normalize_failure_reason(receipt.get("error"))
                run_profiles.append(profile)
                print(format_progress_log(index=index, total=total, profile=profile), flush=True)
                warning = slow_repo_warning(profile)
                if warning:
                    print(warning, flush=True)
                existing_rows = [p.to_row() for p in load_profiles(cfg.profile_path)]
                merged = merge_profiles(existing_rows, [profile])
                write_profiles(
                    merged,
                    cfg.profile_path,
                    csv_path=cfg.profile_path.with_suffix(".csv"),
                )

            write_receipt(cfg.receipts_dir, repo_id, receipt)
            processed_repo_ids.add(repo_id)

            status = receipt["status"]
            n_events = len(receipt.get("events") or [])
            if status in {"ok", "no_matches"}:
                queue.mark_succeeded(repo_id, cfg.family, cfg.extraction_wave, n_events=n_events)
                new_events.extend(receipt.get("events") or [])
            elif status == "skipped":
                reason = receipt.get("skip_reason") or "skipped"
                queue.mark_failed(
                    repo_id,
                    cfg.family,
                    cfg.extraction_wave,
                    reason=reason,
                    n_events=0,
                )
            else:
                reason = normalize_failure_reason(receipt.get("error"))
                queue.mark_failed(
                    repo_id,
                    cfg.family,
                    cfg.extraction_wave,
                    reason=reason,
                    n_events=0,
                )

        queue_counts = queue.counts_by_state()

    t0 = time.perf_counter()
    merged = _merge_events(existing_events, new_events, replaced_repo_ids=processed_repo_ids)
    if merged:
        table = pa.Table.from_pylist(merged, schema=file_event_log_schema())
        row_count = write_parquet(table, out_path, expected_columns=FILE_EVENT_LOG_COLUMNS)
    else:
        table = pa.table(
            {col: pa.array([], type=file_event_log_schema().field(col).type) for col in FILE_EVENT_LOG_COLUMNS}
        )
        row_count = write_parquet(table, out_path, expected_columns=FILE_EVENT_LOG_COLUMNS)
    parquet_write_s = time.perf_counter() - t0

    t0 = time.perf_counter()
    write_manifest(
        cfg.events_dir / "manifest.yaml",
        dataset_name="file_event_log",
        version=cfg.extraction_wave,
        input_datasets=[str(cfg.registry_path)],
        protocol_version=family_version(cfg.family),
        row_count=row_count,
        columns=FILE_EVENT_LOG_COLUMNS,
        extra={
            "family": cfg.family,
            "dataset_version": cfg.dataset_version,
        },
    )
    manifest_write_s = time.perf_counter() - t0

    assign_batch_write_shares(
        run_profiles,
        parquet_write_s=parquet_write_s,
        manifest_write_s=manifest_write_s,
    )

    if run_profiles:
        existing_rows = [p.to_row() for p in load_profiles(cfg.profile_path)]
        merged_profiles = merge_profiles(existing_rows, run_profiles)
        write_profiles(
            merged_profiles,
            cfg.profile_path,
            csv_path=cfg.profile_path.with_suffix(".csv"),
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
