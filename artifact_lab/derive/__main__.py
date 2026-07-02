"""Derive CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from artifact_lab.contracts.datasets import l1_dataset_dir, l2_dataset_dir
from artifact_lab.contracts.paths import EXTRACTION_QUEUE_PATH
from artifact_lab.derive.panel import run_panel
from artifact_lab.derive.summary import build_summary, format_summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="platform.derive", description="Derive datasets from L1")
    sub = parser.add_subparsers(dest="command", required=True)

    panel_p = sub.add_parser("panel", help="Build L2 monthly file-state panel from L1 events")
    panel_p.add_argument("--events", type=Path, default=None)
    panel_p.add_argument("--output", type=Path, default=None)
    panel_p.add_argument("--T", type=int, default=180)

    summary_p = sub.add_parser("summary", help="Print pilot summary from L1/L2 and job queue")
    summary_p.add_argument("--l1", type=Path, default=None)
    summary_p.add_argument("--l2", type=Path, default=None)
    summary_p.add_argument("--queue", type=Path, default=EXTRACTION_QUEUE_PATH)
    summary_p.add_argument("--receipts", type=Path, default=Path("data/receipts"))
    summary_p.add_argument("--blobs", type=Path, default=Path("data/blobs"))

    args = parser.parse_args(argv)
    if args.command == "panel":
        events = args.events or l1_dataset_dir()
        output = args.output or l2_dataset_dir()
        out = run_panel(events_path=events, output_dir=output, T=args.T)
        print(f"wrote L2 panel -> {out}")
        return 0
    if args.command == "summary":
        l1 = args.l1 or l1_dataset_dir()
        l2 = args.l2 or l2_dataset_dir()
        summary = build_summary(
            l1_path=l1,
            l2_path=l2,
            queue_path=args.queue,
            receipts_dir=args.receipts,
            blobs_dir=args.blobs,
        )
        print(format_summary(summary), end="")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
