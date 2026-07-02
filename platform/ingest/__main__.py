"""Ingest CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from platform.ingest.extract import ExtractConfig, run_extract


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="platform.ingest", description="Ingest git repositories")
    sub = parser.add_subparsers(dest="command", required=True)

    extract_p = sub.add_parser("extract", help="Clone-extract-delete repos from registry")
    extract_p.add_argument("--registry", type=Path, required=True)
    extract_p.add_argument("--family", default="ai_conventions_v1")
    extract_p.add_argument("--scratch", type=Path, default=Path("scratch"))
    extract_p.add_argument("--events-dir", type=Path, default=Path("data/l1/file_event_log"))
    extract_p.add_argument("--blobs-dir", type=Path, default=Path("data/blobs"))
    extract_p.add_argument("--receipts-dir", type=Path, default=Path("data/receipts"))
    extract_p.add_argument("--wave", default="pilot_v1")

    args = parser.parse_args(argv)
    if args.command == "extract":
        cfg = ExtractConfig(
            registry_path=args.registry,
            family=args.family,
            scratch_dir=args.scratch,
            events_dir=args.events_dir,
            blobs_dir=args.blobs_dir,
            receipts_dir=args.receipts_dir,
            extraction_wave=args.wave,
        )
        out = run_extract(cfg)
        print(f"wrote L1 events -> {out}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
