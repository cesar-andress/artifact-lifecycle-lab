"""Unit tests for RQ3 observational analysis."""

from __future__ import annotations

from artifact_lab.experiments.truth_decay.rq3_analysis import (
    build_reference_trajectories,
    compute_regime_metrics,
    compute_transition_matrix,
)
from artifact_lab.experiments.truth_decay.rq3_attribution import (
    build_file_regimes,
    classify_maintenance_regime,
    is_agent_maintenance,
)


def _long_row(
    *,
    commit: str,
    commit_time: str,
    state: str,
    reference: str = "src/a.py",
    reference_type: str = "path",
    previous_state: str = "",
    transition: str = "",
    repair_event: bool = False,
) -> dict:
    return {
        "repo_id": "r1",
        "instruction_path": "AGENTS.md",
        "commit": commit,
        "commit_time": commit_time,
        "reference": reference,
        "reference_type": reference_type,
        "state": state,
        "previous_state": previous_state,
        "transition": transition,
        "first_failure": state == "MISSING",
        "repair_event": repair_event,
        "reference_removed": False,
        "reference_added": False,
    }


def test_classify_maintenance_regime_thresholds():
    assert classify_maintenance_regime(agent_commits=0, human_commits=5, unknown_commits=0) == "human_only"
    assert classify_maintenance_regime(agent_commits=1, human_commits=4, unknown_commits=0) == "agent_assisted"
    assert classify_maintenance_regime(agent_commits=3, human_commits=3, unknown_commits=0) == "agent_dominated"
    assert classify_maintenance_regime(agent_commits=0, human_commits=0, unknown_commits=3) == "unknown"


def test_build_file_regimes_from_attribution():
    rows = [
        _long_row(commit="c1", commit_time="2024-01-01T00:00:00+00:00", state="VERIFIED"),
        _long_row(commit="c2", commit_time="2024-02-01T00:00:00+00:00", state="VERIFIED"),
        _long_row(commit="c3", commit_time="2024-03-01T00:00:00+00:00", state="VERIFIED"),
    ]
    attribution = {
        ("r1", "AGENTS.md", "c1"): {
            "attribution_class": "human",
            "signature_type": "none",
            "author_name": "",
            "author_email": "",
            "evidence": "",
        },
        ("r1", "AGENTS.md", "c2"): {
            "attribution_class": "agent_coauthored",
            "signature_type": "co_authored_by",
            "author_name": "",
            "author_email": "",
            "evidence": "Co-Authored-By: Claude",
        },
        ("r1", "AGENTS.md", "c3"): {
            "attribution_class": "human",
            "signature_type": "none",
            "author_name": "",
            "author_email": "",
            "evidence": "",
        },
    }
    regimes = build_file_regimes(rows, attribution)
    assert regimes[("r1", "AGENTS.md")] == "agent_assisted"


def test_birth_integrity_verified_and_born_stale():
    rows = [
        _long_row(commit="c1", commit_time="2024-01-01T00:00:00+00:00", state="VERIFIED"),
        _long_row(
            commit="c1",
            commit_time="2024-01-01T00:00:00+00:00",
            state="MISSING",
            reference="missing.py",
        ),
    ]
    regimes = {("r1", "AGENTS.md"): "human_only"}
    attribution = {}
    records = build_reference_trajectories(rows, regimes, attribution)
    by_ref = {r.reference: r for r in records}
    assert by_ref["src/a.py"].birth_integrity == "verified_birth"
    assert by_ref["missing.py"].birth_integrity == "born_stale"


def test_decay_and_repair_metrics():
    rows = [
        _long_row(commit="c1", commit_time="2024-01-01T00:00:00+00:00", state="VERIFIED"),
        _long_row(
            commit="c2",
            commit_time="2024-02-01T00:00:00+00:00",
            state="MISSING",
            previous_state="VERIFIED",
            transition="VERIFIED->MISSING",
        ),
        _long_row(
            commit="c3",
            commit_time="2024-03-01T00:00:00+00:00",
            state="REPAIRED",
            previous_state="MISSING",
            transition="MISSING->REPAIRED",
            repair_event=True,
        ),
    ]
    regimes = {("r1", "AGENTS.md"): "human_only"}
    records = build_reference_trajectories(rows, regimes, {})
    metrics = compute_regime_metrics(records)[0]
    assert metrics["p_decay_given_verified"] == 1.0
    assert metrics["p_repair_given_decay"] == 1.0


def test_transition_matrix_counts():
    rows = [
        _long_row(
            commit="c2",
            commit_time="2024-02-01T00:00:00+00:00",
            state="MISSING",
            previous_state="VERIFIED",
        ),
    ]
    regimes = {("r1", "AGENTS.md"): "human_only"}
    transitions = compute_transition_matrix(rows, regimes)
    assert any(
        t["from_state"] == "VERIFIED" and t["to_state"] == "MISSING" and t["count"] == 1
        for t in transitions
    )


def test_is_agent_maintenance_excludes_dependabot():
    row = {
        "attribution_class": "bot_author",
        "signature_type": "none",
        "author_name": "dependabot[bot]",
        "author_email": "",
        "evidence": "",
    }
    assert is_agent_maintenance(row) is False
