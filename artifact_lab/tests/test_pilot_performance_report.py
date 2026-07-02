"""Pilot performance report tests."""

from __future__ import annotations

from pathlib import Path

from artifact_lab.experiments.pilot_performance.report import build_report, write_report
from artifact_lab.ingest.profiling import ExtractionProfile, PhaseTimings, write_profiles


def test_build_report_includes_medians(tmp_path: Path):
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


def test_write_report_exports_to_paper_path(tmp_path: Path):
    profile_path = tmp_path / "profiles.parquet"
    output_path = tmp_path / "paper" / "notes" / "pilot_performance.md"
    write_profiles(
        [
            ExtractionProfile(
                repo_id="abc",
                repo_url="https://github.com/o/r",
                extraction_wave="pilot_v1",
                status="ok",
                timings=PhaseTimings(clone_s=1.0, wall_s=2.0),
                clone_bytes=1000,
            )
        ],
        profile_path,
    )
    write_report(profile_path=profile_path, output_path=output_path)
    assert output_path.exists()
    assert "Pilot extraction performance" in output_path.read_text(encoding="utf-8")
