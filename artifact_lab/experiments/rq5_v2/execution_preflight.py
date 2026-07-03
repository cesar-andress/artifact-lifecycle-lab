"""Execution preflight: cwd resolution, command normalization, and smoke tests (no agents)."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass, replace
from pathlib import Path

from artifact_lab.experiments.rq5_v2.execution_viability_checks import (
    BARE_RUNNER_NAMES,
    detect_ecosystem,
    infer_go_module_root,
)
from artifact_lab.ingest.git_utils import blob_at_commit, clone_bare, remove_clone, run_git

DEFAULT_SMOKE_TIMEOUT = 120
CARGO_SMOKE_TIMEOUT = 300
LAB_ROOT_MARKERS = ("artifact-lifecycle-lab", "artifact_lifecycle_lab")

MARKER_FILES = {
    "node": ("package.json",),
    "python": ("pyproject.toml", "setup.py", "setup.cfg"),
    "go": ("go.mod",),
    "rust": ("Cargo.toml",),
}

CLASSIFICATIONS = ("READY", "MINOR_SETUP", "REQUIRES_MANUAL_FIX", "DROP")


@dataclass(frozen=True)
class PackageScripts:
    path: str
    scripts: dict[str, str]


@dataclass(frozen=True)
class PreflightPlan:
    raw_test_command: str
    normalized_test_command: str
    cwd: str
    ecosystem: str
    normalization_notes: str


@dataclass(frozen=True)
class SmokePreflightResult:
    case_id: str
    repository: str
    raw_test_command: str
    normalized_test_command: str
    cwd: str
    classification: str
    exit_code: int
    stderr_excerpt: str
    runtime: float
    failure_class: str
    recommended_action: str
    long_compile: bool
    timed_out: bool


def _marker_dirs(paths: set[str], markers: tuple[str, ...]) -> list[str]:
    dirs: list[str] = []
    for path in paths:
        name = path.split("/")[-1]
        if name in markers:
            parent = str(Path(path).parent) if "/" in path else "."
            dirs.append("." if parent == "" else parent)
    if not dirs and any(m in paths for m in markers):
        dirs.append(".")
    return sorted(set(dirs), key=lambda d: (d.count("/"), d))


def _has_tests_dir(paths: set[str], cwd: str) -> bool:
    prefix = "" if cwd == "." else f"{cwd}/"
    return any(
        p == f"{prefix}tests"
        or p.startswith(f"{prefix}tests/")
        or p.endswith("/test")
        or "/test/" in p
        or p.endswith("_test.go")
        for p in paths
    )


def infer_cwd(*, test_command: str, paths: set[str]) -> str:
    """Infer working directory relative to repository root for test_command."""
    ecosystem = detect_ecosystem(test_command, paths)
    markers = MARKER_FILES.get(ecosystem, MARKER_FILES["python"])
    candidates = _marker_dirs(paths, markers)

    if ecosystem == "go":
        go_root = infer_go_module_root(paths)
        if go_root:
            return go_root
        return candidates[0] if candidates else "."

    if ecosystem == "rust":
        if "Cargo.toml" in paths:
            return "."
        cargo_dirs = _marker_dirs(paths, ("Cargo.toml",))
        if cargo_dirs:
            return cargo_dirs[0]
        return "."

    if ecosystem == "node":
        cmd = test_command.lower()
        if candidates:
            if len(candidates) == 1:
                return candidates[0]
            with_tests = [c for c in candidates if _has_tests_dir(paths, c)]
            if with_tests:
                return sorted(with_tests, key=lambda d: d.count("/"))[0]
            return sorted(candidates, key=lambda d: d.count("/"))[0]
        return "."

    if ecosystem == "python":
        cmd = test_command.lower()
        py_dirs = _marker_dirs(paths, MARKER_FILES["python"])
        if py_dirs:
            with_tests = [c for c in py_dirs if _has_tests_dir(paths, c)]
            if with_tests:
                return sorted(with_tests, key=lambda d: d.count("/"))[0]
            return sorted(py_dirs, key=lambda d: d.count("/"))[0]
        return "."

    return candidates[0] if candidates else "."


def _read_package_scripts(repo_dir: Path, commit_sha: str, cwd: str) -> PackageScripts | None:
    rel = "package.json" if cwd in (".", "") else f"{cwd}/package.json"
    raw = blob_at_commit(repo_dir, commit_sha, rel)
    if raw is None:
        return None
    try:
        data = json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    scripts = data.get("scripts") or {}
    if not isinstance(scripts, dict):
        scripts = {}
    return PackageScripts(path=rel, scripts={str(k): str(v) for k, v in scripts.items()})


def _package_scripts_from_file(package_json: Path) -> PackageScripts | None:
    if not package_json.is_file():
        return None
    try:
        data = json.loads(package_json.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    scripts = data.get("scripts") or {}
    if not isinstance(scripts, dict):
        scripts = {}
    rel = "." if package_json.parent == package_json.parent.anchor else str(package_json.parent.name)
    return PackageScripts(path=str(package_json.relative_to(package_json.parents[1]) if len(package_json.parts) > 1 else "package.json"), scripts={str(k): str(v) for k, v in scripts.items()})


def _has_script(scripts: PackageScripts | None, name: str = "test") -> bool:
    return bool(scripts and name in scripts.scripts and scripts.scripts[name].strip())


def pytest_isolated_command(*, extra_args: str = "") -> str:
    args = extra_args.strip()
    base = "PYTHONNOUSERSITE=1 python -m pytest --confcutdir=. --rootdir=."
    return f"{base} {args}".strip()


def normalize_test_command(
    *,
    test_command: str,
    paths: set[str],
    cwd: str,
    package_scripts: PackageScripts | None = None,
) -> PreflightPlan:
    """Normalize invalid bare runners to ecosystem entrypoints."""
    raw = (test_command or "").strip()
    eco = detect_ecosystem(raw, paths)
    notes: list[str] = []
    normalized = raw

    if not raw:
        return PreflightPlan(raw, raw, cwd, eco, "empty command")

    bare = raw.split()[0]
    bare_lower = bare.lower()

    if bare_lower in {"vitest", "jest"} or raw in {"Vitest", "Jest"}:
        if _has_script(package_scripts):
            pm = "yarn" if "yarn" in raw.lower() else "npm"
            normalized = f"{pm} test"
            notes.append(f"{bare} -> {normalized} (package.json test script)")
        else:
            runner = bare_lower if bare_lower in {"vitest", "jest"} else bare.lower()
            normalized = f"npx {runner}"
            notes.append(f"{bare} -> {normalized}")

    elif bare_lower == "pytest" or raw.lower() == "pytest":
        normalized = pytest_isolated_command()
        notes.append("pytest -> isolated python -m pytest with confcutdir/rootdir")

    elif raw.lower().startswith("pytest ") and "python -m pytest" not in raw.lower():
        rest = raw.split(None, 1)[1] if len(raw.split()) > 1 else ""
        normalized = pytest_isolated_command(extra_args=rest)
        notes.append("pytest args -> isolated python -m pytest")

    elif raw.lower() in {"go test", "go"} or (bare_lower == "go" and "test" in raw.lower()):
        normalized = "go test ./..."
        notes.append("go test -> go test ./... from module root")

    elif raw.lower() in {"cargo test", "cargo"}:
        normalized = "cargo test"
        notes.append("cargo test from workspace root")

    elif raw.lower() == "yarn test":
        if _has_script(package_scripts):
            normalized = "yarn test"
            notes.append("yarn test script present")
        else:
            notes.append("yarn test rejected: no test script in package.json")
            normalized = raw

    elif raw.lower() == "npm test":
        if _has_script(package_scripts):
            normalized = "npm test"
            notes.append("npm test script present")
        else:
            notes.append("npm test rejected: no test script in package.json")
            normalized = raw

    elif bare in BARE_RUNNER_NAMES and len(raw.split()) == 1:
        notes.append(f"bare runner `{raw}` could not be fully normalized")

    return PreflightPlan(
        raw_test_command=raw,
        normalized_test_command=normalized,
        cwd=cwd,
        ecosystem=eco,
        normalization_notes="; ".join(notes) if notes else "unchanged",
    )


def classify_smoke_outcome(
    *,
    plan: PreflightPlan,
    exit_code: int,
    stdout: str,
    stderr: str,
    runtime: float,
    timed_out: bool,
    long_compile: bool,
    clone_ok: bool,
) -> tuple[str, str, str]:
    """Return (classification, failure_class, recommended_action)."""
    out = (stdout or "") + (stderr or "")
    out_lower = out.lower()

    if not clone_ok:
        return "DROP", "clone failed", "exclude: repository cannot be checked out"

    if not plan.raw_test_command:
        return "DROP", "invalid test command", "exclude: empty test command"

    bare = plan.raw_test_command.split()[0]
    if bare in {"Vitest", "Jest"} and plan.normalized_test_command == plan.raw_test_command:
        return "DROP", "invalid test command", "exclude: bare runner without package script"

    if plan.normalization_notes.endswith("no test script in package.json"):
        return "DROP", "invalid test command", "exclude: npm/yarn test script missing"

    if timed_out and long_compile:
        return "MINOR_SETUP", "long compile", "allow 300s cargo timeout or narrow test target"

    if timed_out:
        return "REQUIRES_MANUAL_FIX", "timeout", "increase timeout or choose faster smoke target"

    if "not found" in out_lower or "command not found" in out_lower or "enoent" in out_lower:
        if plan.normalized_test_command != plan.raw_test_command or plan.normalized_test_command.startswith(
            ("npm ", "yarn ", "pnpm ", "npx ", "go ", "cargo ", "make ")
        ):
            return "MINOR_SETUP", "missing dependency", "install deps before agent execution"
        return "REQUIRES_MANUAL_FIX", "missing test runner", "install runner or fix normalized command"

    if any(marker in out_lower for marker in LAB_ROOT_MARKERS) and "collected 0 items" in out_lower:
        return "REQUIRES_MANUAL_FIX", "wrong working directory", "pytest picked up lab config; cwd guard required"

    if "collected 0 items" in out_lower or "no tests ran" in out_lower:
        return "REQUIRES_MANUAL_FIX", "invalid test command", "command finds zero tests at cwd"

    if "cannot find main module" in out_lower or "go: go.mod file not found" in out_lower:
        return "REQUIRES_MANUAL_FIX", "wrong working directory", "run from Go module root"

    if "missing script" in out_lower and "test" in out_lower:
        return "DROP", "invalid test command", "package.json lacks test script"

    if exit_code == 0:
        return "READY", "", "proceed to Phase 0/1 execution"

    if any(tok in out_lower for tok in ("passed", "failed", "test result", "running", "test session")):
        return "READY", "", "tests executed (non-zero exit acceptable for smoke)"

    if "npm err!" in out_lower or "error:" in out_lower:
        if "install" in out_lower or "module not found" in out_lower:
            return "MINOR_SETUP", "missing dependency", "run install before agent execution"
        return "REQUIRES_MANUAL_FIX", "actual test failure after valid execution", "environment ran; review test output"

    if runtime > 0 and exit_code != 127:
        return "MINOR_SETUP", "missing dependency", "install deps or add setup step before runs"

    return "REQUIRES_MANUAL_FIX", "unknown", "manual review required"


def _compile_progressing(output: str, *, elapsed: float) -> bool:
    if "compiling" not in output.lower():
        return False
    return elapsed < CARGO_SMOKE_TIMEOUT


def run_smoke_command(
    *,
    command: str,
    cwd: Path,
    ecosystem: str,
    timeout: int = DEFAULT_SMOKE_TIMEOUT,
) -> tuple[int, str, str, float, bool, bool]:
    """Run normalized test command; return exit, stdout, stderr, runtime, timed_out, long_compile."""
    env = os.environ.copy()
    env["PYTHONNOUSERSITE"] = "1"
    env.pop("PYTEST_ADDOPTS", None)
    lab_root = str(Path.cwd().resolve())
    existing_pp = env.get("PYTHONPATH", "")
    if existing_pp:
        parts = [p for p in existing_pp.split(os.pathsep) if p and lab_root not in p]
        if parts:
            env["PYTHONPATH"] = os.pathsep.join(parts)
        else:
            env.pop("PYTHONPATH", None)

    effective_timeout = CARGO_SMOKE_TIMEOUT if ecosystem == "rust" else timeout
    started = time.perf_counter()
    timed_out = False
    long_compile = False
    stdout = ""
    stderr = ""

    try:
        proc = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=effective_timeout,
            env=env,
        )
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        elapsed = time.perf_counter() - started
        combined = stdout + stderr
        if proc.returncode != 0 and _compile_progressing(combined, elapsed=elapsed):
            long_compile = True
        return proc.returncode, stdout, stderr, elapsed, timed_out, long_compile
    except subprocess.TimeoutExpired as exc:
        elapsed = time.perf_counter() - started
        stdout = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        stderr = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
        combined = stdout + stderr
        long_compile = ecosystem == "rust" and _compile_progressing(combined, elapsed=elapsed)
        return -1, stdout, stderr, elapsed, True, long_compile


@dataclass
class _Checkout:
    workspace: Path
    clone_path: Path


class CheckoutCache:
    """Reuse bare clones; detach worktrees per commit."""

    def __init__(self, scratch_dir: Path, clone_timeout: int = 180) -> None:
        self.scratch_dir = scratch_dir.resolve()
        self.clone_timeout = clone_timeout
        self._clone_paths: dict[str, Path] = {}

    def checkout(
        self,
        *,
        repo_url: str,
        repo_id: str,
        commit_sha: str,
    ) -> _Checkout:
        self.scratch_dir.mkdir(parents=True, exist_ok=True)
        clone_path = self._clone_paths.get(repo_id)
        if clone_path is None or not clone_path.exists():
            clone_path = self.scratch_dir / f"preflight_clone_{repo_id}"
            if not clone_path.exists():
                clone_bare(repo_url, clone_path, timeout=self.clone_timeout)
            self._clone_paths[repo_id] = clone_path

        workspace = self.scratch_dir / f"preflight_ws_{repo_id}_{commit_sha[:8]}"
        if workspace.exists():
            run_git(["git", "worktree", "remove", "--force", str(workspace)], cwd=clone_path, timeout=60)
        checkout = run_git(
            ["git", "worktree", "add", "--detach", str(workspace), commit_sha],
            cwd=clone_path,
            timeout=self.clone_timeout,
        )
        if checkout.returncode != 0:
            raise RuntimeError(checkout.stderr.strip() or "git worktree add failed")
        return _Checkout(workspace=workspace, clone_path=clone_path)

    def release(self, checkout: _Checkout) -> None:
        run_git(
            ["git", "worktree", "remove", "--force", str(checkout.workspace)],
            cwd=checkout.clone_path,
            timeout=60,
        )


def checkout_case_workspace(
    *,
    repo_url: str,
    repo_id: str,
    commit_sha: str,
    scratch_dir: Path,
    clone_timeout: int = 180,
    cache: CheckoutCache | None = None,
) -> _Checkout:
    if cache is not None:
        return cache.checkout(repo_url=repo_url, repo_id=repo_id, commit_sha=commit_sha)
    scratch_dir = scratch_dir.resolve()
    clone_path = scratch_dir / f"preflight_clone_{repo_id}"
    workspace = scratch_dir / f"preflight_ws_{repo_id}_{commit_sha[:8]}"
    if workspace.exists():
        shutil.rmtree(workspace, ignore_errors=True)
    if not clone_path.exists():
        clone_bare(repo_url, clone_path, timeout=clone_timeout)
    checkout = run_git(
        ["git", "worktree", "add", "--detach", str(workspace), commit_sha],
        cwd=clone_path,
        timeout=clone_timeout,
    )
    if checkout.returncode != 0:
        raise RuntimeError(checkout.stderr.strip() or "git worktree add failed")
    return _Checkout(workspace=workspace, clone_path=clone_path)


def cleanup_checkout(checkout: _Checkout, *, cache: CheckoutCache | None = None) -> None:
    if cache is not None:
        cache.release(checkout)
        return
    run_git(["git", "worktree", "remove", "--force", str(checkout.workspace)], cwd=checkout.clone_path, timeout=60)
    remove_clone(checkout.clone_path)


def run_case_preflight(
    *,
    case_id: str,
    repository: str,
    repo_url: str,
    repo_id: str,
    commit_sha: str,
    test_command: str,
    paths: set[str],
    scratch_dir: Path,
    skip_smoke: bool = False,
    clone_timeout: int = 180,
    checkout_cache: CheckoutCache | None = None,
) -> SmokePreflightResult:
    """Full preflight for one factorial case."""
    cwd_rel = infer_cwd(test_command=test_command, paths=paths)
    clone_ok = True
    package_scripts: PackageScripts | None = None

    try:
        checkout = checkout_case_workspace(
            repo_url=repo_url,
            repo_id=repo_id,
            commit_sha=commit_sha,
            scratch_dir=scratch_dir,
            clone_timeout=clone_timeout,
            cache=checkout_cache,
        )
        package_scripts = _read_package_scripts(checkout.clone_path, commit_sha, cwd_rel)
        if package_scripts is None:
            ws_pkg = checkout.workspace / cwd_rel / "package.json" if cwd_rel != "." else checkout.workspace / "package.json"
            package_scripts = _package_scripts_from_file(ws_pkg)
    except Exception as exc:  # noqa: BLE001 — record and classify
        clone_ok = False
        plan = normalize_test_command(test_command=test_command, paths=paths, cwd=cwd_rel, package_scripts=None)
        classification, failure_class, action = classify_smoke_outcome(
            plan=plan,
            exit_code=127,
            stdout="",
            stderr=str(exc)[:300],
            runtime=0.0,
            timed_out=False,
            long_compile=False,
            clone_ok=False,
        )
        return SmokePreflightResult(
            case_id=case_id,
            repository=repository,
            raw_test_command=test_command,
            normalized_test_command=plan.normalized_test_command,
            cwd=cwd_rel,
            classification=classification,
            exit_code=127,
            stderr_excerpt=str(exc)[:300],
            runtime=0.0,
            failure_class=failure_class,
            recommended_action=action,
            long_compile=False,
            timed_out=False,
        )

    plan = normalize_test_command(
        test_command=test_command,
        paths=paths,
        cwd=cwd_rel,
        package_scripts=package_scripts,
    )

    if skip_smoke:
        classification = "MINOR_SETUP" if plan.normalization_notes != "unchanged" else "REQUIRES_MANUAL_FIX"
        if "rejected" in plan.normalization_notes:
            classification = "DROP"
        return SmokePreflightResult(
            case_id=case_id,
            repository=repository,
            raw_test_command=test_command,
            normalized_test_command=plan.normalized_test_command,
            cwd=cwd_rel,
            classification=classification,
            exit_code=-1,
            stderr_excerpt=plan.normalization_notes,
            runtime=0.0,
            failure_class="" if classification == "READY" else "not executed",
            recommended_action="run smoke preflight",
            long_compile=False,
            timed_out=False,
        )

    test_root = checkout.workspace if cwd_rel in (".", "") else checkout.workspace / cwd_rel
    exit_code, stdout, stderr, runtime, timed_out, long_compile = run_smoke_command(
        command=plan.normalized_test_command,
        cwd=test_root,
        ecosystem=plan.ecosystem,
    )
    classification, failure_class, action = classify_smoke_outcome(
        plan=plan,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        runtime=runtime,
        timed_out=timed_out,
        long_compile=long_compile,
        clone_ok=clone_ok,
    )

    try:
        cleanup_checkout(checkout, cache=checkout_cache)
    except OSError:
        pass

    excerpt = (stderr or stdout or "")[:400]
    return SmokePreflightResult(
        case_id=case_id,
        repository=repository,
        raw_test_command=test_command,
        normalized_test_command=plan.normalized_test_command,
        cwd=cwd_rel,
        classification=classification,
        exit_code=exit_code,
        stderr_excerpt=excerpt,
        runtime=round(runtime, 3),
        failure_class=failure_class,
        recommended_action=action,
        long_compile=long_compile,
        timed_out=timed_out,
    )


def repair_case_from_preflight(case, result: SmokePreflightResult):
    """Return FactorialCase with repaired execution fields (does not mutate prompts)."""
    from artifact_lab.experiments.rq5_v2.models import FactorialCase

    return replace(
        case,
        test_command=result.normalized_test_command,
        execution_cwd=result.cwd,
    )
