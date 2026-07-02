"""E1 adoption census CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from artifact_lab.contracts.datasets import l1_dataset_dir
from artifact_lab.experiments.e1_adoption_census.census import run_census
from artifact_lab.experiments.e1_adoption_census.cohort_accounting import (
    ENRICHED_COHORT_NOTE,
    count_repos_with_matches,
    filter_rows_to_registry,
    is_e1_100_registry,
    load_registry_repo_ids,
)
from artifact_lab.experiments.e1_adoption_census.export_paper import export_to_paper_repo
from artifact_lab.experiments.e1_adoption_census.export_paths import (
    DEFAULT_FIG1_CSV,
    DEFAULT_FIG1_PDF,
    DEFAULT_REPORT,
    DEFAULT_TABLE1,
)
from artifact_lab.experiments.e1_adoption_census.fig1 import run_fig1
from artifact_lab.experiments.e1_adoption_census.report import render_report, write_report
from artifact_lab.experiments.e1_adoption_census.table1 import run_table1
from artifact_lab.store.parquet import read_parquet

DEFAULT_CENSUS_DIR = Path("data/derived/adoption_census/v1")
DEFAULT_REGISTRY = Path("data/registry/pilot_repos.csv")
DEFAULT_PAPER_ROOT = Path("../paper")


def _l1_events_path(l1: Path) -> Path:
    if l1.is_dir():
        candidate = l1 / "events.parquet"
        if candidate.exists():
            return candidate
        files = sorted(l1.glob("*.parquet"))
        if not files:
            raise FileNotFoundError(f"no L1 parquet in {l1}")
        return files[0]
    return l1


def run_all(
    *,
    l1_path: Path,
    census_dir: Path,
    fig1_csv: Path,
    fig1_pdf: Path,
    table1_path: Path,
    report_path: Path,
    registry_path: Path,
    paper_root: Path | None = None,
) -> None:
    events_path = _l1_events_path(l1_path)
    census = run_census(l1_path=events_path, output_dir=census_dir)
    registry_repo_ids = load_registry_repo_ids(registry_path)
    filtered_path = filter_rows_to_registry(census["path"], registry_repo_ids)
    filtered_repo = filter_rows_to_registry(census["repo"], registry_repo_ids)
    filtered_repo_family = filter_rows_to_registry(census["repo_family"], registry_repo_ids)

    events = read_parquet(events_path).to_pylist()
    filtered_events = [event for event in events if event.get("repo_id") in registry_repo_ids]
    run_fig1(events=filtered_events, csv_path=fig1_csv, pdf_path=fig1_pdf)
    run_table1(repo_family_rows=filtered_repo_family, output_path=table1_path)
    report = render_report(
        census_dir=census_dir,
        fig1_csv=fig1_csv,
        table1_csv=table1_path,
        n_registry_repos=len(registry_repo_ids),
        n_repos_with_matches=count_repos_with_matches(filtered_repo, registry_repo_ids),
        n_path_rows=len(filtered_path),
        cohort_note=ENRICHED_COHORT_NOTE if is_e1_100_registry(registry_path) else None,
    )
    write_report(report, report_path)
    print(f"wrote census -> {census_dir}")
    print(f"wrote fig1 -> {fig1_pdf}")
    print(f"wrote table1 -> {table1_path}")
    print(f"wrote report -> {report_path}")
    if paper_root is not None:
        exported = export_to_paper_repo(paper_root=paper_root)
        for path in exported:
            print(f"exported -> {path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="artifact_lab.experiments.e1_adoption_census")
    parser.add_argument("--l1", type=Path, default=None)
    parser.add_argument("--census-dir", type=Path, default=DEFAULT_CENSUS_DIR)
    parser.add_argument("--fig1-csv", type=Path, default=DEFAULT_FIG1_CSV)
    parser.add_argument("--fig1-pdf", type=Path, default=DEFAULT_FIG1_PDF)
    parser.add_argument("--table1", type=Path, default=DEFAULT_TABLE1)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument(
        "--paper-root",
        type=Path,
        default=None,
        help="Optional sibling paper repository root for one-way export",
    )
    parser.add_argument(
        "--no-export",
        action="store_true",
        help="Skip export to the paper repository",
    )
    args = parser.parse_args(argv)

    l1 = args.l1 or l1_dataset_dir()
    paper_root = None if args.no_export else (args.paper_root or DEFAULT_PAPER_ROOT)
    run_all(
        l1_path=l1,
        census_dir=args.census_dir,
        fig1_csv=args.fig1_csv,
        fig1_pdf=args.fig1_pdf,
        table1_path=args.table1,
        report_path=args.report,
        registry_path=args.registry,
        paper_root=paper_root,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
