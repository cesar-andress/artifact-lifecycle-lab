"""Verify references against repository state at a specific commit."""

from __future__ import annotations

import re
from pathlib import Path

from artifact_lab.experiments.truth_pilots.references import ExtractedReference
from artifact_lab.experiments.truth_pilots.verify_refs import (
    DEPENDENCY_MANIFESTS,
    _directory_exists,
    _manifest_paths,
    _path_exists,
    _verify_command,
)
from artifact_lab.ingest.git_utils import blob_at_commit, list_paths_at_commit


class CommitTreeCache:
    """Per-repo cache of ls-tree results keyed by commit_sha."""

    def __init__(self, repo_dir: Path, *, timeout: int = 120) -> None:
        self.repo_dir = repo_dir
        self.timeout = timeout
        self._paths: dict[str, set[str]] = {}

    def paths_at(self, commit_sha: str) -> set[str]:
        if commit_sha not in self._paths:
            self._paths[commit_sha] = list_paths_at_commit(
                self.repo_dir, commit_sha, timeout=self.timeout
            )
        return self._paths[commit_sha]


def _dependency_in_manifests_at_commit(
    repo_dir: Path,
    commit_sha: str,
    dep: str,
    manifest_paths: list[str],
    *,
    timeout: int,
) -> bool:
    dep_lower = dep.lower().split("[")[0]
    for manifest in manifest_paths:
        content = blob_at_commit(repo_dir, commit_sha, manifest, timeout=timeout)
        if content is None:
            continue
        text = content.decode("utf-8", errors="replace").lower()
        if dep_lower in text:
            return True
    return False


def verify_reference_at_commit(
    ref: ExtractedReference,
    *,
    repo_dir: Path,
    commit_sha: str,
    tree_cache: CommitTreeCache | None = None,
    tree_paths: set[str] | None = None,
    timeout: int = 120,
) -> tuple[str, str]:
    if tree_paths is not None:
        paths = tree_paths
    elif tree_cache is not None:
        paths = tree_cache.paths_at(commit_sha)
    else:
        paths = list_paths_at_commit(repo_dir, commit_sha, timeout=timeout)

    if ref.reference_type in ("path", "script_name"):
        if _path_exists(ref.reference_text, paths):
            return "verified", "path exists at commit"
        return "missing", "path not in commit tree"

    if ref.reference_type == "directory":
        if _directory_exists(ref.reference_text, paths):
            return "verified", "directory prefix exists at commit"
        return "missing", "directory prefix not in commit tree"

    if ref.reference_type == "dependency":
        manifests = _manifest_paths(paths)
        if not manifests:
            return "unverifiable", "no dependency manifest at commit"
        if _dependency_in_manifests_at_commit(
            repo_dir, commit_sha, ref.reference_text, manifests, timeout=timeout
        ):
            return "verified", "dependency name found in commit manifest"
        return "missing", "dependency name not found in commit manifests"

    if ref.reference_type == "command":
        return _verify_command(ref.reference_text, paths, repo_dir, timeout=timeout)

    return "unverifiable", f"unknown reference type: {ref.reference_type}"
