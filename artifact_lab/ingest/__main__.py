"""Ingest CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from artifact_lab.contracts.datasets import l1_dataset_dir
from artifact_lab.contracts.paths import EXTRACTION_QUEUE_PATH
from artifact_lab.ingest.extract import (
    DEFAULT_CLONE_TIMEOUT,
    DEFAULT_INSPECTION_MODE,
    DEFAULT_REPO_TIMEOUT,
    INSPECTION_MODES,
    SKIP_SLOW_CLONE_TIMEOUT,
    SKIP_SLOW_REPO_TIMEOUT,
    ExtractConfig,
    run_extract,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="platform.ingest", description="Ingest git repositories")
    sub = parser.add_subparsers(dest="command", required=True)

    extract_p = sub.add_parser("extract", help="Clone-extract-delete repos from registry")
    extract_p.add_argument("--registry", type=Path, required=True)
    extract_p.add_argument("--family", default="ai_conventions_v1")
    extract_p.add_argument("--scratch", type=Path, default=Path("scratch"))
    extract_p.add_argument("--events-dir", type=Path, default=None)
    extract_p.add_argument("--blobs-dir", type=Path, default=Path("data/blobs"))
    extract_p.add_argument("--receipts-dir", type=Path, default=Path("data/receipts"))
    extract_p.add_argument("--queue", type=Path, default=EXTRACTION_QUEUE_PATH)
    extract_p.add_argument("--wave", default="pilot_v1")
    extract_p.add_argument(
        "--registry-version",
        default=None,
        help="Registry version label recorded in L1 manifest (e.g. e1_1000_v1)",
    )
    extract_p.add_argument("--clone-timeout", type=int, default=DEFAULT_CLONE_TIMEOUT)
    extract_p.add_argument("--repo-timeout", type=int, default=DEFAULT_REPO_TIMEOUT)
    extract_p.add_argument("--max-clone-mb", type=int, default=500)
    extract_p.add_argument("--limit", type=int, default=None, help="Process only first N registry rows")
    extract_p.add_argument(
        "--skip-slow",
        action="store_true",
        help=f"Cap clone/repo timeouts at {SKIP_SLOW_CLONE_TIMEOUT}s (bounded pilot runs)",
    )
    extract_p.add_argument("--force", action="store_true")
    extract_p.add_argument(
        "--inspection-mode",
        choices=INSPECTION_MODES,
        default=DEFAULT_INSPECTION_MODE,
        help="head-only: HEAD tree paths (E1 adoption census); full-history: all paths ever touched",
    )

    args = parser.parse_args(argv)
    if args.command == "extract":
        clone_timeout = args.clone_timeout
        repo_timeout = args.repo_timeout
        if args.skip_slow:
            clone_timeout = min(clone_timeout, SKIP_SLOW_CLONE_TIMEOUT)
            repo_timeout = min(repo_timeout, SKIP_SLOW_REPO_TIMEOUT)

        cfg = ExtractConfig(
            registry_path=args.registry,
            family=args.family,
            scratch_dir=args.scratch,
            events_dir=args.events_dir or l1_dataset_dir(),
            blobs_dir=args.blobs_dir,
            receipts_dir=args.receipts_dir,
            queue_path=args.queue,
            extraction_wave=args.wave,
            registry_version=args.registry_version,
            clone_timeout=clone_timeout,
            repo_timeout=repo_timeout,
            max_clone_bytes=args.max_clone_mb * 1_000_000,
            force=args.force,
            limit=args.limit,
            inspection_mode=args.inspection_mode,
        )
        out = run_extract(cfg)
        print(f"wrote L1 events -> {out}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
