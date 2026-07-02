"""Tests for RQ5 causal experiment infrastructure."""

from __future__ import annotations

import json
from pathlib import Path

from artifact_lab.experiments.truth_decay.rq5_experiment.agents.stub import StubAgent
from artifact_lab.experiments.truth_decay.rq5_experiment.models import ExperimentCase
from artifact_lab.experiments.truth_decay.rq5_experiment.runner import dataset_rows, run_experiment_matrix
from artifact_lab.experiments.truth_decay.rq5_experiment.statistics import compute_effect_sizes
from artifact_lab.experiments.truth_decay.rq5_experiment.task_selection import select_experiment_cases
from artifact_lab.experiments.truth_decay.rq5_experiment.traces import compute_trace_statistics
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


def test_select_experiment_cases_from_exports():
    candidate = Path("exports/truth_decay_pilot/rq5_candidate_dataset.csv")
    gfc = Path("exports/truth_decay_pilot/gfc_confirmatory_audit.csv")
    if not candidate.exists() or not gfc.exists():
        return
    cases = select_experiment_cases(candidate_csv=candidate, gfc_confirmatory_csv=gfc)
    assert cases
    assert all(case.confirmed_false for case in cases)
    assert all(case.condition_a_blob_sha for case in cases)
    assert all(case.condition_b_blob_sha for case in cases)


def test_stub_agent_matrix_and_statistics(tmp_path: Path):
    blob_store = BlobStore(tmp_path / "blobs")
    blob_a = blob_store.put_text(b"# truthful\nUse src/ok.py\n")
    blob_b = blob_store.put_text(b"# false\nUse src/missing.py\n")
    case = ExperimentCase(
        case_id="case1",
        spec_id="spec1",
        repo_id="repo1",
        repo_url="https://github.com/example/example",
        instruction_path="AGENTS.md",
        task_commit_sha="abc123",
        anchor_reference="src/missing.py",
        anchor_reference_type="path",
        condition_a_blob_sha=blob_a,
        condition_b_blob_sha=blob_b,
        born_stale_commit_sha="def456",
        truthful_commit_sha="abc123",
        task_prompt="Do task",
        test_command="pytest",
        selection_reason="test",
        confirmed_false=True,
        p1_sample=False,
    )

    results = run_experiment_matrix(
        cases=[case],
        agents=[StubAgent()],
        scratch_dir=tmp_path / "scratch",
        traces_dir=tmp_path / "traces",
        blob_store=blob_store,
        replicates=2,
        use_git_workspaces=False,
    )
    assert len(results) == 4  # A/B × 2 replicates
    assert sum(1 for r in results if r.condition == "A" and r.success) == 2
    assert sum(1 for r in results if r.condition == "B" and not r.success) == 2

    effects = compute_effect_sizes(results, bootstrap_iterations=200, seed=0)
    assert effects[0].paired_success_difference == 1.0
    traces = compute_trace_statistics(results)
    assert any(row.metric == "rate_read_instruction" for row in traces)

    trace_files = list((tmp_path / "traces").glob("*.jsonl"))
    assert trace_files
    first = json.loads(trace_files[0].read_text(encoding="utf-8").splitlines()[0])
    assert first["event_type"] == "read_instruction"

    dataset = dataset_rows(cases=[case], results=results)
    assert dataset[0]["repo_id"] == "repo1"
