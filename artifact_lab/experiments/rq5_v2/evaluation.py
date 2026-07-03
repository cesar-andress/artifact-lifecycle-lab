"""Post-run evaluation hooks for factorial runs."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

from artifact_lab.experiments.rq5_v2.models import FactorialCase, FactorialRunResult
from artifact_lab.ingest.git_utils import run_git


def _git_metrics(workspace: Path) -> dict[str, int]:
    status = run_git(["git", "status", "--porcelain"], cwd=workspace, timeout=60)
    files = len([ln for ln in status.stdout.splitlines() if ln.strip()]) if status.returncode == 0 else 0
    diff = run_git(["git", "diff", "--numstat", "HEAD"], cwd=workspace, timeout=60)
    patch = 0
    if diff.returncode == 0:
        for line in diff.stdout.splitlines():
            parts = line.split("\t")
            if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                patch += int(parts[0]) + int(parts[1])
    return {"files_modified": files, "patch_size": patch}


def _path_touched(workspace: Path, path: str) -> bool:
    if not path:
        return False
    diff = run_git(["git", "diff", "--name-only", "HEAD"], cwd=workspace, timeout=60)
    if diff.returncode != 0:
        return False
    names = diff.stdout
    base = path.rstrip("/").split("/")[-1]
    return path in names or base in names


def evaluate_factorial_run(
    *,
    case: FactorialCase,
    cell_code: str,
    workspace: Path,
    result: FactorialRunResult,
    run_tests: bool = True,
    test_timeout: int = 600,
) -> FactorialRunResult:
    """Enrich result with git metrics and optional test execution."""
    metrics = _git_metrics(workspace)
    result.files_modified = metrics["files_modified"]

    cell = case.get_cell(cell_code)
    result.anchor_path_touched = _path_touched(workspace, cell.cited_anchor)
    result.decoy_path_touched = _path_touched(workspace, case.decoy_path)

    if run_tests and case.test_command:
        started = time.perf_counter()
        test_root = workspace
        if case.execution_cwd and case.execution_cwd not in (".", ""):
            test_root = workspace / case.execution_cwd
        try:
            proc = subprocess.run(
                case.test_command,
                cwd=test_root,
                shell=True,
                capture_output=True,
                text=True,
                timeout=test_timeout,
            )
            result.tests_passing = proc.returncode == 0
            result.compilation_success = True
            if not result.tests_passing and result.error_message == "":
                result.error_message = (proc.stderr or proc.stdout or "")[:500]
        except subprocess.TimeoutExpired:
            result.tests_passing = False
            result.error_message = result.error_message or "test_timeout"
        result.execution_time_seconds += time.perf_counter() - started

    result.success = bool(result.tests_passing) and result.files_modified > 0
    return result
