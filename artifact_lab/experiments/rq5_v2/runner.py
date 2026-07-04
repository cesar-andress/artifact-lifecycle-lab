"""Factorial experiment runner (execution gated by default)."""

from __future__ import annotations

import os
from pathlib import Path

from artifact_lab.experiments.rq5_v2.agents.registry import build_agents
from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.rq5_v2.evaluation import evaluate_factorial_run
from artifact_lab.experiments.rq5_v2.phase0_trace import enrich_result_from_trace
from artifact_lab.experiments.rq5_v2.factors import levels_for_cell
from artifact_lab.experiments.rq5_v2.ledger import append_result, pending_entries
from artifact_lab.experiments.rq5_v2.models import ExperimentConfig, FactorialCase, FactorialRunResult, RunPlanEntry
from artifact_lab.experiments.rq5_v2.phase0_setup import CaseSetupSpec, run_case_setup
from artifact_lab.experiments.rq5_v2.workspace import prepared_factorial_workspace
from artifact_lab.store.blobs import BlobStore

EXECUTE_ENV_VAR = "RQ5_V2_ALLOW_EXECUTE"


class ExecutionNotAllowedError(RuntimeError):
    """Raised when agent execution is attempted without explicit opt-in."""


def execution_allowed(*, config: ExperimentConfig) -> bool:
    return config.allow_execute or os.environ.get(EXECUTE_ENV_VAR, "") in ("1", "true", "yes")


def dry_run_result(entry: RunPlanEntry) -> FactorialRunResult:
    levels = levels_for_cell(entry.cell_code)
    return FactorialRunResult(
        run_id=entry.run_id,
        case_id=entry.case_id,
        cell_code=entry.cell_code,
        agent_id=entry.agent_id,
        replicate_id=entry.replicate_id,
        factor_a=levels.factor_a,
        factor_b=levels.factor_b,
        factor_c=levels.factor_c,
        dry_run=True,
        error_message="planned_only",
    )


def run_factorial_matrix(
    *,
    cases: list[FactorialCase],
    plan: list[RunPlanEntry],
    config: ExperimentConfig,
    blob_store: BlobStore,
    scratch_dir: Path,
    results_csv: Path,
    traces_dir: Path,
    execute: bool = False,
    run_tests: bool = True,
    clone_timeout: int = 180,
    max_runs: int | None = None,
    case_setup: dict[str, CaseSetupSpec] | None = None,
    setup_log: list | None = None,
    excluded_case_ids: set[str] | None = None,
) -> list[FactorialRunResult]:
    """
    Execute or dry-plan factorial runs.

    When `execute=False` (default), returns planned dry-run stubs without calling agents.
    When `execute=True`, requires `config.allow_execute` or `RQ5_V2_ALLOW_EXECUTE=1`.
    """
    if execute and not execution_allowed(config=config):
        raise ExecutionNotAllowedError(
            f"Agent execution blocked. Set config.allow_execute=True or env {EXECUTE_ENV_VAR}=1"
        )

    case_map = {c.case_id: c for c in cases}
    agents: list = build_agents(list(config.agents)) if execute else []
    agent_map = {a.agent_id: a for a in agents}

    todo = pending_entries(plan=plan, results_csv=results_csv)
    if max_runs is not None:
        todo = todo[:max_runs]

    traces_dir.mkdir(parents=True, exist_ok=True)
    results: list[FactorialRunResult] = []

    excluded = excluded_case_ids or set()
    failed_setup: set[str] = set()

    for entry in todo:
        case = case_map.get(entry.case_id)
        if case is None or entry.case_id in excluded or entry.case_id in failed_setup:
            continue

        if not execute:
            result = dry_run_result(entry)
            results.append(result)
            append_result(results_csv, result)
            continue

        agent = agent_map[entry.agent_id]
        with prepared_factorial_workspace(
            case=case,
            cell_code=entry.cell_code,
            scratch_dir=scratch_dir,
            blob_store=blob_store,
            clone_timeout=clone_timeout,
        ) as workspace:
            spec = (case_setup or {}).get(entry.case_id)
            if spec and spec.setup_command:
                setup_result = run_case_setup(
                    case_id=entry.case_id,
                    workspace=workspace,
                    setup_command=spec.setup_command,
                    execution_cwd=spec.execution_cwd,
                )
                if setup_log is not None:
                    setup_log.append(setup_result)
                if not setup_result.ok:
                    failed_setup.add(entry.case_id)
                    result = FactorialRunResult(
                        run_id=entry.run_id,
                        case_id=entry.case_id,
                        cell_code=entry.cell_code,
                        agent_id=entry.agent_id,
                        replicate_id=entry.replicate_id,
                        factor_a=entry.factor_a,
                        factor_b=entry.factor_b,
                        factor_c=entry.factor_c,
                        success=False,
                        dry_run=False,
                        error_message="setup_failed",
                    )
                    results.append(result)
                    append_result(results_csv, result)
                    continue
            raw = agent.run(
                case=case,
                cell_code=entry.cell_code,
                workspace=workspace,
                replicate_id=entry.replicate_id,
                run_id=entry.run_id,
            )
            result = evaluate_factorial_run(
                case=case,
                cell_code=entry.cell_code,
                workspace=workspace,
                result=raw,
                run_tests=run_tests,
            )
            trace_path = traces_dir / f"{entry.run_id}.jsonl"
            stdout_trace = getattr(raw, "_stdout_trace", "") or ""
            atomic_write_text(trace_path, stdout_trace)
            result.trace_path = str(trace_path)
            if not result.instruction_read or not result.anchor_attempted:
                row = enrich_result_from_trace(
                    case=case,
                    cell_code=entry.cell_code,
                    result_row=result.to_row(),
                    trace_path=trace_path,
                )
                for key in (
                    "instruction_read",
                    "read_instruction",
                    "anchor_attempted",
                    "commands_executed",
                    "iterations",
                    "tool_failures",
                    "cost_usd",
                    "token_usage",
                    "timed_out",
                ):
                    if key in row:
                        setattr(result, key, row[key])
            results.append(result)
            append_result(results_csv, result)

    return results
