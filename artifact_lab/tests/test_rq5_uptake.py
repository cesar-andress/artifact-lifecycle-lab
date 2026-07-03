"""Tests for RQ5 uptake analysis."""

from __future__ import annotations

import json
from pathlib import Path

from artifact_lab.experiments.truth_decay.rq5_experiment.models import AgentRunResult, ExperimentCase, TraceEvent
from artifact_lab.experiments.truth_decay.rq5_experiment.uptake_analysis import (
    classify_uptake,
    load_trace_events,
    uptake_by_condition_rows,
    uptake_flow_counts,
)
from artifact_lab.experiments.truth_decay.run_rq5_uptake_analysis import run_rq5_uptake_analysis


def _sample_case() -> ExperimentCase:
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


def _result(*, condition: str, success: bool, followed: bool) -> AgentRunResult:
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
        trace_classification="instruction_followed" if followed and success else "instruction_read",
    )


def test_classify_uptake_false_claim_used_in_b():
    case = _sample_case()
    events = [
        TraceEvent(timestamp="t1", event_type="read_instruction", payload={"path": "AGENTS.md"}),
        TraceEvent(
            timestamp="t2",
            event_type="Read",
            payload={"input": {"file_path": "/tmp/AGENTS.md"}},
        ),
        TraceEvent(
            timestamp="t3",
            event_type="Bash",
            payload={"input": {"command": "cat src/missing.py"}},
        ),
    ]
    result = _result(condition="B", success=False, followed=True)
    row = classify_uptake(result=result, case=case, events=events)
    assert row.instruction_read is True
    assert row.instruction_quoted is True
    assert row.instruction_followed is True
    assert row.false_claim_encountered is True
    assert row.false_claim_used is True
    assert row.false_claim_ignored is False


def test_classify_uptake_ignored_false_claim_in_b():
    case = _sample_case()
    events = [
        TraceEvent(timestamp="t1", event_type="read_instruction", payload={"path": "AGENTS.md"}),
        TraceEvent(
            timestamp="t2",
            event_type="Read",
            payload={"input": {"file_path": "/tmp/AGENTS.md"}},
        ),
        TraceEvent(
            timestamp="t3",
            event_type="Bash",
            payload={"input": {"command": "pytest"}},
        ),
    ]
    result = _result(condition="B", success=True, followed=False)
    row = classify_uptake(result=result, case=case, events=events)
    assert row.false_claim_encountered is True
    assert row.false_claim_used is False
    assert row.false_claim_ignored is True


def test_classify_uptake_no_false_claim_fields_in_a():
    case = _sample_case()
    events = [
        TraceEvent(timestamp="t1", event_type="read_instruction", payload={"path": "AGENTS.md"}),
    ]
    result = _result(condition="A", success=True, followed=True)
    row = classify_uptake(result=result, case=case, events=events)
    assert row.false_claim_encountered is False
    assert row.false_claim_used is False
    assert row.false_claim_corrected is False
    assert row.false_claim_ignored is False


def test_uptake_by_condition_paired_rows():
    case = _sample_case()
    rows = [
        classify_uptake(result=_result(condition="A", success=True, followed=True), case=case, events=[]),
        classify_uptake(result=_result(condition="B", success=False, followed=True), case=case, events=[]),
        classify_uptake(result=_result(condition="A", success=False, followed=False), case=case, events=[]),
        classify_uptake(result=_result(condition="B", success=True, followed=False), case=case, events=[]),
    ]
    by_condition = uptake_by_condition_rows(rows)
    paired = [r for r in by_condition if r.get("row_type") == "paired_AB"]
    assert paired
    all_row = next(r for r in paired if r["stratum"] == "all")
    assert all_row["n_A"] == 2
    assert all_row["n_B"] == 2


def test_load_trace_events_roundtrip(tmp_path: Path):
    trace = tmp_path / "trace.jsonl"
    trace.write_text(
        json.dumps(
            {
                "timestamp": "2026-01-01T00:00:00+00:00",
                "event_type": "read_instruction",
                "payload": {"path": "AGENTS.md"},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    events = load_trace_events(trace)
    assert len(events) == 1
    assert events[0].event_type == "read_instruction"


def test_uptake_flow_counts():
    case = _sample_case()
    rows = [
        classify_uptake(result=_result(condition="A", success=True, followed=True), case=case, events=[]),
        classify_uptake(result=_result(condition="B", success=False, followed=False), case=case, events=[]),
    ]
    flow = uptake_flow_counts(rows)
    assert flow["A"]["instruction_read"] == 1
    assert flow["B"]["instruction_followed"] == 0


def test_run_rq5_uptake_analysis_on_exports():
    results_csv = Path("exports/rq5_agent_impact/rq5_results.csv")
    if not results_csv.exists():
        return
    outputs = run_rq5_uptake_analysis(output_dir=Path("exports/rq5_agent_impact"))
    assert outputs["dataset_csv"].exists()
    assert outputs["by_condition_csv"].exists()
    assert outputs["analysis_md"].exists()
    assert outputs["figure_uptake_flow"].exists()
