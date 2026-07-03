"""Tests for Execution Viability preflight gate."""

from __future__ import annotations

import csv
from pathlib import Path

from artifact_lab.experiments.rq5_v2.execution_viability import (
    CHECK_WEIGHTS,
    _aggregate_score,
    classify_viability,
    render_viability_summary,
    run_execution_viability,
)
from artifact_lab.experiments.rq5_v2.execution_viability_checks import (
    RepoSignals,
    ViabilityCheckResult,
    check_test_command_exists,
    heuristic_smoke_from_error_patterns,
)


def _check(name: str, score: float, passed: bool, detail: str = "") -> ViabilityCheckResult:
    return ViabilityCheckResult(name, score, passed, detail)


def test_check_weights_sum_to_one():
    assert abs(sum(CHECK_WEIGHTS.values()) - 1.0) < 0.01


def test_bare_vitest_command_fails_exists_check():
    result = check_test_command_exists("Vitest")
    assert not result.passed
    assert result.score <= 0.2


def test_classify_drop_on_clone_failure():
    checks = {
        "clone": _check("clone", 0.0, False, "timeout"),
        "test_command_exists": _check("test_command_exists", 1.0, True),
    }
    cls, action = classify_viability(score=0.5, checks=checks)
    assert cls == "DROP"
    assert "clone" in action.lower() or "exclude" in action.lower()


def test_classify_ready_high_score():
    checks = {
        "clone": _check("clone", 1.0, True),
        "test_command_exists": _check("test_command_exists", 1.0, True),
        "baseline_tests_execute": _check("baseline_tests_execute", 1.0, True),
        "test_starts": _check("test_starts", 1.0, True),
    }
    cls, action = classify_viability(score=0.9, checks=checks)
    assert cls == "READY"
    assert "calibration" in action.lower()


def test_heuristic_smoke_flags_vitest():
    smoke = heuristic_smoke_from_error_patterns(
        test_command="Vitest",
        ecosystem="node",
        paths={"package.json"},
        historical_rate=0.0,
    )
    assert smoke.missing_binary
    assert not smoke.test_started


def test_run_offline_no_clone(tmp_path: Path):
    candidates = tmp_path / "candidates.csv"
    candidates.write_text(
        "candidate_id,repository,task,repo_id,repo_url,commit_sha\n"
        "lbv2_0001,azure/oav,"
        '"Fix bug. Run `npm test` before finishing.",'
        "r1,https://github.com/azure/oav,abc123\n"
        "lbv2_0002,bad/repo,"
        '"Fix bug. Run `Vitest` before finishing.",'
        "r2,https://github.com/bad/repo,def456\n",
        encoding="utf-8",
    )
    out = tmp_path / "out"
    paths = run_execution_viability(
        candidates_csv=candidates,
        output_dir=out,
        scratch_dir=tmp_path / "scratch",
        enable_clone=False,
        repo_root=tmp_path,
    )
    assert paths["viability_csv"].exists()
    rows = list(csv.DictReader(paths["viability_csv"].open(encoding="utf-8")))
    assert len(rows) == 2
    vitest = next(r for r in rows if r["candidate_id"] == "lbv2_0002")
    assert vitest["classification"] == "DROP"
    npm = next(r for r in rows if r["candidate_id"] == "lbv2_0001")
    assert float(npm["score"]) > float(vitest["score"])


def test_render_summary_includes_reduction(tmp_path: Path):
    from artifact_lab.experiments.rq5_v2.execution_viability import ViabilityRow

    rows = [
        ViabilityRow("c1", "a/b", 0.9, "", "proceed", "READY", "npm test", "node"),
        ViabilityRow("c2", "x/y", 0.2, "clone", "exclude", "DROP", "Vitest", "node"),
    ]
    md = render_viability_summary(
        rows=rows,
        provenance={
            "generated_at": "2026-01-01",
            "git_commit": "abc",
            "manifest_sha256": "dead",
            "python_version": "3.12",
            "platform": "linux",
            "analysis_script_hashes": {},
        },
        historical={"x/y": 1.0},
        phase0_toolchain_audit=Path("/nonexistent"),
    )
    assert "Expected infrastructure-failure reduction" in md
    assert "READY" in md


def test_aggregate_score_respects_weights():
    checks = {name: _check(name, 1.0, True) for name in CHECK_WEIGHTS}
    assert _aggregate_score(checks) == 1.0
    checks["clone"] = _check("clone", 0.0, False)
    assert _aggregate_score(checks) < 1.0
