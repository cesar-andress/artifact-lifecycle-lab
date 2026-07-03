"""Pre-run manipulation checks for factorial cases."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from artifact_lab.experiments.rq5_v2.factors import CellCode
from artifact_lab.experiments.rq5_v2.models import FactorialCase
from artifact_lab.experiments.rq5_v2.workspace import apply_cell_instruction
from artifact_lab.ingest.git_utils import run_git
from artifact_lab.store.blobs import BlobStore


@dataclass(frozen=True)
class ValidationResult:
    case_id: str
    cell_code: str
    check: str
    passed: bool
    detail: str


def _path_exists_in_tree(workspace: Path, ref: str) -> bool:
    if not ref or ref.startswith("@"):
        return False
    candidate = workspace / ref.lstrip("/")
    if candidate.exists():
        return True
    # git ls-tree fallback
    proc = run_git(["git", "ls-tree", "-r", "HEAD", "--name-only"], cwd=workspace, timeout=60)
    if proc.returncode != 0:
        return False
    names = set(proc.stdout.splitlines())
    return ref in names or ref.lstrip("/") in names


def validate_case_cells(
    *,
    case: FactorialCase,
    workspace: Path,
    blob_store: BlobStore,
) -> list[ValidationResult]:
    """Mechanical truth and presence checks at pinned commit."""
    results: list[ValidationResult] = []

    for code in CellCode:
        cell = case.get_cell(code.value)
        apply_cell_instruction(
            workspace=workspace,
            case=case,
            cell_code=code.value,
            blob_store=blob_store,
        )
        instruction = workspace / case.instruction_path

        if code == CellCode.N:
            results.append(
                ValidationResult(
                    case_id=case.case_id,
                    cell_code=code.value,
                    check="instruction_absent",
                    passed=not instruction.exists(),
                    detail="instruction file removed" if not instruction.exists() else "file still present",
                )
            )
            continue

        results.append(
            ValidationResult(
                case_id=case.case_id,
                cell_code=code.value,
                check="instruction_present",
                passed=instruction.exists(),
                detail=str(instruction),
            )
        )

        cited = cell.cited_anchor
        exists = _path_exists_in_tree(workspace, cited)
        expected = cell.mechanical_truth
        results.append(
            ValidationResult(
                case_id=case.case_id,
                cell_code=code.value,
                check="mechanical_truth",
                passed=exists == expected,
                detail=f"cited={cited} exists={exists} expected={expected}",
            )
        )

        decoy_ok = _path_exists_in_tree(workspace, case.decoy_path)
        if code in (CellCode.T_P, CellCode.F_P):
            results.append(
                ValidationResult(
                    case_id=case.case_id,
                    cell_code=code.value,
                    check="decoy_exists",
                    passed=decoy_ok,
                    detail=case.decoy_path,
                )
            )

    return results
