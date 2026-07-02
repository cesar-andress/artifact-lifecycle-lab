"""Confirmatory audit of born-stale genuine_false_claim labels."""

from __future__ import annotations

import csv
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from artifact_lab.experiments.truth_decay.born_stale_taxonomy import (
    EXAMPLE_PATTERN,
    PLACEHOLDER_PATTERN,
    classify_heuristic,
)

CONFIRMATORY_CATEGORIES = (
    "confirmed_false",
    "artifact",
    "normative",
    "anchor_issue",
    "template",
    "ambiguous",
)

CATEGORY_LETTERS = {
    "confirmed_false": "A",
    "artifact": "B",
    "normative": "C",
    "anchor_issue": "D",
    "template": "E",
    "ambiguous": "F",
}

BORN_TO_CONFIRMATORY = {
    "extraction_artifact": "artifact",
    "template_placeholder": "template",
    "normative_prescriptive": "normative",
    "verification_anchor_mismatch": "anchor_issue",
    "external_reference": "artifact",
    "pre_observation_evolution": "ambiguous",
}

COMMAND_LIKE = re.compile(
    r"(^|\s)(pytest|poetry run|npm run|yarn |make |cargo |go test|python -m)(\s|$)",
    re.IGNORECASE,
)
GLOB_PATTERN = re.compile(r"[\*\?]")
TEMPLATE_LANGUAGE = re.compile(
    r"\b(example|template|placeholder|e\.g\.|such as|copy from|mkdir -p|path/to)\b",
    re.IGNORECASE,
)
NORMATIVE_LANGUAGE = re.compile(
    r"\b(should|must|convention|pattern|structure|rule|always|never)\b",
    re.IGNORECASE,
)
NODE_MODULE = re.compile(r"^node:[\w/+-]+$")


@dataclass(frozen=True)
class ConfirmatoryRecord:
    repo_id: str
    repo_url: str
    instruction_path: str
    reference_type: str
    reference: str
    first_commit: str
    first_change_type: str
    n_observations: int
    repeated_repo_count: int
    repeated_file_count: int
    snippet_available: bool
    snippet: str
    prior_final_category: str
    prior_adjudication_status: str
    prior_judge_a_category: str
    prior_judge_b_category: str
    heuristic_category: str
    heuristic_confidence: str
    heuristic_rules: str
    heuristic_rationale: str
    adjudication_status: str
    final_category: str
    category_letter: str
    is_confirmed_false: bool
    judge_a_model: str
    judge_a_category: str
    judge_a_rationale: str
    judge_b_model: str
    judge_b_category: str
    judge_b_rationale: str
    judge_agreement: str


def load_genuine_false_claim_rows(taxonomy_csv: Path) -> list[dict]:
    rows: list[dict] = []
    with taxonomy_csv.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("final_category") == "genuine_false_claim":
                rows.append(row)
    return rows


def _command_like(reference: str) -> bool:
    return bool(COMMAND_LIKE.search(reference))


def _strong_template(reference: str, instruction_path: str) -> tuple[bool, tuple[str, ...]]:
    rules: list[str] = []
    if GLOB_PATTERN.search(reference):
        rules.append("glob_wildcard_reference")
    if PLACEHOLDER_PATTERN.search(reference):
        rules.append("placeholder_syntax")
    if EXAMPLE_PATTERN.search(reference) or EXAMPLE_PATTERN.search(instruction_path):
        rules.append("example_path_surface")
    if reference.startswith("path/to/") or reference in {"path/to/test.spec.js", "src/index.js"}:
        rules.append("canonical_placeholder_path")
    return bool(rules), tuple(rules)


def classify_gfc_confirmatory(
    *,
    reference_type: str,
    reference: str,
    instruction_path: str,
    n_observations: int,
    first_change_type: str,
    repeated_repo_count: int,
    repeated_file_count: int,
    snippet: str,
) -> tuple[str, str, tuple[str, ...], str]:
    """Return (category, confidence, rules, rationale)."""
    if NODE_MODULE.match(reference):
        return (
            "artifact",
            "high",
            ("node_module_not_repo_path",),
            "Node built-in module token is not an in-tree path claim.",
        )

    is_template, template_rules = _strong_template(reference, instruction_path)
    if is_template:
        return (
            "template",
            "high",
            template_rules,
            "Placeholder, glob, or example-path token — not a concrete repo claim.",
        )

    if _command_like(reference):
        return (
            "artifact",
            "high",
            ("command_or_script_invocation",),
            "Reference embeds shell command syntax rather than a repository path.",
        )

    born = classify_heuristic(
        reference_type=reference_type,
        reference=reference,
        instruction_path=instruction_path,
        n_observations=n_observations,
        first_change_type=first_change_type,
        repeated_repo_count=repeated_repo_count,
        repeated_file_count=repeated_file_count,
        snippet=snippet,
    )
    if born.category and born.category != "genuine_false_claim":
        mapped = BORN_TO_CONFIRMATORY.get(born.category, "ambiguous")
        return mapped, born.confidence, born.rules_fired, born.rationale

    if TEMPLATE_LANGUAGE.search(snippet):
        return (
            "template",
            "medium",
            ("template_language_in_snippet",),
            "Snippet frames reference as example/template rather than observed repo state.",
        )

    if NORMATIVE_LANGUAGE.search(snippet):
        return (
            "normative",
            "medium",
            ("prescriptive_language_in_snippet",),
            "Reference appears in prescriptive guidance, not descriptive inventory.",
        )

    if born.category == "genuine_false_claim":
        conf = "high" if n_observations >= 3 else "medium"
        return (
            "confirmed_false",
            conf,
            born.rules_fired,
            "Structured in-tree path claim persistently absent across observations.",
        )

    return (
        "ambiguous",
        "low",
        ("insufficient_confirmatory_evidence",),
        "Could not confirm or refute prior genuine_false_claim label deterministically.",
    )


def needs_confirmatory_llm(*, category: str, confidence: str) -> bool:
    return category == "ambiguous"


def record_to_row(record: ConfirmatoryRecord) -> dict:
    return asdict(record)
