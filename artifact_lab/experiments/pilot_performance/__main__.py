"""Pilot performance report CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from artifact_lab.experiments.pilot_performance.registry_filter import DEFAULT_REGISTRY_PATH
from artifact_lab.experiments.pilot_performance.report import (
    DEFAULT_E1_EXPORT,
    DEFAULT_PROFILE_PATH,
    write_report,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="artifact_lab.experiments.pilot_performance")
    parser.add_argument("--profiles", type=Path, default=DEFAULT_PROFILE_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_E1_EXPORT)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Include all profile rows (for tests only; never use for E1 reports)",
    )
    args = parser.parse_args(argv)
    write_report(
        profile_path=args.profiles,
        output_path=args.output,
        registry_path=args.registry,
        test_mode=args.test_mode,
    )
    print(f"wrote performance note -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
