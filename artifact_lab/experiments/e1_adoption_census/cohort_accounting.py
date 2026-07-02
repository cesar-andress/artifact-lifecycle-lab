"""Registry-scoped cohort accounting for E1 adoption census reports."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from artifact_lab.experiments.pilot_performance.registry_filter import (
    load_registry_repo_ids,
)
from artifact_lab.ingest.profiling import ExtractionProfile
from artifact_lab.registry.schema import (
    read_registry_rows,
    validate_e1_1000_registry,
    validate_e1_100_registry,
)

ENRICHED_COHORT_NOTE = (
    "This 100-repository cohort is an enriched engineering cohort, not a population sample. "
    "Adoption rates must not be interpreted as GitHub-wide prevalence."
)

E1_1000_SCIENTIFIC_COHORT_NOTE = (
    "E1-1000 is a deterministic stratified scientific cohort, not a GitHub population sample. "
    "Report AI-instruction discovery-frame prevalence and general-OSS contrast separately. "
    "Adoption is head-only current-presence at HEAD."
)

SUMMARY_MODE_LATEST = "latest-per-repo"
SUMMARY_MODE_CUMULATIVE = "cumulative"


@dataclass(frozen=True)
class RegistryAudit:
    registry_rows: int
    unique_repo_ids: int
    duplicate_repo_ids: list[str]
    duplicate_repo_urls: list[str]


@dataclass(frozen=True)
class ExtractionOutcomeCounts:
    attempted: int
    profiled: int
    succeeded: int
    failed: int
    skipped: int
    missing: int

    def validate(self) -> list[str]:
        warnings: list[str] = []
        total = self.succeeded + self.failed + self.skipped + self.missing
        if total != self.attempted:
            warnings.append(
                f"outcome partition mismatch: succeeded+failed+skipped+missing={total} "
                f"!= attempted={self.attempted}"
            )
        if self.profiled + self.missing != self.attempted:
            warnings.append(
                f"profile coverage mismatch: profiled+missing={self.profiled + self.missing} "
                f"!= attempted={self.attempted}"
            )
        return warnings


@dataclass(frozen=True)
class CohortProfileSelection:
    profiles: list[ExtractionProfile]
    registry_repo_ids: set[str]
    profile_rows_in_registry: int
    latest_profile_rows_used: int
    extraction_waves: dict[str, int]
    summary_mode: str
    primary_extraction_wave: str | None


def audit_registry(registry_path: Path) -> RegistryAudit:
    rows = read_registry_rows(registry_path)
    repo_ids = [row["repo_id"].strip() for row in rows]
    repo_urls = [row["repo_url"].strip().lower().rstrip("/") for row in rows]
    id_counts = Counter(repo_ids)
    url_counts = Counter(repo_urls)
    duplicate_repo_ids = sorted(repo_id for repo_id, count in id_counts.items() if count > 1)
    duplicate_repo_urls = sorted(url for url, count in url_counts.items() if count > 1)
    if duplicate_repo_ids:
        raise ValueError(f"registry {registry_path} duplicate repo_ids: {duplicate_repo_ids}")
    if duplicate_repo_urls:
        raise ValueError(f"registry {registry_path} duplicate repo_urls: {duplicate_repo_urls}")
    return RegistryAudit(
        registry_rows=len(rows),
        unique_repo_ids=len(set(repo_ids)),
        duplicate_repo_ids=duplicate_repo_ids,
        duplicate_repo_urls=duplicate_repo_urls,
    )


def _profile_sort_key(profile: ExtractionProfile) -> tuple[str, str]:
    return (profile.recorded_at or "", profile.extraction_wave or "")


def latest_profile_per_repo(profiles: list[ExtractionProfile]) -> list[ExtractionProfile]:
    """Keep the newest profile row for each repo_id."""
    by_repo: dict[str, ExtractionProfile] = {}
    for profile in profiles:
        existing = by_repo.get(profile.repo_id)
        if existing is None or _profile_sort_key(profile) > _profile_sort_key(existing):
            by_repo[profile.repo_id] = profile
    return sorted(by_repo.values(), key=lambda profile: profile.repo_slug.lower())


def filter_profiles_to_registry(
    profiles: list[ExtractionProfile],
    registry_repo_ids: set[str],
) -> list[ExtractionProfile]:
    return [profile for profile in profiles if profile.repo_id in registry_repo_ids]


def select_cohort_profiles(
    profiles: list[ExtractionProfile],
    registry_path: Path,
    *,
    summary_mode: str = SUMMARY_MODE_LATEST,
    extraction_wave: str | None = None,
) -> CohortProfileSelection:
    registry_repo_ids = load_registry_repo_ids(registry_path)
    in_registry = filter_profiles_to_registry(profiles, registry_repo_ids)

    if extraction_wave is not None:
        in_registry = [profile for profile in in_registry if profile.extraction_wave == extraction_wave]

    if summary_mode == SUMMARY_MODE_CUMULATIVE:
        selected = sorted(in_registry, key=lambda profile: (profile.repo_slug.lower(), profile.extraction_wave))
    elif summary_mode == SUMMARY_MODE_LATEST:
        selected = latest_profile_per_repo(in_registry)
    else:
        raise ValueError(f"unsupported summary mode: {summary_mode}")

    wave_counts = Counter(profile.extraction_wave for profile in selected)
    primary_wave = wave_counts.most_common(1)[0][0] if wave_counts else None

    return CohortProfileSelection(
        profiles=selected,
        registry_repo_ids=registry_repo_ids,
        profile_rows_in_registry=len(in_registry),
        latest_profile_rows_used=len(selected),
        extraction_waves=dict(sorted(wave_counts.items())),
        summary_mode=summary_mode,
        primary_extraction_wave=primary_wave,
    )


def compute_extraction_outcomes(
    registry_repo_ids: set[str],
    latest_profiles: list[ExtractionProfile],
) -> ExtractionOutcomeCounts:
    attempted = len(registry_repo_ids)
    profiled_ids = {profile.repo_id for profile in latest_profiles}
    succeeded = sum(1 for profile in latest_profiles if profile.status in {"ok", "no_matches"})
    skipped = sum(1 for profile in latest_profiles if profile.status == "skipped")
    failed = sum(
        1 for profile in latest_profiles if profile.status not in {"ok", "no_matches", "skipped"}
    )
    missing = attempted - len(profiled_ids)
    return ExtractionOutcomeCounts(
        attempted=attempted,
        profiled=len(profiled_ids),
        succeeded=succeeded,
        failed=failed,
        skipped=skipped,
        missing=missing,
    )


def filter_rows_to_registry(rows: list[dict], registry_repo_ids: set[str]) -> list[dict]:
    return [row for row in rows if row.get("repo_id") in registry_repo_ids]


def count_repos_with_matches(repo_rows: list[dict], registry_repo_ids: set[str]) -> int:
    matched_ids = {
        row["repo_id"]
        for row in repo_rows
        if row.get("repo_id") in registry_repo_ids and int(row.get("total_matched_files") or 0) > 0
    }
    return len(matched_ids)


def is_e1_100_registry(registry_path: Path) -> bool:
    try:
        validate_e1_100_registry(registry_path, expected_rows=100)
        return True
    except ValueError:
        return False


def is_e1_1000_registry(registry_path: Path) -> bool:
    try:
        validate_e1_1000_registry(registry_path)
        return True
    except ValueError:
        return False


def cohort_note_for_registry(registry_path: Path) -> str | None:
    if is_e1_1000_registry(registry_path):
        return E1_1000_SCIENTIFIC_COHORT_NOTE
    if is_e1_100_registry(registry_path):
        return ENRICHED_COHORT_NOTE
    return None
