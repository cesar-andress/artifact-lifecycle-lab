"""Orchestration entrypoints for RQ5 v2 factorial infrastructure."""

from __future__ import annotations

from pathlib import Path

from artifact_lab.experiments.rq5_v2.agents.registry import discover_available_agents
from artifact_lab.experiments.rq5_v2.case_builder import build_factorial_cases
from artifact_lab.experiments.rq5_v2.manifest import (
    load_case_manifest,
    load_config,
    load_run_plan_csv,
    write_experiment_bundle,
)
from artifact_lab.experiments.rq5_v2.models import DEFAULT_AGENTS, ExperimentConfig
from artifact_lab.experiments.rq5_v2.plan import build_run_plan
from artifact_lab.experiments.rq5_v2.runner import dry_run_result, run_factorial_matrix
from artifact_lab.store.blobs import BlobStore

DEFAULT_EXPORT_DIR = Path("exports/rq5_v2_factorial")


def build_experiment_plan(
    *,
    output_dir: Path = DEFAULT_EXPORT_DIR,
    max_cases: int | None = 20,
    agents: tuple[str, ...] = DEFAULT_AGENTS,
    replicates: int = 3,
    seed: int = 42,
) -> dict[str, Path]:
    """Build case manifest + run plan without executing agents."""
    cases = build_factorial_cases(max_cases=max_cases)
    config = ExperimentConfig(
        agents=agents,
        replicates=replicates,
        allow_execute=False,
        metadata={
            "available_agents": discover_available_agents(),
            "seed": seed,
        },
    )
    plan = build_run_plan(cases=cases, config=config, seed=seed)
    return write_experiment_bundle(
        cases=cases,
        plan=plan,
        config=config,
        output_dir=output_dir,
    )


def plan_dry_run_results(
    *,
    output_dir: Path = DEFAULT_EXPORT_DIR,
) -> Path:
    """Write dry-run stub results for the full planned matrix (no agents)."""
    cases = load_case_manifest(output_dir / "factorial_case_manifest.json")
    plan = load_run_plan_csv(output_dir / "run_plan.csv")
    config = load_config(output_dir / "experiment_config.json")

    results_csv = output_dir / "results_dry_run.csv"
    results_csv.unlink(missing_ok=True)

    run_factorial_matrix(
        cases=cases,
        plan=plan,
        config=config,
        blob_store=BlobStore(Path("data/blobs")),
        scratch_dir=Path("scratch"),
        results_csv=results_csv,
        traces_dir=output_dir / "traces_dry_run",
        execute=False,
    )
    return results_csv
