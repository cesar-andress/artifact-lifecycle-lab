"""Semantic path redaction for blind annotation packets.

Replaces complete path tokens only. Never substring-replaces short anchors
inside numbers, versions, or unrelated words.
"""

from __future__ import annotations

import re
from typing import Iterable

REF_TOKEN = "[[REF]]"

# Path-like spans: optional backticks, optional leading ./ or /, segments joined by /.
_PATH_SPAN_RE = re.compile(
    r"`([^`\n]{1,240})`"
    r"|(?<![A-Za-z0-9_])((?:\.{1,2}/|/)?"
    r"[A-Za-z0-9_@.+-]+(?:/[A-Za-z0-9_@.+-]+)+/?)"
    r"|(?<![A-Za-z0-9_])((?:[A-Za-z0-9_@.+-]+/)+)"  # trailing-slash dirs like 2/
)

_PATH_CONTINUATION = re.compile(r"[A-Za-z0-9_./@+-]")


def normalize_path_token(token: str) -> str:
    t = token.strip().strip("`").strip()
    return t


def _is_short_or_numeric_anchor(anchor: str) -> bool:
    core = anchor.strip("/").strip()
    if len(core) < 3:
        return True
    if core.isdigit():
        return True
    # Single-char or two-char bare names are unsafe for substring rules.
    if len(core) <= 2:
        return True
    return False


def path_matches_anchor(span: str, anchor: str) -> bool:
    """True iff span is the cited path (or a safe whole-path equivalent)."""
    s = normalize_path_token(span)
    a = normalize_path_token(anchor)
    if not s or not a:
        return False

    if _is_short_or_numeric_anchor(a):
        return s.rstrip("/") == a.rstrip("/") or s == a

    if s == a or s.rstrip("/") == a.rstrip("/"):
        return True

    # Leading-slash style anchors often appear without the leading slash in prose.
    if a.startswith("/") and (s == a[1:] or s.rstrip("/") == a[1:].rstrip("/")):
        return True
    if not a.startswith("/") and ("/" + s).rstrip("/") == a.rstrip("/"):
        return True

    # Multi-segment anchors: allow suffix match at path segment boundary.
    if "/" in a.rstrip("/"):
        a_core = a.lstrip("./")
        if s == a_core or s.endswith("/" + a_core.lstrip("/")):
            return True

    # Leading-slash file anchors like `/route.ts`: match exact basename path forms only.
    if a.startswith("/") and "/" not in a.strip("/"):
        base = a.lstrip("/")
        return s == base or s == a or s.endswith("/" + base)

    return False


def iter_path_spans(text: str) -> list[tuple[int, int, str]]:
    spans: list[tuple[int, int, str]] = []
    for m in _PATH_SPAN_RE.finditer(text):
        raw = m.group(0)
        # Prefer inner backtick content for matching, keep outer for replacement length.
        spans.append((m.start(), m.end(), raw))
    return spans


def redact_paths(text: str, anchors: Iterable[str]) -> str:
    """Replace complete path spans that match any anchor with [[REF]]."""
    anchor_list = [normalize_path_token(a) for a in anchors if normalize_path_token(a)]
    if not text or not anchor_list:
        return text

    spans = iter_path_spans(text)
    if not spans:
        # Fallback: exact whole-string occurrences of multi-segment anchors only.
        out = text
        for a in sorted(anchor_list, key=len, reverse=True):
            if _is_short_or_numeric_anchor(a):
                # Exact token with path boundaries.
                pat = re.compile(
                    rf"(?<![A-Za-z0-9_./]){re.escape(a)}(?![A-Za-z0-9_./])"
                )
                out = pat.sub(REF_TOKEN, out)
            else:
                pat = re.compile(
                    rf"(?<![A-Za-z0-9_]){re.escape(a)}(?![A-Za-z0-9_])"
                )
                out = pat.sub(REF_TOKEN, out)
        return out

    pieces: list[str] = []
    cursor = 0
    for start, end, raw in spans:
        pieces.append(text[cursor:start])
        inner = raw[1:-1] if raw.startswith("`") and raw.endswith("`") else raw
        matched = any(path_matches_anchor(inner, a) or path_matches_anchor(raw, a) for a in anchor_list)
        if matched:
            if raw.startswith("`") and raw.endswith("`"):
                pieces.append(f"`{REF_TOKEN}`")
            else:
                pieces.append(REF_TOKEN)
        else:
            pieces.append(raw)
        cursor = end
    pieces.append(text[cursor:])
    return "".join(pieces)


def redact_instruction_path_mentions(text: str, instruction_path: str) -> str:
    """Hide the instruction file's own path if it appears as a complete path span."""
    if not instruction_path:
        return text
    return redact_paths(text, [instruction_path, instruction_path.split("/")[-1]])


def assert_no_raw_anchors(text: str, anchors: Iterable[str]) -> list[str]:
    """Return anchors that still appear as complete path spans (not bare substrings)."""
    remaining: list[str] = []
    for a in anchors:
        a_n = normalize_path_token(a)
        if not a_n:
            continue
        found = False
        for _s, _e, raw in iter_path_spans(text):
            inner = raw[1:-1] if raw.startswith("`") and raw.endswith("`") else raw
            if path_matches_anchor(inner, a_n):
                remaining.append(a_n)
                found = True
                break
        if found:
            continue
        if "/" in a_n.rstrip("/") and not _is_short_or_numeric_anchor(a_n):
            pat = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(a_n)}(?![A-Za-z0-9_])")
            if pat.search(text):
                remaining.append(a_n)
    return remaining


def corruption_markers(text: str) -> list[str]:
    """Detect classic over-redaction artifacts from substring sanitizers."""
    markers: list[str] = []
    patterns = [
        (r"\d\[\[REF\]\]\d", "digit_ref_digit"),
        (r"\[\[REF\]\]\.\d", "ref_version_fragment"),
        (r"\d\[\[REF\]\]", "digit_ref"),
        (r"\[\[REF\]\]\d", "ref_digit"),
        (r"[A-Za-z]\[\[REF\]\]>", "broken_placeholder"),
    ]
    for pat, code in patterns:
        if re.search(pat, text):
            markers.append(code)
    return markers
