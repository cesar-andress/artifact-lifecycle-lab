"""Verify extracted references against repository HEAD state."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from artifact_lab.ingest.git_utils import blob_at_commit, list_head_paths, run_git
from artifact_lab.experiments.truth_pilots.references import ExtractedReference

DEPENDENCY_MANIFESTS = (
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "Pipfile",
    "poetry.lock",
    "Cargo.toml",
    "go.mod",
)


@dataclass(frozen=True)
class ReferenceAuditRow:
    sample_id: int
    repo_id: str
    repo_url: str
    instruction_path: str
    reference_type: str
    reference_text: str
    verification_status: str
    evidence: str


def _head_paths(repo_dir: Path, *, timeout: int) -> set[str]:
    return list_head_paths(repo_dir, timeout=timeout)


def _path_exists(path: str, head_paths: set[str]) -> bool:
    if path in head_paths:
        return True
    return any(p.startswith(path.rstrip("/") + "/") for p in head_paths)


def _directory_exists(path: str, head_paths: set[str]) -> bool:
    prefix = path if path.endswith("/") else path + "/"
    return any(p.startswith(prefix) or p + "/" == prefix for p in head_paths) or _path_exists(path.rstrip("/"), head_paths)


def _manifest_paths(head_paths: set[str]) -> list[str]:
    return [p for p in head_paths if p.split("/")[-1] in DEPENDENCY_MANIFESTS]


def _dependency_in_manifests(
    repo_dir: Path,
    dep: str,
    manifest_paths: list[str],
    *,
    timeout: int,
) -> bool:
    dep_lower = dep.lower().split("[")[0]
    for manifest in manifest_paths:
        content = blob_at_commit(repo_dir, "HEAD", manifest, timeout=timeout)
        if content is None:
            continue
        text = content.decode("utf-8", errors="replace").lower()
        if dep_lower in text:
            return True
    return False


def _verify_command(reference_text: str, head_paths: set[str], repo_dir: Path, *, timeout: int) -> tuple[str, str]:
    text = reference_text.strip()
    make_match = re.match(r"make\s+([\w-]+)", text)
    if make_match:
        if not any(p.endswith("Makefile") or p == "Makefile" for p in head_paths):
            return "unverifiable", "Makefile not present at HEAD"
        return "unverifiable", "make target not mechanically resolved in pilot"

    script_match = re.search(r"([\w./-]+\.(?:py|sh))", text)
    if script_match:
        script = script_match.group(1).lstrip("./")
        if script in head_paths or _path_exists(script, head_paths):
            return "verified", f"script present at HEAD: {script}"
        return "missing", f"script not at HEAD: {script}"

    return "unverifiable", "command not mapped to filesystem check in pilot"


def verify_reference(
    ref: ExtractedReference,
    *,
    repo_dir: Path,
    head_paths: set[str] | None = None,
    timeout: int = 120,
) -> tuple[str, str]:
    paths = head_paths if head_paths is not None else _head_paths(repo_dir, timeout=timeout)

    if ref.reference_type in ("path", "script_name"):
        if _path_exists(ref.reference_text, paths):
            return "verified", "path exists at HEAD"
        return "missing", "path not in HEAD tree"

    if ref.reference_type == "directory":
        if _directory_exists(ref.reference_text, paths):
            return "verified", "directory prefix exists at HEAD"
        return "missing", "directory prefix not in HEAD tree"

    if ref.reference_type == "dependency":
        manifests = _manifest_paths(paths)
        if not manifests:
            return "unverifiable", "no dependency manifest at HEAD"
        if _dependency_in_manifests(repo_dir, ref.reference_text, manifests, timeout=timeout):
            return "verified", "dependency name found in HEAD manifest"
        return "missing", "dependency name not found in HEAD manifests"

    if ref.reference_type == "command":
        return _verify_command(ref.reference_text, paths, repo_dir, timeout=timeout)

    return "unverifiable", f"unknown reference type: {ref.reference_type}"


def audit_references_for_sample(
    *,
    sample_id: int,
    repo_id: str,
    repo_url: str,
    instruction_path: str,
    references: list[ExtractedReference],
    repo_dir: Path,
    timeout: int = 120,
) -> list[ReferenceAuditRow]:
    head_paths = _head_paths(repo_dir, timeout=timeout)
    rows: list[ReferenceAuditRow] = []
    for ref in references:
        status, evidence = verify_reference(ref, repo_dir=repo_dir, head_paths=head_paths, timeout=timeout)
        rows.append(
            ReferenceAuditRow(
                sample_id=sample_id,
                repo_id=repo_id,
                repo_url=repo_url,
                instruction_path=instruction_path,
                reference_type=ref.reference_type,
                reference_text=ref.reference_text,
                verification_status=status,
                evidence=evidence,
            )
        )
    return rows


def commit_message(repo_dir: Path, commit_sha: str, *, timeout: int = 60) -> str:
    proc = run_git(["git", "log", "-1", "--format=%B", commit_sha], cwd=repo_dir, timeout=timeout)
    if proc.returncode != 0:
        return ""
    return proc.stdout


def commit_metadata(repo_dir: Path, commit_sha: str, *, timeout: int = 60) -> tuple[str, str, str]:
    proc = run_git(
        ["git", "log", "-1", "--format=%an|%ae|%at", commit_sha],
        cwd=repo_dir,
        timeout=timeout,
    )
    if proc.returncode != 0 or "|" not in proc.stdout:
        return "", "", ""
    name, email, ts = proc.stdout.strip().split("|", 2)
    return name, email, ts
