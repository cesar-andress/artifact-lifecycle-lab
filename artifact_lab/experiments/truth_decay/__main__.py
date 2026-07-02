"""CLI for truth-decay RQ1 (feasibility) and RQ2 (survival)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from artifact_lab.experiments.truth_decay.run_born_stale_audit import run_born_stale_audit
from artifact_lab.experiments.truth_decay.run_born_stale_autopsy import run_born_stale_autopsy
from artifact_lab.experiments.truth_decay.run_rq1 import DEFAULT_EXPORT_DIR, DEFAULT_L1_PATHS, run_rq1_feasibility_study
from artifact_lab.experiments.truth_decay.run_rq2 import DEFAULT_RQ2_EXPORT, run_rq2_survival_analysis
from artifact_lab.experiments.truth_decay.run_rq3 import DEFAULT_EXPORT as DEFAULT_RQ3_EXPORT, run_rq3_observational_analysis
from artifact_lab.experiments.truth_decay.run_rq4 import DEFAULT_RQ4_EXPORT, run_rq4_lifecycle_analysis
from artifact_lab.experiments.truth_decay.run_rq5_prep import DEFAULT_RQ5_EXPORT, run_rq5_preparation
from artifact_lab.experiments.truth_pilots.gates_common import DEFAULT_RQ1_LONGITUDINAL


def _cmd_rq1(args: argparse.Namespace) -> int:
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


def _cmd_rq2(args: argparse.Namespace) -> int:
    outputs = run_rq2_survival_analysis(
        longitudinal_csv=args.longitudinal_csv,
        output_dir=args.output_dir,
    )
    for label, path in outputs.items():
        print(f"{label} -> {path}")
    return 0


def _cmd_rq3(args: argparse.Namespace) -> int:
    outputs = run_rq3_observational_analysis(
        longitudinal_csv=args.longitudinal_csv,
        attribution_csv=args.attribution_csv,
        output_dir=args.output_dir,
    )
    for label, path in outputs.items():
        print(f"{label} -> {path}")
    return 0


def _cmd_rq4(args: argparse.Namespace) -> int:
    outputs = run_rq4_lifecycle_analysis(
        longitudinal_csv=args.longitudinal_csv,
        output_dir=args.output_dir,
    )
    for label, path in outputs.items():
        print(f"{label} -> {path}")
    return 0


def _cmd_rq5_prep(args: argparse.Namespace) -> int:
    outputs = run_rq5_preparation(
        longitudinal_csv=args.longitudinal_csv,
        l1_paths=args.l1_paths,
        blobs_dir=args.blobs_dir,
        reference_summary_csv=args.reference_summary_csv,
        output_dir=args.output_dir,
    )
    for label, path in outputs.items():
        print(f"{label} -> {path}")
    return 0


def _cmd_born_stale_autopsy(args: argparse.Namespace) -> int:
    outputs = run_born_stale_autopsy(
        longitudinal_csv=args.longitudinal_csv,
        l1_paths=args.l1_paths,
        blobs_dir=args.blobs_dir,
        output_dir=args.output_dir,
        enable_llm=not args.skip_llm,
        max_llm_cases=args.max_llm_cases,
        ollama_url=args.ollama_url,
    )
    for label, path in outputs.items():
        print(f"{label} -> {path}")
    return 0


def _cmd_born_stale(args: argparse.Namespace) -> int:
    outputs = run_born_stale_audit(
        longitudinal_csv=args.longitudinal_csv,
        output_dir=args.output_dir,
    )
    for label, path in outputs.items():
        print(f"{label} -> {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="artifact_lab.experiments.truth_decay",
        description="Truth-decay RQ1 feasibility and RQ2 survival analysis",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    rq1 = sub.add_parser("rq1", help="RQ1 longitudinal feasibility (rebuild from L1)")
    rq1.add_argument("--l1", type=Path, action="append", dest="l1_paths")
    rq1.add_argument("--blobs-dir", type=Path, default=Path("data/blobs"))
    rq1.add_argument("--scratch", type=Path, default=Path("scratch"))
    rq1.add_argument("--output-dir", type=Path, default=DEFAULT_EXPORT_DIR)
    rq1.add_argument("--clone-timeout", type=int, default=180)
    rq1.add_argument("--max-files", type=int, default=None)
    rq1.set_defaults(func=_cmd_rq1)

    rq2 = sub.add_parser("rq2", help="RQ2 survival analysis from RQ1 longitudinal CSV")
    rq2.add_argument(
        "--longitudinal-csv",
        type=Path,
        default=DEFAULT_RQ1_LONGITUDINAL,
    )
    rq2.add_argument("--output-dir", type=Path, default=DEFAULT_RQ2_EXPORT)
    rq2.set_defaults(func=_cmd_rq2)

    rq3 = sub.add_parser("rq3", help="RQ3 observational integrity by maintenance regime")
    rq3.add_argument("--longitudinal-csv", type=Path, default=DEFAULT_RQ1_LONGITUDINAL)
    rq3.add_argument(
        "--attribution-csv",
        type=Path,
        default=Path("exports/truth_pilot/agent_commit_candidates.csv"),
    )
    rq3.add_argument("--output-dir", type=Path, default=DEFAULT_RQ3_EXPORT)
    rq3.set_defaults(func=_cmd_rq3)

    rq4 = sub.add_parser("rq4", help="RQ4 multi-state lifecycle dynamics")
    rq4.add_argument("--longitudinal-csv", type=Path, default=DEFAULT_RQ1_LONGITUDINAL)
    rq4.add_argument("--output-dir", type=Path, default=DEFAULT_RQ4_EXPORT)
    rq4.set_defaults(func=_cmd_rq4)

    rq5 = sub.add_parser("rq5-prep", help="RQ5 experimental corpus preparation (no agent runs)")
    rq5.add_argument("--longitudinal-csv", type=Path, default=DEFAULT_RQ1_LONGITUDINAL)
    rq5.add_argument("--l1", type=Path, action="append", dest="l1_paths")
    rq5.add_argument("--blobs-dir", type=Path, default=Path("data/blobs"))
    rq5.add_argument(
        "--reference-summary-csv",
        type=Path,
        default=Path("exports/truth_pilot/reference_summary.csv"),
    )
    rq5.add_argument("--output-dir", type=Path, default=DEFAULT_RQ5_EXPORT)
    rq5.set_defaults(func=_cmd_rq5_prep)

    audit = sub.add_parser("born-stale-audit", help="Audit never-verified (born-stale) references")
    audit.add_argument("--longitudinal-csv", type=Path, default=DEFAULT_RQ1_LONGITUDINAL)
    audit.add_argument("--output-dir", type=Path, default=DEFAULT_RQ2_EXPORT)
    audit.set_defaults(func=_cmd_born_stale)

    autopsy = sub.add_parser("born-stale-autopsy", help="Born-stale taxonomy autopsy with dual LLM judges")
    autopsy.add_argument("--longitudinal-csv", type=Path, default=DEFAULT_RQ1_LONGITUDINAL)
    autopsy.add_argument("--l1", type=Path, action="append", dest="l1_paths")
    autopsy.add_argument("--blobs-dir", type=Path, default=Path("data/blobs"))
    autopsy.add_argument("--output-dir", type=Path, default=DEFAULT_RQ2_EXPORT)
    autopsy.add_argument("--skip-llm", action="store_true", help="Deterministic heuristics only")
    autopsy.add_argument("--max-llm-cases", type=int, default=None)
    autopsy.add_argument("--ollama-url", default="http://127.0.0.1:11434/api/generate")
    autopsy.set_defaults(func=_cmd_born_stale_autopsy)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
