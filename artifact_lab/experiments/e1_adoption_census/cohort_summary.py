"""Cohort summary report for E1 adoption census runs."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from artifact_lab.contracts.paths import EXTRACTION_PROFILE_PATH
from artifact_lab.experiments.pilot_performance.registry_filter import filter_pilot_profiles
from artifact_lab.ingest.profiling import load_profiles, median_or_none
from artifact_lab.registry.schema import validate_e1_100_registry
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


def build_cohort_summary(
    *,
    registry_path: Path,
    census_dir: Path,
    table1_path: Path,
    profile_path: Path,
) -> str:
    registry_rows = validate_e1_100_registry(registry_path)
    profiles = filter_pilot_profiles(load_profiles(profile_path), registry_path)

    succeeded = [p for p in profiles if p.status in {"ok", "no_matches"}]
    failed = [p for p in profiles if p.status not in {"ok", "no_matches", "skipped"}]
    skipped = [p for p in profiles if p.status == "skipped"]

    matched_repos = 0
    matched_paths = 0
    repo_census = census_dir / "repo_census.parquet"
    path_census = census_dir / "path_census.parquet"
    if repo_census.exists():
        repo_rows = read_parquet(repo_census).to_pylist()
        matched_repos = sum(1 for row in repo_rows if int(row.get("total_matched_files") or 0) > 0)
    if path_census.exists():
        matched_paths = len(read_parquet(path_census).to_pylist())

    totals = [p.timings.total_s for p in profiles if p.timings.total_s > 0]
    slowest = sorted(profiles, key=lambda p: p.timings.total_s, reverse=True)[:10]
    family_rows = _load_table1_distribution(table1_path)

    lines = [
        "# E1 100-repository cohort summary",
        "",
        "## Registry",
        f"- Attempted repositories: **{len(registry_rows)}**",
        f"- Profiled in latest extraction wave: **{len(profiles)}**",
        "",
        "## Extraction outcomes",
        f"- Succeeded: **{len(succeeded)}**",
        f"- Failed: **{len(failed)}**",
        f"- Skipped: **{len(skipped)}**",
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
                "| Rank | Repository | Total (s) | Status | Inspection mode |",
                "|------|------------|-----------|--------|-----------------|",
            ]
        )
        for rank, profile in enumerate(slowest, start=1):
            lines.append(
                f"| {rank} | {profile.repo_slug} | {profile.timings.total_s:.1f} | "
                f"{profile.status} | {profile.inspection_mode} |"
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
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        build_cohort_summary(
            registry_path=registry_path,
            census_dir=census_dir,
            table1_path=table1_path,
            profile_path=profile_path,
        ),
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="artifact_lab.experiments.e1_adoption_census.cohort_summary")
    parser.add_argument("--registry", type=Path, default=Path("data/registry/e1_100_repos.csv"))
    parser.add_argument("--census-dir", type=Path, default=DEFAULT_CENSUS_DIR)
    parser.add_argument("--table1", type=Path, default=DEFAULT_TABLE1)
    parser.add_argument("--profiles", type=Path, default=EXTRACTION_PROFILE_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    write_cohort_summary(
        registry_path=args.registry,
        census_dir=args.census_dir,
        table1_path=args.table1,
        profile_path=args.profiles,
        output_path=args.output,
    )
    print(f"wrote cohort summary -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
