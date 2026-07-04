"""CLI for RQ5 v2 factorial experiment infrastructure."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from artifact_lab.experiments.rq5_v2.models import DEFAULT_AGENTS
from artifact_lab.experiments.rq5_v2.phase0_relaunch import DEFAULT_REPAIRED_MANIFEST, DEFAULT_VIABILITY_CSV
from artifact_lab.experiments.rq5_v2.run import DEFAULT_EXPORT_DIR, build_experiment_plan, plan_dry_run_results
from artifact_lab.experiments.rq5_v2.phase0_audit import audit_phase0_plan
from artifact_lab.experiments.rq5_v2.phase0_run import run_phase0_calibration


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="RQ5 v2 factorial experiment infrastructure (no agent execution by default)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build-plan", help="Build case manifest and run plan")
    build.add_argument("--output-dir", type=Path, default=DEFAULT_EXPORT_DIR)
    build.add_argument("--max-cases", type=int, default=20)
    build.add_argument("--replicates", type=int, default=3)
    build.add_argument("--seed", type=int, default=42)
    build.add_argument("--agents", nargs="+", default=list(DEFAULT_AGENTS))
    build.set_defaults(func=_cmd_build)

    dry = sub.add_parser("dry-run-ledger", help="Write planned-only dry-run result stubs")
    dry.add_argument("--output-dir", type=Path, default=DEFAULT_EXPORT_DIR)
    dry.set_defaults(func=_cmd_dry)

    agents = sub.add_parser("agents", help="List registered and available CLI agents")
    agents.set_defaults(func=_cmd_agents)

    audit = sub.add_parser("audit-phase0", help="Audit Phase 0 calibration plan (no agents)")
    audit.add_argument("--manifest", type=Path, default=DEFAULT_EXPORT_DIR / "factorial_case_manifest.json")
    audit.add_argument("--output-dir", type=Path, default=DEFAULT_EXPORT_DIR)
    audit.add_argument("--scratch-dir", type=Path, default=Path("scratch"))
    audit.set_defaults(func=_cmd_audit_phase0)

    prepare = sub.add_parser(
        "prepare-phase0-relaunch",
        help="Prepare Phase 0 relaunch plan from repaired manifest (no agents)",
    )
    prepare.add_argument("--output-dir", type=Path, default=DEFAULT_EXPORT_DIR)
    prepare.add_argument("--manifest", type=Path, default=DEFAULT_REPAIRED_MANIFEST)
    prepare.add_argument("--viability-csv", type=Path, default=DEFAULT_VIABILITY_CSV)
    prepare.add_argument("--seed", type=int, default=42)
    prepare.set_defaults(func=_cmd_prepare_relaunch)

    phase0 = sub.add_parser("run-phase0", help="Run Phase 0 calibration (T+L only, 60 runs)")
    phase0.add_argument("--output-dir", type=Path, default=DEFAULT_EXPORT_DIR)
    phase0.add_argument("--manifest", type=Path, default=DEFAULT_REPAIRED_MANIFEST)
    phase0.add_argument("--viability-csv", type=Path, default=DEFAULT_VIABILITY_CSV)
    phase0.add_argument("--audit-csv", type=Path, default=DEFAULT_EXPORT_DIR / "phase0_case_audit.csv")
    phase0.add_argument("--scratch-dir", type=Path, default=Path("scratch"))
    phase0.add_argument("--seed", type=int, default=42)
    phase0.add_argument("--preflight-only", action="store_true", help="Verify gates without executing agents")
    phase0.add_argument("--prepare-only", action="store_true", help="Build relaunch plan only (no agents)")
    phase0.add_argument("--analyze-only", action="store_true", help="Recompute exports from existing results")
    phase0.set_defaults(func=_cmd_run_phase0)

    args = parser.parse_args(argv)
    return args.func(args)


def _cmd_build(args: argparse.Namespace) -> int:
    paths = build_experiment_plan(
        output_dir=args.output_dir,
        max_cases=args.max_cases,
        agents=tuple(args.agents),
        replicates=args.replicates,
        seed=args.seed,
    )
    for label, path in paths.items():
        print(f"{label} -> {path}")
    return 0


def _cmd_dry(args: argparse.Namespace) -> int:
    path = plan_dry_run_results(output_dir=args.output_dir)
    print(f"results_dry_run -> {path}")
    return 0


def _cmd_agents(_: argparse.Namespace) -> int:
    from artifact_lab.experiments.rq5_v2.agents.registry import REGISTERED_AGENTS, discover_available_agents

    print("Registered:", ", ".join(sorted(REGISTERED_AGENTS)))
    available = discover_available_agents()
    print("Available:", ", ".join(available) if available else "(none detected on PATH)")
    return 0


def _cmd_audit_phase0(args: argparse.Namespace) -> int:
    paths = audit_phase0_plan(
        manifest_path=args.manifest,
        output_dir=args.output_dir,
        scratch_dir=args.scratch_dir,
    )
    for label, path in paths.items():
        print(f"{label} -> {path}")
    return 0


def _cmd_prepare_relaunch(args: argparse.Namespace) -> int:
    from artifact_lab.experiments.rq5_v2.phase0_relaunch import prepare_phase0_relaunch

    paths = prepare_phase0_relaunch(
        output_dir=args.output_dir,
        manifest_path=args.manifest,
        viability_csv=args.viability_csv,
        seed=args.seed,
    )
    for label, path in paths.items():
        print(f"{label} -> {path}")
    return 0


def _cmd_run_phase0(args: argparse.Namespace) -> int:
    from artifact_lab.experiments.rq5_v2.phase0_run import analyze_phase0_results

    if args.analyze_only:
        paths = analyze_phase0_results(output_dir=args.output_dir, manifest_path=args.manifest)
    else:
        paths = run_phase0_calibration(
            output_dir=args.output_dir,
            manifest_path=args.manifest,
            audit_csv=args.audit_csv,
            viability_csv=args.viability_csv,
            scratch_dir=args.scratch_dir,
            execute=not args.preflight_only and not args.prepare_only,
            seed=args.seed,
            preflight_only=args.preflight_only,
            prepare_only=args.prepare_only,
        )
    for label, path in paths.items():
        print(f"{label} -> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
