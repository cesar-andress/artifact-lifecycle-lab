"""Tests for RQ5 A/B/C redesign and load-bearing strata."""

from __future__ import annotations

from pathlib import Path

from artifact_lab.experiments.truth_decay.rq5_experiment.agents.cli_utils import build_experiment_prompt
from artifact_lab.experiments.truth_decay.rq5_experiment.agents.stub import StubAgent
from artifact_lab.experiments.truth_decay.rq5_experiment.load_bearing import classify_load_bearing_stratum
from artifact_lab.experiments.truth_decay.rq5_experiment.models import ExperimentCase
from artifact_lab.experiments.truth_decay.rq5_experiment.runner import run_experiment_matrix
from artifact_lab.experiments.truth_decay.rq5_experiment.task_selection import select_experiment_cases
from artifact_lab.experiments.truth_decay.rq5_experiment.workspace import write_instruction_to_workspace
from artifact_lab.experiments.truth_decay.run_rq5_redesign_plan import generate_rq5_redesign_plan
from artifact_lab.store.blobs import BlobStore


def _sample_case(**overrides) -> ExperimentCase:
    base = dict(
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
    base.update(overrides)
    return ExperimentCase(**base)


def test_condition_c_removes_instruction_file(tmp_path: Path):
    blob_store = BlobStore(tmp_path / "blobs")
    blob_a = blob_store.put_text(b"# truthful\nUse src/ok.py\n")
    case = _sample_case(condition_a_blob_sha=blob_a, condition_b_blob_sha=blob_a)
    workspace = tmp_path / "ws"
    workspace.mkdir()
    (workspace / "AGENTS.md").write_text("original", encoding="utf-8")

    write_instruction_to_workspace(workspace=workspace, case=case, condition="C", blob_store=blob_store)
    assert not (workspace / "AGENTS.md").exists()


def test_condition_c_prompt_omits_instruction():
    case = _sample_case()
    prompt = build_experiment_prompt(case, condition="C")
    assert "No project instruction file" in prompt
    assert "Anchor reference" not in prompt


def test_stub_agent_condition_c_succeeds(tmp_path: Path):
    blob_store = BlobStore(tmp_path / "blobs")
    blob_a = blob_store.put_text(b"# truthful\n")
    blob_b = blob_store.put_text(b"# false\nUse src/missing.py\n")
    case = _sample_case(condition_a_blob_sha=blob_a, condition_b_blob_sha=blob_b)
    workspace = tmp_path / "ws"
    workspace.mkdir()

    results = run_experiment_matrix(
        cases=[case],
        agents=[StubAgent()],
        scratch_dir=tmp_path / "scratch",
        traces_dir=tmp_path / "traces",
        blob_store=blob_store,
        replicates=1,
        conditions=("C",),
        use_git_workspaces=False,
    )
    assert len(results) == 1
    assert results[0].condition == "C"
    assert results[0].success
    assert not results[0].read_instruction


def test_load_bearing_classification():
    stratum, likely, _ = classify_load_bearing_stratum(
        anchor_reference="src/core.py",
        anchor_reference_type="path",
        instruction_path="AGENTS.md",
        task_availability=True,
        task_availability_reason="verified_reference_anchors_only",
        issue_availability=True,
        issue_availability_reason="stale_verifiable_references_present",
        n_missing_verifiable=2,
        n_verifiable=4,
        instruction_text="See src/core.py for setup",
    )
    assert stratum == "load_bearing"
    assert likely


def test_select_cases_include_load_bearing_flags():
    candidate = Path("exports/truth_decay_pilot/rq5_candidate_dataset.csv")
    gfc = Path("exports/truth_decay_pilot/gfc_confirmatory_audit.csv")
    if not candidate.exists() or not gfc.exists():
        return
    cases = select_experiment_cases(
        candidate_csv=candidate,
        gfc_confirmatory_csv=gfc,
        results_csv_for_traces=Path("exports/rq5_agent_impact/rq5_results.csv"),
    )
    assert cases
    assert all(c.load_bearing_stratum in {"load_bearing", "peripheral", "unknown"} for c in cases)


def test_generate_redesign_plan(tmp_path: Path):
    out = generate_rq5_redesign_plan(
        output_path=tmp_path / "rq5_redesign_plan.md",
        results_csv=Path("exports/rq5_agent_impact/rq5_results.csv"),
    )
    text = out.read_text(encoding="utf-8")
    assert "A/B/C" in text
    assert "Condition C" in text
    assert "Reusable A/B runs" in text
