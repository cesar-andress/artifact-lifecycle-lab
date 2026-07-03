"""Tests for RQ5 v2 Phase 0 plan audit logic."""

from __future__ import annotations

from pathlib import Path

from artifact_lab.experiments.rq5_v2.factors import CellCode
from artifact_lab.experiments.rq5_v2.instruction_variants import build_factorial_cells
from artifact_lab.experiments.rq5_v2.models import FactorialCase, FactorialCell
from artifact_lab.experiments.rq5_v2.phase0_audit import (
    CaseAuditRow,
    _ecosystem_balance_ok,
    _verdict,
    all_cells_feasible,
    audit_case,
    false_path_syntactically_plausible,
    lb_task_load_bearing,
    path_resolves,
    pb_task_peripheral,
    task_text_leaks_answer,
)
from artifact_lab.experiments.rq5_v2.instruction_variants import build_factorial_cells
from artifact_lab.store.blobs import BlobStore


def _make_case(
    *,
    anchor_true: str = "src/foo.py",
    anchor_false: str | None = None,
    decoy: str = "README.md",
    ecosystem: str = "python",
    success: float = 0.5,
    repo_id: str = "repo1",
    case_id: str = "case1",
    blob_dir: Path | None = None,
) -> FactorialCase:
    false_path = anchor_false or "src/foo_helper.py"
    store = BlobStore(blob_dir or Path("/tmp/rq5_phase0_audit_test_blobs"))
    cells = build_factorial_cells(
        base_instruction_text="# Rules\n",
        anchor_true=anchor_true,
        test_command="pytest",
        blob_store=store,
        anchor_false=false_path,
        decoy_path=decoy,
    )
    return FactorialCase(
        case_id=case_id,
        candidate_id="lbv2_test",
        repo_id=repo_id,
        repo_url="https://github.com/a/b",
        repository="a/b",
        instruction_path="AGENTS.md",
        commit_sha="deadbeef",
        anchor_path_true=anchor_true,
        anchor_path_false=false_path,
        decoy_path=decoy,
        test_command="pytest",
        reference_type="path",
        load_bearing_role="edit",
        ecosystem=ecosystem,
        calibrated_expected_success=success,
        cells=cells,
    )


def test_path_resolves_exact_and_prefix():
    tree = {"src/foo.py", "src/bar.py", "README.md"}
    assert path_resolves("src/foo.py", tree)
    assert not path_resolves("src/missing.py", tree)


def test_false_path_rejects_missing_suffix():
    ok, reason = false_path_syntactically_plausible(
        "tests/test_replay.py",
        "tests/_test_replay.py.missing",
    )
    assert not ok
    assert "missing" in reason.lower()


def test_false_path_accepts_plausible_sibling():
    ok, _ = false_path_syntactically_plausible(
        "src/foo_utils.py",
        "src/foo_helper.py",
    )
    assert ok


def test_false_path_rejects_typo_distance_one():
    ok, reason = false_path_syntactically_plausible("src/helper.py", "src/helpers.py")
    assert not ok
    assert "typo" in reason.lower()


def test_lb_and_pb_construction_on_synthetic_case():
    case = _make_case()
    assert lb_task_load_bearing(case)[0]
    assert pb_task_peripheral(case)[0]
    assert task_text_leaks_answer(case)[0]


def test_all_cells_feasible_with_tree():
    case = _make_case(
        anchor_true="src/foo.py",
        anchor_false="src/foo_helper.py",
        decoy="README.md",
    )
    tree = {
        "src/foo.py",
        "README.md",
    }
    ok, reason = all_cells_feasible(case, tree)
    assert ok, reason


def test_all_cells_feasible_fails_when_false_resolves():
    case = _make_case(anchor_true="src/foo.py", anchor_false="src/foo.py")
    tree = {"src/foo.py", "README.md"}
    ok, _ = all_cells_feasible(case, tree)
    assert not ok


def test_audit_case_valid_when_checks_pass():
    case = _make_case(
        anchor_true="tests/test_replay.py",
        anchor_false="tests/test_replay_alt.py",
        decoy="tests/README.md",
        success=0.55,
    )
    tree = {
        "tests/test_replay.py",
        "tests/README.md",
    }
    row = audit_case(
        case,
        tree_paths=tree,
        calibration_row={"calibrated_expected_success": "0.55"},
        candidate_row={"estimated_success_rate": "0.55"},
        repo_case_counts={case.repo_id: 1},
        path_dup_keys=set(),
    )
    assert row.checks["true_anchor_resolves"]
    assert row.checks["false_anchor_not_resolves"]
    assert row.checks["false_anchor_plausible"]
    assert row.checks["success_rate_in_band"]
    assert row.checks["repairability_score_present"]
    assert row.valid_phase0


def test_audit_case_invalid_on_missing_suffix_false_path():
    case = _make_case(
        anchor_true="tests/test_replay.py",
        anchor_false="tests/_test_replay.py.missing",
        decoy="tests/conftest.py",
    )
    tree = {"tests/test_replay.py", "tests/conftest.py"}
    row = audit_case(
        case,
        tree_paths=tree,
        calibration_row={},
        candidate_row={"estimated_success_rate": "0.55"},
        repo_case_counts={case.repo_id: 1},
        path_dup_keys=set(),
    )
    assert not row.checks["false_anchor_plausible"]
    assert not row.valid_phase0


def test_ecosystem_balance():
    rows = [
        CaseAuditRow(
            case_id="a",
            candidate_id="c",
            repository="r",
            repo_id="r1",
            ecosystem="python",
            commit_sha="x",
            anchor_path_true="a",
            anchor_path_false="b",
            decoy_path="d",
            load_bearing_role="edit",
            calibrated_expected_success=0.5,
            estimated_success_rate=0.5,
            repairability_score=None,
        ),
        CaseAuditRow(
            case_id="b",
            candidate_id="c2",
            repository="r2",
            repo_id="r2",
            ecosystem="node",
            commit_sha="x",
            anchor_path_true="a",
            anchor_path_false="b",
            decoy_path="d",
            load_bearing_role="edit",
            calibrated_expected_success=0.5,
            estimated_success_rate=0.5,
            repairability_score=None,
        ),
    ]
    ok, _ = _ecosystem_balance_ok(rows)
    assert ok


def test_verdict_thresholds():
    assert _verdict(20) == "PASS"
    assert _verdict(15) == "WARN"
    assert _verdict(5) == "FAIL"
