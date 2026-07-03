"""Commit-aware false/decoy path derivation and repairability scoring."""

from __future__ import annotations

import re
from dataclasses import dataclass

from artifact_lab.experiments.truth_pilots.verify_refs import _path_exists

FALSE_STEM_ALTERNATIVES: tuple[str, ...] = (
    "manager",
    "client",
    "helper",
    "service",
    "handler",
    "config",
    "setup",
    "api",
    "core",
    "adapter",
    "controller",
    "worker",
    "builder",
    "parser",
    "validator",
    "factory",
    "runner",
    "gateway",
    "provider",
    "registry",
    "store",
    "module",
    "component",
    "resource",
    "context",
    "session",
    "profile",
    "settings",
    "options",
    "schema",
    "model",
    "entity",
    "repository",
    "dispatcher",
    "resolver",
    "formatter",
    "renderer",
    "compiler",
    "loader",
    "writer",
    "reader",
    "monitor",
    "tracker",
    "scheduler",
    "executor",
    "processor",
    "transformer",
    "collector",
    "aggregator",
    "connector",
    "bridge",
    "proxy",
    "wrapper",
    "facade",
)

STEM_SWAP_PAIRS: tuple[tuple[str, str], ...] = (
    ("service", "manager"),
    ("utils", "helpers"),
    ("util", "helper"),
    ("test", "spec"),
    ("tests", "specs"),
    ("api", "client"),
    ("auth", "session"),
    ("config", "settings"),
    ("version", "release"),
    ("build", "setup"),
    ("replay", "runner"),
    ("shared", "common"),
    ("dashboard", "panel"),
    ("template", "layout"),
    ("instruction", "guide"),
    ("release", "deploy"),
)

ARTIFICIAL_MARKERS = re.compile(r"(?:^|[/_])(?:missing|null|fake|dummy|placeholder|nonexistent)\b", re.I)


@dataclass(frozen=True)
class PathDerivationResult:
    false_path: str
    decoy_path: str
    repairability_score: int
    repairability_reason: str


@dataclass(frozen=True)
class _PathParts:
    parent: str
    stem: str
    ext: str
    full_name: str

    @property
    def full_path(self) -> str:
        if self.parent:
            return f"{self.parent}/{self.full_name}"
        return self.full_name


def _normalize_path(path: str) -> str:
    return path.strip().strip("`").strip("/")


def _split_path(path: str) -> _PathParts:
    path = _normalize_path(path)
    if "/" in path:
        parent, name = path.rsplit("/", 1)
    else:
        parent, name = "", path
    if "." in name and not name.startswith("."):
        stem, ext = name.rsplit(".", 1)
        return _PathParts(parent=parent, stem=stem, ext=f".{ext}", full_name=name)
    return _PathParts(parent=parent, stem=name, ext="", full_name=name)


def _join_path(parent: str, name: str) -> str:
    return f"{parent}/{name}" if parent else name


def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            curr.append(min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost))
        prev = curr
    return prev[-1]


def _path_in_tree(path: str, tree_paths: set[str]) -> bool:
    return _path_exists(path.strip().strip("/"), tree_paths)


def _same_directory(path: str, parent: str) -> bool:
    path = path.strip().strip("/")
    if parent:
        if not path.startswith(f"{parent}/"):
            return False
        return "/" not in path[len(parent) + 1 :]
    return "/" not in path


def _is_plausible_false_name(true_stem: str, false_stem: str) -> bool:
    if not false_stem or false_stem.lower() == true_stem.lower():
        return False
    if _levenshtein(true_stem.lower(), false_stem.lower()) <= 1:
        return False
    if ARTIFICIAL_MARKERS.search(false_stem):
        return False
    return True


def _candidate_false_stems(parts: _PathParts) -> list[str]:
    stems: list[str] = []
    seen: set[str] = set()

    def add(stem: str) -> None:
        key = stem.lower()
        if key in seen:
            return
        if _is_plausible_false_name(parts.stem, stem):
            seen.add(key)
            stems.append(stem)

    for alt in FALSE_STEM_ALTERNATIVES:
        add(alt)

    for left, right in STEM_SWAP_PAIRS:
        low = parts.stem.lower()
        if left in low:
            add(low.replace(left, right, 1))
        if right in low:
            add(low.replace(right, left, 1))

    for sep in ("_", "-", "."):
        if sep in parts.stem:
            prefix, suffix = parts.stem.rsplit(sep, 1)
            if prefix:
                for alt in FALSE_STEM_ALTERNATIVES[:12]:
                    add(f"{prefix}{sep}{alt}")

    return stems


def derive_false_path(true_path: str, tree_paths: set[str]) -> str | None:
    """
    Return a syntactically plausible sibling path that does not resolve at commit.

    Same directory when possible, same extension, no artificial markers.
    """
    true_path = true_path.strip().strip("`")
    if not true_path or not _path_in_tree(true_path, tree_paths):
        return None

    parts = _split_path(true_path)
    candidates: list[str] = []

    for stem in _candidate_false_stems(parts):
        name = f"{stem}{parts.ext}" if parts.ext else stem
        candidate = _join_path(parts.parent, name)
        if candidate == true_path:
            continue
        if ".missing" in candidate.lower() or candidate.lower().endswith("-missing"):
            continue
        if _path_in_tree(candidate, tree_paths):
            continue
        candidates.append(candidate)

    if not candidates:
        return None

    candidates.sort(
        key=lambda p: (
            _levenshtein(parts.stem, _split_path(p).stem),
            len(p),
        )
    )
    return candidates[0]


def _decoy_score(true_path: str, candidate: str, parts: _PathParts) -> tuple[int, int, int]:
    cand = _split_path(candidate)
    score = 0
    if parts.ext and cand.ext == parts.ext:
        score += 40
    elif not parts.ext and not cand.ext:
        score += 20
    if parts.parent == cand.parent:
        score += 30
    elif parts.parent and cand.parent.startswith(parts.parent.rsplit("/", 1)[0]):
        score += 10
    dist = _levenshtein(parts.stem, cand.stem)
    if 2 <= dist <= 8:
        score += 15
    if candidate.endswith(".md") and true_path.endswith(".md"):
        score += 10
    depth_penalty = abs(candidate.count("/") - true_path.count("/"))
    return score, depth_penalty, dist


def derive_decoy_path(
    true_path: str,
    tree_paths: set[str],
    *,
    exclude: frozenset[str] | None = None,
) -> str | None:
    """Pick an existing file distinct from the true anchor, preferably same directory/extension."""
    true_path = true_path.strip().strip("`")
    blocked = {true_path.strip().strip("/")} | {p.strip().strip("/") for p in (exclude or frozenset())}
    parts = _split_path(true_path)

    candidates: list[str] = []
    for path in sorted(tree_paths):
        norm = path.strip().strip("/")
        if norm in blocked:
            continue
        if norm == parts.full_path:
            continue
        if parts.parent and not _same_directory(norm, parts.parent):
            continue
        if ARTIFICIAL_MARKERS.search(norm):
            continue
        candidates.append(norm)

    if not candidates and parts.parent:
        parent_prefix = f"{parts.parent}/"
        grandparent = parts.parent.rsplit("/", 1)[0] if "/" in parts.parent else ""
        for path in sorted(tree_paths):
            norm = path.strip().strip("/")
            if norm in blocked or norm == parts.full_path:
                continue
            if norm.startswith(parent_prefix):
                continue
            if grandparent and not norm.startswith(f"{grandparent}/"):
                continue
            if "/" in norm[len(grandparent) + 1 :] if grandparent else norm:
                # allow one level up siblings only
                if grandparent:
                    rest = norm[len(grandparent) + 1 :]
                    if rest.count("/") > 1:
                        continue
            candidates.append(norm)

    if not candidates:
        for path in sorted(tree_paths):
            norm = path.strip().strip("/")
            if norm in blocked or norm == parts.full_path:
                continue
            if parts.ext and not norm.endswith(parts.ext):
                continue
            candidates.append(norm)

    if not candidates:
        return None

    ranked = sorted(
        candidates,
        key=lambda p: (
            -_decoy_score(true_path, p, parts)[0],
            _decoy_score(true_path, p, parts)[1],
            p,
        ),
    )
    return ranked[0]


def score_repairability(
    true_path: str,
    false_path: str,
    tree_paths: set[str],
) -> tuple[int, str]:
    """
    Score repairability on integer scale 0–3.

    0 = impossible, 1 = difficult, 2 = moderate, 3 = easy
    """
    true_parts = _split_path(true_path)
    false_parts = _split_path(false_path)
    reasons: list[str] = []
    points = 0.0

    if true_parts.ext and true_parts.ext == false_parts.ext:
        points += 0.8
        reasons.append("same extension")
    if true_parts.parent == false_parts.parent:
        points += 1.0
        reasons.append("same-directory sibling")

    dist = _levenshtein(true_parts.stem.lower(), false_parts.stem.lower())
    if 2 <= dist <= 6:
        points += 1.0
        reasons.append("similar basename")
    elif dist <= 8:
        points += 0.5
        reasons.append("moderately similar basename")
    else:
        reasons.append("distant basename")

    prefix = true_parts.stem.split("_")[0].split("-")[0][:4].lower()
    if prefix and len(prefix) >= 3:
        pattern_matches = sum(
            1
            for p in tree_paths
            if _same_directory(p, true_parts.parent)
            and prefix in _split_path(p).stem.lower()
        )
        if pattern_matches >= 2:
            points += 0.6
            reasons.append("shared naming pattern nearby")

    depth = true_path.count("/")
    if depth <= 2:
        points += 0.4
        reasons.append("shallow path depth")
    elif depth >= 5:
        points -= 0.3
        reasons.append("deep path")

    repo_size = len(tree_paths)
    if repo_size <= 800:
        points += 0.5
        reasons.append("small repository")
    elif repo_size >= 8000:
        points -= 0.5
        reasons.append("large repository")

    if true_parts.parent:
        sibling_count = sum(1 for p in tree_paths if _same_directory(p, true_parts.parent))
        if sibling_count >= 5:
            points += 0.4
            reasons.append("dense sibling directory")

    score = int(max(0, min(3, round(points))))
    if not reasons:
        reasons.append("minimal signals")
    return score, "; ".join(reasons)


def derive_case_paths(
    true_path: str,
    tree_paths: set[str],
) -> PathDerivationResult | None:
    true_path = _normalize_path(true_path)
    if not true_path or not _path_in_tree(true_path, tree_paths):
        return None
    false_path = derive_false_path(true_path, tree_paths)
    if not false_path:
        return None
    decoy = derive_decoy_path(true_path, tree_paths, exclude=frozenset({false_path}))
    if not decoy:
        return None
    repair_score, repair_reason = score_repairability(true_path, false_path, tree_paths)
    return PathDerivationResult(
        false_path=false_path,
        decoy_path=decoy,
        repairability_score=repair_score,
        repairability_reason=repair_reason,
    )
