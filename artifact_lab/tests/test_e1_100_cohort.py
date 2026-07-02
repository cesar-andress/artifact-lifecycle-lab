"""Tests for E1 100-repository cohort registry and make targets."""

from __future__ import annotations

import subprocess
from pathlib import Path

from artifact_lab.experiments.e1_adoption_census.export_paths import (
    E1_100_EXPORT_DIR,
    E1_EXPORT_DIR,
)
from artifact_lab.experiments.e1_adoption_census.cohort_accounting import audit_registry
from artifact_lab.registry.schema import E1_100_REGISTRY_COLUMNS, validate_e1_100_registry

REPO_ROOT = Path(__file__).resolve().parents[2]
E1_100_REGISTRY = REPO_ROOT / "data/registry/e1_100_repos.csv"


def test_e1_100_registry_schema_and_size():
    rows = validate_e1_100_registry(E1_100_REGISTRY, expected_rows=100)
    repo_ids = {row["repo_id"] for row in rows}
    repo_urls = {row["repo_url"].strip().lower().rstrip("/") for row in rows}
    assert len(repo_ids) == 100
    assert len(repo_urls) == 100
    assert rows[0]["repo_id"]
    assert rows[0]["repo_url"].startswith("https://github.com/")
    assert rows[0]["owner"]
    assert rows[0]["name"]
    assert rows[0]["source"] in {"pilot_repos.csv", "vsdlc_eligible"}
    assert rows[0]["selection_stratum"]


def test_e1_100_registry_audit_passes():
    audit = audit_registry(E1_100_REGISTRY)
    assert audit.registry_rows == 100
    assert audit.unique_repo_ids == 100
    assert audit.duplicate_repo_ids == []
    assert audit.duplicate_repo_urls == []


def test_e1_100_registry_columns_match_schema():
    with E1_100_REGISTRY.open(encoding="utf-8", newline="") as handle:
        header = handle.readline().strip().split(",")
    assert header == list(E1_100_REGISTRY_COLUMNS)


def test_make_e1_100_appears_in_dry_run():
    result = subprocess.run(
        ["make", "-n", "e1-100"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    output = result.stdout + result.stderr
    assert "e1_100_repos.csv" in output
    assert "artifact_lab.ingest extract" in output
    assert "exports/e1_100" in output
    assert "artifact_lab.experiments.e1_adoption_census.cohort_summary" in output
    assert "exports/e1/" not in output.replace("exports/e1_100", "")


def test_e1_100_export_paths_are_isolated_from_pilot():
    assert E1_100_EXPORT_DIR != E1_EXPORT_DIR
    assert str(E1_100_EXPORT_DIR).endswith("exports/e1_100")
    assert str(E1_EXPORT_DIR).endswith("exports/e1")
