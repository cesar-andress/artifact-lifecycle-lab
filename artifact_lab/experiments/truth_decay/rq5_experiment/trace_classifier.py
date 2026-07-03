"""Automatic trace behavior classification for RQ5."""

from __future__ import annotations

from collections import Counter

from artifact_lab.experiments.truth_decay.rq5_experiment.models import AgentRunResult, ExperimentCase

TRACE_CLASSES = (
    "instruction_read",
    "instruction_ignored",
    "instruction_followed",
    "instruction_contradicted",
    "hallucinated_path",
    "hallucinated_command",
    "recovered_without_help",
    "manual_correction_by_agent",
    "tool_failure",
    "unknown",
)


def classify_run_trace(*, result: AgentRunResult, case: ExperimentCase) -> str:
    if result.error_message:
        return "tool_failure"
    if not result.read_instruction:
        return "instruction_ignored"
    if result.repaired_reference:
        return "manual_correction_by_agent"
    if result.detected_inconsistency:
        return "instruction_contradicted"
    if result.followed_reference and result.success:
        return "instruction_followed"
    if result.followed_reference and not result.success and result.condition == "B":
        return "hallucinated_path"
    if result.read_instruction and not result.followed_reference:
        return "instruction_ignored"
    if result.success and result.condition == "B":
        return "recovered_without_help"
    if result.read_instruction:
        return "instruction_read"
    return "unknown"


def apply_trace_classifications(
    *,
    results: list[AgentRunResult],
    cases: list[ExperimentCase],
) -> list[AgentRunResult]:
    case_map = {case.case_id: case for case in cases}
    updated: list[AgentRunResult] = []
    for result in results:
        case = case_map[result.case_id]
        classification = classify_run_trace(result=result, case=case)
        result.trace_classification = classification
        updated.append(result)
    return updated


def trace_class_frequencies(results: list[AgentRunResult]) -> list[dict]:
    rows: list[dict] = []
    grouped: dict[tuple[str, str], Counter[str]] = {}
    for result in results:
        key = (result.condition, result.agent_id)
        grouped.setdefault(key, Counter())
        grouped[key][result.trace_classification or "unknown"] += 1

    for (condition, agent_id), counter in sorted(grouped.items()):
        total = sum(counter.values()) or 1
        for label in TRACE_CLASSES:
            count = counter.get(label, 0)
            if count == 0:
                continue
            rows.append(
                {
                    "condition": condition,
                    "agent_id": agent_id,
                    "trace_class": label,
                    "count": count,
                    "frequency": round(count / total, 6),
                    "n_runs": total,
                }
            )
    return rows


def failure_mode_rows(results: list[AgentRunResult]) -> list[dict]:
    rows: list[dict] = []
    for result in results:
        if result.success:
            mode = "success"
        elif not result.tests_passing:
            mode = "tests_failed"
        elif not result.compilation_success:
            mode = "compile_failed"
        elif result.tool_failures:
            mode = "tool_failure"
        elif result.error_message:
            mode = "agent_error"
        else:
            mode = "other_failure"
        row = result.to_row()
        row["failure_mode"] = mode
        rows.append(row)
    return rows
