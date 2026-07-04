"""Tests for Phase 0 calibration planning, metrics, and decision gates."""

from __future__ import annotations

import os
from pathlib import Path

from artifact_lab.experiments.rq5_v2.models import ExperimentConfig, FactorialCase, FactorialCell
from artifact_lab.experiments.rq5_v2.phase0_run import (
    PHASE0_AGENT,
    PHASE0_CELL,
    PHASE0_EXPECTED_RUNS,
    build_phase0_plan,
    compute_phase0_metrics,
    evaluate_phase0_decision,
    verify_phase0_preflight,
    wilson_ci,
)


def _minimal_case(case_id: str = "c1") -> FactorialCase:
    cells = {
        PHASE0_CELL: FactorialCell(
            cell_code=PHASE0_CELL,
            instruction_blob_sha="abc",
            cited_anchor="src/x.py",
            mechanical_truth=True,
            task_prompt="task",
            load_bearing=True,
        )
    }
    return FactorialCase(
        case_id=case_id,
        candidate_id="lbv2_0001",
        repo_id="r1",
        repo_url="https://github.com/a/b",
        repository="a/b",
        instruction_path="AGENTS.md",
        commit_sha="deadbeef",
        anchor_path_true="src/x.py",
        anchor_path_false="src/x_helper.py",
        decoy_path="README.md",
        test_command="pytest",
        reference_type="path",
        load_bearing_role="edit",
        ecosystem="python",
        calibrated_expected_success=0.5,
        cells=cells,
    )


def test_phase0_plan_scope():
    cases = [_minimal_case(f"c{i}") for i in range(20)]
    plan, config = build_phase0_plan(cases=cases, seed=42)
    assert len(plan) == PHASE0_EXPECTED_RUNS
    assert config.cells == (PHASE0_CELL,)
    assert config.agents == (PHASE0_AGENT,)
    assert config.replicates == 3
    assert {e.cell_code for e in plan} == {PHASE0_CELL}
    assert {e.agent_id for e in plan} == {PHASE0_AGENT}


def test_wilson_ci():
    p, lo, hi = wilson_ci(45, 100)
    assert 0.35 < p < 0.55
    assert lo < p < hi


def test_preflight_requires_execute_env(tmp_path: Path):
    cases = [_minimal_case()]
    plan, config = build_phase0_plan(cases=cases)
    os.environ.pop("RQ5_V2_ALLOW_EXECUTE", None)
    (tmp_path / "phase0_manifest_repaired.json").write_text("[]", encoding="utf-8")
    report = verify_phase0_preflight(
        plan=plan,
        config=config,
        results_csv=tmp_path / "results.csv",
        traces_dir=tmp_path / "traces",
        require_execute_env=True,
        manifest_path=tmp_path / "phase0_manifest_repaired.json",
    )
    assert not report.checks["execute_env_required"]


def test_decision_pass():
    rows = []
    for i in range(60):
        rows.append(
            {
                "success": "True" if i < 33 else "False",
                "anchor_attempted": "True" if i < 45 else "False",
                "instruction_read": "True",
                "files_modified": "3",
                "commands_executed": "5",
                "tool_failures": "0",
                "timed_out": "False",
                "execution_time_seconds": "120",
                "cost_usd": "0.01",
            }
        )
    metrics = compute_phase0_metrics(rows)
    decision = evaluate_phase0_decision(metrics)
    assert decision.verdict == "PASS"
    assert not decision.proceed_phase1a


def test_decision_fail_low_success():
    rows = [
        {
            "success": "False",
            "anchor_attempted": "True",
            "instruction_read": "True",
            "files_modified": "2",
            "commands_executed": "1",
            "tool_failures": "0",
            "timed_out": "False",
            "execution_time_seconds": "60",
        }
    ] * 60
    metrics = compute_phase0_metrics(rows)
    assert metrics.success_rate == 0.0
    decision = evaluate_phase0_decision(metrics)
    assert decision.verdict == "FAIL"
