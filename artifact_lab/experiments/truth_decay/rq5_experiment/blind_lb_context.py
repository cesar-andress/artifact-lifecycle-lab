"""Pinned-snapshot repository context for blind LB packets."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from artifact_lab.ingest.git_utils import blob_at_commit, clone_bare, list_paths_at_commit

SOURCE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".swift",
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hpp",
    ".rb",
    ".php",
    ".cs",
    ".scala",
    ".m",
    ".mm",
}
DOC_NAMES = {
    "readme.md",
    "readme.rst",
    "contributing.md",
    "agents.md",
    "claude.md",
    "makefile",
    "package.json",
    "pyproject.toml",
    "cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "composer.json",
    "gemfile",
    "cmakelists.txt",
}
CONFIG_SUFFIXES = {
    ".toml",
    ".yaml",
    ".yml",
    ".json",
    ".ini",
    ".cfg",
    ".config",
}


@dataclass
class RepoSnapshotContext:
    available: bool
    reason: str = ""
    paths: list[str] = field(default_factory=list)
    tree_excerpt: list[str] = field(default_factory=list)
    neighbor_paths: list[str] = field(default_factory=list)
    nearby_docs: list[str] = field(default_factory=list)
    nearby_configs: list[str] = field(default_factory=list)
    verification_command: str | None = None
    verification_evidence: str = ""
    is_software_repository: bool = False
    software_signals: list[str] = field(default_factory=list)
    reference_path_aliases: list[str] = field(default_factory=list)
    file_excerpts: list[dict[str, str]] = field(default_factory=list)
    clone_path: Path | None = None


class BlindRepoCache:
    def __init__(self, scratch_dir: Path, *, clone_timeout: int = 300) -> None:
        self.scratch_dir = scratch_dir.resolve()
        self.scratch_dir.mkdir(parents=True, exist_ok=True)
        self.clone_timeout = clone_timeout
        self._paths: dict[tuple[str, str], set[str]] = {}

    def clone_path(self, repo_id: str) -> Path:
        return self.scratch_dir / f"rq5_blind_tree_{repo_id}"

    def ensure_clone(self, *, repo_id: str, repo_url: str) -> Path:
        dest = self.clone_path(repo_id)
        if not dest.exists():
            clone_bare(repo_url, dest, timeout=self.clone_timeout)
        return dest

    def paths_at(self, *, repo_id: str, repo_url: str, commit_sha: str) -> set[str]:
        key = (repo_id, commit_sha)
        if key in self._paths:
            return self._paths[key]
        clone = self.ensure_clone(repo_id=repo_id, repo_url=repo_url)
        paths = list_paths_at_commit(clone, commit_sha, timeout=self.clone_timeout)
        self._paths[key] = paths
        return paths

    def read_text(
        self, *, repo_id: str, repo_url: str, commit_sha: str, path: str, max_bytes: int = 8000
    ) -> str | None:
        clone = self.ensure_clone(repo_id=repo_id, repo_url=repo_url)
        raw = blob_at_commit(clone, commit_sha, path, timeout=60)
        if raw is None:
            return None
        if len(raw) > max_bytes:
            raw = raw[:max_bytes]
        return raw.decode("utf-8", errors="replace")


def _parent_prefix(path: str) -> str:
    if "/" not in path:
        return ""
    return path.rsplit("/", 1)[0]


def _anchor_candidates(anchor: str) -> list[str]:
    a = anchor.strip()
    out = [a]
    if a.startswith("/"):
        out.append(a[1:])
    if a.endswith("/"):
        out.append(a.rstrip("/"))
    if a.startswith("cd "):
        out.append(a[3:].strip())
    return list(dict.fromkeys(out))


def resolve_reference_paths(paths: set[str], anchor: str) -> list[str]:
    """Map an anchor citation to zero or more concrete tree paths (aliases, not existence claims)."""
    cands = _anchor_candidates(anchor)
    hits: list[str] = []
    for p in sorted(paths):
        for c in cands:
            c_stripped = c.rstrip("/")
            if not c_stripped:
                continue
            if p == c_stripped or p.startswith(c_stripped + "/"):
                hits.append(p)
                break
            if c_stripped.startswith("@") and c_stripped in p:
                # package name citation — soft match on path segment
                if c_stripped.split("/")[-1] in p.split("/"):
                    hits.append(p)
                    break
    # Cap
    return hits[:40]


def detect_verification_command(
    cache: BlindRepoCache,
    *,
    repo_id: str,
    repo_url: str,
    commit_sha: str,
    paths: set[str],
) -> tuple[str | None, str]:
    """Infer a real verification command from pinned files. Never invent."""
    lower_map = {p.lower(): p for p in paths}

    def read(path_key: str) -> str | None:
        real = lower_map.get(path_key)
        if not real:
            return None
        return cache.read_text(
            repo_id=repo_id, repo_url=repo_url, commit_sha=commit_sha, path=real, max_bytes=20000
        )

    # package.json scripts
    pkg = read("package.json")
    if pkg:
        try:
            data = json.loads(pkg)
            scripts = data.get("scripts") or {}
            for key in ("test", "check", "lint", "build"):
                if key in scripts and isinstance(scripts[key], str) and scripts[key].strip():
                    # Prefer package manager agnostic form.
                    return f"npm run {key}", f"package.json scripts.{key}"
        except json.JSONDecodeError:
            pass

    makefile = read("makefile") or read("Makefile".lower())
    # Makefile path may be exact "Makefile"
    for p in paths:
        if p.split("/")[-1].lower() == "makefile":
            makefile = cache.read_text(
                repo_id=repo_id, repo_url=repo_url, commit_sha=commit_sha, path=p, max_bytes=20000
            )
            if makefile:
                if re.search(r"(?m)^test\s*:", makefile):
                    return "make test", f"{p} target test"
                if re.search(r"(?m)^check\s*:", makefile):
                    return "make check", f"{p} target check"
            break

    if "go.mod" in lower_map:
        return "go test ./...", "go.mod present"
    if "cargo.toml" in lower_map:
        return "cargo test", "Cargo.toml present"
    if "pom.xml" in lower_map:
        return "mvn test", "pom.xml present"
    if any(p.endswith("build.gradle") or p.endswith("build.gradle.kts") for p in lower_map):
        return "gradle test", "Gradle build file present"
    if "pyproject.toml" in lower_map or "pytest.ini" in lower_map or "setup.cfg" in lower_map:
        return "pytest", "Python test config present"
    if any(p.endswith("_test.go") or p.endswith(".test.ts") or p.endswith(".test.js") for p in paths):
        # Evidence of tests exists but command unknown
        return None, "test files present; command not identified from manifests"
    return None, "no verification command identified from pinned manifests"


def detect_software_repository(paths: set[str]) -> tuple[bool, list[str]]:
    signals: list[str] = []
    source_count = 0
    for p in paths:
        low = p.lower()
        name = low.split("/")[-1]
        suffix = Path(low).suffix
        if suffix in SOURCE_EXTENSIONS:
            source_count += 1
        if name in DOC_NAMES or low in DOC_NAMES:
            signals.append(f"manifest_or_doc:{name}")
    if source_count >= 5:
        signals.append(f"source_files:{source_count}")
    if source_count >= 5 or any(s.startswith("manifest_or_doc:package.json") for s in signals) or any(
        x in {p.lower() for p in paths}
        for x in ("go.mod", "cargo.toml", "pyproject.toml", "pom.xml")
    ):
        return True, signals[:12]
    # Mostly markdown skill packs
    md = sum(1 for p in paths if p.lower().endswith(".md"))
    if md > 0 and source_count < 5:
        signals.append(f"markdown_heavy:md={md},source={source_count}")
        return False, signals
    return source_count > 0, signals


def build_tree_excerpt(paths: set[str], focus_paths: list[str], *, limit: int = 60) -> list[str]:
    if not paths:
        return []
    prefixes: set[str] = set()
    for fp in focus_paths:
        prefixes.add(_parent_prefix(fp))
        parts = fp.split("/")
        for i in range(1, min(len(parts), 4)):
            prefixes.add("/".join(parts[:i]))
    # Always include top-level listing
    top = sorted({p.split("/")[0] for p in paths})[:25]
    selected: list[str] = []
    for p in sorted(paths):
        parent = _parent_prefix(p)
        if parent in prefixes or p in focus_paths or p.split("/")[0] in top[:8]:
            selected.append(p)
        if len(selected) >= limit:
            break
    # Ensure focus paths included
    for fp in focus_paths[:20]:
        if fp not in selected:
            selected.append(fp)
    return selected[:limit]


def classify_neighbors(paths: set[str], focus_paths: list[str]) -> tuple[list[str], list[str], list[str]]:
    parents = {_parent_prefix(p) for p in focus_paths if _parent_prefix(p)}
    neighbors: list[str] = []
    docs: list[str] = []
    configs: list[str] = []
    for p in sorted(paths):
        parent = _parent_prefix(p)
        name = p.split("/")[-1].lower()
        suffix = Path(p).suffix.lower()
        if parent in parents and p not in focus_paths:
            neighbors.append(p)
        if name in DOC_NAMES or name.startswith("readme"):
            docs.append(p)
        if suffix in CONFIG_SUFFIXES or name in {
            "makefile",
            "dockerfile",
            "tsconfig.json",
            "webpack.config.js",
        }:
            configs.append(p)
    return neighbors[:25], docs[:15], configs[:15]


def build_repo_context(
    cache: BlindRepoCache,
    *,
    repo_id: str,
    repo_url: str,
    commit_sha: str,
    anchor: str,
    instruction_path: str,
) -> RepoSnapshotContext:
    try:
        paths = cache.paths_at(repo_id=repo_id, repo_url=repo_url, commit_sha=commit_sha)
    except Exception as exc:  # noqa: BLE001 — surface as unavailable context
        return RepoSnapshotContext(available=False, reason=f"clone_or_tree_failed:{exc}")

    if not paths:
        return RepoSnapshotContext(available=False, reason="empty_tree_at_commit")

    focus = resolve_reference_paths(paths, anchor)
    # Always treat instruction path as a focus for neighborhood context.
    if instruction_path in paths and instruction_path not in focus:
        focus = [instruction_path, *focus]

    is_sw, signals = detect_software_repository(paths)
    ver_cmd, ver_ev = detect_verification_command(
        cache, repo_id=repo_id, repo_url=repo_url, commit_sha=commit_sha, paths=paths
    )
    tree = build_tree_excerpt(paths, focus)
    neighbors, docs, configs = classify_neighbors(paths, focus)

    # File excerpts: instruction neighbors + small config/docs near focus (redacted later).
    excerpts: list[dict[str, str]] = []
    candidates = []
    for p in focus[:5] + neighbors[:5] + docs[:3] + configs[:3]:
        if p not in candidates:
            candidates.append(p)
    for p in candidates[:10]:
        text = cache.read_text(
            repo_id=repo_id, repo_url=repo_url, commit_sha=commit_sha, path=p, max_bytes=2500
        )
        if text is None:
            continue
        # Neutral caption — never claim missing.
        excerpts.append(
            {
                "alias": f"snapshot_file_{len(excerpts)+1}",
                "original_path_internal": p,  # stripped before rater emit
                "content": text[:2000],
            }
        )

    return RepoSnapshotContext(
        available=True,
        paths=sorted(paths)[:5000],
        tree_excerpt=tree,
        neighbor_paths=neighbors,
        nearby_docs=docs,
        nearby_configs=configs,
        verification_command=ver_cmd,
        verification_evidence=ver_ev,
        is_software_repository=is_sw,
        software_signals=signals,
        reference_path_aliases=focus,
        file_excerpts=excerpts,
        clone_path=cache.clone_path(repo_id),
    )


def alias_tree_paths(paths: list[str], redact_paths_fn, anchors: list[str]) -> list[str]:
    """Present tree paths with sensitive anchors replaced; other paths may stay as structure."""
    out: list[str] = []
    for p in paths:
        red = redact_paths_fn(p, anchors)
        # If still looks like a real unique path containing banned anchor fragments, alias fully.
        out.append(red)
    return out
