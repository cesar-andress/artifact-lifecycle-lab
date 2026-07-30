#!/usr/bin/env python3
"""Quality control for validation-extension artifacts."""

from __future__ import annotations

import csv
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

EXPECTED_SHA16 = {
    "exports/truth_decay_pilot/rq2_failure_audit.csv": "5efd790630e3de36",
    "exports/truth_decay_pilot/born_stale_taxonomy.csv": "8d340848882a7f42",
    "exports/truth_decay_pilot/gfc_confirmatory_audit.csv": "b55eae8c4d6c22cb",
}


def sha16(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _bool(v: str) -> bool:
    return str(v).strip().lower() in {"1", "true", "yes", "t"}


def main() -> int:
    errors: list[str] = []

    for rel, expect in EXPECTED_SHA16.items():
        path = ROOT / rel
        got = sha16(path)
        if got != expect:
            errors.append(f"hash mismatch {rel}: {got} != {expect}")

    with (ROOT / "exports/truth_decay_pilot/rq2_failure_audit.csv").open() as handle:
        rq2 = list(csv.DictReader(handle))
    if len(rq2) != 121:
        errors.append(f"rq2 rows {len(rq2)} != 121")
    if sum(1 for r in rq2 if _bool(r["is_genuine_decay"])) != 0:
        errors.append("primary 0/121 violated")

    with (ROOT / "exports/truth_decay_pilot/born_stale_taxonomy.csv").open() as handle:
        born = list(csv.DictReader(handle))
    if len(born) != 17747:
        errors.append(f"born-stale {len(born)} != 17747")
    if sum(1 for r in born if r["final_category"] == "genuine_false_claim") != 1405:
        errors.append("prior GFC != 1405")

    with (ROOT / "exports/truth_decay_pilot/gfc_confirmatory_audit.csv").open() as handle:
        gfc = list(csv.DictReader(handle))
    if len(gfc) != 1405:
        errors.append(f"gfc audit {len(gfc)} != 1405")
    if sum(1 for r in gfc if _bool(r["is_confirmed_false"])) != 1200:
        errors.append("confirmed-false != 1200")

    blinded = ROOT / "validation/rq2_second_audit/rq2_audit_blinded.csv"
    if not blinded.exists():
        errors.append("missing blinded audit csv")
    else:
        with blinded.open() as handle:
            brows = list(csv.DictReader(handle))
        if len(brows) != 121:
            errors.append(f"blinded rows {len(brows)} != 121")
        if len({r["event_id"] for r in brows}) != 121:
            errors.append("duplicate event_id in blinded file")
        header = brows[0].keys() if brows else []
        for leak in (
            "final_category",
            "is_genuine_decay",
            "heuristic_category",
            "judge_a_category",
            "category_letter",
        ):
            if leak in header:
                errors.append(f"label leakage column in blinded: {leak}")
        # public private key must not exist
        if (ROOT / "validation/rq2_second_audit/rq2_original_labels_private.csv").exists():
            errors.append("private key exposed at public path")
        text = blinded.read_text(encoding="utf-8").splitlines()[0]
        if re.search(r"is_genuine_decay|final_category", text):
            errors.append("leak pattern in blinded header")
        missing_repo = sum(1 for r in brows if not r.get("repo_id"))
        if missing_repo:
            errors.append(f"blinded missing repo_id: {missing_repo}")

    private = ROOT / "validation/rq2_second_audit/private/rq2_original_labels_private.csv"
    if not private.exists():
        errors.append("missing private answer key (local)")
    else:
        with private.open() as handle:
            prows = list(csv.DictReader(handle))
        if len(prows) != 121:
            errors.append("private key row count")

    scen = ROOT / "validation/rq2_sensitivity/rq2_sensitivity_scenarios.csv"
    if not scen.exists():
        errors.append("missing sensitivity scenarios")
    else:
        with scen.open() as handle:
            srows = list(csv.DictReader(handle))
        primary = next(r for r in srows if r["scenario"] == "primary_frozen")
        if primary.get("available") == "yes" and primary.get("numerator") not in {"0", 0}:
            errors.append("sensitivity primary numerator != 0")

    conc = ROOT / "validation/concentration/concentration_summary.md"
    if not conc.exists():
        errors.append("missing concentration summary")

    if errors:
        print("VALIDATION QC FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("VALIDATION QC PASS")
    print("frozen_counts=121/0,17747,1405,1200")
    print("blinded_leakage=none")
    second = ROOT / "validation/rq2_second_audit/rq2_second_auditor_labels.csv"
    print(
        "second_auditor_labels="
        + ("AVAILABLE" if second.exists() else "NOT_AVAILABLE")
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
