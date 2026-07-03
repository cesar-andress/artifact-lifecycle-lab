"""Post-run evaluation for RQ5 experiment."""

from __future__ import annotations

from pathlib import Path

from artifact_lab.experiments.truth_decay.rq5_experiment.models import AgentRunResult, ExperimentCase
from artifact_lab.experiments.truth_decay.rq5_experiment.workspace import run_shell_command


def evaluate_run(
    *,
    case: ExperimentCase,
    workspace: Path,
    agent_result: AgentRunResult,
    run_tests: bool = True,
    test_timeout: int = 600,
) -> AgentRunResult:
    """Augment agent result with objective test/compile signals from workspace."""
    tests_passing = agent_result.tests_passing
    compilation_success = agent_result.compilation_success
    tool_failures = agent_result.tool_failures
    execution_time = agent_result.execution_time_seconds

    if run_tests and case.test_command:
        code, elapsed = run_shell_command(case.test_command, cwd=workspace, timeout=test_timeout)
        tests_passing = code == 0
        execution_time += elapsed
        if code != 0:
            tool_failures += 1

    success = agent_result.success and tests_passing and compilation_success
    return AgentRunResult(
        agent_id=agent_result.agent_id,
        condition=agent_result.condition,
        case_id=agent_result.case_id,
        replicate_id=agent_result.replicate_id,
        success=success,
        tests_passing=tests_passing,
        compilation_success=compilation_success,
        execution_time_seconds=round(execution_time, 3),
        files_modified=agent_result.files_modified,
        tool_failures=tool_failures,
        iterations=agent_result.iterations,
        commands_executed=agent_result.commands_executed + (1 if run_tests and case.test_command else 0),
        repository_changes=agent_result.repository_changes,
        read_instruction=agent_result.read_instruction,
        followed_reference=agent_result.followed_reference,
        ignored_reference=agent_result.ignored_reference,
        detected_inconsistency=agent_result.detected_inconsistency,
        repaired_reference=agent_result.repaired_reference,
        trace_events=agent_result.trace_events,
        error_message=agent_result.error_message,
        tool_invocations=agent_result.tool_invocations,
        patch_size=agent_result.patch_size,
        token_usage=agent_result.token_usage,
        cost_usd=agent_result.cost_usd,
        trace_classification=agent_result.trace_classification,
    )
