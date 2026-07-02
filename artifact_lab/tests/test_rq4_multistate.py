"""Unit tests for RQ4 multi-state lifecycle analysis."""

from __future__ import annotations

from artifact_lab.experiments.truth_decay.rq4_multistate import (
    build_reference_lifecycle_records,
    compute_phase_transitions,
    compute_state_occupancy,
    first_transition_probability_rows,
    mechanical_to_lifecycle,
    transition_probability_rows,
)


def _row(
    *,
    commit: str,
    commit_time: str,
    state: str,
    reference: str = "src/a.py",
    reference_type: str = "path",
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
        "transition": "",
        "reference_removed": False,
        "reference_added": True,
    }


def test_mechanical_to_lifecycle_mapping():
    assert mechanical_to_lifecycle("VERIFIED") == "operational"
    assert mechanical_to_lifecycle("MISSING") == "integrity_loss"
    assert mechanical_to_lifecycle("REPAIRED") == "repair"
    assert mechanical_to_lifecycle("DELETED") == "deletion"


def test_birth_to_operational_and_decay_repair():
    rows = [
        _row(commit="c1", commit_time="2024-01-01T00:00:00+00:00", state="VERIFIED"),
        _row(commit="c2", commit_time="2024-01-16T00:00:00+00:00", state="MISSING"),
        _row(commit="c3", commit_time="2024-01-20T00:00:00+00:00", state="REPAIRED"),
    ]
    records = build_reference_lifecycle_records(rows)
    assert len(records) == 1
    r = records[0]
    assert r.birth_phase == "operational"
    assert r.ever_operational
    assert r.ever_integrity_loss
    assert r.ever_repair
    assert r.repair_latency_days == 4.0


def test_born_stale_at_birth():
    rows = [
        _row(commit="c1", commit_time="2024-01-01T00:00:00+00:00", state="MISSING"),
    ]
    records = build_reference_lifecycle_records(rows)
    assert records[0].birth_phase == "integrity_loss"
    assert not records[0].ever_operational


def test_first_transition_probabilities():
    rows = [
        _row(commit="c1", commit_time="2024-01-01T00:00:00+00:00", state="VERIFIED", reference="a"),
        _row(commit="c1", commit_time="2024-01-01T00:00:00+00:00", state="MISSING", reference="b"),
    ]
    counts = compute_phase_transitions(rows)
    first = {r["to_phase"]: r["probability"] for r in first_transition_probability_rows(counts)}
    assert first["operational"] == 0.5
    assert first["integrity_loss"] == 0.5


def test_transition_matrix_operational_to_loss():
    rows = [
        _row(commit="c1", commit_time="2024-01-01T00:00:00+00:00", state="VERIFIED"),
        _row(commit="c2", commit_time="2024-02-01T00:00:00+00:00", state="MISSING"),
    ]
    counts = compute_phase_transitions(rows)
    trans = {
        (r["from_phase"], r["to_phase"]): r["probability"]
        for r in transition_probability_rows(counts)
    }
    assert trans[("birth", "operational")] == 1.0
    assert trans[("operational", "integrity_loss")] == 1.0


def test_deletion_latency():
    rows = [
        _row(commit="c1", commit_time="2024-01-01T00:00:00+00:00", state="VERIFIED"),
        _row(commit="c2", commit_time="2024-03-01T00:00:00+00:00", state="DELETED"),
    ]
    records = build_reference_lifecycle_records(rows)
    assert records[0].deletion_latency_days == 60.0
    assert records[0].operational_to_deletion_days == 60.0


def test_state_occupancy_weights_intervals():
    rows = [
        _row(commit="c1", commit_time="2024-01-01T00:00:00+00:00", state="VERIFIED"),
        _row(commit="c2", commit_time="2024-01-31T00:00:00+00:00", state="VERIFIED"),
        _row(commit="c3", commit_time="2024-02-15T00:00:00+00:00", state="MISSING"),
    ]
    occ = {r["lifecycle_phase"]: r["person_days"] for r in compute_state_occupancy(rows)}
    assert occ["operational"] == 45.0
    assert occ["integrity_loss"] == 0.0
