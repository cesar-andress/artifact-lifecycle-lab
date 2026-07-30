"""Tests for RQ5 v1 blind LB packet redesign (spec v2)."""

from __future__ import annotations

import json
from pathlib import Path

from artifact_lab.experiments.truth_decay.rq5_experiment.blind_lb_derive import (
    derive_final_classification,
)
from artifact_lab.experiments.truth_decay.rq5_experiment.blind_lb_packet import (
    PROTOCOL_VERSION,
    leakage_hits,
    stable_neutral_id,
    treatment_ban_paths,
)
from artifact_lab.experiments.truth_decay.rq5_experiment.blind_lb_redact import (
    corruption_markers,
    redact_paths,
)
from artifact_lab.experiments.truth_decay.rq5_experiment.blind_lb_task_brief import (
    extract_task_brief,
)

SCHEMA_PATH = Path(
    "artifact_lab/experiments/truth_decay/rq5_experiment/blind_lb_form_schema.json"
)


def test_derive_load_bearing_only_when_directly_relevant_and_material():
    out = derive_final_classification("directly_relevant", "materially_necessary")
    assert out["final_classification"] == "load_bearing"


def test_derive_contextual_plus_material_is_non_load_bearing_with_warning():
    out = derive_final_classification("contextually_relevant", "materially_necessary")
    assert out["final_classification"] == "non_load_bearing"
    assert out["consistency_warning"] is True


def test_form_schema_omits_final_label():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert "final_classification" not in schema["properties"]
    assert schema["properties"]["protocol_version"]["const"] == PROTOCOL_VERSION


def test_neutral_ids_deterministic():
    assert stable_neutral_id("caseAAA", seed=42) == stable_neutral_id("caseAAA", seed=42)
    assert stable_neutral_id("caseAAA", seed=42) != stable_neutral_id("caseBBB", seed=42)


def test_semantic_redaction_does_not_corrupt_versions_for_short_anchor():
    text = 'Take step 1 blog posts. version: "1.0.0". Ratio 10. Path `1/` is cited.'
    out = redact_paths(text, ["1/"])
    assert "version: \"1.0.0\"" in out
    assert "Ratio 10" in out
    assert "step 1 blog" in out
    assert "`[[REF]]`" in out
    assert not corruption_markers(out)


def test_semantic_redaction_directory_anchor_two_slash():
    text = "See folder `2/` and date 2026-04-01 and value 20."
    out = redact_paths(text, ["2/"])
    assert "2026-04-01" in out
    assert "value 20" in out
    assert "`[[REF]]`" in out
    assert "digit_ref" not in corruption_markers(out)


def test_semantic_redaction_init_py_does_not_break_unrelated_suffixes():
    text = "Edit models/family/__init__.py and also cite `/__init__.py` alone."
    out = redact_paths(text, ["/__init__.py"])
    # Exact leading-slash form redacted; longer path should be handled carefully.
    assert "/__init__.py" not in out or out.count("/__init__.py") == 0
    assert "[[REF]]" in out


def test_treatment_ban_paths_includes_contrast_only_paths():
    banned = treatment_ban_paths(
        "See docs/config.toml\n",
        "See docs/config.toml and missing/false_path.yaml\n",
        "docs/config.toml",
    )
    assert "docs/config.toml" in banned
    assert "missing/false_path.yaml" in banned


def test_task_brief_rejects_empty_and_extracts_purpose():
    empty = extract_task_brief("", verification_command=None)
    assert empty.concrete is False
    text = """---
name: demo-skill
description: Diagnose runtime connectivity failures and streaming errors in the demo stack.
---

# Demo Skill

## Purpose

Help engineers fix unreachable runtime endpoints and broken streaming.

## When to Use

Use when the runtime returns errors.
"""
    brief = extract_task_brief(text, verification_command="npm test")
    assert brief.concrete is True
    assert "npm test" in brief.brief
    assert "pytest" not in brief.brief.lower() or "npm test" in brief.brief


def test_leakage_hits_flag_absence_statements():
    hits = leakage_hits("The path [[REF]] does not exist in the tree.")
    assert "absence_statement" in hits
    # Meta policy text should not trip the gate.
    assert "absence_statement" not in leakage_hits(
        "Do not infer experimental treatment from path placeholders."
    )


def test_leakage_hits_flag_conditions():
    assert "condition_a" in leakage_hits("condition_a leaked")
