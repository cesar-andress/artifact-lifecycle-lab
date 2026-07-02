"""Timeout phase attribution tests."""

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import patch

from artifact_lab.contracts.repo_id import repo_id_from_url
from artifact_lab.ingest.extract import ExtractConfig, extract_one_repo, normalize_failure_reason
from artifact_lab.store.blobs import BlobStore


def _registry_row(url: str = "https://github.com/example/slow") -> dict[str, str]:
    return {
        "repo_id": repo_id_from_url(url),
        "repo_url": url,
        "normalized_repo_url": url,
    }


def _extract_config(tmp_path: Path, *, repo_timeout: int = 1) -> ExtractConfig:
    return ExtractConfig(
        registry_path=tmp_path / "registry.csv",
        family="ai_conventions_v1",
        scratch_dir=tmp_path / "scratch",
        events_dir=tmp_path / "l1" / "v1",
        blobs_dir=tmp_path / "blobs",
        receipts_dir=tmp_path / "receipts",
        queue_path=tmp_path / "jobs.db",
        repo_timeout=repo_timeout,
    )


def test_normalize_failure_reason_preserves_timeout_phase():
    assert normalize_failure_reason("timeout:inspection") == "timeout:inspection"
    assert normalize_failure_reason("timeout:blobs") == "timeout:blobs"


def test_timeout_during_inspection(tmp_path: Path):
    cfg = _extract_config(tmp_path)
    row = _registry_row()
    blob_store = BlobStore(cfg.blobs_dir)

    def fast_clone(url, dest, timeout=300):
        dest.mkdir(parents=True, exist_ok=True)

    def slow_list(repo_dir, timeout=300):
        time.sleep(2)
        return []

    with (
        patch("artifact_lab.ingest.extract.clone_bare", side_effect=fast_clone),
        patch("artifact_lab.ingest.extract.clone_size_bytes", return_value=1000),
        patch("artifact_lab.ingest.git_utils.list_head_paths", side_effect=slow_list),
        patch("artifact_lab.ingest.extract.remove_clone"),
    ):
        receipt = extract_one_repo(cfg, row, blob_store)

    profile = receipt["profile"]
    assert profile.failure_reason == "timeout:inspection"
    assert profile.timeout_phase == "inspection"
    assert profile.timings.clone_s > 0
    assert profile.timings.inspection_s > 0


def test_timeout_during_blobs(tmp_path: Path):
    cfg = _extract_config(tmp_path)
    row = _registry_row("https://github.com/example/blobby")
    blob_store = BlobStore(cfg.blobs_dir)
    touch = {
        "commit_sha": "abc123",
        "commit_ts": 1_700_000_000,
        "author_name": "Author",
        "author_email": "a@example.com",
    }

    def fast_clone(url, dest, timeout=300):
        dest.mkdir(parents=True, exist_ok=True)

    with (
        patch("artifact_lab.ingest.extract.clone_bare", side_effect=fast_clone),
        patch("artifact_lab.ingest.extract.clone_size_bytes", return_value=1000),
        patch(
            "artifact_lab.ingest.extract.discover_matched_paths",
            return_value={".cursorrules"},
        ),
        patch("artifact_lab.ingest.extract.log_follow", return_value=[touch]),
        patch("artifact_lab.ingest.extract.deletion_commits", return_value=set()),
        patch("artifact_lab.ingest.extract.is_text_candidate", return_value=True),
        patch("artifact_lab.ingest.extract.blob_at_commit", side_effect=lambda *a, **k: time.sleep(2)),
        patch("artifact_lab.ingest.extract.remove_clone"),
    ):
        receipt = extract_one_repo(cfg, row, blob_store)

    profile = receipt["profile"]
    assert profile.failure_reason == "timeout:blobs"
    assert profile.timeout_phase == "blobs"
    assert profile.timings.clone_s >= 0
    assert profile.timings.blobs_s > 0


def test_failed_profile_preserves_elapsed_time_for_prior_phases(tmp_path: Path):
    cfg = _extract_config(tmp_path)
    row = _registry_row("https://github.com/example/partial")
    blob_store = BlobStore(cfg.blobs_dir)

    def fast_clone(url, dest, timeout=300):
        time.sleep(0.05)
        dest.mkdir(parents=True, exist_ok=True)

    def slow_list(repo_dir, timeout=300):
        time.sleep(2)
        return []

    with (
        patch("artifact_lab.ingest.extract.clone_bare", side_effect=fast_clone),
        patch("artifact_lab.ingest.extract.clone_size_bytes", return_value=1000),
        patch("artifact_lab.ingest.git_utils.list_head_paths", side_effect=slow_list),
        patch("artifact_lab.ingest.extract.remove_clone"),
    ):
        receipt = extract_one_repo(cfg, row, blob_store)

    profile = receipt["profile"]
    assert profile.timings.clone_s >= 0.04
    assert profile.timings.inspection_s > 0
    assert profile.failure_reason == "timeout:inspection"
