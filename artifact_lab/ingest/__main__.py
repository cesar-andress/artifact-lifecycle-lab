"""Ingest CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from artifact_lab.contracts.datasets import l1_dataset_dir
from artifact_lab.ingest.extract import ExtractConfig, run_extract


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
    extract_p.add_argument("--queue", type=Path, default=Path("data/state/extraction_jobs.db"))
    extract_p.add_argument("--wave", default="pilot_v1")
    extract_p.add_argument("--clone-timeout", type=int, default=300)
    extract_p.add_argument("--repo-timeout", type=int, default=600)
    extract_p.add_argument("--max-clone-mb", type=int, default=500)
    extract_p.add_argument("--force", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "extract":
        cfg = ExtractConfig(
            registry_path=args.registry,
            family=args.family,
            scratch_dir=args.scratch,
            events_dir=args.events_dir or l1_dataset_dir(),
            blobs_dir=args.blobs_dir,
            receipts_dir=args.receipts_dir,
            queue_path=args.queue,
            extraction_wave=args.wave,
            clone_timeout=args.clone_timeout,
            repo_timeout=args.repo_timeout,
            max_clone_bytes=args.max_clone_mb * 1_000_000,
            force=args.force,
        )
        out = run_extract(cfg)
        print(f"wrote L1 events -> {out}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
