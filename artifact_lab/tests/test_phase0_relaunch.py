"""Tests for Phase 0 relaunch preparation and setup gate."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from artifact_lab.experiments.rq5_v2.models import FactorialCase, FactorialCell
from artifact_lab.experiments.rq5_v2.phase0_relaunch import (
    DEFAULT_REPAIRED_MANIFEST,
    RepairedManifestRequiredError,
    apply_setup_failures,
    assert_repaired_manifest,
    build_setup_specs,
    is_repaired_manifest,
    prepare_phase0_relaunch,
)
from artifact_lab.experiments.rq5_v2.phase0_run import (
    PHASE0_CELL,
    PHASE0_EXPECTED_RUNS,
    build_phase0_plan,
    run_phase0_calibration,
    verify_phase0_preflight,
)
from artifact_lab.experiments.rq5_v2.phase0_setup import (
    ALLOWED_SETUP_COMMANDS,
    select_setup_command,
    setup_root,
)


def _case(case_id: str = "c1", execution_cwd: str = ".") -> FactorialCase:
    return FactorialCase(
        case_id=case_id,
        candidate_id="lbv2_0001",
        repo_id="r1",
        repo_url="https://github.com/a/b",
        repository="a/b",
        instruction_path="AGENTS.md",
        commit_sha="abc",
        anchor_path_true="src/a.py",
        anchor_path_false="src/b.py",
        decoy_path="README.md",
        test_command="npm test",
        reference_type="path",
        load_bearing_role="edit",
        ecosystem="node",
        calibrated_expected_success=0.5,
        execution_cwd=execution_cwd,
        cells={
            PHASE0_CELL: FactorialCell(
                cell_code=PHASE0_CELL,
                instruction_blob_sha="x",
                cited_anchor="src/a.py",
                mechanical_truth=True,
                task_prompt="task",
                load_bearing=True,
            )
        },
    )


def test_is_repaired_manifest():
    assert is_repaired_manifest(Path("phase0_manifest_repaired.json"))
    assert not is_repaired_manifest(Path("factorial_case_manifest.json"))


def test_original_manifest_rejected(tmp_path: Path):
    original = tmp_path / "factorial_case_manifest.json"
    original.write_text("[]", encoding="utf-8")
    with pytest.raises(RepairedManifestRequiredError):
        assert_repaired_manifest(original)


def test_repaired_manifest_accepted(tmp_path: Path):
    repaired = tmp_path / "phase0_manifest_repaired.json"
    repaired.write_text("[]", encoding="utf-8")
    digest = assert_repaired_manifest(repaired)
    assert len(digest) == 64


def test_select_setup_command_npm_ci(tmp_path: Path):
    root = tmp_path / "pkg"
    root.mkdir()
    (root / "package-lock.json").write_text("{}", encoding="utf-8")
    (root / "package.json").write_text("{}", encoding="utf-8")
    assert select_setup_command(root=root) == "npm ci"


def test_select_setup_command_yarn(tmp_path: Path):
    root = tmp_path / "pkg"
    root.mkdir()
    (root / "yarn.lock").write_text("", encoding="utf-8")
    (root / "package.json").write_text("{}", encoding="utf-8")
    assert select_setup_command(root=root) == "yarn install"


def test_select_setup_command_pnpm(tmp_path: Path):
    root = tmp_path / "pkg"
    root.mkdir()
    (root / "pnpm-lock.yaml").write_text("", encoding="utf-8")
    (root / "package.json").write_text("{}", encoding="utf-8")
    assert select_setup_command(root=root) == "pnpm install"


def test_setup_root_execution_cwd(tmp_path: Path):
    ws = tmp_path / "repo"
    ws.mkdir()
    (ws / "app").mkdir()
    assert setup_root(workspace=ws, execution_cwd="app") == ws / "app"


def test_build_setup_specs_ready_vs_minor():
    cases = [_case("ready1"), _case("minor1", execution_cwd="app")]
    index = {
        "ready1": {"classification": "READY", "cwd": "."},
        "minor1": {"classification": "MINOR_SETUP", "cwd": "app"},
    }
    specs = build_setup_specs(cases=cases, viability_index=index)
    assert specs["ready1"].setup_command is None
    assert specs["minor1"].classification == "MINOR_SETUP"


def test_apply_setup_failures_replaces_case():
    active = [_case(f"c{i}") for i in range(19)] + [_case("fail")]
    specs = build_setup_specs(
        cases=active,
        viability_index={c.case_id: {"classification": "READY", "cwd": "."} for c in active},
    )
    replacement = _case("replacement")
    kept, new_specs, pool, excluded = apply_setup_failures(
        active_cases=active,
        setup_specs=specs,
        failed_case_ids={"fail"},
        replacement_pool=[replacement],
        viability_index={"replacement": {"classification": "READY", "cwd": "."}},
    )
    assert len(kept) == 20
    assert "fail" in excluded
    assert any(c.case_id == "replacement" for c in kept)


def test_phase0_plan_60_runs_from_repaired_cases():
    cases = [_case(f"c{i}") for i in range(20)]
    plan, config = build_phase0_plan(cases=cases, seed=42)
    assert len(plan) == PHASE0_EXPECTED_RUNS
    assert len({p.case_id for p in plan}) == 20


def test_verify_preflight_requires_repaired_manifest(tmp_path: Path):
    cases = [_case()]
    plan, config = build_phase0_plan(cases=cases)
    repaired = tmp_path / "phase0_manifest_repaired.json"
    repaired.write_text("[]", encoding="utf-8")
    original = tmp_path / "factorial_case_manifest.json"
    original.write_text("[]", encoding="utf-8")

    ok_report = verify_phase0_preflight(
        plan=plan,
        config=config,
        results_csv=tmp_path / "results.csv",
        traces_dir=tmp_path / "traces",
        require_execute_env=False,
        manifest_path=repaired,
    )
    assert ok_report.checks["repaired_manifest_selected"]

    bad_report = verify_phase0_preflight(
        plan=plan,
        config=config,
        results_csv=tmp_path / "results.csv",
        traces_dir=tmp_path / "traces",
        require_execute_env=False,
        manifest_path=original,
    )
    assert not bad_report.checks["repaired_manifest_selected"]


def test_prepare_relaunch_uses_repaired_manifest(tmp_path: Path):
    manifest = tmp_path / "phase0_manifest_repaired.json"
    cases = []
    for i in range(20):
        cases.append(
            {
                "case_id": f"case_{i:02d}",
                "candidate_id": f"lbv2_{i:04d}",
                "repo_id": f"repo_{i}",
                "repo_url": f"https://github.com/a/r{i}",
                "repository": f"a/r{i}",
                "instruction_path": "AGENTS.md",
                "commit_sha": f"sha{i}",
                "anchor_path_true": "src/a.py",
                "anchor_path_false": "src/b.py",
                "decoy_path": "README.md",
                "test_command": "npm test",
                "reference_type": "path",
                "load_bearing_role": "edit",
                "ecosystem": "node",
                "calibrated_expected_success": 0.5,
                "execution_cwd": ".",
                "cells": {
                    PHASE0_CELL: {
                        "cell_code": PHASE0_CELL,
                        "instruction_blob_sha": "x",
                        "cited_anchor": "src/a.py",
                        "mechanical_truth": True,
                        "task_prompt": "task",
                        "load_bearing": True,
                    }
                },
            }
        )
    manifest.write_text(json.dumps(cases), encoding="utf-8")

    viability = tmp_path / "execution_viability.csv"
    with viability.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["case_id", "classification", "cwd"],
        )
        writer.writeheader()
        for c in cases:
            writer.writerow(
                {
                    "case_id": c["case_id"],
                    "classification": "READY" if c["case_id"] != "case_00" else "MINOR_SETUP",
                    "cwd": ".",
                }
            )

    out = tmp_path / "out"
    with patch(
        "artifact_lab.experiments.rq5_v2.phase0_relaunch.RepoTreeCache"
    ) as mock_tree:
        mock_tree.return_value.paths_at.return_value = {"package.json", "package-lock.json"}
        with patch(
            "artifact_lab.experiments.rq5_v2.phase0_relaunch.build_replacement_pool",
            return_value=[],
        ):
            paths = prepare_phase0_relaunch(
                output_dir=out,
                manifest_path=manifest,
                viability_csv=viability,
                scratch_dir=tmp_path / "scratch",
            )

    assert paths["run_plan_csv"].exists()
    plan_rows = list(csv.DictReader(paths["run_plan_csv"].open(encoding="utf-8")))
    assert len(plan_rows) == PHASE0_EXPECTED_RUNS
    relaunch = json.loads(paths["relaunch_json"].read_text(encoding="utf-8"))
    assert relaunch["run_count"] == PHASE0_EXPECTED_RUNS
    assert relaunch["manifest_sha256"]


def test_run_phase0_prepare_only_no_execute(tmp_path: Path):
    manifest = tmp_path / "phase0_manifest_repaired.json"
    if DEFAULT_REPAIRED_MANIFEST.exists():
        manifest.write_text(DEFAULT_REPAIRED_MANIFEST.read_text(encoding="utf-8"), encoding="utf-8")
    else:
        pytest.skip("repaired manifest not present in workspace")

    viability = tmp_path / "execution_viability.csv"
    if Path("exports/rq5_v2_factorial/execution_viability.csv").exists():
        viability.write_text(
            Path("exports/rq5_v2_factorial/execution_viability.csv").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    else:
        pytest.skip("viability csv not present")

    with patch("artifact_lab.experiments.rq5_v2.phase0_relaunch.build_replacement_pool", return_value=[]):
        with patch("artifact_lab.experiments.rq5_v2.phase0_relaunch.RepoTreeCache") as mock_tree:
            mock_tree.return_value.paths_at.return_value = {"package.json"}
            paths = run_phase0_calibration(
                output_dir=tmp_path / "out",
                manifest_path=manifest,
                viability_csv=viability,
                execute=False,
                prepare_only=True,
                scratch_dir=tmp_path / "scratch",
            )
    assert "run_plan_csv" in paths


def test_allowed_setup_commands_frozen():
    assert "npm install" in ALLOWED_SETUP_COMMANDS
    assert "npm ci" in ALLOWED_SETUP_COMMANDS
    assert "yarn install" in ALLOWED_SETUP_COMMANDS
    assert "pnpm install" in ALLOWED_SETUP_COMMANDS
