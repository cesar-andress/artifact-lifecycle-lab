"""Clone cleanup on failure."""

from pathlib import Path
from unittest.mock import patch

import pytest

from platform.ingest.extract import ExtractConfig, extract_one_repo
from platform.store.blobs import BlobStore


def test_clone_removed_on_failure(tmp_path):
    registry_row = {"repo_id": "fail_repo", "repo_url": "https://github.com/example/fail.git"}
    scratch = tmp_path / "scratch"
    cfg = ExtractConfig(
        registry_path=tmp_path / "registry.csv",
        family="ai_conventions_v1",
        scratch_dir=scratch,
        events_dir=tmp_path / "l1",
        blobs_dir=tmp_path / "blobs",
        receipts_dir=tmp_path / "receipts",
    )
    clone_path = scratch / "example_fail"

    def boom(url, dest, timeout=300):
        dest.mkdir(parents=True)
        (dest / "HEAD").write_text("ref: refs/heads/main\n")
        raise RuntimeError("simulated extract failure")

    with patch("platform.ingest.extract.clone_bare", side_effect=boom):
        receipt = extract_one_repo(cfg, registry_row, BlobStore(cfg.blobs_dir))

    assert receipt["status"] == "failed"
    assert receipt["clone_removed"] is True
    assert not clone_path.exists()
