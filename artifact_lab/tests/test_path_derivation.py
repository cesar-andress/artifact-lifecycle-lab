"""Tests for commit-aware path derivation, deduplication, and repairability."""

from __future__ import annotations

from artifact_lab.experiments.rq5_v2.case_builder import deduplicate_candidates
from artifact_lab.experiments.rq5_v2.path_derivation import (
    derive_case_paths,
    derive_decoy_path,
    derive_false_path,
    score_repairability,
)
from artifact_lab.experiments.rq5_v2.phase0_audit import (
    _verdict,
    audit_case,
    false_path_syntactically_plausible,
    path_resolves,
)
from artifact_lab.experiments.rq5_v2.instruction_variants import build_factorial_cells
from artifact_lab.experiments.rq5_v2.models import FactorialCase
from artifact_lab.store.blobs import BlobStore
from pathlib import Path


def _tree() -> set[str]:
    return {
        "src/auth/service.py",
        "src/auth/session.py",
        "src/auth/config.py",
        "src/auth/manager.py",
        "tests/test_api.py",
        "tests/test_utils.py",
        "tests/conftest.py",
        "scripts/build.sh",
        "scripts/deploy.sh",
        "README.md",
    }


def test_derive_false_path_plausible_sibling():
    tree = _tree()
    false_path = derive_false_path("src/auth/service.py", tree)
    assert false_path is not None
    assert false_path.startswith("src/auth/")
    assert false_path.endswith(".py")
    assert ".missing" not in false_path
    assert false_path not in tree
    ok, _ = false_path_syntactically_plausible("src/auth/service.py", false_path)
    assert ok


def test_derive_false_path_examples():
    tree = _tree() | {"tests/test_client.py"}
    false_path = derive_false_path("tests/test_api.py", tree)
    assert false_path is not None
    assert false_path.startswith("tests/")
    assert false_path not in tree

    tree2 = _tree()
    false_sh = derive_false_path("scripts/build.sh", tree2)
    assert false_sh is not None
    assert false_sh.endswith(".sh")
    assert false_sh not in tree2


def test_derive_false_path_non_resolution():
    tree = _tree()
    true_path = "src/auth/service.py"
    false_path = derive_false_path(true_path, tree)
    assert false_path is not None
    assert not path_resolves(false_path, tree)
    assert path_resolves(true_path, tree)


def test_derive_decoy_path_resolves_and_distinct():
    tree = _tree()
    true_path = "src/auth/service.py"
    false_path = derive_false_path(true_path, tree)
    assert false_path is not None
    decoy = derive_decoy_path(true_path, tree, exclude=frozenset({false_path}))
    assert decoy is not None
    assert decoy != true_path
    assert decoy != false_path
    assert path_resolves(decoy, tree)


def test_derive_decoy_prefers_same_directory():
    tree = _tree()
    decoy = derive_decoy_path("src/auth/service.py", tree)
    assert decoy is not None
    assert decoy.startswith("src/auth/")


def test_repairability_score_range():
    tree = _tree()
    derived = derive_case_paths("src/auth/service.py", tree)
    assert derived is not None
    score, reason = score_repairability("src/auth/service.py", derived.false_path, tree)
    assert 0 <= score <= 3
    assert 0 <= derived.repairability_score <= 3
    assert reason


def test_deduplicate_candidates_prefers_confidence_and_calibration():
    calibration = {
        "a": {"calibrated_expected_success": "0.55"},
        "b": {"calibrated_expected_success": "0.48"},
    }
    rows = [
        {
            "candidate_id": "a",
            "repo_id": "r1",
            "reference": "src/x.py",
            "commit_sha": "c1",
            "confidence": "0.7",
        },
        {
            "candidate_id": "b",
            "repo_id": "r1",
            "reference": "src/x.py",
            "commit_sha": "c1",
            "confidence": "0.9",
        },
    ]
    deduped = deduplicate_candidates(rows, calibration)
    assert len(deduped) == 1
    assert deduped[0]["candidate_id"] == "b"


def test_audit_pass_condition_on_derived_case(tmp_path: Path):
    tree = _tree()
    derived = derive_case_paths("src/auth/service.py", tree)
    assert derived is not None
    store = BlobStore(tmp_path / "blobs")
    cells = build_factorial_cells(
        base_instruction_text="# Rules\n",
        anchor_true="src/auth/service.py",
        test_command="pytest",
        blob_store=store,
        anchor_false=derived.false_path,
        decoy_path=derived.decoy_path,
    )
    case = FactorialCase(
        case_id="case1",
        candidate_id="lbv2_test",
        repo_id="repo1",
        repo_url="https://github.com/a/b",
        repository="a/b",
        instruction_path="AGENTS.md",
        commit_sha="deadbeef",
        anchor_path_true="src/auth/service.py",
        anchor_path_false=derived.false_path,
        decoy_path=derived.decoy_path,
        test_command="pytest",
        reference_type="path",
        load_bearing_role="edit",
        ecosystem="python",
        calibrated_expected_success=0.5,
        repairability_score=derived.repairability_score,
        repairability_reason=derived.repairability_reason,
        cells=cells,
    )
    row = audit_case(
        case,
        tree_paths=tree,
        calibration_row={"calibrated_expected_success": "0.5"},
        candidate_row={"estimated_success_rate": "0.69"},
        repo_case_counts={case.repo_id: 1},
        path_dup_keys=set(),
    )
    assert row.valid_phase0
    assert row.checks["repairability_score_present"]


def test_verdict_pass_requires_twenty():
    assert _verdict(20) == "PASS"
