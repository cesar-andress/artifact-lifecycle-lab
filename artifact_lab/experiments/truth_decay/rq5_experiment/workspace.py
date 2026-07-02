"""Workspace preparation for RQ5 experiment runs."""

from __future__ import annotations

import shutil
import subprocess
from contextlib import contextmanager
from pathlib import Path

from artifact_lab.experiments.truth_decay.rq5_experiment.models import ExperimentCase
from artifact_lab.ingest.git_utils import clone_bare, remove_clone, run_git
from artifact_lab.store.blobs import BlobStore


@contextmanager
def prepared_workspace(
    *,
    case: ExperimentCase,
    condition: str,
    scratch_dir: Path,
    blob_store: BlobStore,
    clone_timeout: int = 180,
):
    """Clone repo at task commit and swap instruction blob for condition A or B."""
    workspace = scratch_dir / f"rq5_{case.case_id}_{condition}"
    clone_path = scratch_dir / f"rq5_clone_{case.repo_id}"
    if workspace.exists():
        shutil.rmtree(workspace)
    if clone_path.exists():
        shutil.rmtree(clone_path)

    clone_bare(case.repo_url, clone_path, timeout=clone_timeout)
    try:
        checkout = run_git(
            ["git", "worktree", "add", "--detach", str(workspace), case.task_commit_sha],
            cwd=clone_path,
            timeout=clone_timeout,
        )
        if checkout.returncode != 0:
            raise RuntimeError(checkout.stderr.strip() or "git worktree add failed")

        blob_sha = case.condition_a_blob_sha if condition == "A" else case.condition_b_blob_sha
        instruction = workspace / case.instruction_path
        instruction.parent.mkdir(parents=True, exist_ok=True)
        instruction.write_bytes(blob_store.get_text(blob_sha))

        yield workspace
    finally:
        run_git(["git", "worktree", "remove", "--force", str(workspace)], cwd=clone_path, timeout=60)
        remove_clone(clone_path)


def write_instruction_to_workspace(
    *,
    workspace: Path,
    case: ExperimentCase,
    condition: str,
    blob_store: BlobStore,
) -> Path:
    """Write instruction file for an already-materialized workspace (tests)."""
    blob_sha = case.condition_a_blob_sha if condition == "A" else case.condition_b_blob_sha
    instruction = workspace / case.instruction_path
    instruction.parent.mkdir(parents=True, exist_ok=True)
    instruction.write_bytes(blob_store.get_text(blob_sha))
    return instruction


def run_shell_command(command: str, *, cwd: Path, timeout: int = 600) -> tuple[int, float]:
    import time

    started = time.perf_counter()
    proc = subprocess.run(
        command,
        cwd=cwd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    elapsed = time.perf_counter() - started
    return proc.returncode, elapsed
