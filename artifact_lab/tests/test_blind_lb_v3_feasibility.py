"""Tests for RQ5 v1 annotation instrument v3 feasibility gates."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from artifact_lab.experiments.truth_decay.rq5_experiment.blind_lb_v3_feasibility import (
    DEFAULT_OUTPUT,
    run_audit,
)

DO_NOT_DISTRIBUTE = Path("exports/rq5_lb_blind_annotation/DO_NOT_DISTRIBUTE_V2.md")
V2_KIT = Path("exports/rq5_lb_blind_annotation/human_annotation_kit")


@pytest.fixture(scope="module")
def audit_dir(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("v3_feas")
    run_audit(output_dir=out)
    return out


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_v2_kit_marked_non_distributable():
    assert DO_NOT_DISTRIBUTE.is_file()
    text = DO_NOT_DISTRIBUTE.read_text(encoding="utf-8").lower()
    assert "must not be sent" in text or "must not be sent to annotators" in text
    assert "non-distributable" in text or "do not distribute" in text
    # Stale distribution path must be called out.
    assert "human_annotation_kit" in text


def test_all_cases_have_explicit_exclusion_or_eligible(audit_dir: Path):
    rows = _rows(audit_dir / "case_reeligibility_v3.csv")
    assert len(rows) == 35
    for row in rows:
        if row["eligible_boolean"] == "true":
            assert row["exclusion_reason"] == ""
            assert row["eligibility_verdict"] == "eligible"
        else:
            assert row["exclusion_reason"]
            assert row["eligibility_verdict"] == "ineligible"


def test_no_eligible_without_independent_task_oracle(audit_dir: Path):
    for row in _rows(audit_dir / "case_reeligibility_v3.csv"):
        if row["eligible_boolean"] == "true":
            assert row["has_independent_task_oracle"] == "true"
            assert row["task_oracle_source"] not in {
                "",
                "none",
                "instruction_file",
                "instruction_derived_summary",
                "generic_instruction_coupled_prompt",
            }


def test_no_eligible_when_task_source_is_instruction_coupled(audit_dir: Path):
    for row in _rows(audit_dir / "case_reeligibility_v3.csv"):
        if row["task_oracle_source"] == "generic_instruction_coupled_prompt":
            assert row["eligible_boolean"] == "false"
            assert row["exclusion_reason"] == "no_independent_task_oracle"


def test_no_non_software_task_marked_eligible(audit_dir: Path):
    for row in _rows(audit_dir / "case_reeligibility_v3.csv"):
        if row["is_genuine_software_engineering_task"] != "true":
            assert row["eligible_boolean"] == "false"


def test_no_eligible_without_r1_presentable(audit_dir: Path):
    for row in _rows(audit_dir / "case_reeligibility_v3.csv"):
        if row["eligible_boolean"] == "true":
            assert row["r1_content_safely_presentable"] == "true"


def test_no_eligible_without_anonymization_assessment(audit_dir: Path):
    for row in _rows(audit_dir / "case_reeligibility_v3.csv"):
        assert row["repository_identity_anonymizable"] in {
            "true",
            "false",
            "uncertain",
        }
        assert row["reidentification_risk"]
        if row["eligible_boolean"] == "true":
            assert row["repository_identity_anonymizable"] == "true"
            assert row["reidentification_risk"] != "unresolved_critical"


def test_no_eligible_with_non_independent_circularity(audit_dir: Path):
    for row in _rows(audit_dir / "case_reeligibility_v3.csv"):
        if row["circularity_class"] != "independent":
            assert row["eligible_boolean"] == "false"
    for row in _rows(audit_dir / "circularity_audit_v3.csv"):
        assert row["circularity_evidence"]
        if row["circularity_class"] != "independent":
            # Cross-check reeligibility
            pass


def test_current_rq5_v1_has_zero_eligible(audit_dir: Path):
    rows = _rows(audit_dir / "case_reeligibility_v3.csv")
    assert sum(1 for r in rows if r["eligible_boolean"] == "true") == 0
    summary = json.loads((audit_dir / "feasibility_summary.json").read_text(encoding="utf-8"))
    assert summary["n_eligible_all_criteria"] == 0
    assert summary["feasibility_verdict"] == "NOT_FEASIBLE_WITH_CURRENT_RQ5_V1_DATA"
    assert summary["n_independent_task_oracles"] == 0


def test_committed_v3_outputs_exist_when_present():
    """If the repo has committed audit outputs, they must satisfy the zero-eligible fact."""
    path = DEFAULT_OUTPUT / "case_reeligibility_v3.csv"
    if not path.exists():
        pytest.skip("committed audit not present")
    rows = _rows(path)
    assert len(rows) == 35
    assert all(r["eligible_boolean"] == "false" for r in rows)
    assert all(r["exclusion_reason"] == "no_independent_task_oracle" for r in rows)
