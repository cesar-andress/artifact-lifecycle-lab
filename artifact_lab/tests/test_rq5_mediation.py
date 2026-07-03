"""Tests for RQ5 mediation audit."""

from __future__ import annotations

import json
from pathlib import Path

from artifact_lab.experiments.truth_decay.rq5_experiment.mediation_analysis import (
    CAUSAL_ROLES_B,
    classify_mediation,
    classify_mediation_b,
    mediation_by_condition_rows,
    mediation_flow_counts,
    reference_obstacle_encountered,
    reference_used_in_tool_call,
)
from artifact_lab.experiments.truth_decay.rq5_experiment.models import AgentRunResult, ExperimentCase, TraceEvent
from artifact_lab.experiments.truth_decay.run_rq5_mediation_analysis import run_rq5_mediation_analysis


def _case() -> ExperimentCase:
    return ExperimentCase(
        case_id="case1",
        spec_id="spec1",
        repo_id="repo1",
        repo_url="https://github.com/example/example",
        instruction_path="AGENTS.md",
        task_commit_sha="abc123",
        anchor_reference="src/missing.py",
        anchor_reference_type="path",
        condition_a_blob_sha="",
        condition_b_blob_sha="",
        born_stale_commit_sha="def456",
        truthful_commit_sha="abc123",
        task_prompt="Do task",
        test_command="pytest",
        selection_reason="test",
        confirmed_false=True,
        p1_sample=False,
    )


def _result(*, condition: str, success: bool, followed: bool, trace_class: str = "") -> AgentRunResult:
    return AgentRunResult(
        agent_id="claude_code",
        condition=condition,
        case_id="case1",
        replicate_id=1,
        success=success,
        tests_passing=success,
        compilation_success=True,
        execution_time_seconds=1.0,
        files_modified=0,
        tool_failures=0,
        iterations=1,
        commands_executed=1,
        repository_changes=0,
        read_instruction=True,
        followed_reference=followed,
        ignored_reference=not followed,
        detected_inconsistency=False,
        repaired_reference=False,
        trace_classification=trace_class,
    )


def test_reference_used_in_tool_call_detects_bash():
    events = [
        TraceEvent(
            timestamp="t1",
            event_type="Bash",
            payload={"input": {"command": "cat src/missing.py"}},
        )
    ]
    assert reference_used_in_tool_call(events, "src/missing.py") is True


def test_reference_obstacle_after_use():
    events = [
        TraceEvent(
            timestamp="t1",
            event_type="Bash",
            payload={"input": {"command": "ls src/missing.py"}},
        ),
        TraceEvent(
            timestamp="t2",
            event_type="tool_failure",
            payload={"content": "No such file or directory: src/missing.py"},
        ),
    ]
    assert reference_obstacle_encountered(events, "src/missing.py") is True


def test_classify_mediation_b_caused_failure():
    case = _case()
    events = [
        TraceEvent(timestamp="t1", event_type="read_instruction", payload={"path": "AGENTS.md"}),
        TraceEvent(
            timestamp="t2",
            event_type="Bash",
            payload={"input": {"command": "cat src/missing.py"}},
        ),
        TraceEvent(
            timestamp="t3",
            event_type="tool_failure",
            payload={"content": "File does not exist: src/missing.py"},
        ),
    ]
    result = _result(condition="B", success=False, followed=True, trace_class="hallucinated_path")
    row = classify_mediation_b(result=result, case=case, events=events)
    assert row.false_claim_used_in_tool_call is True
    assert row.false_claim_encountered_as_obstacle is True
    assert row.task_failed_because_of_false_claim is True
    assert row.causal_role == "false_claim_caused_failure"


def test_classify_mediation_b_not_load_bearing():
    case = _case()
    events = [
        TraceEvent(timestamp="t1", event_type="read_instruction", payload={"path": "AGENTS.md"}),
        TraceEvent(
            timestamp="t2",
            event_type="Read",
            payload={"input": {"file_path": "/tmp/AGENTS.md"}},
        ),
        TraceEvent(timestamp="t3", event_type="Bash", payload={"input": {"command": "pytest"}}),
    ]
    result = _result(condition="B", success=False, followed=False)
    row = classify_mediation_b(result=result, case=case, events=events)
    assert row.false_claim_ignored_after_reading is True
    assert row.causal_role == "uptake_but_not_load_bearing"


def test_classify_mediation_a_reference_usage():
    case = _case()
    events = [
        TraceEvent(timestamp="t1", event_type="read_instruction", payload={"path": "AGENTS.md"}),
        TraceEvent(
            timestamp="t2",
            event_type="Bash",
            payload={"input": {"command": "pytest src/missing.py"}},
        ),
    ]
    result = _result(condition="A", success=True, followed=True, trace_class="instruction_followed")
    row = classify_mediation(result=result, case=case, events=events)
    assert row.false_claim_present_in_instruction is False
    assert row.false_claim_used_in_tool_call is True
    assert row.causal_role == "reference_used_and_succeeded"


def test_mediation_by_condition_rows_include_roles():
    case = _case()
    rows = [
        classify_mediation_b(
            result=_result(condition="B", success=False, followed=True, trace_class="hallucinated_path"),
            case=case,
            events=[],
        ),
        classify_mediation(
            result=_result(condition="A", success=True, followed=True),
            case=case,
            events=[],
        ),
    ]
    by_condition = mediation_by_condition_rows(rows)
    assert any(r.get("row_type") == "causal_role" for r in by_condition)
    assert any(r.get("row_type") == "paired_comparison" for r in by_condition)


def test_mediation_flow_counts():
    case = _case()
    rows = [
        classify_mediation_b(
            result=_result(condition="B", success=False, followed=True, trace_class="hallucinated_path"),
            case=case,
            events=[],
        )
    ]
    flow = mediation_flow_counts(rows)
    assert flow["present"] == 1


def test_run_rq5_mediation_analysis_on_exports():
    results_csv = Path("exports/rq5_agent_impact/rq5_results.csv")
    if not results_csv.exists():
        return
    outputs = run_rq5_mediation_analysis(output_dir=Path("exports/rq5_agent_impact"))
    assert outputs["dataset_csv"].exists()
    assert outputs["summary_md"].exists()
    assert outputs["by_condition_csv"].exists()
    assert outputs["figure_mediation_flow"].exists()
