"""Preregistered dependency setup for Phase 0 MINOR_SETUP cases (infrastructure only)."""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from io import StringIO
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text

ALLOWED_SETUP_COMMANDS = frozenset(
    {
        "npm install",
        "npm ci",
        "yarn install",
        "pnpm install",
    }
)
DEFAULT_SETUP_TIMEOUT = 600
CLASSIFICATION_READY = "READY"
CLASSIFICATION_MINOR_SETUP = "MINOR_SETUP"


@dataclass(frozen=True)
class CaseSetupSpec:
    case_id: str
    repository: str
    classification: str
    setup_command: str | None
    execution_cwd: str


@dataclass(frozen=True)
class SetupRunResult:
    case_id: str
    setup_command: str
    execution_cwd: str
    exit_code: int
    runtime_seconds: float
    stderr_excerpt: str
    ok: bool


def setup_root(*, workspace: Path, execution_cwd: str) -> Path:
    if execution_cwd in (".", ""):
        return workspace
    return workspace / execution_cwd


def select_setup_command(*, root: Path) -> str | None:
    """Choose preregistered install command from lockfiles in execution_cwd."""
    if not root.is_dir():
        return None
    if (root / "pnpm-lock.yaml").is_file():
        return "pnpm install"
    if (root / "yarn.lock").is_file():
        return "yarn install"
    if (root / "package-lock.json").is_file():
        return "npm ci"
    if (root / "package.json").is_file():
        return "npm install"
    return None


def infer_setup_command_from_paths(*, paths: set[str], execution_cwd: str) -> str | None:
    prefix = "" if execution_cwd in (".", "") else f"{execution_cwd}/"
    if any(p == f"{prefix}pnpm-lock.yaml" or p.endswith("/pnpm-lock.yaml") for p in paths):
        if execution_cwd not in (".", "") and f"{prefix}pnpm-lock.yaml" in paths:
            return "pnpm install"
        if "pnpm-lock.yaml" in paths:
            return "pnpm install"
    if any(p == f"{prefix}yarn.lock" or p.endswith("/yarn.lock") for p in paths):
        if f"{prefix}yarn.lock" in paths or (execution_cwd == "." and "yarn.lock" in paths):
            return "yarn install"
    if any(p == f"{prefix}package-lock.json" for p in paths) or (
        execution_cwd == "." and "package-lock.json" in paths
    ):
        return "npm ci"
    if any(p == f"{prefix}package.json" for p in paths) or (
        execution_cwd == "." and "package.json" in paths
    ):
        return "npm install"
    return None


def build_case_setup_spec(
    *,
    case_id: str,
    repository: str,
    classification: str,
    execution_cwd: str,
    workspace: Path | None = None,
    paths: set[str] | None = None,
) -> CaseSetupSpec:
    cmd: str | None = None
    if classification == CLASSIFICATION_MINOR_SETUP:
        if workspace is not None:
            cmd = select_setup_command(root=setup_root(workspace=workspace, execution_cwd=execution_cwd))
        elif paths is not None:
            cmd = infer_setup_command_from_paths(paths=paths, execution_cwd=execution_cwd)
    return CaseSetupSpec(
        case_id=case_id,
        repository=repository,
        classification=classification,
        setup_command=cmd,
        execution_cwd=execution_cwd,
    )


def run_case_setup(
    *,
    case_id: str,
    workspace: Path,
    setup_command: str,
    execution_cwd: str,
    timeout: int = DEFAULT_SETUP_TIMEOUT,
) -> SetupRunResult:
    if setup_command not in ALLOWED_SETUP_COMMANDS:
        raise ValueError(f"setup command not preregistered: {setup_command}")
    root = setup_root(workspace=workspace, execution_cwd=execution_cwd)
    started = time.perf_counter()
    try:
        proc = subprocess.run(
            setup_command,
            cwd=root,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        elapsed = time.perf_counter() - started
        excerpt = (proc.stderr or proc.stdout or "")[:400]
        return SetupRunResult(
            case_id=case_id,
            setup_command=setup_command,
            execution_cwd=execution_cwd,
            exit_code=proc.returncode,
            runtime_seconds=round(elapsed, 3),
            stderr_excerpt=excerpt,
            ok=proc.returncode == 0,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = time.perf_counter() - started
        excerpt = ((exc.stderr or "") if isinstance(exc.stderr, str) else "")[:400]
        return SetupRunResult(
            case_id=case_id,
            setup_command=setup_command,
            execution_cwd=execution_cwd,
            exit_code=-1,
            runtime_seconds=round(elapsed, 3),
            stderr_excerpt=excerpt or "setup timeout",
            ok=False,
        )


def write_setup_log(*, path: Path, rows: list[SetupRunResult]) -> None:
    buffer = StringIO()
    fields = (
        "case_id",
        "setup_command",
        "execution_cwd",
        "exit_code",
        "runtime_seconds",
        "stderr_excerpt",
        "ok",
    )
    buffer.write(",".join(fields) + "\n")
    for row in rows:
        buffer.write(
            ",".join(
                [
                    row.case_id,
                    row.setup_command,
                    row.execution_cwd,
                    str(row.exit_code),
                    f"{row.runtime_seconds:.3f}",
                    f'"{row.stderr_excerpt.replace(chr(34), chr(39))}"',
                    str(row.ok),
                ]
            )
            + "\n"
        )
    atomic_write_text(path, buffer.getvalue())
