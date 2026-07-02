"""Map legacy owner/repo identifiers to canonical repo_id values."""

from __future__ import annotations

import re

from artifact_lab.contracts.repo_id import normalize_repo_url, repo_id_from_url

_LEGACY_SLUG_RE = re.compile(r"^([^/]+)/([^/]+)$")


def legacy_slug_to_url(legacy_id: str) -> str:
    """Convert legacy ``owner/repo`` slug to normalized GitHub HTTPS URL.

    Legacy corpora (e.g. ``ai-convention-lifecycle-corpus``) used ``repo_id``
    values like ``rails/rails`` or ``astral-sh/ruff`` in discovered CSVs.
    """
    slug = legacy_id.strip()
    match = _LEGACY_SLUG_RE.match(slug)
    if not match:
        raise ValueError(f"legacy id must be owner/repo form: {legacy_id!r}")
    owner, repo = match.group(1), match.group(2)
    return normalize_repo_url(f"https://github.com/{owner}/{repo}")


def legacy_id_to_repo_id(legacy_id: str) -> str:
    """Map legacy ``owner/repo`` slug to canonical 16-char ``repo_id`` hash."""
    return repo_id_from_url(legacy_slug_to_url(legacy_id))


def legacy_mapping(legacy_id: str) -> dict[str, str]:
    """Return legacy slug, normalized URL, and canonical repo_id."""
    url = legacy_slug_to_url(legacy_id)
    return {
        "legacy_id": legacy_id.strip(),
        "normalized_repo_url": url,
        "repo_id": repo_id_from_url(url),
    }
