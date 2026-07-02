"""Filter profiling records to pilot registry repositories only."""

from __future__ import annotations

from pathlib import Path

from artifact_lab.ingest.extract import read_registry
from artifact_lab.ingest.profiling import ExtractionProfile

DEFAULT_REGISTRY_PATH = Path("data/registry/pilot_repos.csv")


def load_registry_repo_ids(registry_path: Path) -> set[str]:
    rows = read_registry(registry_path)
    return {row["repo_id"] for row in rows}


def filter_pilot_profiles(
    profiles: list[ExtractionProfile],
    registry_path: Path,
    *,
    test_mode: bool = False,
) -> list[ExtractionProfile]:
    """Keep only repositories listed in the pilot registry CSV."""
    if test_mode:
        return profiles
    allowed = load_registry_repo_ids(registry_path)
    return [profile for profile in profiles if profile.repo_id in allowed]
