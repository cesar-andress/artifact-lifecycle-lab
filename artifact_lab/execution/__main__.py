"""CLI for crash-safe recovery and verification."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from artifact_lab.contracts.datasets import L1_DATASET_VERSION
from artifact_lab.contracts.paths import EXTRACTION_QUEUE_PATH
from artifact_lab.execution.recover import run_recover
from artifact_lab.execution.verify import run_verify
from artifact_lab.protocol.loader import family_version


def _print_recover_report(report) -> None:
    print("Recovery report")
    print(f"  stale reset ........ {report.stale_reset}")
    print(f"  scratch removed .... {len(report.scratch_removed)}")
    print(f"  tmp removed ........ {len(report.tmp_removed)}")
    print(f"  reverted to failed . {len(report.reverted_to_failed)}")
    print(f"  inconsistent ....... {len(report.inconsistent)}")
    print(f"  incomplete ....... {len(report.incomplete)}")
    print(f"  global rebuilt ..... {report.global_events_rebuilt}")
    if report.inconsistent:
        print("Inconsistent repositories:")
        for repo_id in report.inconsistent:
            print(f"  - {repo_id}")
    for action in report.actions:
        print(f"  [{action.category}] {action.detail}")


def _print_verify_report(report) -> None:
    if report.ok:
        print("verify: OK — no issues found")
        return
    print(f"verify: FAILED — {len(report.issues)} issue(s)")
    for issue in report.issues:
        prefix = issue.repo_id or "(global)"
        print(f"  [{issue.category}] {prefix}: {issue.message}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="artifact_lab.execution", description="Crash-safe execution tools")
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--registry", type=Path, required=True)
    common.add_argument("--family", default="ai_conventions_v1")
    common.add_argument("--wave", default="e1_1000_v1")
    common.add_argument("--events-dir", type=Path, required=True)
    common.add_argument("--blobs-dir", type=Path, default=Path("data/blobs"))
    common.add_argument("--receipts-dir", type=Path, default=Path("data/receipts"))
    common.add_argument("--queue", type=Path, default=EXTRACTION_QUEUE_PATH)
    common.add_argument("--scratch", type=Path, default=Path("scratch"))
    common.add_argument("--registry-version", default=None)

    sub.add_parser("recover", parents=[common], help="Repair stale jobs and orphan artifacts")
    sub.add_parser("verify", parents=[common], help="Diagnostic integrity check (no repairs)")

    args = parser.parse_args(argv)
    family = args.family
    protocol_version = family_version(family)

    if args.command == "recover":
        report = run_recover(
            registry_path=args.registry,
            events_dir=args.events_dir,
            receipts_dir=args.receipts_dir,
            blobs_dir=args.blobs_dir,
            queue_path=args.queue,
            scratch_dir=args.scratch,
            family=family,
            wave=args.wave,
            protocol_version=protocol_version,
            extraction_wave=args.wave,
            registry_version=args.registry_version,
            dataset_version=L1_DATASET_VERSION,
        )
        _print_recover_report(report)
        return 0

    if args.command == "verify":
        report = run_verify(
            registry_path=args.registry,
            events_dir=args.events_dir,
            receipts_dir=args.receipts_dir,
            blobs_dir=args.blobs_dir,
            queue_path=args.queue,
            family=family,
            wave=args.wave,
        )
        _print_verify_report(report)
        return 0 if report.ok else 1

    return 1


if __name__ == "__main__":
    sys.exit(main())
