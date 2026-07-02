"""CLI for TOSEM go/no-go truth pilots (P1, P2)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from artifact_lab.experiments.truth_pilots.go_no_go import run_go_no_go_report
from artifact_lab.experiments.truth_pilots.p1_reference import run_p1_reference_density_pilot
from artifact_lab.experiments.truth_pilots.p2_attribution import run_p2_attribution_pilot

DEFAULT_L1_PATHS = (
    Path("data/l1/file_event_log/v1/events.parquet"),
    Path("data/l1/e1_100/v1/events.parquet"),
    Path("data/l1/e1_1000/v1/events.parquet"),
)
DEFAULT_EXPORT_DIR = Path("exports/truth_pilot")


def _resolve_l1(l1_paths: list[Path] | None) -> list[Path]:
    paths = l1_paths if l1_paths else list(DEFAULT_L1_PATHS)
    existing = [p for p in paths if p.exists() and (p.is_dir() or p.stat().st_size > 100)]
    return existing


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="artifact_lab.experiments.truth_pilots",
        description="TOSEM go/no-go pilots — reference density + agent attribution",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--l1",
        type=Path,
        action="append",
        dest="l1_paths",
        help="L1 events parquet or directory (repeatable)",
    )
    common.add_argument("--blobs-dir", type=Path, default=Path("data/blobs"))
    common.add_argument("--scratch", type=Path, default=Path("scratch"))
    common.add_argument("--output-dir", type=Path, default=DEFAULT_EXPORT_DIR)
    common.add_argument("--seed", type=int, default=42)
    common.add_argument("--clone-timeout", type=int, default=180)

    p1_parser = sub.add_parser("p1", parents=[common], help="Reference density pilot")
    p1_parser.add_argument("--n-samples", type=int, default=400)
    p1_parser.add_argument("--n-min", type=int, default=300)
    p1_parser.add_argument("--n-max", type=int, default=500)

    sub.add_parser("p2", parents=[common], help="Agent attribution pilot")
    sub.add_parser("go-no-go", parents=[common], help="Generate go/no-go report from P1/P2 outputs")
    sub.add_parser("all", parents=[common], help="Run P1, P2, and go/no-go")

    all_parser = sub.choices["all"]
    all_parser.add_argument("--n-samples", type=int, default=400)
    all_parser.add_argument("--n-min", type=int, default=300)
    all_parser.add_argument("--n-max", type=int, default=500)

    args = parser.parse_args(argv)
    l1_paths = _resolve_l1(args.l1_paths)
    if not l1_paths and args.command != "go-no-go":
        print("error: no L1 inputs found; run e1 or e1-100 extraction first", file=sys.stderr)
        return 1

    if args.command in {"p1", "all"}:
        density, examples, summary = run_p1_reference_density_pilot(
            l1_paths=l1_paths,
            blobs_dir=args.blobs_dir,
            scratch_dir=args.scratch,
            output_dir=args.output_dir,
            n_samples=args.n_samples,
            n_min=args.n_min,
            n_max=args.n_max,
            seed=args.seed,
            clone_timeout=args.clone_timeout,
        )
        print(f"P1 density -> {density}")
        print(f"P1 examples -> {examples}")
        print(f"P1 summary -> {summary}")

    if args.command in {"p2", "all"}:
        attribution, candidates, summary = run_p2_attribution_pilot(
            l1_paths=l1_paths,
            scratch_dir=args.scratch,
            output_dir=args.output_dir,
            clone_timeout=args.clone_timeout,
        )
        print(f"P2 attribution -> {attribution}")
        print(f"P2 candidates -> {candidates}")
        print(f"P2 summary -> {summary}")

    if args.command in {"go-no-go", "all"}:
        report = run_go_no_go_report(output_dir=args.output_dir)
        print(f"Go/no-go -> {report}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
