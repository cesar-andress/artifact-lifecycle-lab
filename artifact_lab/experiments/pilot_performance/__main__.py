"""Pilot performance report CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from artifact_lab.experiments.pilot_performance.report import (
    DEFAULT_PAPER_NOTE,
    DEFAULT_PROFILE_PATH,
    write_report,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="artifact_lab.experiments.pilot_performance")
    parser.add_argument("--profiles", type=Path, default=DEFAULT_PROFILE_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_PAPER_NOTE)
    args = parser.parse_args(argv)
    write_report(profile_path=args.profiles, output_path=args.output)
    print(f"wrote performance note -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
