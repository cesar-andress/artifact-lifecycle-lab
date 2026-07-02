"""QA command for E1 cohort accounting."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from artifact_lab.experiments.e1_adoption_census.cohort_accounting import (
    SUMMARY_MODE_LATEST,
    audit_registry,
    compute_extraction_outcomes,
    count_repos_with_matches,
    filter_rows_to_registry,
    select_cohort_profiles,
)
from artifact_lab.ingest.profiling import load_profiles
from artifact_lab.store.parquet import read_parquet


def run_qa(
    *,
    registry_path: Path,
    census_dir: Path,
    profile_path: Path,
    summary_mode: str = SUMMARY_MODE_LATEST,
    extraction_wave: str | None = None,
) -> int:
    audit = audit_registry(registry_path)
    if audit.registry_rows != 100:
        warnings: list[str] = [f"expected 100 registry rows, got {audit.registry_rows}"]
    else:
        warnings = []

    selection = select_cohort_profiles(
        load_profiles(profile_path),
        registry_path,
        summary_mode=summary_mode,
        extraction_wave=extraction_wave,
    )
    outcomes = compute_extraction_outcomes(selection.registry_repo_ids, selection.profiles)

    matched_repos = 0
    repo_census = census_dir / "repo_census.parquet"
    if repo_census.exists():
        repo_rows = read_parquet(repo_census).to_pylist()
        filtered = filter_rows_to_registry(repo_rows, selection.registry_repo_ids)
        matched_repos = count_repos_with_matches(filtered, selection.registry_repo_ids)

    warnings.extend(outcomes.validate())
    if audit.duplicate_repo_ids:
        warnings.append(f"duplicate repo_ids in registry: {audit.duplicate_repo_ids}")
    if audit.duplicate_repo_urls:
        warnings.append(f"duplicate repo_urls in registry: {audit.duplicate_repo_urls}")
    if selection.profile_rows_in_registry > selection.latest_profile_rows_used:
        print(
            "info: multiple profile rows per repo_id in registry; "
            "latest-per-repo selection applied"
        )

    print(f"registry rows: {audit.registry_rows}")
    print(f"unique repo_ids: {audit.unique_repo_ids}")
    print(f"duplicate repo_ids: {audit.duplicate_repo_ids or 'none'}")
    print(f"duplicate repo_urls: {audit.duplicate_repo_urls or 'none'}")
    print(f"matched repos: {matched_repos}")
    print(f"profile rows in registry: {selection.profile_rows_in_registry}")
    print(f"latest profile rows used: {selection.latest_profile_rows_used}")
    print(f"summary mode: {selection.summary_mode}")
    print(f"extraction waves: {selection.extraction_waves or 'none'}")
    print(
        "outcomes: "
        f"succeeded={outcomes.succeeded} "
        f"failed={outcomes.failed} "
        f"skipped={outcomes.skipped} "
        f"missing={outcomes.missing}"
    )
    if warnings:
        print("warnings:")
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("warnings: none")
    return 1 if warnings else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="artifact_lab.experiments.e1_adoption_census.qa")
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--census-dir", type=Path, required=True)
    parser.add_argument("--profiles", type=Path, required=True)
    parser.add_argument(
        "--summary-mode",
        choices=("latest-per-repo", "cumulative"),
        default=SUMMARY_MODE_LATEST,
    )
    parser.add_argument("--extraction-wave", type=str, default=None)
    args = parser.parse_args(argv)
    return run_qa(
        registry_path=args.registry,
        census_dir=args.census_dir,
        profile_path=args.profiles,
        summary_mode=args.summary_mode,
        extraction_wave=args.extraction_wave,
    )


if __name__ == "__main__":
    sys.exit(main())
