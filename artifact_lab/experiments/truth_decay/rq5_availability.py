"""Deterministic issue/task availability heuristics for RQ5 preparation."""

from __future__ import annotations

import re

# Issue-tracker cues in instruction text (no external API).
ISSUE_TEXT_PATTERNS = (
    re.compile(r"github\.com/[^/\s]+/[^/\s]+/issues", re.I),
    re.compile(r"\b(?:fixes|closes|resolves)\s+#\d+", re.I),
    re.compile(r"\bissue\s+#?\d+\b", re.I),
    re.compile(r"\bjira\.[a-z0-9.-]+\.[a-z]+\b", re.I),
    re.compile(r"\b(?:bug|defect|regression)\b", re.I),
)

# Test-task cues in instruction text.
TEST_COMMAND_PATTERNS = (
    re.compile(r"\bpytest\b", re.I),
    re.compile(r"\bnpm\s+(?:run\s+)?test\b", re.I),
    re.compile(r"\byarn\s+test\b", re.I),
    re.compile(r"\bcargo\s+test\b", re.I),
    re.compile(r"\bgo\s+test\b", re.I),
    re.compile(r"\bmake\s+test\b", re.I),
    re.compile(r"\btox\b", re.I),
    re.compile(r"\bvitest\b", re.I),
    re.compile(r"\bjest\b", re.I),
    re.compile(r"\bmvn\s+test\b", re.I),
)

TEST_PATH_PATTERN = re.compile(
    r"(?:^|[/\\])(?:tests?|__tests__|spec|test_[^/\\]+|[^/\\]+_test\.(?:py|rs|go|ts|js|tsx|jsx))(?:[/\\]|$|\.(?:py|rs|go|ts|js|tsx|jsx)$)",
    re.I,
)

SOURCE_PATH_PATTERN = re.compile(
    r"\.(?:py|rs|go|ts|tsx|js|jsx|java|kt|cs|cpp|c|h|rb|php|swift)$",
    re.I,
)

TEST_CONFIG_PATHS = frozenset(
    {
        "package.json",
        "pyproject.toml",
        "setup.py",
        "Cargo.toml",
        "go.mod",
        "Makefile",
        "tox.ini",
        "pytest.ini",
        "vitest.config.ts",
        "jest.config.js",
    }
)


def assess_issue_availability(
    *,
    snapshot_type: str,
    instruction_text: str,
    n_missing_verifiable: int,
    n_verifiable: int,
) -> tuple[bool, str]:
    """Return (available, reason) without external calls."""
    if instruction_text:
        for pattern in ISSUE_TEXT_PATTERNS:
            if pattern.search(instruction_text):
                return True, "issue_tracker_or_defect_language_in_spec"

    if snapshot_type in ("born_stale", "degraded") and n_missing_verifiable > 0:
        return True, "stale_verifiable_references_present"

    if snapshot_type == "repaired" and n_verifiable > 0:
        return True, "post_repair_integrity_context"

    if snapshot_type == "truthful" and n_verifiable > 0:
        return False, "no_stale_reference_or_issue_cue"

    return False, "no_issue_signal"


def assess_task_availability(
    *,
    instruction_text: str,
    verified_refs: list[str],
) -> tuple[bool, str]:
    """Return (available, reason) from spec text and verified reference anchors."""
    reasons: list[str] = []

    if instruction_text:
        for pattern in TEST_COMMAND_PATTERNS:
            if pattern.search(instruction_text):
                reasons.append("test_command_in_spec")
                break

    test_path = False
    source_anchor = False
    config_anchor = False
    for ref in verified_refs:
        base = ref.rstrip("/").split("/")[-1]
        if base in TEST_CONFIG_PATHS:
            config_anchor = True
        if TEST_PATH_PATTERN.search(ref):
            test_path = True
        if SOURCE_PATH_PATTERN.search(ref):
            source_anchor = True

    if test_path:
        reasons.append("verified_test_path_reference")
    if config_anchor:
        reasons.append("verified_test_config_reference")
    if source_anchor:
        reasons.append("verified_source_path_reference")

    if not verified_refs:
        return False, "no_verified_reference_anchors"

    if reasons:
        return True, "+".join(sorted(set(reasons)))

    return True, "verified_reference_anchors_only"
