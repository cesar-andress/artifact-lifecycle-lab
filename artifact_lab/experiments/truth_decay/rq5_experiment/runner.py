"""RQ5 experiment orchestration."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from artifact_lab.experiments.truth_decay.rq5_experiment.agents.base import AgentRunner
from artifact_lab.experiments.truth_decay.rq5_experiment.agents.recording import RecordingAgent
from artifact_lab.experiments.truth_decay.rq5_experiment.evaluation import evaluate_run
from artifact_lab.experiments.truth_decay.rq5_experiment.models import DEFAULT_CONDITIONS_AB, AgentRunResult, ExperimentCase
from artifact_lab.experiments.truth_decay.rq5_experiment.workspace import prepared_workspace, write_instruction_to_workspace
from artifact_lab.store.blobs import BlobStore


def run_experiment_matrix(
    *,
    cases: list[ExperimentCase],
    agents: list[AgentRunner],
    scratch_dir: Path,
    traces_dir: Path,
    blob_store: BlobStore,
    replicates: int = 1,
    conditions: tuple[str, ...] = DEFAULT_CONDITIONS_AB,
    run_tests: bool = False,
    use_git_workspaces: bool = True,
    clone_timeout: int = 180,
) -> list[AgentRunResult]:
    """Execute full condition × case × agent × replicate matrix."""
    results: list[AgentRunResult] = []
    for case in cases:
        for condition in conditions:
            for agent in agents:
                recorder = RecordingAgent(agent, traces_dir)
                for replicate_id in range(1, replicates + 1):
                    if use_git_workspaces:
                        with prepared_workspace(
                            case=case,
                            condition=condition,
                            scratch_dir=scratch_dir,
                            blob_store=blob_store,
                            clone_timeout=clone_timeout,
                        ) as workspace:
                            raw = recorder.run(
                                case=case,
                                condition=condition,
                                workspace=workspace,
                                replicate_id=replicate_id,
                            )
                            result = evaluate_run(
                                case=case,
                                workspace=workspace,
                                agent_result=raw,
                                run_tests=run_tests,
                            )
                    else:
                        workspace = scratch_dir / f"local_{case.case_id}_{condition}"
                        workspace.mkdir(parents=True, exist_ok=True)
                        write_instruction_to_workspace(
                            workspace=workspace,
                            case=case,
                            condition=condition,
                            blob_store=blob_store,
                        )
                        raw = recorder.run(
                            case=case,
                            condition=condition,
                            workspace=workspace,
                            replicate_id=replicate_id,
                        )
                        result = evaluate_run(
                            case=case,
                            workspace=workspace,
                            agent_result=raw,
                            run_tests=run_tests,
                        )
                    results.append(result)
    return results


def dataset_rows(
    *,
    cases: list[ExperimentCase],
    results: list[AgentRunResult],
) -> list[dict]:
    case_map = {case.case_id: case for case in cases}
    rows: list[dict] = []
    for result in results:
        case = case_map[result.case_id]
        row = result.to_row()
        row.update(
            {
                "spec_id": case.spec_id,
                "repo_id": case.repo_id,
                "repo_url": case.repo_url,
                "instruction_path": case.instruction_path,
                "task_commit_sha": case.task_commit_sha,
                "anchor_reference": case.anchor_reference,
                "confirmed_false": case.confirmed_false,
                "test_command": case.test_command,
            }
        )
        rows.append(row)
    return rows


def case_manifest_rows(cases: list[ExperimentCase]) -> list[dict]:
    return [asdict(case) for case in cases]
