"""Derive CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from platform.derive.panel import run_panel


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="platform.derive", description="Derive datasets from L1")
    sub = parser.add_subparsers(dest="command", required=True)

    panel_p = sub.add_parser("panel", help="Build L2 monthly file-state panel from L1 events")
    panel_p.add_argument("--events", type=Path, required=True)
    panel_p.add_argument("--output", type=Path, default=Path("data/derived/file_state_panel"))
    panel_p.add_argument("--T", type=int, default=180)

    args = parser.parse_args(argv)
    if args.command == "panel":
        out = run_panel(events_path=args.events, output_dir=args.output, T=args.T)
        print(f"wrote L2 panel -> {out}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
