"""Scientific taxonomy for why born-stale references never reach VERIFIED."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from artifact_lab.experiments.truth_decay.born_stale_audit import (
    VALID_FILENAME,
    _is_prose_token,
    is_likely_external,
    is_relative_path_candidate,
)

# Inferred scientific categories (not hardcoded A–F letters in logic).
TAXONOMY_LABELS = (
    "extraction_artifact",
    "template_placeholder",
    "normative_prescriptive",
    "pre_observation_evolution",
    "external_reference",
    "verification_anchor_mismatch",
    "genuine_false_claim",
)

Confidence = Literal["high", "medium", "low"]

PLACEHOLDER_PATTERN = re.compile(
    r"(<[^>]+>|\{[^}]+\}|\[\w+\]|\*\*|\.{3}|_your_|path_to_|placeholder|TODO|FIXME|xxx|\btest\.py\b)",
    re.IGNORECASE,
)
EXAMPLE_PATTERN = re.compile(r"(^|[/_.-])examples?([/_.-]|$)", re.IGNORECASE)
URL_PATTERN = re.compile(r"^https?://|^//|^www\.", re.IGNORECASE)
NORMATIVE_PATH_HINT = re.compile(
    r"(^|/)(AGENTS\.md|SKILL\.md|README\.md|CONTRIBUTING\.md|CLAUDE\.md)$",
    re.IGNORECASE,
)
NORMATIVE_INSTRUCTION = re.compile(
    r"(\.cursor/rules/|/skills/|/\.agents/|prompts/)",
    re.IGNORECASE,
)
GENERIC_TEMPLATE_REFS = frozenset(
    {
        "SKILL.md",
        "/SKILL.md",
        "AGENTS.md",
        "README.md",
        "package.json",
        "team-lead.md",
        "tasks.md",
        "index.ts",
        "lib.rs",
        "Node.js",
        "Next.js",
    }
)
INVALID_PATH_CHARS = re.compile(r"[`$]|:{2,}|models\.py:")


@dataclass(frozen=True)
class HeuristicVerdict:
    category: str | None
    confidence: Confidence
    rules_fired: tuple[str, ...]
    rationale: str


def _invalid_extraction(reference: str, reference_type: str) -> bool:
    if reference_type == "directory" and reference in {"/", "w/"}:
        return True
    if INVALID_PATH_CHARS.search(reference):
        return True
    if URL_PATTERN.search(reference) and reference_type != "dependency":
        return True
    if _is_prose_token(reference):
        return True
    if reference_type == "path" and not VALID_FILENAME.match(reference) and "/" not in reference:
        if not reference.endswith("/"):
            return True
    return False


def _template_signals(
    reference: str,
    instruction_path: str,
    *,
    repeated_repo_count: int,
    repeated_file_count: int,
) -> tuple[bool, list[str]]:
    rules: list[str] = []
    if EXAMPLE_PATTERN.search(reference) or EXAMPLE_PATTERN.search(instruction_path):
        rules.append("example_path_or_directory")
    if PLACEHOLDER_PATTERN.search(reference):
        rules.append("placeholder_syntax_in_reference")
    if reference in GENERIC_TEMPLATE_REFS and repeated_repo_count >= 3:
        rules.append("cross_repo_generic_template_token")
    if repeated_file_count >= 10 and repeated_repo_count >= 5:
        rules.append("high_cross_file_repetition")
    return bool(rules), rules


def _normative_signals(reference: str, instruction_path: str, snippet: str) -> tuple[bool, list[str]]:
    rules: list[str] = []
    if NORMATIVE_INSTRUCTION.search(instruction_path):
        rules.append("instruction_file_is_rule_or_skill_surface")
    if NORMATIVE_PATH_HINT.search(reference):
        rules.append("reference_points_to_convention_doc")
    lower = snippet.lower()
    if reference in snippet and any(w in lower for w in ("should", "must", "convention", "structure", "pattern")):
        rules.append("prescriptive_language_near_reference")
    return bool(rules), rules


def classify_heuristic(
    *,
    reference_type: str,
    reference: str,
    instruction_path: str,
    n_observations: int,
    first_change_type: str,
    repeated_repo_count: int,
    repeated_file_count: int,
    snippet: str = "",
) -> HeuristicVerdict:
    """Deterministic first-pass classification with explicit confidence."""
    rules: list[str] = []

    if _invalid_extraction(reference, reference_type):
        return HeuristicVerdict(
            category="extraction_artifact",
            confidence="high",
            rules_fired=("invalid_or_prose_extraction",),
            rationale="Token fails path grammar or matches prose false-positive profile.",
        )

    if reference_type == "dependency" or (
        reference_type != "dependency" and is_likely_external(reference_type, reference)
    ):
        if reference_type == "dependency" or URL_PATTERN.search(reference) or _is_prose_token(reference):
            return HeuristicVerdict(
                category="external_reference",
                confidence="high",
                rules_fired=("external_or_dependency_token",),
            rationale="Package, URL, or non-repo product token — not an in-tree path claim.",
        )

    if is_relative_path_candidate(reference, reference_type):
        return HeuristicVerdict(
            category="verification_anchor_mismatch",
            confidence="high",
            rules_fired=("relative_or_single_segment_anchor",),
            rationale="Path likely requires instruction-relative anchor; verified from repo root only.",
        )

    is_template, template_rules = _template_signals(
        reference,
        instruction_path,
        repeated_repo_count=repeated_repo_count,
        repeated_file_count=repeated_file_count,
    )
    if is_template:
        conf: Confidence = "high" if "placeholder_syntax_in_reference" in template_rules else "medium"
        return HeuristicVerdict(
            category="template_placeholder",
            confidence=conf,
            rules_fired=tuple(template_rules),
            rationale="Example, placeholder, or cross-repo template token — not a concrete repo claim.",
        )

    is_normative, norm_rules = _normative_signals(reference, instruction_path, snippet)
    if is_normative:
        return HeuristicVerdict(
            category="normative_prescriptive",
            confidence="medium",
            rules_fired=tuple(norm_rules),
            rationale="Reference appears in prescriptive rule/skill context describing conventions.",
        )

    structured = reference_type in ("path", "directory", "script_name") and (
        VALID_FILENAME.match(reference) or "/" in reference
    )
    if structured and first_change_type == "modify" and n_observations >= 2:
        return HeuristicVerdict(
            category="pre_observation_evolution",
            confidence="medium",
            rules_fired=("file_predates_panel_with_persistent_missing",),
            rationale="Structured path missing from first panel snapshot; file existed before observation window.",
        )

    if structured:
        return HeuristicVerdict(
            category="genuine_false_claim",
            confidence="low",
            rules_fired=("structured_path_always_missing",),
            rationale="Plausible repo path persistently absent — may be false claim or unobserved confound.",
        )

    return HeuristicVerdict(
        category=None,
        confidence="low",
        rules_fired=("insufficient_heuristic_evidence",),
        rationale="No deterministic category met confidence threshold.",
    )


def needs_llm_adjudication(verdict: HeuristicVerdict) -> bool:
    if verdict.category is None:
        return True
    if verdict.confidence == "low":
        return True
    if verdict.confidence == "medium" and verdict.category == "genuine_false_claim":
        return True
    return False
