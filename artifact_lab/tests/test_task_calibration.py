"""Unit tests for task difficulty calibration."""

from __future__ import annotations

from pathlib import Path

from artifact_lab.experiments.task_calibration.historical import load_historical_index
from artifact_lab.experiments.task_calibration.model import (
    calibration_tier,
    composite_difficulty,
    fit_calibrator,
    predict_success,
    recalibrate_to_target_band,
)
from artifact_lab.experiments.task_calibration.scoring import (
    DifficultyDimensions,
    TaskFeatures,
    score_all_dimensions,
    score_compilation_complexity,
)


def test_monorepo_raises_compilation_score():
    easy = TaskFeatures(
        repository="acme/simple",
        reference="src/foo.py",
        instruction_path="AGENTS.md",
        reference_type="path",
        role="edit",
        test_command="pytest",
        context_snippet="",
    )
    hard = TaskFeatures(
        repository="automattic/wp-calypso",
        reference="packages/grid/src/index.ts",
        instruction_path="packages/grid/AGENTS.md",
        reference_type="path",
        role="edit",
        test_command="npm test",
        context_snippet="",
    )
    assert score_compilation_complexity(hard) > score_compilation_complexity(easy)


def test_composite_difficulty_in_unit_interval():
    dims = DifficultyDimensions(0.2, 0.3, 0.4, 0.5, 0.6)
    c = composite_difficulty(dims)
    assert 0.0 <= c <= 1.0


def test_calibration_tier_bands():
    assert calibration_tier(0.50) == "target_band"
    assert calibration_tier(0.30) == "too_hard"
    assert calibration_tier(0.70) == "too_easy"


def test_calibrator_predicts_lower_success_for_harder_tasks():
    params = fit_calibrator(
        [
            (DifficultyDimensions(0.1, 0.1, 0.1, 0.1, 0.2), 0.75),
            (DifficultyDimensions(0.8, 0.8, 0.8, 0.8, 0.9), 0.05),
        ]
    )
    easy = composite_difficulty(DifficultyDimensions(0.1, 0.1, 0.1, 0.1, 0.2), weights=params.weights)
    hard = composite_difficulty(DifficultyDimensions(0.8, 0.8, 0.8, 0.8, 0.9), weights=params.weights)
    assert predict_success(easy, params) > predict_success(hard, params)


def test_recalibrate_moves_toward_target_band():
    params = fit_calibrator([])
    raw = 0.15
    adjusted = recalibrate_to_target_band(raw, composite=0.45, params=params)
    assert 0.34 <= adjusted <= 0.75


def test_run_calibration_export(tmp_path: Path):
    root = Path("exports")
    candidates = root / "rq5_v2" / "load_bearing_candidates.csv"
    results = root / "rq5_agent_impact" / "rq5_results.csv"
    manifest = root / "rq5_agent_impact" / "rq5_case_manifest.csv"
    if not candidates.exists() or not results.exists():
        return

    from artifact_lab.experiments.task_calibration.run import run_task_calibration

    out = tmp_path / "cal"
    paths = run_task_calibration(
        candidates_csv=candidates,
        results_csv=results,
        manifest_csv=manifest,
        output_dir=out,
    )
    assert paths["scores_csv"].exists()
    assert paths["distribution_pdf"].exists()
    text = paths["scores_csv"].read_text(encoding="utf-8")
    assert "composite_difficulty" in text
    assert "calibrated_expected_success" in text


def test_load_historical_index_from_exports():
    results = Path("exports/rq5_agent_impact/rq5_results.csv")
    manifest = Path("exports/rq5_agent_impact/rq5_case_manifest.csv")
    if not results.exists():
        return
    index = load_historical_index(results_csv=results, manifest_csv=manifest)
    assert index.global_failure_rate > 0.5
    assert index.cases
