"""Tests for RQ5 causal evidence collection with real agent adapters."""

from __future__ import annotations

import csv
from pathlib import Path
from unittest.mock import patch

from artifact_lab.experiments.truth_decay.rq5_experiment.agents.registry import (
    discover_available_agent_names,
)
from artifact_lab.experiments.truth_decay.rq5_experiment.causal_statistics import (
    compute_causal_statistics,
    mcnemar_exact_p,
)
from artifact_lab.experiments.truth_decay.rq5_experiment.models import AgentRunResult, ExperimentCase
from artifact_lab.experiments.truth_decay.rq5_experiment.trace_classifier import (
    apply_trace_classifications,
    classify_run_trace,
    trace_class_frequencies,
)
from artifact_lab.experiments.truth_decay.run_rq5_causal_evidence import (
    run_causal_matrix_with_checkpoint,
)
from artifact_lab.experiments.truth_decay.rq5_experiment.agents.stub import StubAgent
from artifact_lab.store.blobs import BlobStore


def _sample_case(case_id: str = "case1") -> ExperimentCase:
    return ExperimentCase(
        case_id=case_id,
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


def _result(
    *,
    condition: str,
    success: bool,
    replicate_id: int = 1,
    agent_id: str = "stub_agent_v1",
) -> AgentRunResult:
    return AgentRunResult(
        agent_id=agent_id,
        condition=condition,
        case_id="case1",
        replicate_id=replicate_id,
        success=success,
        tests_passing=success,
        compilation_success=True,
        execution_time_seconds=1.0,
        files_modified=0,
        tool_failures=0 if success else 1,
        iterations=1,
        commands_executed=1,
        repository_changes=0,
        read_instruction=True,
        followed_reference=success,
        ignored_reference=not success,
        detected_inconsistency=False,
        repaired_reference=False,
    )


def test_mcnemar_exact_p_symmetric():
    assert mcnemar_exact_p(0, 0) == 1.0
    assert 0.0 < mcnemar_exact_p(3, 0) < 1.0


def test_trace_classifier_labels():
    case = _sample_case()
    followed = _result(condition="A", success=True)
    followed.trace_classification = classify_run_trace(result=followed, case=case)
    assert followed.trace_classification == "instruction_followed"

    ignored = _result(condition="B", success=False)
    ignored.read_instruction = False
    ignored.followed_reference = False
    ignored.ignored_reference = True
    ignored.tool_failures = 0
    ignored.trace_classification = classify_run_trace(result=ignored, case=case)
    assert ignored.trace_classification == "instruction_ignored"

    tests_failed = _result(condition="A", success=False)
    tests_failed.tool_failures = 2
    tests_failed.tests_passing = False
    tests_failed.followed_reference = True
    tests_failed.ignored_reference = False
    tests_failed.error_message = ""
    tests_failed.trace_classification = classify_run_trace(result=tests_failed, case=case)
    assert tests_failed.trace_classification == "instruction_read"


def test_causal_statistics_paired_difference():
    results = [
        _result(condition="A", success=True, replicate_id=1),
        _result(condition="B", success=False, replicate_id=1),
        _result(condition="A", success=True, replicate_id=2),
        _result(condition="B", success=False, replicate_id=2),
    ]
    stats = compute_causal_statistics(results, bootstrap_iterations=100, seed=0)
    diff = next(row for row in stats if row.estimand == "paired_success_difference_a_minus_b")
    assert diff.value == 1.0
    mcnemar = next(row for row in stats if row.estimand == "mcnemar_p_value")
    assert mcnemar.n_a_only_success == 2


def test_checkpoint_skips_completed_runs(tmp_path: Path):
    blob_store = BlobStore(tmp_path / "blobs")
    blob_a = blob_store.put_text(b"# truthful\nUse src/ok.py\n")
    blob_b = blob_store.put_text(b"# false\nUse src/missing.py\n")
    case = _sample_case()
    case = ExperimentCase(
        **{
            **case.__dict__,
            "condition_a_blob_sha": blob_a,
            "condition_b_blob_sha": blob_b,
        }
    )
    results_csv = tmp_path / "rq5_results.csv"
    traces_dir = tmp_path / "traces"

    first = run_causal_matrix_with_checkpoint(
        cases=[case],
        agents=[StubAgent()],
        scratch_dir=tmp_path / "scratch",
        traces_dir=traces_dir,
        blob_store=blob_store,
        results_csv=results_csv,
        replicates=1,
        run_tests=False,
        use_git_workspaces=False,
    )
    assert len(first) == 2
    assert results_csv.exists()

    second = run_causal_matrix_with_checkpoint(
        cases=[case],
        agents=[StubAgent()],
        scratch_dir=tmp_path / "scratch2",
        traces_dir=traces_dir,
        blob_store=blob_store,
        results_csv=results_csv,
        replicates=1,
        run_tests=False,
        use_git_workspaces=False,
    )
    assert len(second) == 2
    with results_csv.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2


@patch(
    "artifact_lab.experiments.truth_decay.rq5_experiment.agents.claude_code.run_subprocess"
)
def test_claude_code_adapter_parses_stream_json(mock_run):
    from artifact_lab.experiments.truth_decay.rq5_experiment.agents.claude_code import ClaudeCodeAgent

    stream = "\n".join(
        [
            '{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Read","input":{"path":"AGENTS.md"}}]}}',
            '{"type":"result","num_turns":2,"usage":{"input_tokens":10,"output_tokens":5},"total_cost_usd":0.01}',
        ]
    )
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = stream
    mock_run.return_value.stderr = ""

    agent = ClaudeCodeAgent(use_stream_json=True)
    case = _sample_case()
    workspace = Path("/tmp/rq5-test-workspace")
    with patch(
        "artifact_lab.experiments.truth_decay.rq5_experiment.agents.claude_code.git_workspace_metrics",
        return_value={"files_modified": 1, "repository_changes": 1, "patch_size": 4},
    ):
        result = agent.run(case=case, condition="A", workspace=workspace, replicate_id=1)

    assert result.success
    assert result.token_usage == 15
    assert result.cost_usd == 0.01
    assert result.tool_invocations == 1


def test_discover_available_agents_includes_claude_when_present():
    names = discover_available_agent_names()
    assert "claude_code" in names or names == []


def test_trace_frequencies():
    case = _sample_case()
    results = apply_trace_classifications(
        results=[_result(condition="A", success=True), _result(condition="B", success=False)],
        cases=[case],
    )
    freqs = trace_class_frequencies(results)
    assert freqs
    assert all("frequency" in row for row in freqs)
