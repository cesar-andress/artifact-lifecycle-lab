"""Shared cohort pool loading and exclusion rules for E1 registries."""

from __future__ import annotations

import json
import re
from pathlib import Path

from artifact_lab.contracts.repo_id import normalize_repo_url, repo_id_from_url

EXCLUDE_NAME_RE = re.compile(
    r"(template|boilerplate|cookiecutter|starter-kit|awesome-|/awesome$|-awesome$|/mirror$|-mirror$)",
    re.IGNORECASE,
)

MIRROR_HINT_RE = re.compile(r"\bmirror\b", re.IGNORECASE)

STRATUM_AI_INSTRUCTION = "ai_instruction_discovery"
STRATUM_GENERAL_OSS = "general_oss"
STRATUM_MIXED_CONTROL = "mixed_control"

COHORT_STRATA: tuple[str, ...] = (
    STRATUM_AI_INSTRUCTION,
    STRATUM_GENERAL_OSS,
    STRATUM_MIXED_CONTROL,
)


def parse_owner_name(repo_url: str) -> tuple[str, str]:
    normalized = normalize_repo_url(repo_url)
    match = re.match(r"https://github\.com/([^/]+)/([^/]+)$", normalized)
    if not match:
        raise ValueError(f"cannot parse owner/name from {repo_url!r}")
    return match.group(1), match.group(2)


def artifact_family(queries: list[str]) -> str:
    joined = " ".join(queries).lower()
    if ".cursor/rules" in joined or "cursor/rules" in joined:
        return "cursor_rules"
    if "agents.md" in joined:
        return "agents_md"
    if "claude.md" in joined:
        return "claude_md"
    if "copilot" in joined:
        return "copilot"
    if "prompt" in joined:
        return "prompts"
    if ".rules" in joined or "/rules" in joined:
        return "rules"
    return "other"


def star_stratum(stars: int) -> str:
    if stars < 500:
        return "stars_small"
    if stars < 5000:
        return "stars_medium"
    return "stars_large"


def topic_predicate(queries: list[str]) -> str:
    for query in queries:
        if query.startswith("topic:"):
            return query
    return queries[0] if queries else "topic:unknown"


def is_excluded_name(full_name: str, *, description: str | None = None) -> bool:
    if EXCLUDE_NAME_RE.search(full_name):
        return True
    if description and MIRROR_HINT_RE.search(description) and "mirror of" in description.casefold():
        return True
    return False


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def candidate_row(
    *,
    repo_url: str,
    stars: int,
    language: str,
    pushed_at: str,
    source: str,
    cohort_stratum: str,
    selection_stratum: str,
    notes: str = "",
) -> dict[str, str]:
    owner, name = parse_owner_name(repo_url)
    return {
        "repo_id": repo_id_from_url(repo_url),
        "repo_url": normalize_repo_url(repo_url),
        "owner": owner,
        "name": name,
        "source": source,
        "stars": str(stars),
        "language": language,
        "pushed_at": pushed_at,
        "cohort_stratum": cohort_stratum,
        "selection_stratum": selection_stratum,
        "notes": notes,
    }
