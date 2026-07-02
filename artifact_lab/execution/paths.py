"""Path helpers for per-repository L1 artifacts."""

from __future__ import annotations

from pathlib import Path


def repo_events_path(events_dir: Path, repo_id: str) -> Path:
    return events_dir / "repos" / f"{repo_id}.parquet"


def repo_manifest_path(events_dir: Path, repo_id: str) -> Path:
    return events_dir / "repos" / f"{repo_id}.manifest.yaml"


def global_events_path(events_dir: Path) -> Path:
    return events_dir / "events.parquet"


def global_manifest_path(events_dir: Path) -> Path:
    return events_dir / "manifest.yaml"


def receipt_path(receipts_dir: Path, repo_id: str) -> Path:
    return receipts_dir / f"{repo_id}.json"


def execution_log_path(events_dir: Path) -> Path:
    return events_dir / "execution.log"
