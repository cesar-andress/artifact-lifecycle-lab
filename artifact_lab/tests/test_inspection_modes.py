"""Inspection mode tests — head-only vs full-history."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from unittest.mock import patch

from artifact_lab.contracts.repo_id import repo_id_from_url
from artifact_lab.ingest.extract import (
    DEFAULT_INSPECTION_MODE,
    INSPECTION_MODE_FULL_HISTORY,
    INSPECTION_MODE_HEAD_ONLY,
    ExtractConfig,
    discover_matched_paths,
    extract_one_repo,
)
from artifact_lab.ingest.git_utils import list_all_paths, list_head_paths
from artifact_lab.ingest.profiling import PhaseTimings, load_profiles, write_profiles
from artifact_lab.store.blobs import BlobStore
from artifact_lab.tests.golden_repo import build_golden_bare_repo


def _git(args: list[str], cwd: Path, env: dict | None = None) -> None:
    import os

    merged = os.environ.copy()
    if env:
        merged.update(env)
    proc = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, env=merged)
    assert proc.returncode == 0, proc.stderr


def _make_repo_with_deleted_agents(tmp_path: Path) -> Path:
    bare = tmp_path / "repo.git"
    _git(["init", "--bare", str(bare)], tmp_path)
    work = tmp_path / "work"
    work.mkdir()
    _git(["clone", str(bare), str(work)], tmp_path)
    _git(["config", "user.email", "a@example.com"], work)
    _git(["config", "user.name", "Alice"], work)
    branch = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=work,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    (work / "AGENTS.md").write_text("v1\n")
    _git(["add", "AGENTS.md"], work)
    _git(
        ["commit", "-m", "add agents"],
        work,
        env={"GIT_AUTHOR_DATE": "2024-01-15T12:00:00", "GIT_COMMITTER_DATE": "2024-01-15T12:00:00"},
    )
    _git(["push", "origin", branch], work)

    _git(["rm", "AGENTS.md"], work)
    _git(
        ["commit", "-m", "remove agents"],
        work,
        env={"GIT_AUTHOR_DATE": "2024-06-15T12:00:00", "GIT_COMMITTER_DATE": "2024-06-15T12:00:00"},
    )
    _git(["push", "origin", branch], work)
    return bare


def test_head_only_detects_current_matched_files(tmp_path: Path):
    bare = build_golden_bare_repo(tmp_path)
    matched = discover_matched_paths(
        bare,
        "ai_conventions_v1",
        git_timeout=60,
        timings=PhaseTimings(),
        inspection_mode=INSPECTION_MODE_HEAD_ONLY,
    )
    assert "AGENTS.md" in matched
    assert ".cursor/rules/style.md" in matched


def test_full_history_finds_deleted_matched_files(tmp_path: Path):
    bare = _make_repo_with_deleted_agents(tmp_path)
    head_paths = list_head_paths(bare, timeout=60)
    all_paths = list_all_paths(bare, timeout=60)

    assert "AGENTS.md" not in head_paths
    assert "AGENTS.md" in all_paths

    head_matched = discover_matched_paths(
        bare,
        "ai_conventions_v1",
        git_timeout=60,
        timings=PhaseTimings(),
        inspection_mode=INSPECTION_MODE_HEAD_ONLY,
    )
    full_matched = discover_matched_paths(
        bare,
        "ai_conventions_v1",
        git_timeout=60,
        timings=PhaseTimings(),
        inspection_mode=INSPECTION_MODE_FULL_HISTORY,
    )

    assert "AGENTS.md" not in head_matched
    assert "AGENTS.md" in full_matched


def test_head_only_inspection_is_faster_than_full_history(tmp_path: Path):
    bare = build_golden_bare_repo(tmp_path)
    t0 = time.perf_counter()
    discover_matched_paths(
        bare,
        "ai_conventions_v1",
        git_timeout=60,
        timings=PhaseTimings(),
        inspection_mode=INSPECTION_MODE_HEAD_ONLY,
    )
    head_elapsed = time.perf_counter() - t0

    timings = PhaseTimings()
    t0 = time.perf_counter()
    discover_matched_paths(
        bare,
        "ai_conventions_v1",
        git_timeout=60,
        timings=timings,
        inspection_mode=INSPECTION_MODE_FULL_HISTORY,
    )
    full_elapsed = time.perf_counter() - t0

    assert head_elapsed <= full_elapsed


def test_inspection_mode_recorded_in_profile(tmp_path: Path):
    cfg = ExtractConfig(
        registry_path=tmp_path / "registry.csv",
        family="ai_conventions_v1",
        scratch_dir=tmp_path / "scratch",
        events_dir=tmp_path / "l1" / "v1",
        blobs_dir=tmp_path / "blobs",
        receipts_dir=tmp_path / "receipts",
        queue_path=tmp_path / "jobs.db",
        repo_timeout=5,
        inspection_mode=INSPECTION_MODE_HEAD_ONLY,
    )
    row = {
        "repo_id": repo_id_from_url("https://github.com/example/repo"),
        "repo_url": "https://github.com/example/repo",
        "normalized_repo_url": "https://github.com/example/repo",
    }

    def fast_clone(url, dest, timeout=300):
        dest.mkdir(parents=True, exist_ok=True)

    with (
        patch("artifact_lab.ingest.extract.clone_bare", side_effect=fast_clone),
        patch("artifact_lab.ingest.extract.clone_size_bytes", return_value=1000),
        patch("artifact_lab.ingest.git_utils.list_head_paths", return_value={"AGENTS.md"}),
        patch("artifact_lab.ingest.extract.log_follow", return_value=[]),
        patch("artifact_lab.ingest.extract.remove_clone"),
    ):
        receipt = extract_one_repo(cfg, row, BlobStore(cfg.blobs_dir))

    profile = receipt["profile"]
    assert profile.inspection_mode == INSPECTION_MODE_HEAD_ONLY

    profile_path = tmp_path / "profiles.parquet"
    write_profiles([profile], profile_path)
    loaded = load_profiles(profile_path)
    assert loaded[0].inspection_mode == INSPECTION_MODE_HEAD_ONLY


def test_default_inspection_mode_is_head_only():
    assert DEFAULT_INSPECTION_MODE == INSPECTION_MODE_HEAD_ONLY
