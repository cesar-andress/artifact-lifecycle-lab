"""Tests for Phase 0 toolchain failure audit."""

from __future__ import annotations

from pathlib import Path

from artifact_lab.experiments.rq5_v2.models import FactorialCase, FactorialCell
from artifact_lab.experiments.rq5_v2.phase0_run import PHASE0_CELL
from artifact_lab.experiments.rq5_v2.phase0_toolchain_audit import (
    classify_toolchain_failure,
    run_toolchain_failure_audit,
    summarize_case_quality,
)


def _case(**kwargs) -> FactorialCase:
    cells = {
        PHASE0_CELL: FactorialCell(
            cell_code=PHASE0_CELL,
            instruction_blob_sha="x",
            cited_anchor="src/a.py",
            mechanical_truth=True,
            task_prompt="task",
            load_bearing=True,
        )
    }
    defaults = dict(
        case_id="c1",
        candidate_id="lbv2_0001",
        repo_id="r1",
        repo_url="https://github.com/a/b",
        repository="a/b",
        instruction_path="AGENTS.md",
        commit_sha="deadbeef",
        anchor_path_true="src/a.py",
        anchor_path_false="src/a_helper.py",
        decoy_path="README.md",
        test_command="Vitest",
        reference_type="path",
        load_bearing_role="edit",
        ecosystem="node",
        calibrated_expected_success=0.5,
        cells=cells,
    )
    defaults.update(kwargs)
    return FactorialCase(**defaults)


def test_classify_missing_runner_vitest(tmp_path: Path):
    row = {
        "run_id": "r1",
        "case_id": "c1",
        "cell_code": PHASE0_CELL,
        "success": "False",
        "error_message": "/bin/sh: 1: Vitest: not found\n",
        "tests_passing": "False",
        "compilation_success": "True",
        "files_modified": "2",
    }
    result = classify_toolchain_failure(row=row, case=_case(), trace_path=tmp_path / "missing.jsonl")
    assert result.failure_class == "missing test runner"
    assert result.preflight_preventable == "yes"


def test_classify_pytest_zero_collected(tmp_path: Path):
    row = {
        "run_id": "r2",
        "case_id": "c2",
        "cell_code": PHASE0_CELL,
        "success": "False",
        "error_message": "collected 0 items\nno tests ran",
        "tests_passing": "False",
        "compilation_success": "True",
        "files_modified": "1",
    }
    result = classify_toolchain_failure(
        row=row,
        case=_case(case_id="c2", test_command="pytest", ecosystem="python"),
        trace_path=tmp_path / "missing.jsonl",
    )
    assert result.failure_class == "invalid test command"


def test_classify_go_wrong_module(tmp_path: Path):
    row = {
        "run_id": "r3",
        "case_id": "c3",
        "cell_code": PHASE0_CELL,
        "success": "False",
        "error_message": "go: cannot find main module, but found .git/config",
        "tests_passing": "False",
        "compilation_success": "True",
        "files_modified": "0",
    }
    result = classify_toolchain_failure(
        row=row,
        case=_case(case_id="c3", test_command="go test", ecosystem="other"),
        trace_path=tmp_path / "missing.jsonl",
    )
    assert result.failure_class == "wrong working directory"


def test_classify_success(tmp_path: Path):
    row = {"run_id": "r4", "case_id": "c4", "cell_code": PHASE0_CELL, "success": "True"}
    result = classify_toolchain_failure(row=row, case=_case(case_id="c4", test_command="npm test"), trace_path=tmp_path / "x")
    assert result.failure_class == ""
    assert result.exclude_case_recommended == "no"


def test_case_quality_valid_toolchain():
    from artifact_lab.experiments.rq5_v2.phase0_toolchain_audit import ToolchainFailureRow

    rows = [
        ToolchainFailureRow("r1", "c1", "a/b", "node", PHASE0_CELL, "npm test", True, "", "", "n/a", "no", "none"),
        ToolchainFailureRow("r2", "c1", "a/b", "node", PHASE0_CELL, "npm test", True, "", "", "n/a", "no", "none"),
    ]
    verdicts = summarize_case_quality(rows)
    assert verdicts[0].valid_toolchain == "yes"
    assert verdicts[0].recommendation == "keep"


def test_run_audit_synthetic(tmp_path: Path):
    export_dir = tmp_path / "out"
    export_dir.mkdir()
    (export_dir / "factorial_case_manifest.json").write_text("[]")
    (export_dir / "phase0_results.csv").write_text(
        "run_id,case_id,cell_code,success,error_message,tests_passing,compilation_success,files_modified,timed_out,trace_path\n"
        "r1,c1,T+L,False,Vitest: not found,False,True,1,False,\n"
    )
    (export_dir / "phase0_run.log").write_text("started\n")
    (export_dir / "phase0_trace_audit.csv").write_text("run_id\n")
    paths = run_toolchain_failure_audit(output_dir=export_dir, manifest_path=export_dir / "factorial_case_manifest.json")
    assert paths["audit_csv"].exists()
    text = paths["summary_md"].read_text()
    assert "execution-environment audit" in text
