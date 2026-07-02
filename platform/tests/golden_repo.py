"""Build a deterministic synthetic repository for golden tests."""

from __future__ import annotations

import subprocess
from pathlib import Path


def _git(args: list[str], cwd: Path, env: dict | None = None) -> None:
    import os

    merged = os.environ.copy()
    merged["TZ"] = "UTC"
    if env:
        merged.update(env)
    proc = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, env=merged)
    assert proc.returncode == 0, proc.stderr


def build_golden_bare_repo(tmp_path: Path) -> Path:
    """Repository with AGENTS.md and .cursor/rules/style.md at fixed dates."""
    repo = tmp_path / "golden.git"
    _git(["init", "--bare", str(repo)], tmp_path)
    work = tmp_path / "work"
    work.mkdir()
    _git(["clone", str(repo), str(work)], tmp_path)
    _git(["config", "user.email", "golden@example.com"], work)
    _git(["config", "user.name", "Golden"], work)
    branch = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=work,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    (work / "AGENTS.md").write_text("# agents v1\n")
    _git(["add", "AGENTS.md"], work)
    _git(
        ["commit", "-m", "add agents"],
        work,
        env={"GIT_AUTHOR_DATE": "2024-01-15T10:00:00", "GIT_COMMITTER_DATE": "2024-01-15T10:00:00"},
    )

    rules = work / ".cursor" / "rules"
    rules.mkdir(parents=True)
    (rules / "style.md").write_text("# style rules\n")
    _git(["add", ".cursor/rules/style.md"], work)
    _git(
        ["commit", "-m", "add cursor rules"],
        work,
        env={"GIT_AUTHOR_DATE": "2024-02-01T10:00:00", "GIT_COMMITTER_DATE": "2024-02-01T10:00:00"},
    )

    (work / "AGENTS.md").write_text("# agents v2\n")
    _git(["add", "AGENTS.md"], work)
    _git(
        ["commit", "-m", "update agents"],
        work,
        env={"GIT_AUTHOR_DATE": "2024-03-15T10:00:00", "GIT_COMMITTER_DATE": "2024-03-15T10:00:00"},
    )

    _git(["push", "origin", branch], work)
    return repo
