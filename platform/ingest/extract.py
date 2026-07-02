"""L1 extraction: ephemeral clone → file event log + blob store."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pyarrow as pa

from platform.contracts.schemas import (
    FILE_EVENT_LOG_COLUMNS,
    file_event_log_schema,
    hash_email,
)
from platform.ingest.git_utils import (
    blob_at_commit,
    clone_bare,
    deletion_commits,
    log_follow,
    parse_github_url,
    remove_clone,
    repo_id_from_url,
    ts_to_datetime,
)
from platform.protocol.detector import is_matched_path, is_text_candidate, safe_normalize_path
from platform.protocol.loader import family_version, load_family
from platform.store.blobs import BlobStore
from platform.store.manifest import write_manifest
from platform.store.parquet import write_parquet


@dataclass
class ExtractConfig:
    registry_path: Path
    family: str
    scratch_dir: Path
    events_dir: Path
    blobs_dir: Path
    receipts_dir: Path
    extraction_wave: str = "pilot_v1"
    clone_timeout: int = 300


def read_registry(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    required = {"repo_id", "repo_url"}
    for row in rows:
        if not required.issubset(row):
            raise ValueError(f"registry row missing columns {required}: {row}")
        if not row.get("repo_id"):
            row["repo_id"] = repo_id_from_url(row["repo_url"])
    return rows


def discover_matched_paths(repo_dir: Path, family: str) -> set[str]:
    from platform.ingest.git_utils import list_all_paths

    matched: set[str] = set()
    for raw in list_all_paths(repo_dir):
        norm = safe_normalize_path(raw)
        if norm and is_matched_path(norm, family):
            matched.add(norm)
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
) -> list[dict]:
    paths = discover_matched_paths(repo_dir, family)
    events: list[dict] = []
    for path in sorted(paths):
        history = log_follow(repo_dir, path)
        if not history:
            continue
        deletes = deletion_commits(repo_dir, path)
        for idx, touch in enumerate(history):
            change_type = "add" if idx == 0 else "modify"
            if touch["commit_sha"] in deletes:
                change_type = "delete"
            blob_sha = ""
            if change_type != "delete" and is_text_candidate(path, family):
                content = blob_at_commit(repo_dir, touch["commit_sha"], path)
                if content is not None and b"\x00" not in content:
                    blob_sha = blob_store.put_text(content)
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


def extract_one_repo(cfg: ExtractConfig, row: dict[str, str], blob_store: BlobStore) -> dict:
    repo_id = row["repo_id"]
    repo_url = row["repo_url"]
    parsed = parse_github_url(repo_url)
    slug = f"{parsed[0]}_{parsed[1]}" if parsed else repo_id
    clone_path = cfg.scratch_dir / slug
    started = datetime.now(timezone.utc)
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
    }
    try:
        clone_bare(repo_url, clone_path, timeout=cfg.clone_timeout)
        events = extract_repo_events(
            clone_path,
            repo_id=repo_id,
            repo_url=repo_url,
            family=cfg.family,
            extraction_wave=cfg.extraction_wave,
            detector_version=family_version(cfg.family),
            blob_store=blob_store,
        )
        receipt["matched_paths"] = sorted({e["path"] for e in events})
        receipt["n_events"] = len(events)
        receipt["status"] = "ok" if events else "no_matches"
        receipt["events"] = events
    except Exception as exc:  # noqa: BLE001 — record and continue pilot
        receipt["error"] = f"{exc.__class__.__name__}: {exc}"
        receipt["events"] = []
    finally:
        remove_clone(clone_path)
        receipt["clone_removed"] = not clone_path.exists()
        receipt["finished_at"] = datetime.now(timezone.utc).isoformat()
    return receipt


def run_extract(cfg: ExtractConfig) -> Path:
    load_family(cfg.family)
    registry = read_registry(cfg.registry_path)
    blob_store = BlobStore(cfg.blobs_dir)
    all_events: list[dict] = []
    cfg.receipts_dir.mkdir(parents=True, exist_ok=True)

    for row in registry:
        receipt = extract_one_repo(cfg, row, blob_store)
        receipt_path = cfg.receipts_dir / f"{row['repo_id']}.json"
        serializable = {k: v for k, v in receipt.items() if k != "events"}
        receipt_path.write_text(json.dumps(serializable, indent=2) + "\n", encoding="utf-8")
        all_events.extend(receipt.get("events") or [])

    cfg.events_dir.mkdir(parents=True, exist_ok=True)
    out_path = cfg.events_dir / "events.parquet"
    if all_events:
        table = pa.Table.from_pylist(all_events, schema=file_event_log_schema())
        row_count = write_parquet(table, out_path, expected_columns=FILE_EVENT_LOG_COLUMNS)
    else:
        table = pa.table({col: pa.array([], type=file_event_log_schema().field(col).type) for col in FILE_EVENT_LOG_COLUMNS})
        row_count = write_parquet(table, out_path, expected_columns=FILE_EVENT_LOG_COLUMNS)

    write_manifest(
        cfg.events_dir / "manifest.yaml",
        dataset_name="file_event_log",
        version=cfg.extraction_wave,
        input_datasets=[str(cfg.registry_path)],
        protocol_version=family_version(cfg.family),
        row_count=row_count,
        columns=FILE_EVENT_LOG_COLUMNS,
        extra={"family": cfg.family},
    )
    return out_path
