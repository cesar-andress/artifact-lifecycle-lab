"""Canonical path constants."""

from artifact_lab.contracts.paths import EXTRACTION_PROFILE_CSV, EXTRACTION_PROFILE_PATH, EXTRACTION_QUEUE_PATH


def test_extraction_queue_path():
    from pathlib import Path

    assert EXTRACTION_QUEUE_PATH == Path("data/state/extraction_jobs.db")
    assert EXTRACTION_PROFILE_PATH == Path("data/profiling/extraction_profile.parquet")
    assert EXTRACTION_PROFILE_CSV == Path("data/profiling/extraction_profile.csv")
