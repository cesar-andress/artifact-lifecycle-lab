"""Cohort summary report for E1 adoption census runs."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text

from artifact_lab.contracts.paths import EXTRACTION_PROFILE_PATH
from artifact_lab.experiments.e1_adoption_census.cohort_accounting import (
    SUMMARY_MODE_LATEST,
    cohort_note_for_registry,
    compute_extraction_outcomes,
    count_repos_with_matches,
    filter_rows_to_registry,
    is_e1_1000_registry,
    is_e1_100_registry,
    select_cohort_profiles,
)
from artifact_lab.ingest.profiling import load_profiles, median_or_none
from artifact_lab.registry.schema import validate_e1_1000_registry, validate_e1_100_registry
from artifact_lab.store.parquet import read_parquet

DEFAULT_CENSUS_DIR = Path("data/derived/adoption_census/e1_100/v1")
DEFAULT_TABLE1 = Path("exports/e1_100/table1.csv")
DEFAULT_OUTPUT = Path("exports/e1_100/cohort_summary.md")


def _load_table1_distribution(table1_path: Path) -> list[tuple[str, int, int]]:
    if not table1_path.exists():
        return []
    with table1_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [(row["artifact_family"], int(row["n_repos"]), int(row["n_files"])) for row in rows]


def _wave_summary(waves: dict[str, int]) -> str:
    if not waves:
        return "none"
    return ", ".join(f"{wave} ({count})" for wave, count in waves.items())


def _stratum_counts(registry_path: Path) -> list[tuple[str, int]]:
    if not is_e1_1000_registry(registry_path):
        return []
    rows = validate_e1_1000_registry(registry_path)
    counts: dict[str, int] = {}
    for row in rows:
        stratum = row["cohort_stratum"]
        counts[stratum] = counts.get(stratum, 0) + 1
    return sorted(counts.items())


def build_cohort_summary(
    *,
    registry_path: Path,
    census_dir: Path,
    table1_path: Path,
    profile_path: Path,
    summary_mode: str = SUMMARY_MODE_LATEST,
    extraction_wave: str | None = None,
) -> str:
    if is_e1_1000_registry(registry_path):
        validate_e1_1000_registry(registry_path)
    elif is_e1_100_registry(registry_path):
        validate_e1_100_registry(registry_path, expected_rows=100)

    cohort_note = cohort_note_for_registry(registry_path)
    title = "# E1 cohort summary"
    if is_e1_1000_registry(registry_path):
        title = "# E1 1000-repository scientific cohort summary"
    elif is_e1_100_registry(registry_path):
        title = "# E1 100-repository cohort summary"

    selection = select_cohort_profiles(
        load_profiles(profile_path),
        registry_path,
        summary_mode=summary_mode,
        extraction_wave=extraction_wave,
    )
    profiles = selection.profiles
    outcomes = compute_extraction_outcomes(selection.registry_repo_ids, profiles)

    matched_repos = 0
    matched_paths = 0
    repo_census = census_dir / "repo_census.parquet"
    path_census = census_dir / "path_census.parquet"
    if repo_census.exists():
        repo_rows = filter_rows_to_registry(
            read_parquet(repo_census).to_pylist(),
            selection.registry_repo_ids,
        )
        matched_repos = count_repos_with_matches(repo_rows, selection.registry_repo_ids)
    if path_census.exists():
        path_rows = filter_rows_to_registry(
            read_parquet(path_census).to_pylist(),
            selection.registry_repo_ids,
        )
        matched_paths = len(path_rows)

    totals = [profile.timings.total_s for profile in profiles if profile.timings.total_s > 0]
    slowest = sorted(profiles, key=lambda profile: profile.timings.total_s, reverse=True)[:10]
    family_rows = _load_table1_distribution(table1_path)

    lines = [
        title,
        "",
    ]
    if cohort_note:
        lines.extend(
            [
                "## Cohort interpretation",
                f"> {cohort_note}",
                "",
            ]
        )
    stratum_counts = _stratum_counts(registry_path)
    if stratum_counts:
        lines.extend(["## Strata", ""])
        for stratum, count in stratum_counts:
            lines.append(f"- `{stratum}`: **{count}** repositories")
        lines.append("")

    lines.extend(
        [
        "## Registry",
        f"- Attempted repositories: **{outcomes.attempted}**",
        f"- Profile accounting mode: **{selection.summary_mode}**",
        f"- Extraction wave(s) in summary: **{_wave_summary(selection.extraction_waves)}**",
        f"- Profile rows matching registry (all waves): **{selection.profile_rows_in_registry}**",
        f"- Profile rows used in summary: **{selection.latest_profile_rows_used}**",
        "",
        "## Extraction outcomes",
        f"- Succeeded: **{outcomes.succeeded}**",
        f"- Failed: **{outcomes.failed}**",
        f"- Skipped: **{outcomes.skipped}**",
        f"- Missing (no profile row): **{outcomes.missing}**",
        "",
        "## Adoption census",
        f"- Repositories with matched convention files: **{matched_repos}**",
        f"- Matched convention paths: **{matched_paths}**",
        "",
        "## Runtime",
        f"- Median extraction time: **{median_or_none(totals) or 0:.1f} s**",
        "",
        "## Artifact family distribution",
        "",
        ]
    )
    if family_rows:
        lines.extend(
            [
                "| Artifact family | Repositories | Files |",
                "|-----------------|--------------|-------|",
            ]
        )
        for family, n_repos, n_files in family_rows:
            lines.append(f"| {family} | {n_repos} | {n_files} |")
    else:
        lines.append("No table1 export found.")

    lines.extend(["", "## Slowest repositories", ""])
    if not slowest:
        lines.append("No profiling records found.")
    else:
        lines.extend(
            [
                "| Rank | Repository | Wave | Total (s) | Status | Inspection mode |",
                "|------|------------|------|-----------|--------|-----------------|",
            ]
        )
        for rank, profile in enumerate(slowest, start=1):
            lines.append(
                f"| {rank} | {profile.repo_slug} | {profile.extraction_wave} | "
                f"{profile.timings.total_s:.1f} | {profile.status} | {profile.inspection_mode} |"
            )
    lines.append("")
    return "\n".join(lines)


def write_cohort_summary(
    *,
    registry_path: Path,
    census_dir: Path,
    table1_path: Path,
    profile_path: Path,
    output_path: Path,
    summary_mode: str = SUMMARY_MODE_LATEST,
    extraction_wave: str | None = None,
) -> None:
    atomic_write_text(
        output_path,
        build_cohort_summary(
            registry_path=registry_path,
            census_dir=census_dir,
            table1_path=table1_path,
            profile_path=profile_path,
            summary_mode=summary_mode,
            extraction_wave=extraction_wave,
        ),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="artifact_lab.experiments.e1_adoption_census.cohort_summary")
    parser.add_argument("--registry", type=Path, default=Path("data/registry/e1_100_repos.csv"))
    parser.add_argument("--census-dir", type=Path, default=DEFAULT_CENSUS_DIR)
    parser.add_argument("--table1", type=Path, default=DEFAULT_TABLE1)
    parser.add_argument("--profiles", type=Path, default=EXTRACTION_PROFILE_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--summary-mode",
        choices=("latest-per-repo", "cumulative"),
        default=SUMMARY_MODE_LATEST,
    )
    parser.add_argument("--extraction-wave", type=str, default=None)
    args = parser.parse_args(argv)
    write_cohort_summary(
        registry_path=args.registry,
        census_dir=args.census_dir,
        table1_path=args.table1,
        profile_path=args.profiles,
        output_path=args.output,
        summary_mode=args.summary_mode,
        extraction_wave=args.extraction_wave,
    )
    print(f"wrote cohort summary -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
