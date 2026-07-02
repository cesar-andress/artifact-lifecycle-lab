"""Unit tests for RQ5 experimental preparation."""

from __future__ import annotations

from artifact_lab.experiments.truth_decay.rq5_availability import (
    assess_issue_availability,
    assess_task_availability,
)
from artifact_lab.experiments.truth_decay.rq5_candidates import (
    build_commit_spec_states,
    build_rq5_candidate_snapshots,
    stable_id,
)


def _row(
    *,
    commit: str,
    commit_time: str,
    state: str,
    reference: str = "src/a.py",
    reference_type: str = "path",
    transition: str = "",
) -> dict:
    return {
        "repo_id": "r1",
        "instruction_path": "AGENTS.md",
        "commit": commit,
        "commit_time": commit_time,
        "reference": reference,
        "reference_type": reference_type,
        "state": state,
        "previous_state": "",
        "transition": transition,
        "reference_removed": False,
        "reference_added": True,
    }


def test_stable_id_deterministic():
    assert stable_id("a", "b") == stable_id("a", "b")
    assert stable_id("a", "b") != stable_id("a", "c")


def test_truthful_and_degraded_snapshots():
    rows = [
        _row(commit="c1", commit_time="2024-01-01T00:00:00+00:00", state="VERIFIED"),
        _row(
            commit="c2",
            commit_time="2024-02-01T00:00:00+00:00",
            state="MISSING",
            transition="VERIFIED->MISSING",
        ),
    ]
    blob_index = {
        ("r1", "AGENTS.md", "c1"): "blob1",
        ("r1", "AGENTS.md", "c2"): "blob2",
    }
    snapshots = build_rq5_candidate_snapshots(
        rows=rows,
        repo_urls={"r1": "https://github.com/x/y"},
        blob_index=blob_index,
        blob_store=None,
        family_by_spec={("r1", "AGENTS.md"): "AGENTS.md"},
        p1_keys=set(),
    )
    by_type = {s.snapshot_type: s for s in snapshots}
    assert "truthful" in by_type
    assert by_type["truthful"].commit_sha == "c1"
    assert "degraded" in by_type
    assert by_type["degraded"].commit_sha == "c2"
    assert by_type["degraded"].paired_truthful_commit_sha == "c1"


def test_born_stale_snapshot():
    rows = [
        _row(commit="c1", commit_time="2024-01-01T00:00:00+00:00", state="MISSING", transition="INIT->MISSING"),
    ]
    snapshots = build_rq5_candidate_snapshots(
        rows=rows,
        repo_urls={"r1": "https://github.com/x/y"},
        blob_index={("r1", "AGENTS.md", "c1"): "blob1"},
        blob_store=None,
        family_by_spec={},
        p1_keys=set(),
    )
    born = [s for s in snapshots if s.snapshot_type == "born_stale"]
    assert len(born) == 1
    assert born[0].issue_availability is True


def test_issue_and_task_heuristics():
    issue_ok, _ = assess_issue_availability(
        snapshot_type="degraded",
        instruction_text="Please fix bug #123",
        n_missing_verifiable=1,
        n_verifiable=1,
    )
    assert issue_ok
    task_ok, reason = assess_task_availability(
        instruction_text="Run pytest before commit",
        verified_refs=["tests/test_a.py"],
    )
    assert task_ok
    assert "test" in reason


def test_commit_spec_state_aggregation():
    rows = [
        _row(commit="c1", commit_time="2024-01-01T00:00:00+00:00", state="VERIFIED", reference="a"),
        _row(commit="c1", commit_time="2024-01-01T00:00:00+00:00", state="MISSING", reference="b"),
    ]
    states = build_commit_spec_states(rows)
    assert len(states[("r1", "AGENTS.md")]) == 1
    assert len(states[("r1", "AGENTS.md")][0].references) == 2
