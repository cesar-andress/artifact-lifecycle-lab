"""CLI for RQ1 truth-decay feasibility study."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from artifact_lab.experiments.truth_decay.run_rq1 import DEFAULT_EXPORT_DIR, DEFAULT_L1_PATHS, run_rq1_feasibility_study


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="artifact_lab.experiments.truth_decay",
        description="RQ1 truth-decay feasibility study (no survival models)",
    )
    parser.add_argument(
        "--l1",
        type=Path,
        action="append",
        dest="l1_paths",
        help="L1 events parquet (repeatable)",
    )
    parser.add_argument("--blobs-dir", type=Path, default=Path("data/blobs"))
    parser.add_argument("--scratch", type=Path, default=Path("scratch"))
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_EXPORT_DIR)
    parser.add_argument("--clone-timeout", type=int, default=180)
    parser.add_argument(
        "--max-files",
        type=int,
        default=None,
        help="Limit instruction files (for dev runs only)",
    )
    args = parser.parse_args(argv)

    l1_paths = args.l1_paths if args.l1_paths else list(DEFAULT_L1_PATHS)
    existing = [p for p in l1_paths if p.exists() and (p.is_dir() or p.stat().st_size > 100)]
    if not existing:
        print("error: no L1 inputs found", file=sys.stderr)
        return 1

    outputs = run_rq1_feasibility_study(
        l1_paths=existing,
        blobs_dir=args.blobs_dir,
        scratch_dir=args.scratch,
        output_dir=args.output_dir,
        clone_timeout=args.clone_timeout,
        max_files=args.max_files,
    )
    for label, path in outputs.items():
        print(f"{label} -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
