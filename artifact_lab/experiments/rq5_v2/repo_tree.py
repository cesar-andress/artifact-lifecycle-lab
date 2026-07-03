"""Cached git tree lookup for case construction and audits."""

from __future__ import annotations

from pathlib import Path

from artifact_lab.ingest.git_utils import clone_bare, list_paths_at_commit


class RepoTreeCache:
    """Bare-clone cache keyed by repo_id; paths fetched per commit_sha."""

    def __init__(
        self,
        *,
        scratch_dir: Path,
        clone_timeout: int = 180,
        clone_prefix: str = "rq5v2_tree",
    ) -> None:
        self.scratch_dir = scratch_dir.resolve()
        self.clone_timeout = clone_timeout
        self.clone_prefix = clone_prefix
        self._paths: dict[tuple[str, str], set[str]] = {}

    def _clone_path(self, repo_id: str) -> Path:
        return self.scratch_dir / f"{self.clone_prefix}_{repo_id}"

    def paths_at(self, *, repo_id: str, repo_url: str, commit_sha: str) -> set[str]:
        key = (repo_id, commit_sha)
        if key in self._paths:
            return self._paths[key]

        clone_path = self._clone_path(repo_id)
        if not clone_path.exists():
            clone_bare(repo_url, clone_path, timeout=self.clone_timeout)

        paths = list_paths_at_commit(clone_path, commit_sha, timeout=self.clone_timeout)
        if not paths:
            paths = list_paths_at_commit(clone_path, "HEAD", timeout=self.clone_timeout)
        self._paths[key] = paths
        return paths
