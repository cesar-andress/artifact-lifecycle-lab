"""Workspace preparation for factorial cells."""

from __future__ import annotations

import shutil
from contextlib import contextmanager
from pathlib import Path

from artifact_lab.experiments.rq5_v2.factors import CellCode
from artifact_lab.experiments.rq5_v2.models import FactorialCase
from artifact_lab.ingest.git_utils import clone_bare, remove_clone, run_git
from artifact_lab.store.blobs import BlobStore


def apply_cell_instruction(
    *,
    workspace: Path,
    case: FactorialCase,
    cell_code: str,
    blob_store: BlobStore,
) -> None:
    """Write or remove instruction file for factorial cell."""
    instruction = workspace / case.instruction_path
    if CellCode(cell_code) == CellCode.N:
        if instruction.exists():
            instruction.unlink()
        return

    cell = case.get_cell(cell_code)
    if not cell.instruction_blob_sha:
        raise ValueError(f"cell {cell_code} missing instruction blob for case {case.case_id}")

    instruction.parent.mkdir(parents=True, exist_ok=True)
    instruction.write_bytes(blob_store.get_text(cell.instruction_blob_sha))


@contextmanager
def prepared_factorial_workspace(
    *,
    case: FactorialCase,
    cell_code: str,
    scratch_dir: Path,
    blob_store: BlobStore,
    clone_timeout: int = 180,
):
    """Clone repo at commit and apply factorial instruction treatment."""
    scratch_dir = scratch_dir.resolve()
    workspace = scratch_dir / f"rq5v2_{case.case_id}_{cell_code.replace('+', '_')}"
    clone_path = scratch_dir / f"rq5v2_clone_{case.repo_id}"

    if workspace.exists():
        shutil.rmtree(workspace)
    if clone_path.exists():
        shutil.rmtree(clone_path)

    clone_bare(case.repo_url, clone_path, timeout=clone_timeout)
    try:
        checkout = run_git(
            ["git", "worktree", "add", "--detach", str(workspace), case.commit_sha],
            cwd=clone_path,
            timeout=clone_timeout,
        )
        if checkout.returncode != 0:
            raise RuntimeError(checkout.stderr.strip() or "git worktree add failed")

        apply_cell_instruction(
            workspace=workspace,
            case=case,
            cell_code=cell_code,
            blob_store=blob_store,
        )
        yield workspace.resolve()
    finally:
        run_git(["git", "worktree", "remove", "--force", str(workspace)], cwd=clone_path, timeout=60)
        remove_clone(clone_path)
