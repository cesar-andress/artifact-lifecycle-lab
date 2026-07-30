"""CLI for task difficulty calibration."""

from __future__ import annotations

import argparse
import sys

from artifact_lab.experiments.task_calibration.run import (
    DEFAULT_CALIBRATION_EXPORT,
    DEFAULT_CANDIDATES_CSV,
    DEFAULT_RQ5_FAILURE_MODES,
    DEFAULT_RQ5_MANIFEST,
    DEFAULT_RQ5_RESULTS,
    run_task_calibration,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Score and calibrate task difficulty before RQ5 v2 inclusion (no agent runs)",
    )
    parser.add_argument("--candidates-csv", type=str, default=str(DEFAULT_CANDIDATES_CSV))
    parser.add_argument("--results-csv", type=str, default=str(DEFAULT_RQ5_RESULTS))
    parser.add_argument("--manifest-csv", type=str, default=str(DEFAULT_RQ5_MANIFEST))
    parser.add_argument("--failure-modes-csv", type=str, default=str(DEFAULT_RQ5_FAILURE_MODES))
    parser.add_argument("--output-dir", type=str, default=str(DEFAULT_CALIBRATION_EXPORT))
    args = parser.parse_args(argv)

    from pathlib import Path

    outputs = run_task_calibration(
        candidates_csv=Path(args.candidates_csv),
        results_csv=Path(args.results_csv),
        manifest_csv=Path(args.manifest_csv),
        failure_modes_csv=Path(args.failure_modes_csv),
        output_dir=Path(args.output_dir),
    )
    for label, path in outputs.items():
        print(f"{label} -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
