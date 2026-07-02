"""Canonical filesystem paths for the research artifact."""

from __future__ import annotations

from pathlib import Path

EXTRACTION_QUEUE_PATH = Path("data/state/extraction_jobs.db")
EXTRACTION_PROFILE_PATH = Path("data/profiling/extraction_profile.parquet")
