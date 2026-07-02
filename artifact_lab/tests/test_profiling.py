"""Profiling instrumentation tests."""

from __future__ import annotations

from pathlib import Path

from artifact_lab.ingest.profiling import (
    ExtractionProfile,
    PhaseTimings,
    assign_parquet_write_share,
    format_progress_log,
    load_profiles,
    merge_profiles,
    slow_repo_warning,
    write_profiles,
)


def test_format_progress_log():
    profile = ExtractionProfile(
        repo_id="abc",
        repo_url="https://github.com/astral-sh/ruff",
        extraction_wave="pilot_v1",
        status="ok",
        timings=PhaseTimings(
            clone_s=8.2,
            history_s=4.7,
            detector_s=0.5,
            blobs_s=1.3,
            parquet_write_s=0.2,
            cleanup_s=0.1,
            wall_s=14.6,
        ),
        clone_bytes=12_000_000,
        n_events=68,
        n_matched_paths=3,
        recorded_at="2026-01-01T00:00:00+00:00",
    )
    text = format_progress_log(index=3, total=16, profile=profile)
    assert text.splitlines()[0] == "[3/16]"
    assert text.splitlines()[1] == "astral-sh/ruff"
    assert "clone=8.2s" in text
    assert "total=14.8s" in text


def test_slow_repo_warning():
    profile = ExtractionProfile(
        repo_id="abc",
        repo_url="https://github.com/continuedev/continue",
        extraction_wave="pilot_v1",
        status="failed",
        timings=PhaseTimings(clone_s=10, history_s=320, wall_s=330),
    )
    warning = slow_repo_warning(profile, threshold_s=300)
    assert warning is not None
    assert "continuedev/continue" in warning
    assert "history" in warning


def test_profile_parquet_roundtrip(tmp_path: Path):
    path = tmp_path / "profiles.parquet"
    profile = ExtractionProfile(
        repo_id="abc",
        repo_url="https://github.com/o/r",
        extraction_wave="pilot_v1",
        status="ok",
        timings=PhaseTimings(clone_s=1.0, wall_s=2.0, parquet_write_s=0.5),
        clone_bytes=1000,
        n_events=5,
        n_matched_paths=2,
        recorded_at="2026-01-01T00:00:00+00:00",
    )
    write_profiles([profile], path)
    loaded = load_profiles(path)
    assert len(loaded) == 1
    assert loaded[0].repo_id == "abc"
    assert loaded[0].timings.clone_s == 1.0
    assert loaded[0].timings.total_s == 2.5


def test_merge_profiles_replaces_same_repo_wave(tmp_path: Path):
    path = tmp_path / "profiles.parquet"
    first = ExtractionProfile(
        repo_id="abc",
        repo_url="https://github.com/o/r",
        extraction_wave="pilot_v1",
        status="ok",
        timings=PhaseTimings(clone_s=1.0, wall_s=1.0),
        recorded_at="t1",
    )
    write_profiles([first], path)
    second = ExtractionProfile(
        repo_id="abc",
        repo_url="https://github.com/o/r",
        extraction_wave="pilot_v1",
        status="ok",
        timings=PhaseTimings(clone_s=9.0, wall_s=9.0),
        recorded_at="t2",
    )
    merged = merge_profiles([p.to_row() for p in load_profiles(path)], [second])
    assert len(merged) == 1
    assert merged[0].timings.clone_s == 9.0


def test_assign_parquet_write_share():
    profiles = [
        ExtractionProfile(
            repo_id="a",
            repo_url="https://github.com/o/a",
            extraction_wave="w",
            status="ok",
            timings=PhaseTimings(wall_s=1.0),
        ),
        ExtractionProfile(
            repo_id="b",
            repo_url="https://github.com/o/b",
            extraction_wave="w",
            status="ok",
            timings=PhaseTimings(wall_s=2.0),
        ),
    ]
    assign_parquet_write_share(profiles, 1.0)
    assert profiles[0].timings.parquet_write_s == 0.5
    assert profiles[1].timings.total_s == 2.5
