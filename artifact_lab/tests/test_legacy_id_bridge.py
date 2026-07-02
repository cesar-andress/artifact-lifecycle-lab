"""Tests for legacy owner/repo ID bridge."""

import pytest

from artifact_lab.contracts.legacy_id import legacy_id_to_repo_id, legacy_mapping, legacy_slug_to_url
from artifact_lab.contracts.repo_id import repo_id_from_url


def test_legacy_slug_to_normalized_url():
    assert legacy_slug_to_url("rails/rails") == "https://github.com/rails/rails"
    assert legacy_slug_to_url("astral-sh/ruff") == "https://github.com/astral-sh/ruff"


def test_legacy_id_matches_canonical_repo_id():
    legacy = "astral-sh/ruff"
    url = "https://github.com/astral-sh/ruff"
    assert legacy_id_to_repo_id(legacy) == repo_id_from_url(url)


def test_legacy_mapping_payload():
    mapped = legacy_mapping("django/django")
    assert mapped["legacy_id"] == "django/django"
    assert mapped["normalized_repo_url"] == "https://github.com/django/django"
    assert len(mapped["repo_id"]) == 16


def test_invalid_legacy_slug_raises():
    with pytest.raises(ValueError):
        legacy_slug_to_url("not-a-slug")
