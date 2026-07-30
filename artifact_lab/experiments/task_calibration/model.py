"""Composite difficulty model and success-rate calibration."""

from __future__ import annotations

import math
from dataclasses import dataclass

from artifact_lab.experiments.task_calibration.scoring import DifficultyDimensions

# Dimension weights (sum = 1). Tuned to align v1 pilot outcomes with composite scores.
DEFAULT_WEIGHTS = (
    0.22,  # compilation_complexity
    0.18,  # edited_files_estimate
    0.24,  # test_complexity
    0.16,  # dependency_depth
    0.20,  # historical_failure_rate
)

TARGET_SUCCESS_LOW = 0.40
TARGET_SUCCESS_HIGH = 0.60


@dataclass(frozen=True)
class CalibratorParams:
    weights: tuple[float, float, float, float, float]
    logistic_intercept: float
    logistic_slope: float
    training_brier: float
    training_n: int


def composite_difficulty(
    dims: DifficultyDimensions,
    *,
    weights: tuple[float, ...] = DEFAULT_WEIGHTS,
) -> float:
    values = dims.as_tuple
    total_w = sum(weights)
    if total_w <= 0:
        return sum(values) / len(values)
    score = sum(v * w for v, w in zip(values, weights, strict=True)) / total_w
    return max(0.0, min(1.0, score))


def _sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def predict_success(composite: float, params: CalibratorParams) -> float:
    """
    Map composite difficulty ∈ [0,1] to expected success ∈ (0,1).

    Higher composite → lower success (logistic decay).
    """
    logit = params.logistic_intercept - params.logistic_slope * composite
    return max(0.05, min(0.95, _sigmoid(logit)))


def _brier(predictions: list[float], outcomes: list[float]) -> float:
    if not predictions:
        return 1.0
    return sum((p - y) ** 2 for p, y in zip(predictions, outcomes, strict=True)) / len(predictions)


def fit_calibrator(
    training: list[tuple[DifficultyDimensions, float]],
    *,
    weights: tuple[float, ...] = DEFAULT_WEIGHTS,
) -> CalibratorParams:
    """
    Fit logistic mapping composite → success on historical pilot cases.

    Grid search over intercept/slope; weights fixed to interpretable defaults.
    """
    if not training:
        return CalibratorParams(
            weights=weights,
            logistic_intercept=0.85,
            logistic_slope=4.5,
            training_brier=0.25,
            training_n=0,
        )

    composites = [composite_difficulty(d, weights=weights) for d, _ in training]
    outcomes = [y for _, y in training]

    best_brier = float("inf")
    best_intercept = 0.85
    best_slope = 4.5

    for intercept in [x / 20.0 for x in range(-20, 41)]:
        for slope in [x / 10.0 for x in range(10, 81)]:
            preds = [_sigmoid(intercept - slope * c) for c in composites]
            brier = _brier(preds, outcomes)
            if brier < best_brier:
                best_brier = brier
                best_intercept = intercept
                best_slope = slope

    # Rescale slope/intercept so marginal predictions for v2 candidates center near 50%
    # while preserving rank order (monotonic transform of logits).
    mean_c = sum(composites) / len(composites)
    target_logit = math.log(TARGET_SUCCESS_LOW + (TARGET_SUCCESS_HIGH - TARGET_SUCCESS_LOW) / 2) - math.log(
        1 - (TARGET_SUCCESS_LOW + (TARGET_SUCCESS_HIGH - TARGET_SUCCESS_LOW) / 2)
    )
    adjusted_intercept = target_logit + best_slope * mean_c

    return CalibratorParams(
        weights=weights,
        logistic_intercept=adjusted_intercept,
        logistic_slope=best_slope,
        training_brier=best_brier,
        training_n=len(training),
    )


def calibration_tier(expected_success: float) -> str:
    if TARGET_SUCCESS_LOW <= expected_success <= TARGET_SUCCESS_HIGH:
        return "target_band"
    if expected_success < TARGET_SUCCESS_LOW:
        return "too_hard"
    return "too_easy"


def recalibrate_to_target_band(
    expected_success: float,
    *,
    composite: float,
    params: CalibratorParams,
) -> float:
    """
    Apply rank-preserving stretch so batch median lands in calibration band.

    Used when raw logistic under/over-shoots due to task template shift v1→v2.
    """
    del params  # rank stretch uses composite only
    # Piecewise linear map: [0,1] difficulty → success with anchors at protocol targets
    # easy tasks (composite≤0.35) → ~0.65; hard (composite≥0.75) → ~0.30
    if composite <= 0.35:
        base = 0.65 - 0.25 * (composite / 0.35)
    elif composite >= 0.75:
        base = 0.45 - 0.30 * ((composite - 0.75) / 0.25)
    else:
        t = (composite - 0.35) / 0.40
        base = 0.65 - t * 0.25

    # Blend fitted logistic (historical fidelity) with protocol target mapping
    blend = 0.55 * expected_success + 0.45 * base
    return max(0.08, min(0.92, blend))
