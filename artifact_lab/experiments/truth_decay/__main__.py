"""CLI for truth-decay RQ1 (feasibility) and RQ2 (survival)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from artifact_lab.experiments.truth_decay.run_born_stale_audit import run_born_stale_audit
from artifact_lab.experiments.truth_decay.run_born_stale_autopsy import run_born_stale_autopsy
from artifact_lab.experiments.truth_decay.run_cited_uncited_audit import run_cited_uncited_audit
from artifact_lab.experiments.truth_decay.run_gfc_confirmatory_audit import run_gfc_confirmatory_audit
from artifact_lab.experiments.truth_decay.run_rq2_failure_audit import run_rq2_failure_audit
from artifact_lab.experiments.truth_decay.run_rq1 import DEFAULT_EXPORT_DIR, DEFAULT_L1_PATHS, run_rq1_feasibility_study
from artifact_lab.experiments.truth_decay.run_rq2 import DEFAULT_RQ2_EXPORT, run_rq2_survival_analysis
from artifact_lab.experiments.truth_decay.run_rq3 import DEFAULT_EXPORT as DEFAULT_RQ3_EXPORT, run_rq3_observational_analysis
from artifact_lab.experiments.truth_decay.run_rq4 import DEFAULT_RQ4_EXPORT, run_rq4_lifecycle_analysis
from artifact_lab.experiments.truth_decay.run_rq5_causal_evidence import (
    DEFAULT_RQ5_CAUSAL_EXPORT,
    generate_rq5_outputs,
    run_rq5_causal_evidence,
    _load_existing_results,
)
from artifact_lab.experiments.truth_decay.run_rq5_experiment import (
    DEFAULT_RQ5_EXPERIMENT_EXPORT,
    run_rq5_experiment,
)
from artifact_lab.experiments.truth_decay.rq5_experiment.task_selection import select_experiment_cases
from artifact_lab.experiments.truth_decay.run_rq5_prep import DEFAULT_RQ5_EXPORT, run_rq5_preparation
from artifact_lab.experiments.truth_decay.run_rq5_mediation_analysis import run_rq5_mediation_analysis
from artifact_lab.experiments.truth_decay.run_rq5_uptake_analysis import run_rq5_uptake_analysis
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


def _cmd_rq5_mediation(args: argparse.Namespace) -> int:
    outputs = run_rq5_mediation_analysis(
        candidate_csv=args.candidate_csv,
        gfc_confirmatory_csv=args.gfc_confirmatory_csv,
        output_dir=args.output_dir,
        max_cases=args.max_cases,
        require_p1=args.require_p1,
    )
    for label, path in outputs.items():
        print(f"{label} -> {path}")
    return 0


def _cmd_rq5_uptake(args: argparse.Namespace) -> int:
    outputs = run_rq5_uptake_analysis(
        candidate_csv=args.candidate_csv,
        gfc_confirmatory_csv=args.gfc_confirmatory_csv,
        output_dir=args.output_dir,
        max_cases=args.max_cases,
        require_p1=args.require_p1,
    )
    for label, path in outputs.items():
        print(f"{label} -> {path}")
    return 0


def _cmd_rq5_report(args: argparse.Namespace) -> int:
    results_csv = args.output_dir / "rq5_results.csv"
    if not results_csv.exists():
        print(f"error: missing {results_csv}", file=sys.stderr)
        return 1
    cases = select_experiment_cases(
        candidate_csv=args.candidate_csv,
        gfc_confirmatory_csv=args.gfc_confirmatory_csv,
        max_cases=args.max_cases,
        require_p1=args.require_p1,
    )
    results = _load_existing_results(results_csv, cases)
    agents = sorted({result.agent_id for result in results})
    outputs = generate_rq5_outputs(
        cases=cases,
        results=results,
        output_dir=args.output_dir,
        agent_names=agents,
        replicates=args.replicates,
    )
    for label, path in outputs.items():
        print(f"{label} -> {path}")
    return 0


def _cmd_rq5_run(args: argparse.Namespace) -> int:
    outputs = run_rq5_causal_evidence(
        candidate_csv=args.candidate_csv,
        gfc_confirmatory_csv=args.gfc_confirmatory_csv,
        blobs_dir=args.blobs_dir,
        scratch_dir=args.scratch,
        output_dir=args.output_dir,
        agents=args.agents,
        replicates=args.replicates,
        max_cases=args.max_cases,
        require_p1=args.require_p1,
        run_tests=args.run_tests,
        use_git_workspaces=args.use_git_workspaces,
        clone_timeout=args.clone_timeout,
        resume=not args.no_resume,
    )
    for label, path in outputs.items():
        print(f"{label} -> {path}")
    return 0


def _cmd_rq5(args: argparse.Namespace) -> int:
    outputs = run_rq5_experiment(
        candidate_csv=args.candidate_csv,
        gfc_confirmatory_csv=args.gfc_confirmatory_csv,
        blobs_dir=args.blobs_dir,
        scratch_dir=args.scratch,
        output_dir=args.output_dir,
        agents=args.agents,
        replicates=args.replicates,
        max_cases=args.max_cases,
        require_p1=args.require_p1,
        run_tests=args.run_tests,
        use_git_workspaces=args.use_git_workspaces,
        clone_timeout=args.clone_timeout,
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


def _cmd_gfc_confirmatory_audit(args: argparse.Namespace) -> int:
    outputs = run_gfc_confirmatory_audit(
        taxonomy_csv=args.taxonomy_csv,
        output_dir=args.output_dir,
        enable_llm=not args.skip_llm,
        max_llm_cases=args.max_llm_cases,
        ollama_url=args.ollama_url,
    )
    for label, path in outputs.items():
        print(f"{label} -> {path}")
    return 0


def _cmd_cited_uncited_audit(args: argparse.Namespace) -> int:
    outputs = run_cited_uncited_audit(
        longitudinal_csv=args.longitudinal_csv,
        scratch_dir=args.scratch,
        output_dir=args.output_dir,
        max_cited_per_repo=args.max_cited_per_repo,
        seed=args.seed,
        clone_timeout=args.clone_timeout,
    )
    for label, path in outputs.items():
        print(f"{label} -> {path}")
    return 0


def _cmd_rq2_failure_audit(args: argparse.Namespace) -> int:
    outputs = run_rq2_failure_audit(
        survival_csv=args.survival_csv,
        longitudinal_csv=args.longitudinal_csv,
        born_stale_taxonomy_csv=args.born_stale_taxonomy_csv,
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

    rq5_prep = sub.add_parser("rq5-prep", help="RQ5 experimental corpus preparation (no agent runs)")
    rq5_prep.add_argument("--longitudinal-csv", type=Path, default=DEFAULT_RQ1_LONGITUDINAL)
    rq5_prep.add_argument("--l1", type=Path, action="append", dest="l1_paths")
    rq5_prep.add_argument("--blobs-dir", type=Path, default=Path("data/blobs"))
    rq5_prep.add_argument(
        "--reference-summary-csv",
        type=Path,
        default=Path("exports/truth_pilot/reference_summary.csv"),
    )
    rq5_prep.add_argument("--output-dir", type=Path, default=DEFAULT_RQ5_EXPORT)
    rq5_prep.set_defaults(func=_cmd_rq5_prep)

    rq5_report = sub.add_parser(
        "rq5-report",
        help="Regenerate RQ5 statistics/figures from existing rq5_results.csv",
    )
    rq5_report.add_argument(
        "--candidate-csv",
        type=Path,
        default=Path("exports/truth_decay_pilot/rq5_candidate_dataset.csv"),
    )
    rq5_report.add_argument(
        "--gfc-confirmatory-csv",
        type=Path,
        default=Path("exports/truth_decay_pilot/gfc_confirmatory_audit.csv"),
    )
    rq5_report.add_argument("--output-dir", type=Path, default=DEFAULT_RQ5_CAUSAL_EXPORT)
    rq5_report.add_argument("--replicates", type=int, default=3)
    rq5_report.add_argument("--max-cases", type=int, default=None)
    rq5_report.add_argument("--require-p1", action="store_true")
    rq5_report.set_defaults(func=_cmd_rq5_report)

    rq5_uptake = sub.add_parser(
        "rq5-uptake",
        help="Post-hoc RQ5 instruction uptake analysis from existing traces",
    )
    rq5_uptake.add_argument(
        "--candidate-csv",
        type=Path,
        default=Path("exports/truth_decay_pilot/rq5_candidate_dataset.csv"),
    )
    rq5_uptake.add_argument(
        "--gfc-confirmatory-csv",
        type=Path,
        default=Path("exports/truth_decay_pilot/gfc_confirmatory_audit.csv"),
    )
    rq5_uptake.add_argument("--output-dir", type=Path, default=DEFAULT_RQ5_CAUSAL_EXPORT)
    rq5_uptake.add_argument("--max-cases", type=int, default=None)
    rq5_uptake.add_argument("--require-p1", action="store_true")
    rq5_uptake.set_defaults(func=_cmd_rq5_uptake)

    rq5_mediation = sub.add_parser(
        "rq5-mediation",
        help="Post-hoc RQ5 null-result mediation audit from existing traces",
    )
    rq5_mediation.add_argument(
        "--candidate-csv",
        type=Path,
        default=Path("exports/truth_decay_pilot/rq5_candidate_dataset.csv"),
    )
    rq5_mediation.add_argument(
        "--gfc-confirmatory-csv",
        type=Path,
        default=Path("exports/truth_decay_pilot/gfc_confirmatory_audit.csv"),
    )
    rq5_mediation.add_argument("--output-dir", type=Path, default=DEFAULT_RQ5_CAUSAL_EXPORT)
    rq5_mediation.add_argument("--max-cases", type=int, default=None)
    rq5_mediation.add_argument("--require-p1", action="store_true")
    rq5_mediation.set_defaults(func=_cmd_rq5_mediation)

    rq5_run = sub.add_parser(
        "rq5-run",
        help="RQ5 causal evidence collection with real CLI agents (checkpoint/resume)",
    )
    rq5_run.add_argument(
        "--candidate-csv",
        type=Path,
        default=Path("exports/truth_decay_pilot/rq5_candidate_dataset.csv"),
    )
    rq5_run.add_argument(
        "--gfc-confirmatory-csv",
        type=Path,
        default=Path("exports/truth_decay_pilot/gfc_confirmatory_audit.csv"),
    )
    rq5_run.add_argument("--blobs-dir", type=Path, default=Path("data/blobs"))
    rq5_run.add_argument("--scratch", type=Path, default=Path("scratch"))
    rq5_run.add_argument("--output-dir", type=Path, default=DEFAULT_RQ5_CAUSAL_EXPORT)
    rq5_run.add_argument(
        "--agents",
        action="append",
        default=None,
        help="Agent ids (default: auto-detect claude_code/copilot_cli)",
    )
    rq5_run.add_argument("--replicates", type=int, default=3)
    rq5_run.add_argument("--max-cases", type=int, default=None)
    rq5_run.add_argument("--require-p1", action="store_true")
    rq5_run.add_argument("--run-tests", action="store_true", default=True)
    rq5_run.add_argument("--no-run-tests", action="store_false", dest="run_tests")
    rq5_run.add_argument("--use-git-workspaces", action="store_true", default=True)
    rq5_run.add_argument("--no-git-workspaces", action="store_false", dest="use_git_workspaces")
    rq5_run.add_argument("--clone-timeout", type=int, default=180)
    rq5_run.add_argument("--no-resume", action="store_true", help="Ignore existing rq5_results.csv")
    rq5_run.set_defaults(func=_cmd_rq5_run)

    rq5 = sub.add_parser("rq5", help="RQ5 causal agent-impact experiment (stub/infrastructure)")
    rq5.add_argument(
        "--candidate-csv",
        type=Path,
        default=Path("exports/truth_decay_pilot/rq5_candidate_dataset.csv"),
    )
    rq5.add_argument(
        "--gfc-confirmatory-csv",
        type=Path,
        default=Path("exports/truth_decay_pilot/gfc_confirmatory_audit.csv"),
    )
    rq5.add_argument("--blobs-dir", type=Path, default=Path("data/blobs"))
    rq5.add_argument("--scratch", type=Path, default=Path("scratch"))
    rq5.add_argument("--output-dir", type=Path, default=DEFAULT_RQ5_EXPERIMENT_EXPORT)
    rq5.add_argument("--agents", action="append", default=["stub"])
    rq5.add_argument("--replicates", type=int, default=1)
    rq5.add_argument("--max-cases", type=int, default=None)
    rq5.add_argument("--require-p1", action="store_true")
    rq5.add_argument("--run-tests", action="store_true")
    rq5.add_argument("--use-git-workspaces", action="store_true")
    rq5.add_argument("--clone-timeout", type=int, default=180)
    rq5.set_defaults(func=_cmd_rq5)

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

    rq2_audit = sub.add_parser(
        "rq2-failure-audit",
        help="Audit RQ2 post-verification first_missing events",
    )
    rq2_audit.add_argument(
        "--survival-csv",
        type=Path,
        default=Path("exports/truth_decay_pilot/rq2_survival.csv"),
    )
    rq2_audit.add_argument("--longitudinal-csv", type=Path, default=DEFAULT_RQ1_LONGITUDINAL)
    rq2_audit.add_argument(
        "--born-stale-taxonomy-csv",
        type=Path,
        default=Path("exports/truth_decay_pilot/born_stale_taxonomy.csv"),
    )
    rq2_audit.add_argument("--l1", type=Path, action="append", dest="l1_paths")
    rq2_audit.add_argument("--blobs-dir", type=Path, default=Path("data/blobs"))
    rq2_audit.add_argument("--output-dir", type=Path, default=DEFAULT_RQ2_EXPORT)
    rq2_audit.add_argument("--skip-llm", action="store_true", help="Deterministic heuristics only")
    rq2_audit.add_argument("--max-llm-cases", type=int, default=None)
    rq2_audit.add_argument("--ollama-url", default="http://127.0.0.1:11434/api/generate")
    rq2_audit.set_defaults(func=_cmd_rq2_failure_audit)

    gfc_audit = sub.add_parser(
        "gfc-confirmatory-audit",
        help="Confirmatory audit of born-stale genuine_false_claim labels",
    )
    gfc_audit.add_argument(
        "--taxonomy-csv",
        type=Path,
        default=Path("exports/truth_decay_pilot/born_stale_taxonomy.csv"),
    )
    gfc_audit.add_argument("--output-dir", type=Path, default=DEFAULT_RQ2_EXPORT)
    gfc_audit.add_argument("--skip-llm", action="store_true", help="Deterministic heuristics only")
    gfc_audit.add_argument("--max-llm-cases", type=int, default=None)
    gfc_audit.add_argument("--ollama-url", default="http://127.0.0.1:11434/api/generate")
    gfc_audit.set_defaults(func=_cmd_gfc_confirmatory_audit)

    cited_audit = sub.add_parser(
        "cited-uncited-audit",
        help="Contrast git churn of cited vs matched uncited paths",
    )
    cited_audit.add_argument("--longitudinal-csv", type=Path, default=DEFAULT_RQ1_LONGITUDINAL)
    cited_audit.add_argument("--scratch", type=Path, default=Path("scratch"))
    cited_audit.add_argument("--output-dir", type=Path, default=DEFAULT_RQ2_EXPORT)
    cited_audit.add_argument("--max-cited-per-repo", type=int, default=40)
    cited_audit.add_argument("--seed", type=int, default=42)
    cited_audit.add_argument("--clone-timeout", type=int, default=180)
    cited_audit.set_defaults(func=_cmd_cited_uncited_audit)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
