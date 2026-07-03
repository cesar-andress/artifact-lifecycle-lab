"""CLI for RQ5 v2 factorial experiment infrastructure."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from artifact_lab.experiments.rq5_v2.models import DEFAULT_AGENTS
from artifact_lab.experiments.rq5_v2.run import DEFAULT_EXPORT_DIR, build_experiment_plan, plan_dry_run_results
from artifact_lab.experiments.rq5_v2.phase0_audit import audit_phase0_plan


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


if __name__ == "__main__":
    sys.exit(main())
