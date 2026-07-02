"""Tests for deterministic repo_id normalization."""

import pytest

from artifact_lab.contracts.repo_id import normalize_repo_url, repo_id_from_url


def test_github_url_normalization_is_case_insensitive():
    a = normalize_repo_url("https://github.com/Org/Repo.git")
    b = normalize_repo_url("https://github.com/org/repo")
    assert a == b == "https://github.com/org/repo"


def test_repo_id_is_stable_across_equivalent_urls():
    ids = [
        repo_id_from_url("https://github.com/Org/Repo.git"),
        repo_id_from_url("https://github.com/org/repo"),
        repo_id_from_url("https://github.com/org/repo/"),
    ]
    assert len(set(ids)) == 1
    assert len(ids[0]) == 16


def test_repo_id_known_vector():
    normalized = "https://github.com/astral-sh/ruff"
    expected = repo_id_from_url(normalized)
    assert repo_id_from_url("https://github.com/astral-sh/ruff.git") == expected


def test_invalid_url_raises():
    with pytest.raises(ValueError):
        normalize_repo_url("not-a-url")
