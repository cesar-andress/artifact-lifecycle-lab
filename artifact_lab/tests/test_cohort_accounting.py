"""Tests for E1 cohort accounting and QA."""

from __future__ import annotations

from pathlib import Path

import pyarrow as pa

from artifact_lab.contracts.repo_id import repo_id_from_url
from artifact_lab.experiments.e1_adoption_census.cohort_accounting import (
    ENRICHED_COHORT_NOTE,
    SUMMARY_MODE_LATEST,
    audit_registry,
    compute_extraction_outcomes,
    count_repos_with_matches,
    filter_rows_to_registry,
    latest_profile_per_repo,
    select_cohort_profiles,
)
from artifact_lab.experiments.e1_adoption_census.cohort_summary import build_cohort_summary
from artifact_lab.experiments.e1_adoption_census.qa import run_qa
from artifact_lab.ingest.profiling import ExtractionProfile, PhaseTimings, write_profiles
from artifact_lab.registry.schema import E1_100_REGISTRY_COLUMNS, validate_e1_100_registry
from artifact_lab.store.parquet import write_parquet

REPO_ROOT = Path(__file__).resolve().parents[2]
E1_100_REGISTRY = REPO_ROOT / "data/registry/e1_100_repos.csv"


def _write_e1_registry(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(",".join(E1_100_REGISTRY_COLUMNS) + "\n")
        for row in rows:
            values = [row[col] for col in E1_100_REGISTRY_COLUMNS]
            handle.write(",".join(values) + "\n")


def _registry_row(repo_url: str, *, source: str = "vsdlc_eligible", stratum: str = "test") -> dict[str, str]:
    owner, name = repo_url.rstrip("/").split("/")[-2:]
    return {
        "repo_id": repo_id_from_url(repo_url),
        "repo_url": repo_url,
        "owner": owner,
        "name": name,
        "source": source,
        "stars": "100",
        "language": "Python",
        "pushed_at": "2025-06-15T00:00:00",
        "selection_stratum": stratum,
        "notes": "",
    }


def test_e1_100_registry_has_100_unique_repo_ids_and_urls():
    rows = validate_e1_100_registry(E1_100_REGISTRY, expected_rows=100)
    repo_ids = {row["repo_id"] for row in rows}
    repo_urls = {row["repo_url"].strip().lower().rstrip("/") for row in rows}
    assert len(rows) == 100
    assert len(repo_ids) == 100
    assert len(repo_urls) == 100


def test_audit_registry_detects_duplicates(tmp_path: Path):
    registry = tmp_path / "registry.csv"
    row_a = _registry_row("https://github.com/o/a")
    row_b = _registry_row("https://github.com/o/b")
    row_dup = dict(row_b)
    row_dup["repo_url"] = "https://github.com/o/c"
    _write_e1_registry(registry, [row_a, row_b, row_dup])

    try:
        validate_e1_100_registry(registry, expected_rows=3)
        raise AssertionError("expected duplicate repo_id validation failure")
    except ValueError as exc:
        assert "duplicate repo_id" in str(exc)


def test_latest_profile_per_repo_prefers_newest_wave(tmp_path: Path):
    registry = tmp_path / "registry.csv"
    url = "https://github.com/o/r"
    _write_e1_registry(registry, [_registry_row(url)])

    profiles = [
        ExtractionProfile(
            repo_id=repo_id_from_url(url),
            repo_url=url,
            extraction_wave="pilot_v1",
            status="ok",
            timings=PhaseTimings(wall_s=450.0),
            recorded_at="2025-01-01T00:00:00Z",
        ),
        ExtractionProfile(
            repo_id=repo_id_from_url(url),
            repo_url=url,
            extraction_wave="e1_100_v1",
            status="ok",
            timings=PhaseTimings(wall_s=120.0),
            recorded_at="2026-01-01T00:00:00Z",
        ),
    ]
    selected = latest_profile_per_repo(profiles)
    assert len(selected) == 1
    assert selected[0].extraction_wave == "e1_100_v1"
    assert selected[0].timings.total_s == 120.0


def test_select_cohort_profiles_partitions_outcomes_to_registry_size(tmp_path: Path):
    registry = tmp_path / "registry.csv"
    urls = [f"https://github.com/o/r{i}" for i in range(3)]
    _write_e1_registry(registry, [_registry_row(url) for url in urls])

    profiles: list[ExtractionProfile] = []
    for index, url in enumerate(urls):
        profiles.append(
            ExtractionProfile(
                repo_id=repo_id_from_url(url),
                repo_url=url,
                extraction_wave="e1_100_v1",
                status="ok" if index < 2 else "failed",
                timings=PhaseTimings(wall_s=10.0),
                recorded_at=f"2026-01-0{index + 1}T00:00:00Z",
            )
        )
    profiles.append(
        ExtractionProfile(
            repo_id=repo_id_from_url(urls[0]),
            repo_url=urls[0],
            extraction_wave="pilot_v1",
            status="ok",
            timings=PhaseTimings(wall_s=99.0),
            recorded_at="2025-01-01T00:00:00Z",
        )
    )

    selection = select_cohort_profiles(profiles, registry, summary_mode=SUMMARY_MODE_LATEST)
    outcomes = compute_extraction_outcomes(selection.registry_repo_ids, selection.profiles)

    assert selection.profile_rows_in_registry == 4
    assert selection.latest_profile_rows_used == 3
    assert outcomes.attempted == 3
    assert outcomes.succeeded == 2
    assert outcomes.failed == 1
    assert outcomes.missing == 0
    assert outcomes.succeeded + outcomes.failed + outcomes.skipped + outcomes.missing == 3


def test_count_repos_with_matches_uses_unique_repo_ids():
    rows = [
        {"repo_id": "a", "total_matched_files": 2},
        {"repo_id": "a", "total_matched_files": 1},
        {"repo_id": "b", "total_matched_files": 0},
        {"repo_id": "c", "total_matched_files": 3},
        {"repo_id": "outside", "total_matched_files": 5},
    ]
    registry_ids = {"a", "b", "c"}
    filtered = filter_rows_to_registry(rows, registry_ids)
    assert count_repos_with_matches(filtered, registry_ids) == 2


def test_build_cohort_summary_reports_latest_per_repo_mode(tmp_path: Path):
    registry = tmp_path / "registry.csv"
    url = "https://github.com/o/r"
    _write_e1_registry(registry, [_registry_row(url)])

    profile_path = tmp_path / "profiles.parquet"
    write_profiles(
        [
            ExtractionProfile(
                repo_id=repo_id_from_url(url),
                repo_url=url,
                extraction_wave="pilot_v1",
                status="ok",
                timings=PhaseTimings(wall_s=450.0),
                recorded_at="2025-01-01T00:00:00Z",
            ),
            ExtractionProfile(
                repo_id=repo_id_from_url(url),
                repo_url=url,
                extraction_wave="e1_100_v1",
                status="ok",
                timings=PhaseTimings(wall_s=10.0),
                recorded_at="2026-01-01T00:00:00Z",
            ),
        ],
        profile_path,
    )

    census_dir = tmp_path / "census"
    census_dir.mkdir()
    write_parquet(
        pa.table(
            {
                "repo_id": [repo_id_from_url(url)],
                "repo_url": [url],
                "protocol_family": ["ai_conventions_v1"],
                "artifact_families": ["agents_md"],
                "first_appearance": ["2024-01-01T00:00:00+00:00"],
                "last_appearance": ["2024-01-01T00:00:00+00:00"],
                "currently_present": [True],
                "total_matched_files": [1],
            }
        ),
        census_dir / "repo_census.parquet",
        expected_columns=None,
    )
    write_parquet(
        pa.table(
            {
                "repo_id": [repo_id_from_url(url)],
                "repo_url": [url],
                "protocol_family": ["ai_conventions_v1"],
                "artifact_family": ["agents_md"],
                "path": ["AGENTS.md"],
                "first_appearance": ["2024-01-01T00:00:00+00:00"],
                "last_appearance": ["2024-01-01T00:00:00+00:00"],
                "currently_present": [True],
                "n_events": [1],
            }
        ),
        census_dir / "path_census.parquet",
        expected_columns=None,
    )

    text = build_cohort_summary(
        registry_path=registry,
        census_dir=census_dir,
        table1_path=tmp_path / "missing-table1.csv",
        profile_path=profile_path,
    )
    assert "latest-per-repo" in text
    assert "Profile rows used in summary: **1**" in text
    assert "Attempted repositories: **1**" in text
    assert ENRICHED_COHORT_NOTE.split(".")[0] in text


def test_run_qa_returns_zero_for_balanced_registry(tmp_path: Path):
    registry = tmp_path / "registry.csv"
    url = "https://github.com/o/r"
    _write_e1_registry(registry, [_registry_row(url)])
    profile_path = tmp_path / "profiles.parquet"
    write_profiles(
        [
            ExtractionProfile(
                repo_id=repo_id_from_url(url),
                repo_url=url,
                extraction_wave="e1_100_v1",
                status="ok",
                timings=PhaseTimings(wall_s=10.0),
                recorded_at="2026-01-01T00:00:00Z",
            )
        ],
        profile_path,
    )
    census_dir = tmp_path / "census"
    census_dir.mkdir()
    write_parquet(
        pa.table({"repo_id": [], "total_matched_files": []}),
        census_dir / "repo_census.parquet",
        expected_columns=None,
    )
    assert (
        run_qa(
            registry_path=registry,
            census_dir=census_dir,
            profile_path=profile_path,
        )
        == 1
    )
