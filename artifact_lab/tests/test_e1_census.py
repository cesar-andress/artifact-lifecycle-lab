"""Tests for E1 adoption census experiment."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pyarrow as pa

from artifact_lab.contracts.schemas import FILE_EVENT_LOG_COLUMNS, file_event_log_schema
from artifact_lab.experiments.e1_adoption_census.census import (
    build_census_from_events,
    build_path_census_rows,
)
from artifact_lab.experiments.e1_adoption_census.fig1 import build_adoption_timeline
from artifact_lab.experiments.e1_adoption_census.table1 import build_table1_rows
from artifact_lab.store.parquet import write_parquet


def _event(
    *,
    repo_id: str = "repo1",
    repo_url: str = "https://github.com/o/r",
    path: str,
    change_type: str,
    commit_time: str,
) -> dict:
    return {
        "repo_id": repo_id,
        "repo_url": repo_url,
        "family": "ai_conventions_v1",
        "path": path,
        "commit_sha": f"sha-{path}-{change_type}",
        "commit_time": datetime.fromisoformat(commit_time),
        "author_name": "Author",
        "author_email_hash": "abc123",
        "change_type": change_type,
        "blob_sha": "blob1",
        "extraction_wave": "test",
        "detector_version": "1.0.0",
    }


def test_path_census_tracks_presence_and_families():
    events = [
        _event(path="AGENTS.md", change_type="add", commit_time="2024-01-15T10:00:00+00:00"),
        _event(path="AGENTS.md", change_type="modify", commit_time="2024-03-15T10:00:00+00:00"),
        _event(path=".cursor/rules/style.md", change_type="add", commit_time="2024-02-01T10:00:00+00:00"),
        _event(path="CLAUDE.md", change_type="add", commit_time="2024-04-01T10:00:00+00:00"),
        _event(path="CLAUDE.md", change_type="delete", commit_time="2024-05-01T10:00:00+00:00"),
    ]
    path_rows = build_path_census_rows(events)
    assert len(path_rows) == 3

    agents = next(r for r in path_rows if r["path"] == "AGENTS.md")
    assert agents["artifact_family"] == "agents_md"
    assert agents["currently_present"] is True
    assert agents["n_events"] == 2

    claude = next(r for r in path_rows if r["path"] == "CLAUDE.md")
    assert claude["artifact_family"] == "claude_md"
    assert claude["currently_present"] is False

    census = build_census_from_events(events)
    assert len(census["repo"]) == 1
    assert census["repo"][0]["total_matched_files"] == 3
    assert set(census["repo"][0]["artifact_families"].split(",")) == {
        "agents_md",
        "cursor_rules",
        "claude_md",
    }


def test_adoption_timeline_is_cumulative_by_month():
    events = [
        _event(path="AGENTS.md", change_type="add", commit_time="2024-01-15T10:00:00+00:00"),
        _event(path=".cursor/rules/a.md", change_type="add", commit_time="2024-02-01T10:00:00+00:00"),
        _event(path="CLAUDE.md", change_type="add", commit_time="2024-02-20T10:00:00+00:00"),
    ]
    timeline = build_adoption_timeline(build_path_census_rows(events))
    assert timeline == [
        {"month": "2024-01-01", "new_convention_files": 1, "cumulative_convention_files": 1},
        {"month": "2024-02-01", "new_convention_files": 2, "cumulative_convention_files": 3},
    ]


def test_table1_counts_repo_and_file_frequencies():
    census = build_census_from_events(
        [
            _event(path="AGENTS.md", change_type="add", commit_time="2024-01-15T10:00:00+00:00"),
            _event(path=".cursor/rules/a.md", change_type="add", commit_time="2024-02-01T10:00:00+00:00"),
            _event(
                repo_id="repo2",
                repo_url="https://github.com/o/r2",
                path="AGENTS.md",
                change_type="add",
                commit_time="2024-03-01T10:00:00+00:00",
            ),
        ]
    )
    rows = build_table1_rows(census["repo_family"])
    agents = next(r for r in rows if r["artifact_family"] == "agents_md")
    cursor = next(r for r in rows if r["artifact_family"] == "cursor_rules")
    assert agents["n_repos"] == 2
    assert agents["n_files"] == 2
    assert cursor["n_repos"] == 1
    assert cursor["n_files"] == 1


def test_run_census_writes_outputs(tmp_path: Path):
    events = [
        _event(path="AGENTS.md", change_type="add", commit_time="2024-01-15T10:00:00+00:00"),
    ]
    l1 = tmp_path / "events.parquet"
    table = pa.Table.from_pylist(events, schema=file_event_log_schema())
    write_parquet(table, l1, expected_columns=FILE_EVENT_LOG_COLUMNS)

    from artifact_lab.experiments.e1_adoption_census.census import run_census

    out = tmp_path / "census"
    census = run_census(l1_path=l1, output_dir=out)
    assert census["path"]
    assert (out / "path_census.csv").exists()
    assert (out / "repo_family_census.csv").exists()


def test_e1_report_lists_correct_regeneration_commands(tmp_path: Path):
    from artifact_lab.experiments.e1_adoption_census.report import render_report

    text = render_report(
        census_dir=tmp_path / "census",
        fig1_csv=tmp_path / "exports" / "e1" / "fig1.csv",
        table1_csv=tmp_path / "exports" / "e1" / "table1.csv",
        n_registry_repos=17,
        n_repos_with_matches=3,
        n_path_rows=10,
    )
    assert "make e1-pilot" in text
    assert "make e1" in text
    assert "make paper" in text
    assert "paper-artifact" not in text
