"""Canonical filesystem paths for the research artifact."""

from __future__ import annotations

from pathlib import Path

EXTRACTION_QUEUE_PATH = Path("data/state/extraction_jobs.db")
EXECUTION_LOG_PATH = Path("data/state/execution.log")
EXTRACTION_SESSION_PATH = Path("data/state/extraction_session.json")
EXTRACTION_PROFILE_PATH = Path("data/profiling/extraction_profile.parquet")
EXTRACTION_PROFILE_CSV = Path("data/profiling/extraction_profile.csv")
