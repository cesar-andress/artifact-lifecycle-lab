"""Tests for genuine_false_claim confirmatory audit."""

from __future__ import annotations

from artifact_lab.experiments.truth_decay.audit_statistics import wilson_interval
from artifact_lab.experiments.truth_decay.gfc_confirmatory import (
    classify_gfc_confirmatory,
    needs_confirmatory_llm,
)


def test_glob_reference_maps_to_template():
    category, confidence, rules, _ = classify_gfc_confirmatory(
        reference_type="directory",
        reference="packages/datadog-plugin-*/",
        instruction_path="AGENTS.md",
        n_observations=5,
        first_change_type="add",
        repeated_repo_count=1,
        repeated_file_count=1,
        snippet="",
    )
    assert category == "template"
    assert confidence == "high"
    assert "glob_wildcard_reference" in rules


def test_placeholder_path_maps_to_template():
    category, _, _, _ = classify_gfc_confirmatory(
        reference_type="path",
        reference="path/to/test.spec.js",
        instruction_path="AGENTS.md",
        n_observations=3,
        first_change_type="add",
        repeated_repo_count=1,
        repeated_file_count=1,
        snippet="Run mocha on path/to/test.spec.js",
    )
    assert category == "template"


def test_node_module_maps_to_artifact():
    category, confidence, _, _ = classify_gfc_confirmatory(
        reference_type="path",
        reference="node:assert/strict",
        instruction_path="AGENTS.md",
        n_observations=2,
        first_change_type="add",
        repeated_repo_count=1,
        repeated_file_count=1,
        snippet="Use node:assert/strict",
    )
    assert category == "artifact"
    assert confidence == "high"


def test_structured_missing_maps_confirmed_false():
    category, confidence, _, _ = classify_gfc_confirmatory(
        reference_type="path",
        reference="packages/dd-trace/src/tracer.js",
        instruction_path="AGENTS.md",
        n_observations=4,
        first_change_type="add",
        repeated_repo_count=1,
        repeated_file_count=1,
        snippet="Core tracer in packages/dd-trace/src/tracer.js",
    )
    assert category == "confirmed_false"
    assert confidence == "high"


def test_needs_llm_only_for_ambiguous():
    assert not needs_confirmatory_llm(category="confirmed_false", confidence="medium")
    assert needs_confirmatory_llm(category="ambiguous", confidence="low")


def test_wilson_interval():
    lo, hi = wilson_interval(50, 100)
    assert 0.0 <= lo <= hi <= 1.0
