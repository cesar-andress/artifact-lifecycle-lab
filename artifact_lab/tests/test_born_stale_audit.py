"""Tests for born-stale audit heuristics and aggregation."""

from __future__ import annotations

from artifact_lab.experiments.truth_decay.born_stale_audit import (
    build_born_stale_records,
    classify_surface_context,
    collect_born_stale_trajectories,
    is_likely_external,
    is_relative_path_candidate,
    summarize_by_repo,
    summarize_by_type,
)


def _row(
    *,
    commit_time: str,
    state: str,
    reference: str = "src/a.py",
    reference_type: str = "path",
    repo_id: str = "r1",
    instruction_path: str = "AGENTS.md",
) -> dict:
    return {
        "repo_id": repo_id,
        "repo_url": f"https://example.com/{repo_id}",
        "instruction_path": instruction_path,
        "commit": "abc",
        "commit_time": commit_time,
        "reference": reference,
        "reference_type": reference_type,
        "state": state,
        "previous_state": "",
        "transition": f"INIT->{state}",
        "first_failure": state == "MISSING",
        "repair_event": False,
        "reference_removed": False,
        "reference_added": True,
    }


def test_classify_command_as_code_block():
    assert classify_surface_context("command", "npm test", "AGENTS.md") == "code_block"


def test_classify_example_path():
    assert classify_surface_context("directory", "examples/", "docs/AGENTS.md") == "examples"


def test_classify_prose_product_token():
    assert classify_surface_context("path", "Node.js", "AGENTS.md") == "prose"


def test_relative_path_candidate():
    assert is_relative_path_candidate("./src/a.py", "path") is True
    assert is_relative_path_candidate("README.md", "path") is True
    assert is_relative_path_candidate("src/a.py", "path") is False


def test_likely_external_dependency():
    assert is_likely_external("dependency", "requests") is True


def test_collect_born_stale_excludes_verified():
    rows = [
        _row(commit_time="2024-01-01T00:00:00+00:00", state="VERIFIED"),
        _row(commit_time="2024-02-01T00:00:00+00:00", state="MISSING"),
        _row(
            commit_time="2024-01-01T00:00:00+00:00",
            state="MISSING",
            reference="other.py",
            repo_id="r2",
        ),
    ]
    never, meta = collect_born_stale_trajectories(rows)
    assert meta["never_verified_rq2_excluded"] == 1
    assert len(never) == 1
    assert never[0][0][3] == "other.py"


def test_summaries_and_examples():
    rows = [
        _row(commit_time="2024-01-01T00:00:00+00:00", state="MISSING", reference="a.py", repo_id="r1"),
        _row(
            commit_time="2024-01-01T00:00:00+00:00",
            state="MISSING",
            reference="a.py",
            repo_id="r2",
            instruction_path="CLAUDE.md",
        ),
        _row(
            commit_time="2024-01-01T00:00:00+00:00",
            state="MISSING",
            reference="b.py",
            repo_id="r1",
        ),
    ]
    never, _ = collect_born_stale_trajectories(rows)
    records = build_born_stale_records(never, rows)
    by_type = summarize_by_type(records)
    by_repo = summarize_by_repo(records)
    assert by_type[0]["reference_type"] == "path"
    assert by_repo[0]["born_stale_count"] == 2
    assert records[0].repeated_repo_count == 2
