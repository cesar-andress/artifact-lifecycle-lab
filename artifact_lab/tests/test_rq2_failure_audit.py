"""Tests for RQ2 post-verification failure audit."""

from __future__ import annotations

from pathlib import Path

from artifact_lab.experiments.truth_decay.rq2_failure_audit import (
    CATEGORY_LETTERS,
    classify_failure_context,
    load_survival_failures,
    map_llm_category_to_rq2,
    needs_rq2_llm_adjudication,
)
from artifact_lab.experiments.truth_decay.rq2_failure_statistics import (
    compute_audit_statistics,
    wilson_interval,
)
from artifact_lab.experiments.truth_decay.rq2_failure_audit import FailureAuditRecord


def test_map_llm_category_born_stale_alias():
    assert map_llm_category_to_rq2("genuine_false_claim") == "genuine_decay"
    assert map_llm_category_to_rq2("verification_anchor_mismatch") == "verification_anchor_issue"


def test_ever_repaired_maps_to_rename_or_move():
    category, confidence, rules, _, _ = classify_failure_context(
        reference_type="path",
        reference="src/main.py",
        instruction_path="AGENTS.md",
        n_observations=5,
        first_change_type="modify",
        repeated_repo_count=1,
        repeated_file_count=1,
        snippet="",
        ever_repaired=True,
        returned_after_missing=False,
        basename_collision_verified=False,
    )
    assert category == "rename_or_move"
    assert confidence == "medium"
    assert "repair_event_after_first_missing" in rules


def test_relative_path_maps_to_anchor_issue():
    category, confidence, _, _, _ = classify_failure_context(
        reference_type="path",
        reference="./src/foo.py",
        instruction_path=".cursor/rules/x.mdc",
        n_observations=3,
        first_change_type="modify",
        repeated_repo_count=1,
        repeated_file_count=1,
        snippet="",
        ever_repaired=False,
        returned_after_missing=False,
        basename_collision_verified=False,
    )
    assert category == "verification_anchor_issue"
    assert confidence == "high"


def test_needs_llm_for_ambiguous():
    from artifact_lab.experiments.truth_decay.born_stale_taxonomy import HeuristicVerdict

    born = HeuristicVerdict(
        category=None,
        confidence="low",
        rules_fired=(),
        rationale="",
    )
    assert needs_rq2_llm_adjudication(category="ambiguous", confidence="low", born_verdict=born)


def test_wilson_interval_bounds():
    lo, hi = wilson_interval(10, 100)
    assert 0.0 <= lo <= hi <= 1.0


def test_compute_audit_statistics():
    record = FailureAuditRecord(
        repo_id="abc",
        repo_url="https://example.com",
        instruction_path="AGENTS.md",
        reference_type="path",
        reference="foo.py",
        time_origin="2025-01-01T00:00:00+00:00",
        time_end="2025-02-01T00:00:00+00:00",
        duration_days=31.0,
        ever_repaired=False,
        post_failure_followup_days=None,
        failure_commit="deadbeef",
        failure_transition="VERIFIED->MISSING",
        verified_before_failure=True,
        returned_after_missing=False,
        basename_collision_verified=False,
        n_observations=3,
        repeated_repo_count=1,
        repeated_file_count=1,
        snippet_available=False,
        snippet="",
        born_stale_heuristic_category="",
        born_stale_heuristic_confidence="low",
        born_stale_heuristic_rules="",
        heuristic_category="genuine_decay",
        heuristic_confidence="high",
        heuristic_rules="",
        heuristic_rationale="",
        adjudication_status="deterministic_high",
        final_category="genuine_decay",
        category_letter=CATEGORY_LETTERS["genuine_decay"],
        is_genuine_decay=True,
        judge_a_model="",
        judge_a_category="",
        judge_a_rationale="",
        judge_b_model="",
        judge_b_category="",
        judge_b_rationale="",
        judge_agreement="",
    )
    stats = compute_audit_statistics(
        records=[record],
        verified_cohort_size=100,
        born_stale_raw=1000,
        born_stale_genuine_adjusted=100,
        born_by_repo_genuine={"abc": 100},
    )
    assert stats.n_genuine_adjusted == 1
    assert stats.adjusted_decay_rate == 0.01
    assert stats.raw_ratio_born_to_post == 1000.0


def test_load_survival_failures_count():
    survival = Path("exports/truth_decay_pilot/rq2_survival.csv")
    if survival.exists():
        failures = load_survival_failures(survival)
        assert len(failures) == 121
