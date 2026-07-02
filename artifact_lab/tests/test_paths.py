"""Canonical path constants."""

from artifact_lab.contracts.paths import (
    EXECUTION_LOG_PATH,
    EXTRACTION_PROFILE_CSV,
    EXTRACTION_PROFILE_PATH,
    EXTRACTION_QUEUE_PATH,
    EXTRACTION_SESSION_PATH,
)


def test_extraction_queue_path():
    from pathlib import Path

    assert EXTRACTION_QUEUE_PATH == Path("data/state/extraction_jobs.db")
    assert EXECUTION_LOG_PATH == Path("data/state/execution.log")
    assert EXTRACTION_SESSION_PATH == Path("data/state/extraction_session.json")
    assert EXTRACTION_PROFILE_PATH == Path("data/profiling/extraction_profile.parquet")
    assert EXTRACTION_PROFILE_CSV == Path("data/profiling/extraction_profile.csv")
