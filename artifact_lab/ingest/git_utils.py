"""Git helpers for ephemeral bare clones."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from artifact_lab.ingest.git_activity import record_git_subprocess

GIT_ENV = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "Never"}


def run_git(
    args: list[str],
    *,
    cwd: Path | None = None,
    timeout: int | None = None,
) -> subprocess.CompletedProcess[str]:
    t0 = time.perf_counter()
    proc = subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        env=GIT_ENV,
    )
    elapsed = time.perf_counter() - t0
    stdout_bytes = len(proc.stdout.encode("utf-8")) if proc.stdout else 0
    record_git_subprocess(args, elapsed_s=elapsed, stdout_bytes=stdout_bytes)
    return proc


def parse_github_url(url: str) -> tuple[str, str] | None:
    m = re.match(r"https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$", url.strip())
    return (m.group(1), m.group(2)) if m else None


from artifact_lab.contracts.repo_id import normalize_repo_url, repo_id_from_url


def clone_bare(url: str, dest: Path, *, timeout: int = 300) -> None:
    """Bare partial clone (never shallow)."""
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["git", "clone", "--bare", "--filter=blob:none", url, str(dest)]
    proc = run_git(cmd, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(f"git clone failed: {proc.stderr.strip() or proc.stdout.strip()}")


def remove_clone(dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)


def list_head_paths(repo_dir: Path, *, timeout: int = 300) -> set[str]:
    """List paths present in the HEAD tree only (fast adoption-census inspection)."""
    proc = run_git(["git", "ls-tree", "-r", "--name-only", "HEAD"], cwd=repo_dir, timeout=timeout)
    if proc.returncode != 0:
        return set()
    return {line.strip() for line in proc.stdout.splitlines() if line.strip()}


def list_all_paths(repo_dir: Path, *, timeout: int = 300) -> set[str]:
    """List paths ever touched in repository history plus HEAD tree."""
    proc = run_git(
        ["git", "log", "--all", "--pretty=format:", "--name-only", "--diff-filter=AMRD"],
        cwd=repo_dir,
        timeout=timeout,
    )
    paths: set[str] = set()
    if proc.returncode == 0:
        for line in proc.stdout.splitlines():
            line = line.strip()
            if line:
                paths.add(line)
    paths.update(list_head_paths(repo_dir, timeout=timeout))
    return paths


def log_follow(
    repo_dir: Path,
    path: str,
    *,
    timeout: int = 180,
) -> list[dict[str, str]]:
    proc = run_git(
        ["git", "log", "--all", "--follow", "--format=%H|%at|%an|%ae", "--", path],
        cwd=repo_dir,
        timeout=timeout,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        return []
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        sha, ts, author, email = line.split("|", 3)
        if sha in seen:
            continue
        seen.add(sha)
        rows.append({"commit_sha": sha, "commit_ts": ts, "author_name": author, "author_email": email})
    rows.reverse()
    return rows


def deletion_commits(repo_dir: Path, path: str, *, timeout: int = 180) -> set[str]:
    proc = run_git(
        ["git", "log", "--all", "--follow", "--diff-filter=D", "--format=%H", "--", path],
        cwd=repo_dir,
        timeout=timeout,
    )
    if proc.returncode != 0:
        return set()
    return {line.strip() for line in proc.stdout.splitlines() if line.strip()}


def blob_at_commit(repo_dir: Path, commit_sha: str, path: str, *, timeout: int = 60) -> bytes | None:
    proc = run_git(["git", "show", f"{commit_sha}:{path}"], cwd=repo_dir, timeout=timeout)
    if proc.returncode != 0:
        return None
    return proc.stdout.encode("utf-8")


def ts_to_datetime(ts: str) -> datetime:
    return datetime.fromtimestamp(int(ts), tz=timezone.utc)
