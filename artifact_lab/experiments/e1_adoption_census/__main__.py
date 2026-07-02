"""E1 adoption census CLI."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from artifact_lab.contracts.datasets import l1_dataset_dir
from artifact_lab.experiments.e1_adoption_census.census import run_census
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


def _count_registry(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return len(rows)


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
    events = read_parquet(events_path).to_pylist()
    run_fig1(events=events, csv_path=fig1_csv, pdf_path=fig1_pdf)
    run_table1(repo_family_rows=census["repo_family"], output_path=table1_path)
    report = render_report(
        census_dir=census_dir,
        fig1_csv=fig1_csv,
        table1_csv=table1_path,
        n_registry_repos=_count_registry(registry_path),
        n_repos_with_matches=len(census["repo"]),
        n_path_rows=len(census["path"]),
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
