"""Tests for execution preflight (cwd, normalization, smoke classification)."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from artifact_lab.experiments.rq5_v2.execution_preflight import (
    PackageScripts,
    PreflightPlan,
    classify_smoke_outcome,
    infer_cwd,
    normalize_test_command,
    pytest_isolated_command,
    repair_case_from_preflight,
    run_smoke_command,
)
from artifact_lab.experiments.rq5_v2.manifest import load_case_manifest
from artifact_lab.experiments.rq5_v2.models import FactorialCase, FactorialCell
from artifact_lab.experiments.rq5_v2.phase0_execution_viability import (
    preflight_results_to_audit_rows,
    run_phase0_execution_viability,
)
from artifact_lab.experiments.rq5_v2.phase0_toolchain_audit import summarize_case_quality


def _paths(*items: str) -> set[str]:
    return set(items)


def test_infer_cwd_go_module_subdirectory():
    paths = _paths("backend/go.mod", "backend/foo.go", "README.md")
    cwd = infer_cwd(test_command="go test", paths=paths)
    assert cwd == "backend"


def test_infer_cwd_node_package_in_subdirectory():
    paths = _paths("apps/web/package.json", "apps/web/src/index.ts", "package.json")
    cwd = infer_cwd(test_command="npm test", paths=paths)
    assert cwd in {"apps/web", "."}


def test_infer_cwd_python_with_tests_dir():
    paths = _paths("services/api/pyproject.toml", "services/api/tests/test_a.py")
    cwd = infer_cwd(test_command="pytest", paths=paths)
    assert cwd == "services/api"


def test_normalize_vitest_to_npm_test_when_script_exists():
    scripts = PackageScripts(path="package.json", scripts={"test": "vitest run"})
    plan = normalize_test_command(
        test_command="Vitest",
        paths=_paths("package.json"),
        cwd=".",
        package_scripts=scripts,
    )
    assert plan.normalized_test_command == "npm test"
    assert "package.json test script" in plan.normalization_notes


def test_normalize_vitest_to_npx_without_script():
    plan = normalize_test_command(
        test_command="Vitest",
        paths=_paths("package.json"),
        cwd=".",
        package_scripts=PackageScripts("package.json", {}),
    )
    assert plan.normalized_test_command == "npx vitest"


def test_normalize_pytest_isolated():
    plan = normalize_test_command(test_command="pytest", paths=_paths("pyproject.toml"), cwd=".")
    assert "python -m pytest" in plan.normalized_test_command
    assert "--confcutdir=." in plan.normalized_test_command
    assert "--rootdir=." in plan.normalized_test_command


def test_pytest_isolation_command():
    cmd = pytest_isolated_command()
    assert "PYTHONNOUSERSITE=1" in cmd
    assert "--confcutdir=." in cmd


def test_normalize_go_test():
    plan = normalize_test_command(test_command="go test", paths=_paths("go.mod"), cwd="backend")
    assert plan.normalized_test_command == "go test ./..."


def test_normalize_npm_test_requires_script():
    plan = normalize_test_command(
        test_command="npm test",
        paths=_paths("package.json"),
        cwd=".",
        package_scripts=PackageScripts("package.json", {"build": "tsc"}),
    )
    assert "rejected" in plan.normalization_notes


def test_normalize_yarn_test_with_script():
    plan = normalize_test_command(
        test_command="yarn test",
        paths=_paths("package.json", "yarn.lock"),
        cwd=".",
        package_scripts=PackageScripts("package.json", {"test": "jest"}),
    )
    assert plan.normalized_test_command == "yarn test"


def test_cargo_timeout_long_compile_flag():
    with patch("artifact_lab.experiments.rq5_v2.execution_preflight.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stdout="   Compiling foo v0.1.0\n", stderr="")
        code, _, _, _, timed_out, long_compile = run_smoke_command(
            command="cargo test",
            cwd=Path("/tmp"),
            ecosystem="rust",
            timeout=120,
        )
        assert code == 1
        assert not timed_out
        assert long_compile


def test_classify_drop_bare_vitest_no_script():
    plan = PreflightPlan("Vitest", "Vitest", ".", "node", "bare runner")
    cls, failure, _ = classify_smoke_outcome(
        plan=plan,
        exit_code=127,
        stdout="",
        stderr="Vitest: not found",
        runtime=0.1,
        timed_out=False,
        long_compile=False,
        clone_ok=True,
    )
    assert cls == "DROP" or cls == "REQUIRES_MANUAL_FIX"


def test_repaired_manifest_excludes_invalid_toolchains(tmp_path: Path):
    manifest = tmp_path / "factorial_case_manifest.json"
    manifest.write_text(
        json.dumps(
            [
                {
                    "case_id": "good_case",
                    "candidate_id": "lbv2_0001",
                    "repo_id": "r1",
                    "repo_url": "https://github.com/a/good",
                    "repository": "a/good",
                    "instruction_path": "AGENTS.md",
                    "commit_sha": "abc123",
                    "anchor_path_true": "src/a.py",
                    "anchor_path_false": "src/b.py",
                    "decoy_path": "README.md",
                    "test_command": "npm test",
                    "execution_cwd": ".",
                    "reference_type": "path",
                    "load_bearing_role": "edit",
                    "ecosystem": "node",
                    "calibrated_expected_success": 0.5,
                    "cells": {
                        "T+L": {
                            "cell_code": "T+L",
                            "instruction_blob_sha": "x",
                            "cited_anchor": "src/a.py",
                            "mechanical_truth": True,
                            "task_prompt": "task",
                            "load_bearing": True,
                        }
                    },
                },
                {
                    "case_id": "bad_case",
                    "candidate_id": "lbv2_0002",
                    "repo_id": "r2",
                    "repo_url": "https://github.com/a/bad",
                    "repository": "a/bad",
                    "instruction_path": "AGENTS.md",
                    "commit_sha": "def456",
                    "anchor_path_true": "src/a.py",
                    "anchor_path_false": "src/b.py",
                    "decoy_path": "README.md",
                    "test_command": "Vitest",
                    "execution_cwd": ".",
                    "reference_type": "path",
                    "load_bearing_role": "edit",
                    "ecosystem": "node",
                    "calibrated_expected_success": 0.5,
                    "cells": {
                        "T+L": {
                            "cell_code": "T+L",
                            "instruction_blob_sha": "x",
                            "cited_anchor": "src/a.py",
                            "mechanical_truth": True,
                            "task_prompt": "task",
                            "load_bearing": True,
                        }
                    },
                },
            ]
        ),
        encoding="utf-8",
    )

    good_result = MagicMock()
    good_result.case_id = "good_case"
    good_result.repository = "a/good"
    good_result.raw_test_command = "npm test"
    good_result.normalized_test_command = "npm test"
    good_result.cwd = "."
    good_result.classification = "READY"
    good_result.exit_code = 0
    good_result.stderr_excerpt = ""
    good_result.runtime = 1.0
    good_result.failure_class = ""
    good_result.recommended_action = "proceed"
    good_result.long_compile = False
    good_result.timed_out = False

    bad_result = MagicMock()
    bad_result.case_id = "bad_case"
    bad_result.repository = "a/bad"
    bad_result.raw_test_command = "Vitest"
    bad_result.normalized_test_command = "Vitest"
    bad_result.cwd = "."
    bad_result.classification = "DROP"
    bad_result.exit_code = 127
    bad_result.stderr_excerpt = "not found"
    bad_result.runtime = 0.1
    bad_result.failure_class = "invalid test command"
    bad_result.recommended_action = "exclude"
    bad_result.long_compile = False
    bad_result.timed_out = False

    with patch(
        "artifact_lab.experiments.rq5_v2.phase0_execution_viability.run_case_preflight",
    ) as mock_pf:
        mock_pf.side_effect = lambda **kw: good_result if kw["case_id"] == "good_case" else bad_result
        with patch(
            "artifact_lab.experiments.rq5_v2.phase0_execution_viability.RepoTreeCache"
        ) as mock_cache:
            mock_cache.return_value.paths_at.return_value = {"package.json"}
            paths = run_phase0_execution_viability(
                output_dir=tmp_path / "out",
                manifest_path=manifest,
                candidates_csv=tmp_path / "missing.csv",
                scratch_dir=tmp_path / "scratch",
                skip_smoke=True,
                min_cases=1,
            )

    repaired = load_case_manifest(paths["repaired_manifest"])
    assert len(repaired) == 1
    assert repaired[0].case_id == "good_case"
    assert repaired[0].test_command == "npm test"

    audit_rows = list(csv.DictReader(open(paths["preflight_audit_csv"], encoding="utf-8")))
    assert any(r["case_id"] == "good_case" and r["success"] == "True" for r in audit_rows)
    assert not any(r["case_id"] == "bad_case" for r in audit_rows)


def test_preflight_audit_valid_toolchain_for_ready():
    from artifact_lab.experiments.rq5_v2.execution_preflight import SmokePreflightResult
    from artifact_lab.experiments.rq5_v2.phase0_toolchain_audit import summarize_case_quality

    results = [
        SmokePreflightResult(
            case_id="c1",
            repository="a/b",
            raw_test_command="npm test",
            normalized_test_command="npm test",
            cwd=".",
            classification="READY",
            exit_code=0,
            stderr_excerpt="",
            runtime=2.0,
            failure_class="",
            recommended_action="proceed",
            long_compile=False,
            timed_out=False,
        )
    ]
    case = FactorialCase(
        case_id="c1",
        candidate_id="x",
        repo_id="r",
        repo_url="https://github.com/a/b",
        repository="a/b",
        instruction_path="AGENTS.md",
        commit_sha="abc",
        anchor_path_true="a.py",
        anchor_path_false="b.py",
        decoy_path="c.py",
        test_command="npm test",
        reference_type="path",
        load_bearing_role="edit",
        ecosystem="node",
        calibrated_expected_success=0.5,
        cells={
            "T+L": FactorialCell(
                cell_code="T+L",
                instruction_blob_sha="x",
                cited_anchor="a.py",
                mechanical_truth=True,
                task_prompt="t",
                load_bearing=True,
            )
        },
    )
    audit = preflight_results_to_audit_rows(results, {"c1": case})
    verdicts = summarize_case_quality(audit)
    assert verdicts[0].valid_toolchain == "yes"


def test_repair_case_sets_execution_cwd():
    case = FactorialCase(
        case_id="c1",
        candidate_id="x",
        repo_id="r",
        repo_url="https://github.com/a/b",
        repository="a/b",
        instruction_path="AGENTS.md",
        commit_sha="abc",
        anchor_path_true="a.py",
        anchor_path_false="b.py",
        decoy_path="c.py",
        test_command="go test",
        reference_type="path",
        load_bearing_role="edit",
        ecosystem="other",
        calibrated_expected_success=0.5,
        cells={
            "T+L": FactorialCell(
                cell_code="T+L",
                instruction_blob_sha="x",
                cited_anchor="a.py",
                mechanical_truth=True,
                task_prompt="t",
                load_bearing=True,
            )
        },
    )
    from artifact_lab.experiments.rq5_v2.execution_preflight import SmokePreflightResult

    result = SmokePreflightResult(
        case_id="c1",
        repository="a/b",
        raw_test_command="go test",
        normalized_test_command="go test ./...",
        cwd="backend",
        classification="READY",
        exit_code=0,
        stderr_excerpt="",
        runtime=1.0,
        failure_class="",
        recommended_action="proceed",
        long_compile=False,
        timed_out=False,
    )
    repaired = repair_case_from_preflight(case, result)
    assert repaired.test_command == "go test ./..."
    assert repaired.execution_cwd == "backend"
