"""Tests for RQ5 v2 factorial infrastructure."""

from __future__ import annotations

from pathlib import Path

from artifact_lab.experiments.rq5_v2.factors import CellCode, cell_from_factors, levels_for_cell
from artifact_lab.experiments.rq5_v2.instruction_variants import (
    build_cell_instruction_text,
    build_factorial_cells,
)
from artifact_lab.experiments.rq5_v2.models import ExperimentConfig
from artifact_lab.experiments.rq5_v2.plan import build_run_plan
from artifact_lab.experiments.rq5_v2.prompts import build_factorial_prompt
from artifact_lab.experiments.rq5_v2.runner import ExecutionNotAllowedError, dry_run_result, run_factorial_matrix
from artifact_lab.store.blobs import BlobStore


def test_factor_levels_all_cells():
    for code in CellCode:
        levels = levels_for_cell(code)
        if code == CellCode.N:
            assert not levels.instruction_present
            assert levels.factor_b == "na"
        else:
            assert levels.instruction_present
            assert levels.factor_b in ("truthful", "false")
            assert levels.factor_c in ("yes", "no")


def test_cell_from_factors_roundtrip():
    assert cell_from_factors(instruction_present=False, reference_truthful=True, load_bearing=True) == CellCode.N
    assert cell_from_factors(instruction_present=True, reference_truthful=True, load_bearing=True) == CellCode.T_L
    assert cell_from_factors(instruction_present=True, reference_truthful=False, load_bearing=False) == CellCode.F_P


def test_instruction_variants_lb_vs_pb():
    base = "# Project rules\nUse pytest.\n"
    lb_text, cited, truth = build_cell_instruction_text(
        base_text=base,
        cell_code=CellCode.T_L,
        anchor_true="src/foo.py",
        anchor_false="src/_foo.missing",
        decoy_path="README.md",
        test_command="pytest",
    )
    assert "src/foo.py" in lb_text
    assert cited == "src/foo.py"
    assert truth

    pb_text, _, _ = build_cell_instruction_text(
        base_text=base,
        cell_code=CellCode.T_P,
        anchor_true="src/foo.py",
        anchor_false="src/_foo.missing",
        decoy_path="README.md",
        test_command="pytest",
    )
    assert "Related files" in pb_text


def test_build_factorial_cells(tmp_path: Path):
    store = BlobStore(tmp_path / "blobs")
    cells = build_factorial_cells(
        base_instruction_text="# Rules\n",
        anchor_true="src/a.py",
        test_command="pytest",
        blob_store=store,
        anchor_false="src/manager.py",
        decoy_path="README.md",
    )
    assert set(cells) == {"T+L", "F+L", "T+P", "F+P", "N"}
    assert cells["N"].instruction_blob_sha == ""
    assert cells["F+L"].mechanical_truth is False


def test_run_plan_size():
    from artifact_lab.experiments.rq5_v2.models import FactorialCase, FactorialCell

    cells = {}
    for code in CellCode:
        cells[code.value] = FactorialCell(
            cell_code=code.value,
            instruction_blob_sha="abc",
            cited_anchor="src/x.py",
            mechanical_truth=True,
            task_prompt="task",
            load_bearing=code in (CellCode.T_L, CellCode.F_L),
        )
    case = FactorialCase(
        case_id="c1",
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

    config = ExperimentConfig(agents=("claude_code",), replicates=2, cells=("T+L", "N"))
    plan = build_run_plan(cases=[case], config=config, seed=1)
    assert len(plan) == 1 * 2 * 1 * 2  # cases × cells × agents × replicates


def test_execution_blocked_by_default(tmp_path: Path):
    from artifact_lab.experiments.rq5_v2.models import RunPlanEntry

    entry = RunPlanEntry(
        run_id="r1",
        case_id="missing",
        cell_code="T+L",
        agent_id="claude_code",
        replicate_id=1,
        factor_a="present",
        factor_b="truthful",
        factor_c="yes",
        repo_url="",
        commit_sha="",
        instruction_path="",
        test_command="pytest",
    )
    config = ExperimentConfig(allow_execute=False)
    try:
        run_factorial_matrix(
            cases=[],
            plan=[entry],
            config=config,
            blob_store=BlobStore(tmp_path / "blobs"),
            scratch_dir=tmp_path / "scratch",
            results_csv=tmp_path / "results.csv",
            traces_dir=tmp_path / "traces",
            execute=True,
        )
        assert False, "expected ExecutionNotAllowedError"
    except ExecutionNotAllowedError:
        pass


def test_dry_run_stub():
    from artifact_lab.experiments.rq5_v2.models import RunPlanEntry

    entry = RunPlanEntry(
        run_id="r1",
        case_id="c1",
        cell_code="F+L",
        agent_id="codex",
        replicate_id=1,
        factor_a="present",
        factor_b="false",
        factor_c="yes",
        repo_url="",
        commit_sha="",
        instruction_path="AGENTS.md",
        test_command="pytest",
    )
    result = dry_run_result(entry)
    assert result.dry_run
    assert result.factor_b == "false"
