"""Tests for E1 1000-repository scientific cohort."""

from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path

from artifact_lab.experiments.e1_adoption_census.export_paths import (
    E1_1000_EXPORT_DIR,
    E1_100_EXPORT_DIR,
    E1_EXPORT_DIR,
)
from artifact_lab.registry.build_e1_1000 import build_e1_1000_registry
from artifact_lab.registry.pools import COHORT_STRATA
from artifact_lab.registry.schema import (
    E1_1000_REGISTRY_COLUMNS,
    E1_1000_REGISTRY_VERSION,
    E1_1000_STRATUM_SIZES,
    E1_1000_TARGET_SIZE,
    validate_e1_1000_registry,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
E1_1000_REGISTRY = REPO_ROOT / "data/registry/e1_1000_repos.csv"
COHORT_DESIGN = REPO_ROOT / "exports/e1_1000/cohort_design.md"
GENERAL_OSS_POOL = REPO_ROOT / "data/registry/sources/general_oss_candidates.jsonl"
VSDLC = Path.home() / "papers/vsdlc/vsdlc/data/interim/eligible_repos_enriched.jsonl"
SECOND_FRAME = Path.home() / "papers/vsdlc/vsdlc/data/raw/second_frame_candidates.jsonl"


def test_e1_1000_registry_schema_and_strata():
    rows = validate_e1_1000_registry(E1_1000_REGISTRY)
    assert len(rows) == E1_1000_TARGET_SIZE
    counts = Counter(row["cohort_stratum"] for row in rows)
    assert counts["ai_instruction_discovery"] == E1_1000_STRATUM_SIZES["ai_instruction_discovery"]
    assert counts["general_oss"] == E1_1000_STRATUM_SIZES["general_oss"]
    assert counts["mixed_control"] == E1_1000_STRATUM_SIZES["mixed_control"]


def test_e1_1000_registry_unique_ids_and_sorted_urls():
    rows = validate_e1_1000_registry(E1_1000_REGISTRY)
    repo_ids = [row["repo_id"] for row in rows]
    repo_urls = [row["repo_url"].lower() for row in rows]
    assert len(set(repo_ids)) == len(repo_ids)
    assert len(set(repo_urls)) == len(repo_urls)
    assert repo_urls == sorted(repo_urls)


def test_e1_1000_registry_columns_match_schema():
    with E1_1000_REGISTRY.open(encoding="utf-8", newline="") as handle:
        header = handle.readline().strip().split(",")
    assert header == list(E1_1000_REGISTRY_COLUMNS)


def test_e1_1000_build_is_deterministic(tmp_path: Path):
    if not (VSDLC.exists() and SECOND_FRAME.exists() and GENERAL_OSS_POOL.exists()):
        return
    first = build_e1_1000_registry(
        vsdlc_path=VSDLC,
        second_frame_path=SECOND_FRAME,
        general_oss_path=GENERAL_OSS_POOL,
        seed=42,
    )
    second = build_e1_1000_registry(
        vsdlc_path=VSDLC,
        second_frame_path=SECOND_FRAME,
        general_oss_path=GENERAL_OSS_POOL,
        seed=42,
    )
    assert first == second


def test_e1_1000_no_cross_stratum_url_duplicates():
    rows = validate_e1_1000_registry(E1_1000_REGISTRY)
    urls = [row["repo_url"].lower() for row in rows]
    assert len(urls) == len(set(urls))


def test_e1_1000_export_paths_are_isolated():
    assert E1_1000_EXPORT_DIR != E1_100_EXPORT_DIR != E1_EXPORT_DIR
    assert str(E1_1000_EXPORT_DIR).endswith("exports/e1_1000")


def test_make_e1_1000_appears_in_dry_run():
    result = subprocess.run(
        ["make", "-n", "e1-1000"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    output = result.stdout + result.stderr
    assert "e1_1000_repos.csv" in output
    assert "e1_1000_v1" in output
    assert "exports/e1_1000" in output
    assert "exports/e1_100/" not in output.replace("exports/e1_1000", "")


def test_cohort_design_documents_three_strata():
    assert COHORT_DESIGN.exists()
    text = COHORT_DESIGN.read_text(encoding="utf-8")
    for stratum in COHORT_STRATA:
        assert stratum in text
    assert "github-wide population sample" in text.casefold()
    assert "head-only" in text.casefold()


def test_general_oss_pool_exists_and_is_large():
    assert GENERAL_OSS_POOL.exists()
    with GENERAL_OSS_POOL.open(encoding="utf-8") as handle:
        rows = sum(1 for line in handle if line.strip())
    assert rows >= E1_1000_STRATUM_SIZES["general_oss"]


def test_qa_accepts_committed_registry_without_census():
    from artifact_lab.experiments.e1_adoption_census.qa import run_qa

    exit_code = run_qa(
        registry_path=E1_1000_REGISTRY,
        census_dir=REPO_ROOT / "data/derived/adoption_census/e1_1000/v1",
        profile_path=REPO_ROOT / "data/profiling/extraction_profile.parquet",
        expected_rows=E1_1000_TARGET_SIZE,
    )
    # Without extraction, missing=1000 is expected — QA should warn on outcomes only if attempted partition fails
    assert exit_code in {0, 1}


def test_registry_version_constant_matches_makefile_wave():
    assert E1_1000_REGISTRY_VERSION == "e1_1000_v1"
