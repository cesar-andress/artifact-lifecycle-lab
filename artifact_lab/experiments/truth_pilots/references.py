"""Mechanical reference extraction from instruction file text."""

from __future__ import annotations

import re
from dataclasses import dataclass

from artifact_lab.protocol.detector import safe_normalize_path

REFERENCE_TYPES = ("path", "directory", "command", "script_name", "dependency")

SKIP_PREFIXES = ("http://", "https://", "mailto:", "#", "javascript:")

BACKTICK_PATH = re.compile(
    r"`([^`\n]+(?:\.(?:py|md|mdc|ts|tsx|js|jsx|yaml|yml|json|toml|sh|rs|go)|/)[^`\n]*)`"
)
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
BARE_PATH = re.compile(
    r"(?<![\w/.])([\w./-]+\.(?:py|md|mdc|ts|tsx|js|jsx|yaml|yml|json|toml|sh|rs|go))(?![\w.])"
)
DIR_BACKTICK = re.compile(r"`([^`\n]+/)`")
DIR_BARE = re.compile(r"(?:^|\s)([\w][\w./-]*/)(?:\s|$)", re.MULTILINE)
BASH_BLOCK = re.compile(r"```(?:bash|sh|shell|zsh)?\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
INLINE_CMD = re.compile(r"(?:^|\n)\s*(?:npm run|make|pytest|python -m|cargo|go run|pnpm|yarn)\s+([^\n`]+)", re.MULTILINE)
PIP_INSTALL = re.compile(r"\bpip install(?:\s+-[\w]+)*\s+([\w\[\].\-]+)")
NPM_INSTALL = re.compile(r"\bnpm (?:install|i)\s+(?:--[\w-]+\s+)*(@?[\w/@.-]+)")
POETRY_ADD = re.compile(r"\bpoetry add\s+([\w\[\].\-]+)")
SCRIPT_REF = re.compile(
    r"(?<![\w.])([\w./-]+\.(?:py|sh))(?![\w.])|"
    r"`([^`\n]+\.(?:py|sh))`"
)
RUN_SCRIPT = re.compile(r"\b(?:python|bash|sh|\./)\s+([\w./-]+\.(?:py|sh))\b")


@dataclass(frozen=True)
class ExtractedReference:
    reference_type: str
    reference_text: str
    context: str


def _clean_candidate(text: str) -> str | None:
    candidate = text.strip().strip("\"'<>")
    if not candidate or any(candidate.startswith(p) for p in SKIP_PREFIXES):
        return None
    if " " in candidate and not candidate.endswith("/"):
        return None
    norm = safe_normalize_path(candidate)
    return norm


def _add_unique(refs: list[ExtractedReference], seen: set[tuple[str, str]], ref: ExtractedReference) -> None:
    key = (ref.reference_type, ref.reference_text)
    if key in seen:
        return
    seen.add(key)
    refs.append(ref)


def extract_references(text: str) -> list[ExtractedReference]:
    refs: list[ExtractedReference] = []
    seen: set[tuple[str, str]] = set()

    for match in BACKTICK_PATH.finditer(text):
        norm = _clean_candidate(match.group(1))
        if norm:
            _add_unique(
                refs,
                seen,
                ExtractedReference(
                    reference_type="path" if not norm.endswith("/") else "directory",
                    reference_text=norm,
                    context=match.group(0)[:120],
                ),
            )

    for match in MD_LINK.finditer(text):
        norm = _clean_candidate(match.group(1))
        if norm:
            _add_unique(
                refs,
                seen,
                ExtractedReference(
                    reference_type="path" if not norm.endswith("/") else "directory",
                    reference_text=norm,
                    context=match.group(0)[:120],
                ),
            )

    for match in BARE_PATH.finditer(text):
        norm = _clean_candidate(match.group(1))
        if norm and not norm.startswith("www."):
            _add_unique(
                refs,
                seen,
                ExtractedReference(reference_type="path", reference_text=norm, context=match.group(0)[:120]),
            )

    for match in DIR_BACKTICK.finditer(text):
        norm = _clean_candidate(match.group(1))
        if norm:
            _add_unique(
                refs,
                seen,
                ExtractedReference(reference_type="directory", reference_text=norm, context=match.group(0)[:120]),
            )

    for match in DIR_BARE.finditer(text):
        norm = _clean_candidate(match.group(1))
        if norm and norm.count("/") >= 1:
            _add_unique(
                refs,
                seen,
                ExtractedReference(reference_type="directory", reference_text=norm, context=match.group(0)[:120]),
            )

    for block in BASH_BLOCK.finditer(text):
        block_text = block.group(1)
        for line in block_text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            _add_unique(
                refs,
                seen,
                ExtractedReference(reference_type="command", reference_text=line[:200], context="bash_block"),
            )

    for match in INLINE_CMD.finditer(text):
        cmd = match.group(0).strip()
        _add_unique(
            refs,
            seen,
            ExtractedReference(reference_type="command", reference_text=cmd[:200], context=cmd[:120]),
        )

    for pattern in (PIP_INSTALL, NPM_INSTALL, POETRY_ADD):
        for match in pattern.finditer(text):
            dep = match.group(1).strip()
            if dep:
                _add_unique(
                    refs,
                    seen,
                    ExtractedReference(
                        reference_type="dependency",
                        reference_text=dep,
                        context=match.group(0)[:120],
                    ),
                )

    for match in SCRIPT_REF.finditer(text):
        raw = match.group(1) or match.group(2)
        if not raw:
            continue
        norm = _clean_candidate(raw)
        if norm and norm.endswith((".py", ".sh")):
            _add_unique(
                refs,
                seen,
                ExtractedReference(
                    reference_type="script_name",
                    reference_text=norm,
                    context=match.group(0)[:120],
                ),
            )

    for match in RUN_SCRIPT.finditer(text):
        norm = _clean_candidate(match.group(1))
        if norm:
            _add_unique(
                refs,
                seen,
                ExtractedReference(
                    reference_type="script_name",
                    reference_text=norm,
                    context=match.group(0)[:120],
                ),
            )

    return refs
