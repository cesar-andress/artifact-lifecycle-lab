"""Path matching against protocol detector families."""

from __future__ import annotations

import re
from functools import lru_cache

from platform.protocol.loader import load_family


def normalize_path(path: str) -> str:
    p = path.replace("\\", "/").strip()
    if p.startswith("./"):
        p = p[2:]
    if p.startswith("../") or "/../" in f"/{p}":
        raise ValueError(f"path escapes repository root: {path!r}")
    return p


def safe_normalize_path(path: str) -> str | None:
    try:
        return normalize_path(path)
    except ValueError:
        return None


def _compiled_patterns(family: str) -> tuple[list[tuple[str, re.Pattern[str]]], dict]:
    cfg = load_family(family)
    patterns = [(item["id"], re.compile(item["regex"])) for item in cfg["detector_patterns"]]
    return patterns, cfg


@lru_cache(maxsize=16)
def _family_cache(family: str) -> tuple[tuple[tuple[str, str], ...], tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    patterns, cfg = _compiled_patterns(family)
    serializable = tuple((pid, pat.pattern) for pid, pat in patterns)
    prefixes = tuple(cfg.get("exclude_path_prefixes", []))
    basenames = tuple(cfg.get("exclude_basenames", []))
    regexes = tuple(cfg.get("exclude_path_regex", []))
    return serializable, prefixes, basenames, regexes


def is_excluded(path: str, family: str) -> bool:
    _, prefixes, basenames, regexes = _family_cache(family)
    path = normalize_path(path)
    for prefix in prefixes:
        if path == prefix.rstrip("/") or path.startswith(prefix):
            return True
    base = path.rsplit("/", 1)[-1]
    if base in basenames:
        return True
    for pat in regexes:
        if re.search(pat, path):
            return True
    return False


def match_pattern_id(path: str, family: str) -> str | None:
    serializable, prefixes, basenames, regexes = _family_cache(family)
    path = normalize_path(path)
    if is_excluded(path, family):
        return None
    for pid, pattern in serializable:
        if re.search(pattern, path):
            return pid
    return None


def is_matched_path(path: str, family: str) -> bool:
    return match_pattern_id(path, family) is not None


def is_text_candidate(path: str, family: str) -> bool:
    cfg = load_family(family)
    exts = cfg.get("text_extensions") or [".md", ".mdc", ".txt", ".yaml", ".yml"]
    lower = path.lower()
    if lower.endswith(".cursorrules") or lower.endswith("/.cursorrules"):
        return True
    return any(lower.endswith(ext) for ext in exts)
