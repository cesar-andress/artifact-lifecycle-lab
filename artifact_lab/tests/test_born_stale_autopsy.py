"""Tests for born-stale taxonomy heuristics."""

from __future__ import annotations

from artifact_lab.experiments.truth_decay.born_stale_taxonomy import (
    classify_heuristic,
    needs_llm_adjudication,
)


def test_extraction_artifact_prose():
    v = classify_heuristic(
        reference_type="path",
        reference="Node.js",
        instruction_path="AGENTS.md",
        n_observations=1,
        first_change_type="add",
        repeated_repo_count=1,
        repeated_file_count=1,
    )
    assert v.category == "extraction_artifact"
    assert v.confidence == "high"
    assert not needs_llm_adjudication(v)


def test_external_dependency():
    v = classify_heuristic(
        reference_type="dependency",
        reference="requests",
        instruction_path="SKILL.md",
        n_observations=1,
        first_change_type="add",
        repeated_repo_count=1,
        repeated_file_count=1,
    )
    assert v.category == "external_reference"
    assert v.confidence == "high"


def test_verification_anchor_mismatch():
    v = classify_heuristic(
        reference_type="path",
        reference="./src/foo.py",
        instruction_path=".cursor/rules/x.mdc",
        n_observations=2,
        first_change_type="modify",
        repeated_repo_count=1,
        repeated_file_count=1,
    )
    assert v.category == "verification_anchor_mismatch"
    assert v.confidence == "high"


def test_template_placeholder():
    v = classify_heuristic(
        reference_type="path",
        reference="tests/path_to_test.py",
        instruction_path="CLAUDE.md",
        n_observations=1,
        first_change_type="add",
        repeated_repo_count=10,
        repeated_file_count=20,
    )
    assert v.category == "template_placeholder"


def test_genuine_false_claim_needs_llm():
    v = classify_heuristic(
        reference_type="path",
        reference="src/internal/module.py",
        instruction_path="AGENTS.md",
        n_observations=3,
        first_change_type="add",
        repeated_repo_count=1,
        repeated_file_count=1,
    )
    assert v.category == "genuine_false_claim"
    assert needs_llm_adjudication(v)


def test_pre_observation_evolution():
    v = classify_heuristic(
        reference_type="path",
        reference="src/core/handler.py",
        instruction_path="AGENTS.md",
        n_observations=4,
        first_change_type="modify",
        repeated_repo_count=1,
        repeated_file_count=1,
    )
    assert v.category == "pre_observation_evolution"
    assert v.confidence == "medium"
