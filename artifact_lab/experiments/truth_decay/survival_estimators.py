"""Kaplan-Meier, Nelson-Aalen, and repair cumulative incidence for RQ2."""

from __future__ import annotations

import math
from dataclasses import dataclass

from artifact_lab.experiments.truth_decay.survival_dataset import (
    OUTCOME_DELETED,
    OUTCOME_FIRST_MISSING,
    OUTCOME_RIGHT_CENSORED,
    ReferenceSurvivalRecord,
)


@dataclass(frozen=True)
class SurvivalPoint:
    time_days: float
    n_at_risk: int
    n_events: int
    n_censored: int
    survival: float
    survival_lower: float
    survival_upper: float
    cumulative_hazard: float
    cumulative_hazard_lower: float
    cumulative_hazard_upper: float


@dataclass(frozen=True)
class RepairPoint:
    time_days: float
    n_at_risk: int
    n_repairs: int
    cumulative_incidence: float


def _event_indicator(outcome: str) -> int:
    return 1 if outcome == OUTCOME_FIRST_MISSING else 0


def kaplan_meier_with_na(
    records: list[ReferenceSurvivalRecord],
    *,
    z: float = 1.96,
) -> list[SurvivalPoint]:
    if not records:
        return []

    data = sorted(
        [(r.duration_days, _event_indicator(r.outcome)) for r in records],
        key=lambda x: x[0],
    )
    unique_times = sorted({t for t, _ in data})
    n = len(data)
    at_risk = n
    survival = 1.0
    hazard = 0.0
    var_accum = 0.0
    points: list[SurvivalPoint] = []

    for t in unique_times:
        d_i = sum(1 for time, event in data if time == t and event == 1)
        c_i = sum(1 for time, event in data if time == t and event == 0)
        if at_risk <= 0:
            break
        if d_i > 0:
            survival *= 1 - d_i / at_risk
            hazard += d_i / at_risk
            var_accum += d_i / (at_risk * (at_risk - d_i)) if at_risk > d_i else 0.0
        se_log_survival = math.sqrt(var_accum) if var_accum > 0 else 0.0
        log_s = math.log(survival) if survival > 0 else float("-inf")
        lower = math.exp(log_s - z * se_log_survival) if survival > 0 else 0.0
        upper = math.exp(log_s + z * se_log_survival) if survival > 0 else 0.0
        se_hazard = math.sqrt(var_accum) if var_accum > 0 else 0.0
        points.append(
            SurvivalPoint(
                time_days=t,
                n_at_risk=at_risk,
                n_events=d_i,
                n_censored=c_i,
                survival=max(0.0, min(1.0, survival)),
                survival_lower=max(0.0, min(1.0, lower)),
                survival_upper=max(0.0, min(1.0, upper)),
                cumulative_hazard=hazard,
                cumulative_hazard_lower=max(0.0, hazard - z * se_hazard),
                cumulative_hazard_upper=hazard + z * se_hazard,
            )
        )
        at_risk -= d_i + c_i

    return points


def median_survival(points: list[SurvivalPoint]) -> float | None:
    for pt in points:
        if pt.survival <= 0.5:
            return pt.time_days
    return None


def median_survival_ci(points: list[SurvivalPoint]) -> tuple[float | None, float | None]:
    """Brookmeyer-Crowley style CI using survival confidence bands."""
    lower_m: float | None = None
    upper_m: float | None = None
    for pt in points:
        if lower_m is None and pt.survival_upper <= 0.5:
            lower_m = pt.time_days
        if pt.survival_lower <= 0.5:
            upper_m = pt.time_days
    return lower_m, upper_m


def censoring_summary(records: list[ReferenceSurvivalRecord]) -> dict[str, int]:
    counts = {
        OUTCOME_FIRST_MISSING: 0,
        OUTCOME_RIGHT_CENSORED: 0,
        OUTCOME_DELETED: 0,
    }
    for r in records:
        if r.outcome in counts:
            counts[r.outcome] += 1
    counts["repaired_after_failure"] = sum(
        1 for r in records if r.outcome == OUTCOME_FIRST_MISSING and r.ever_repaired
    )
    return counts


def repair_cumulative_incidence(
    records: list[ReferenceSurvivalRecord],
) -> list[RepairPoint]:
    """Cumulative incidence of repair among references that experienced first missing."""
    data: list[tuple[float, int]] = []
    for r in records:
        if r.post_failure_followup_days is None:
            continue
        if r.ever_repaired and r.repair_lag_days is not None:
            data.append((r.repair_lag_days, 1))
        else:
            data.append((r.post_failure_followup_days, 0))
    if not data:
        return []

    data.sort(key=lambda x: x[0])
    unique_times = sorted({t for t, _ in data})
    at_risk = len(data)
    cum = 0.0
    points: list[RepairPoint] = []
    for t in unique_times:
        repairs = sum(1 for time, event in data if time == t and event == 1)
        censored = sum(1 for time, event in data if time == t and event == 0)
        if at_risk <= 0:
            break
        if repairs:
            cum += repairs / at_risk
        points.append(
            RepairPoint(
                time_days=t,
                n_at_risk=at_risk,
                n_repairs=repairs,
                cumulative_incidence=min(1.0, cum),
            )
        )
        at_risk -= repairs + censored
    return points


def survival_curve_rows(points: list[SurvivalPoint]) -> list[dict]:
    return [
        {
            "time_days": round(pt.time_days, 4),
            "n_at_risk": pt.n_at_risk,
            "n_events": pt.n_events,
            "n_censored": pt.n_censored,
            "survival": round(pt.survival, 6),
            "survival_lower_95": round(pt.survival_lower, 6),
            "survival_upper_95": round(pt.survival_upper, 6),
            "cumulative_hazard": round(pt.cumulative_hazard, 6),
            "cumulative_hazard_lower_95": round(pt.cumulative_hazard_lower, 6),
            "cumulative_hazard_upper_95": round(pt.cumulative_hazard_upper, 6),
        }
        for pt in points
    ]
