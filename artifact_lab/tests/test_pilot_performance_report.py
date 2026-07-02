"""Pilot performance report tests."""

from __future__ import annotations

from pathlib import Path

from artifact_lab.contracts.repo_id import repo_id_from_url
from artifact_lab.experiments.pilot_performance.registry_filter import filter_pilot_profiles
from artifact_lab.experiments.pilot_performance.report import (
    build_report,
    report_failure_phase,
    write_report,
)
from artifact_lab.ingest.profiling import ExtractionProfile, PhaseTimings, load_profiles, write_profiles

FIXTURE_SLUGS = (
    "example/slow",
    "example/archived",
    "example/a",
    "example/b",
    "example/fast",
)


def _pilot_registry(tmp_path: Path, repo_urls: list[str]) -> Path:
    registry_path = tmp_path / "pilot_repos.csv"
    lines = ["repo_url,seed_pool,notes"]
    for url in repo_urls:
        lines.append(f"{url},test,")
    registry_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return registry_path


def test_build_report_includes_medians():
    profiles = [
        ExtractionProfile(
            repo_id="slow",
            repo_url="https://github.com/continuedev/continue",
            extraction_wave="pilot_v1",
            status="failed",
            timings=PhaseTimings(clone_s=20, history_s=400, wall_s=420),
            clone_bytes=50_000_000,
        ),
        ExtractionProfile(
            repo_id="fast",
            repo_url="https://github.com/astral-sh/ruff",
            extraction_wave="pilot_v1",
            status="ok",
            timings=PhaseTimings(clone_s=8, history_s=5, blobs_s=1, wall_s=15),
            clone_bytes=10_000_000,
            n_events=68,
            n_matched_paths=3,
        ),
    ]
    text = build_report(profiles)
    assert "Median extraction time" in text
    assert "Median clone size" in text
    assert "continuedev/continue" in text
    assert "Recommendations" in text


def test_write_report_exports_to_e1_path(tmp_path: Path):
    profile_path = tmp_path / "profiles.parquet"
    output_path = tmp_path / "exports" / "e1" / "pilot_performance.md"
    registry_path = _pilot_registry(tmp_path, ["https://github.com/o/r"])
    write_profiles(
        [
            ExtractionProfile(
                repo_id=repo_id_from_url("https://github.com/o/r"),
                repo_url="https://github.com/o/r",
                extraction_wave="pilot_v1",
                status="ok",
                timings=PhaseTimings(
                    clone_s=1.0,
                    inspection_s=0.5,
                    wall_s=2.0,
                ),
                clone_bytes=1000,
            )
        ],
        profile_path,
    )
    write_report(profile_path=profile_path, output_path=output_path, registry_path=registry_path)
    assert output_path.exists()
    assert "Pilot extraction performance" in output_path.read_text(encoding="utf-8")


def test_fixture_repos_excluded_from_e1_report(tmp_path: Path):
    profile_path = tmp_path / "profiles.parquet"
    output_path = tmp_path / "pilot_performance.md"
    registry_path = _pilot_registry(tmp_path, ["https://github.com/continuedev/continue"])

    profiles = [
        ExtractionProfile(
            repo_id=repo_id_from_url("https://github.com/continuedev/continue"),
            repo_url="https://github.com/continuedev/continue",
            extraction_wave="pilot_v1",
            status="ok",
            timings=PhaseTimings(clone_s=5.0, wall_s=5.0),
        ),
    ]
    for slug in FIXTURE_SLUGS:
        url = f"https://github.com/{slug}"
        profiles.append(
            ExtractionProfile(
                repo_id=repo_id_from_url(url),
                repo_url=url,
                extraction_wave="pilot_v1",
                status="ok",
                timings=PhaseTimings(clone_s=1.0, wall_s=1.0),
            )
        )
    write_profiles(profiles, profile_path)

    write_report(profile_path=profile_path, output_path=output_path, registry_path=registry_path)
    text = output_path.read_text(encoding="utf-8")

    assert "continuedev/continue" in text
    for slug in FIXTURE_SLUGS:
        assert slug not in text


def test_test_mode_includes_fixture_repos(tmp_path: Path):
    profile_path = tmp_path / "profiles.parquet"
    registry_path = _pilot_registry(tmp_path, ["https://github.com/continuedev/continue"])
    fixture_url = "https://github.com/example/slow"
    write_profiles(
        [
            ExtractionProfile(
                repo_id=repo_id_from_url(fixture_url),
                repo_url=fixture_url,
                extraction_wave="pilot_v1",
                status="ok",
                timings=PhaseTimings(clone_s=1.0, wall_s=1.0),
            )
        ],
        profile_path,
    )
    filtered = filter_pilot_profiles(load_profiles(profile_path), registry_path, test_mode=True)
    assert len(filtered) == 1

    text = build_report(filtered, test_mode=True)
    assert "example/slow" in text
    assert "test mode" in text.lower()


def test_timeout_failure_reports_phase_and_reason():
    profile = ExtractionProfile(
        repo_id="slow-repo",
        repo_url="https://github.com/example/slow",
        extraction_wave="pilot_v1",
        status="failed",
        timings=PhaseTimings(
            clone_s=1.2,
            inspection_s=118.5,
            wall_s=120.0,
            manifest_write_s=0.0,
            parquet_write_s=0.0,
        ),
        failure_reason="timeout:inspection",
        timeout_phase="inspection",
    )
    assert report_failure_phase(profile) == "timeout:inspection (118.5 s)"

    text = build_report([profile], test_mode=True)
    assert "timeout_phase=inspection" in text
    assert "slowest phase=timeout:inspection (118.5 s)" in text
    assert "failure_reason=timeout:inspection" in text


def test_failed_repo_with_batch_phase_quota_shows_unknown():
    profile = ExtractionProfile(
        repo_id="failed-repo",
        repo_url="https://github.com/org/repo",
        extraction_wave="pilot_v1",
        status="failed",
        timings=PhaseTimings(
            wall_s=30.0,
            manifest_write_s=0.0,
        ),
        failure_reason="CloneTooLargeError: too big",
    )
    assert report_failure_phase(profile) == "timeout/unknown"
