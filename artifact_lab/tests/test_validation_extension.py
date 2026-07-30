"""Assertions for the pre-submission validation extension on frozen exports."""

from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PY = sys.executable


def _sha16(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _bool(v: str) -> bool:
    return str(v).strip().lower() in {"1", "true", "yes", "t"}


def test_frozen_headline_counts() -> None:
    with (ROOT / "exports/truth_decay_pilot/rq2_failure_audit.csv").open() as handle:
        rq2 = list(csv.DictReader(handle))
    assert len(rq2) == 121
    assert sum(1 for r in rq2 if _bool(r["is_genuine_decay"])) == 0

    with (ROOT / "exports/truth_decay_pilot/born_stale_taxonomy.csv").open() as handle:
        born = list(csv.DictReader(handle))
    assert len(born) == 17747
    assert sum(1 for r in born if r["final_category"] == "genuine_false_claim") == 1405

    with (ROOT / "exports/truth_decay_pilot/gfc_confirmatory_audit.csv").open() as handle:
        gfc = list(csv.DictReader(handle))
    assert len(gfc) == 1405
    assert sum(1 for r in gfc if _bool(r["is_confirmed_false"])) == 1200


def test_frozen_input_hashes() -> None:
    expect = {
        "exports/truth_decay_pilot/rq2_failure_audit.csv": "5efd790630e3de36",
        "exports/truth_decay_pilot/born_stale_taxonomy.csv": "8d340848882a7f42",
        "exports/truth_decay_pilot/gfc_confirmatory_audit.csv": "b55eae8c4d6c22cb",
    }
    for rel, digest in expect.items():
        assert _sha16(ROOT / rel) == digest


def test_blinded_package_no_leakage() -> None:
    blinded = ROOT / "validation/rq2_second_audit/rq2_audit_blinded.csv"
    if not blinded.exists():
        pytest.skip("run make validation-package first")
    with blinded.open() as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 121
    header = set(rows[0].keys())
    for leak in (
        "final_category",
        "is_genuine_decay",
        "heuristic_category",
        "judge_a_category",
        "category_letter",
        "adjudication_status",
    ):
        assert leak not in header
    assert not (ROOT / "validation/rq2_second_audit/rq2_original_labels_private.csv").exists()


def test_sensitivity_primary_zero_and_range() -> None:
    path = ROOT / "validation/rq2_sensitivity/rq2_sensitivity_scenarios.csv"
    if not path.exists():
        pytest.skip("run make validation-sensitivity first")
    with path.open() as handle:
        rows = {r["scenario"]: r for r in csv.DictReader(handle)}
    assert rows["primary_frozen"]["numerator"] == "0"
    assert rows["high_specificity"]["numerator"] == "0"
    assert rows["decay_favoring"]["numerator"] == "25"
    assert rows["second_auditor"]["available"] == "no"


def test_validation_qc_script() -> None:
    proc = subprocess.run(
        [PY, str(ROOT / "scripts/validation/run_validation_qc.py")],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
