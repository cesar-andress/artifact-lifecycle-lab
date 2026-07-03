"""Individual checks for execution viability scoring."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from artifact_lab.experiments.task_calibration.scoring import extract_test_command_from_task

SUPPORTED_ECOSYSTEMS = frozenset({"python", "node", "go", "rust", "java", "make", "other"})

BARE_RUNNER_NAMES = frozenset(
    {"vitest", "jest", "pytest", "tox", "mvn", "gradle", "cargo", "go", "make"}
)

LOCKFILE_BY_PM = {
    "npm": ("package-lock.json", "npm-shrinkwrap.json"),
    "yarn": ("yarn.lock",),
    "pnpm": ("pnpm-lock.yaml",),
    "cargo": ("Cargo.lock",),
    "go": ("go.sum",),
    "pip": ("requirements.txt", "poetry.lock", "Pipfile.lock"),
}


@dataclass(frozen=True)
class ViabilityCheckResult:
    name: str
    score: float
    passed: bool
    detail: str


@dataclass(frozen=True)
class RepoSignals:
    clone_ok: bool
    paths: set[str]
    clone_error: str = ""


@dataclass(frozen=True)
class SmokeResult:
    install_ok: bool
    test_started: bool
    tests_executed: bool
    timed_out: bool
    missing_binary: bool
    error_snippet: str
    install_command: str
    test_cwd: str


def detect_ecosystem(test_command: str, paths: set[str]) -> str:
    cmd = test_command.lower().strip()
    if cmd.startswith("npm") or cmd.startswith("yarn") or cmd.startswith("pnpm") or cmd.startswith("npx"):
        return "node"
    if cmd.startswith("go ") or any(p.endswith("/go.mod") or p == "go.mod" for p in paths):
        return "go"
    if cmd.startswith("cargo") or "Cargo.toml" in paths:
        return "rust"
    if cmd.startswith("pytest") or cmd.startswith("tox") or "pyproject.toml" in paths or "setup.py" in paths:
        return "python"
    if cmd.startswith("mvn") or cmd.startswith("gradle"):
        return "java"
    if cmd.startswith("make"):
        return "make"
    if cmd in {"vitest", "jest"} or "vitest" in cmd or "jest" in cmd:
        return "node"
    return "other"


def infer_go_module_root(paths: set[str]) -> str | None:
    mods = sorted(p for p in paths if p.endswith("go.mod") or p == "go.mod")
    if not mods:
        return None
    if "go.mod" in mods:
        return "."
    shortest = min(mods, key=lambda p: p.count("/"))
    return str(Path(shortest).parent) if "/" in shortest else "."


def infer_install_command(*, ecosystem: str, paths: set[str], test_cwd: str = ".") -> str:
    root = test_cwd if test_cwd != "." else ""
    prefix = f"cd {root} && " if root else ""
    if ecosystem == "node":
        if "pnpm-lock.yaml" in paths:
            return f"{prefix}pnpm install --ignore-scripts"
        if "yarn.lock" in paths:
            return f"{prefix}yarn install --ignore-scripts"
        if "package.json" in paths or any(p.endswith("/package.json") for p in paths):
            return f"{prefix}npm ci --ignore-scripts || npm install --ignore-scripts"
    if ecosystem == "go":
        return f"{prefix}go mod download"
    if ecosystem == "rust" and "Cargo.toml" in paths:
        return f"{prefix}cargo fetch"
    if ecosystem == "python" and ("requirements.txt" in paths or "pyproject.toml" in paths):
        return f"{prefix}python -m pip install -q -r requirements.txt || true"
    return ""


def check_test_command_exists(test_command: str) -> ViabilityCheckResult:
    cmd = (test_command or "").strip()
    if not cmd:
        return ViabilityCheckResult("test_command_exists", 0.0, False, "empty test command")
    bare = cmd.split()[0].lower() if cmd.split() else ""
    if bare in BARE_RUNNER_NAMES and len(cmd.split()) == 1:
        return ViabilityCheckResult(
            "test_command_exists",
            0.2,
            False,
            f"bare runner `{cmd}` is not a valid shell command",
        )
    if cmd[0].isupper() and cmd.lower() in BARE_RUNNER_NAMES:
        return ViabilityCheckResult(
            "test_command_exists",
            0.15,
            False,
            f"tool name `{cmd}` must use package script (npm test / npx …)",
        )
    return ViabilityCheckResult("test_command_exists", 1.0, True, cmd)


def check_ecosystem_supported(ecosystem: str) -> ViabilityCheckResult:
    ok = ecosystem in SUPPORTED_ECOSYSTEMS
    return ViabilityCheckResult(
        "ecosystem_supported",
        1.0 if ok else 0.0,
        ok,
        ecosystem,
    )


def check_lockfile_consistency(*, ecosystem: str, paths: set[str]) -> ViabilityCheckResult:
    if ecosystem == "node":
        has_pkg = "package.json" in paths or any(p.endswith("/package.json") for p in paths)
        if not has_pkg:
            return ViabilityCheckResult("lockfile_consistency", 0.3, False, "no package.json")
        locks = [p for p in paths if p.endswith("package-lock.json") or p.endswith("yarn.lock") or p.endswith("pnpm-lock.yaml")]
        return ViabilityCheckResult(
            "lockfile_consistency",
            1.0 if locks else 0.5,
            bool(locks),
            "found lockfile" if locks else "package.json without lockfile",
        )
    if ecosystem == "go":
        ok = any(p.endswith("go.mod") for p in paths) or "go.mod" in paths
        return ViabilityCheckResult("lockfile_consistency", 1.0 if ok else 0.0, ok, "go.mod" if ok else "missing go.mod")
    if ecosystem == "rust":
        ok = "Cargo.toml" in paths
        return ViabilityCheckResult("lockfile_consistency", 1.0 if ok else 0.0, ok, "Cargo.toml" if ok else "missing")
    if ecosystem == "python":
        ok = any(p in paths for p in ("pyproject.toml", "setup.py", "requirements.txt"))
        return ViabilityCheckResult("lockfile_consistency", 1.0 if ok else 0.6, ok, "python project markers")
    return ViabilityCheckResult("lockfile_consistency", 0.7, True, "not applicable")


def check_package_manager_consistency(*, test_command: str, paths: set[str]) -> ViabilityCheckResult:
    cmd = test_command.lower()
    if cmd.startswith("yarn") and not any(p.endswith("yarn.lock") for p in paths):
        return ViabilityCheckResult("package_manager_consistency", 0.3, False, "yarn command without yarn.lock")
    if cmd.startswith("npm") and not any(
        p.endswith("package-lock.json") or p.endswith("package.json") for p in paths
    ):
        return ViabilityCheckResult("package_manager_consistency", 0.4, False, "npm command without package files")
    if cmd.startswith("pnpm") and not any(p.endswith("pnpm-lock.yaml") for p in paths):
        return ViabilityCheckResult("package_manager_consistency", 0.3, False, "pnpm without pnpm-lock.yaml")
    return ViabilityCheckResult("package_manager_consistency", 1.0, True, "consistent")


def check_clone(repo: RepoSignals) -> ViabilityCheckResult:
    if repo.clone_ok:
        return ViabilityCheckResult("clone", 1.0, True, f"{len(repo.paths)} paths indexed")
    return ViabilityCheckResult("clone", 0.0, False, repo.clone_error or "clone failed")


def check_historical_failures(*, repository: str, historical_rate: float) -> ViabilityCheckResult:
    """historical_rate: fraction of failed toolchain runs for this repo in Phase 0 (0-1)."""
    score = max(0.0, 1.0 - historical_rate)
    return ViabilityCheckResult(
        "historical_execution_failures",
        score,
        historical_rate < 0.5,
        f"phase0 toolchain failure rate={historical_rate:.2f}" if historical_rate > 0 else "no phase0 history",
    )


def score_from_smoke(smoke: SmokeResult | None) -> dict[str, ViabilityCheckResult]:
    if smoke is None:
        return {
            "deps_install": ViabilityCheckResult("deps_install", 0.5, False, "smoke not run"),
            "test_starts": ViabilityCheckResult("test_starts", 0.5, False, "smoke not run"),
            "baseline_tests_execute": ViabilityCheckResult("baseline_tests_execute", 0.5, False, "smoke not run"),
            "timeout": ViabilityCheckResult("timeout", 0.5, False, "smoke not run"),
            "missing_binaries": ViabilityCheckResult("missing_binaries", 0.5, False, "smoke not run"),
        }
    return {
        "deps_install": ViabilityCheckResult(
            "deps_install",
            1.0 if smoke.install_ok else 0.0,
            smoke.install_ok,
            smoke.install_command or "skipped",
        ),
        "test_starts": ViabilityCheckResult(
            "test_starts",
            1.0 if smoke.test_started else 0.0,
            smoke.test_started,
            smoke.error_snippet[:120],
        ),
        "baseline_tests_execute": ViabilityCheckResult(
            "baseline_tests_execute",
            1.0 if smoke.tests_executed else 0.0,
            smoke.tests_executed,
            "tests produced output" if smoke.tests_executed else smoke.error_snippet[:120],
        ),
        "timeout": ViabilityCheckResult(
            "timeout",
            0.0 if smoke.timed_out else 1.0,
            not smoke.timed_out,
            "timed out" if smoke.timed_out else "ok",
        ),
        "missing_binaries": ViabilityCheckResult(
            "missing_binaries",
            0.0 if smoke.missing_binary else 1.0,
            not smoke.missing_binary,
            "binary missing" if smoke.missing_binary else "ok",
        ),
    }


def heuristic_smoke_from_error_patterns(
    *,
    test_command: str,
    ecosystem: str,
    paths: set[str],
    historical_rate: float,
    historical_successes: int = 0,
) -> SmokeResult:
    """Estimate smoke outcomes from static signals when live smoke is disabled."""
    cmd = test_command.lower()
    missing_binary = "not found" in cmd or test_command.strip() in {"Vitest", "Jest"}
    install_cmd = infer_install_command(ecosystem=ecosystem, paths=paths)
    test_cwd = infer_go_module_root(paths) or "."
    install_ok = bool(install_cmd) or ecosystem == "python"
    test_started = not missing_binary and check_test_command_exists(test_command).passed
    tests_executed = False
    err = ""
    timed_out = False

    if ecosystem == "python" and cmd.startswith("pytest"):
        err = "heuristic: pytest may resolve wrong root without cwd guard"
        test_started = True
    if ecosystem == "go" and test_cwd == "." and not any(p == "go.mod" for p in paths):
        err = "heuristic: go test at repo root without go.mod"
        test_started = False
    if ecosystem == "node" and test_command.strip() == "Vitest":
        missing_binary = True
        test_started = False
        err = "Vitest binary not on PATH"
    if historical_successes > 0 and check_test_command_exists(test_command).passed:
        tests_executed = True
        test_started = True
        err = f"phase0 confirmed {historical_successes} successful baseline run(s)"
    if historical_rate >= 1.0 and historical_successes == 0:
        tests_executed = False
        test_started = test_started and ecosystem == "node" and cmd.startswith("npm")
    if (
        not tests_executed
        and ecosystem == "node"
        and cmd in {"npm test", "yarn test", "pnpm test"}
        and ("package.json" in paths or any(p.endswith("/package.json") for p in paths))
    ):
        test_started = True
        tests_executed = False
        err = err or "heuristic: package script likely runnable; live smoke not executed"

    return SmokeResult(
        install_ok=install_ok,
        test_started=test_started,
        tests_executed=tests_executed,
        timed_out=timed_out,
        missing_binary=missing_binary,
        error_snippet=err,
        install_command=install_cmd,
        test_cwd=test_cwd,
    )


def run_live_smoke(
    *,
    workspace: Path,
    test_command: str,
    install_command: str,
    test_timeout: int = 120,
    install_timeout: int = 180,
) -> SmokeResult:
    """Run install + test smoke in an existing worktree (no agents)."""
    install_ok = True
    err_parts: list[str] = []
    if install_command:
        try:
            proc = subprocess.run(
                install_command,
                cwd=workspace,
                shell=True,
                capture_output=True,
                text=True,
                timeout=install_timeout,
            )
            install_ok = proc.returncode == 0
            if not install_ok:
                err_parts.append((proc.stderr or proc.stdout or "")[:200])
        except subprocess.TimeoutExpired:
            install_ok = False
            err_parts.append("install timeout")

    timed_out = False
    missing_binary = False
    test_started = False
    tests_executed = False
    try:
        proc = subprocess.run(
            test_command,
            cwd=workspace,
            shell=True,
            capture_output=True,
            text=True,
            timeout=test_timeout,
        )
        test_started = True
        out = (proc.stdout or "") + (proc.stderr or "")
        tests_executed = proc.returncode == 0 or (
            "passed" in out.lower()
            or "failed" in out.lower()
            or "test session" in out.lower()
            or "running" in out.lower()
        )
        if proc.returncode != 0:
            err_parts.append(out[:200])
        if "not found" in out.lower() or "command not found" in out.lower():
            missing_binary = True
        if "collected 0 items" in out.lower():
            tests_executed = False
    except subprocess.TimeoutExpired:
        timed_out = True
        test_started = True
        err_parts.append("test timeout")

    return SmokeResult(
        install_ok=install_ok,
        test_started=test_started,
        tests_executed=tests_executed,
        timed_out=timed_out,
        missing_binary=missing_binary,
        error_snippet="; ".join(err_parts)[:300],
        install_command=install_command,
        test_cwd=str(workspace),
    )


def resolve_test_command(candidate_row: dict) -> str:
    return extract_test_command_from_task(candidate_row.get("task", ""))
