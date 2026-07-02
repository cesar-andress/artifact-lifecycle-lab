"""L2 panel generation on synthetic git repo."""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pyarrow as pa

from artifact_lab.contracts.schemas import FILE_EVENT_LOG_COLUMNS, file_event_log_schema
from artifact_lab.derive.panel import build_panel_rows, classify_state, run_panel
from artifact_lab.ingest.extract import discover_matched_paths, extract_repo_events
from artifact_lab.store.blobs import BlobStore
from artifact_lab.store.parquet import write_parquet


def _git(args: list[str], cwd: Path, env: dict | None = None) -> None:
    import os

    merged = os.environ.copy()
    if env:
        merged.update(env)
    proc = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, env=merged)
    assert proc.returncode == 0, proc.stderr


def _make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo.git"
    _git(["init", "--bare", str(repo)], tmp_path)
    work = tmp_path / "work"
    work.mkdir()
    _git(["clone", str(repo), str(work)], tmp_path)
    _git(["config", "user.email", "a@example.com"], work)
    _git(["config", "user.name", "Alice"], work)
    branch_proc = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=work,
        capture_output=True,
        text=True,
    )
    branch = branch_proc.stdout.strip() or "master"
    (work / "AGENTS.md").write_text("v1\n")
    env = {"GIT_AUTHOR_DATE": "2024-01-15T12:00:00", "GIT_COMMITTER_DATE": "2024-01-15T12:00:00"}
    _git(["add", "AGENTS.md"], work)
    _git(["commit", "-m", "add agents"], work, env=env)
    (work / "AGENTS.md").write_text("v2\n")
    env2 = {"GIT_AUTHOR_DATE": "2024-06-15T12:00:00", "GIT_COMMITTER_DATE": "2024-06-15T12:00:00"}
    _git(["add", "AGENTS.md"], work)
    _git(["commit", "-m", "touch agents"], work, env=env2)
    _git(["push", "origin", branch], work)
    return repo


def test_classify_state_priority():
    assert classify_state(exists=False, ever_existed=False, age_days=None, days_since_touch=None, T=180) == "absent"
    assert classify_state(exists=False, ever_existed=True, age_days=200, days_since_touch=200, T=180) == "deleted"
    assert classify_state(exists=True, ever_existed=True, age_days=30, days_since_touch=5, T=180) == "young"
    assert classify_state(exists=True, ever_existed=True, age_days=200, days_since_touch=30, T=180) == "active"
    assert classify_state(exists=True, ever_existed=True, age_days=200, days_since_touch=200, T=180) == "stale"


def test_panel_from_synthetic_repo(tmp_path):
    bare = _make_repo(tmp_path)
    paths = discover_matched_paths(bare, "ai_conventions_v1", git_timeout=60)
    assert "AGENTS.md" in paths
    events = extract_repo_events(
        bare,
        repo_id="test_repo",
        repo_url="file://test",
        family="ai_conventions_v1",
        extraction_wave="test",
        detector_version="1.0.0",
        blob_store=BlobStore(tmp_path / "blobs"),
        git_timeout=60,
    )
    assert len(events) >= 2
    table = pa.Table.from_pylist(events, schema=file_event_log_schema())
    events_path = tmp_path / "events.parquet"
    write_parquet(table, events_path, expected_columns=FILE_EVENT_LOG_COLUMNS)
    panel_rows = build_panel_rows(table, T=180)
    states = {r["state"] for r in panel_rows if r["path"] == "AGENTS.md"}
    assert "young" in states or "active" in states
    out = run_panel(events_path=events_path, output_dir=tmp_path / "panel", T=180)
    assert out.exists()
