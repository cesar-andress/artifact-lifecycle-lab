"""Unit tests for RQ2 survival dataset and estimators."""

from __future__ import annotations

from artifact_lab.experiments.truth_decay.survival_dataset import (
    OUTCOME_DELETED,
    OUTCOME_FIRST_MISSING,
    OUTCOME_RIGHT_CENSORED,
    build_survival_dataset,
)
from artifact_lab.experiments.truth_decay.survival_estimators import (
    censoring_summary,
    kaplan_meier_with_na,
    median_survival,
    repair_cumulative_incidence,
)


def _row(
    *,
    commit_time: str,
    state: str,
    reference: str = "src/a.py",
    reference_type: str = "path",
    reference_removed: bool = False,
) -> dict:
    return {
        "repo_id": "r1",
        "instruction_path": "AGENTS.md",
        "commit": "abc",
        "commit_time": commit_time,
        "reference": reference,
        "reference_type": reference_type,
        "state": state,
        "previous_state": "",
        "transition": "",
        "first_failure": state == "MISSING",
        "repair_event": state == "REPAIRED",
        "reference_removed": reference_removed,
        "reference_added": False,
    }


def test_build_survival_excludes_never_verified():
    rows = [
        _row(commit_time="2024-01-01T00:00:00+00:00", state="MISSING"),
        _row(commit_time="2024-02-01T00:00:00+00:00", state="MISSING"),
    ]
    records, meta = build_survival_dataset(rows)
    assert records == []
    assert meta["excluded_never_verified"] == 1


def test_build_survival_first_missing_event():
    rows = [
        _row(commit_time="2024-01-01T00:00:00+00:00", state="VERIFIED"),
        _row(commit_time="2024-01-16T00:00:00+00:00", state="MISSING"),
    ]
    records, _ = build_survival_dataset(rows)
    assert len(records) == 1
    r = records[0]
    assert r.outcome == OUTCOME_FIRST_MISSING
    assert r.duration_days == 15.0


def test_build_survival_right_censored():
    rows = [
        _row(commit_time="2024-01-01T00:00:00+00:00", state="VERIFIED"),
        _row(commit_time="2024-06-01T00:00:00+00:00", state="VERIFIED"),
    ]
    records, _ = build_survival_dataset(rows)
    assert records[0].outcome == OUTCOME_RIGHT_CENSORED
    assert records[0].duration_days == 152.0


def test_build_survival_deleted_outcome():
    rows = [
        _row(commit_time="2024-01-01T00:00:00+00:00", state="VERIFIED"),
        _row(commit_time="2024-03-01T00:00:00+00:00", state="DELETED"),
    ]
    records, _ = build_survival_dataset(rows)
    assert records[0].outcome == OUTCOME_DELETED


def test_build_survival_repair_lag():
    rows = [
        _row(commit_time="2024-01-01T00:00:00+00:00", state="VERIFIED"),
        _row(commit_time="2024-02-01T00:00:00+00:00", state="MISSING"),
        _row(commit_time="2024-02-11T00:00:00+00:00", state="REPAIRED"),
        _row(commit_time="2024-03-01T00:00:00+00:00", state="VERIFIED"),
    ]
    records, _ = build_survival_dataset(rows)
    r = records[0]
    assert r.outcome == OUTCOME_FIRST_MISSING
    assert r.ever_repaired is True
    assert r.repair_lag_days == 10.0
    assert r.post_failure_followup_days == 29.0


def test_kaplan_meier_median_on_synthetic_cohort():
    rows = []
    for i, fail_day in enumerate((10, 20, 30, 100)):
        ref = f"src/{i}.py"
        rows.append(_row(commit_time="2024-01-01T00:00:00+00:00", state="VERIFIED", reference=ref))
        if fail_day < 100:
            rows.append(
                _row(
                    commit_time=f"2024-01-{1 + fail_day:02d}T00:00:00+00:00",
                    state="MISSING",
                    reference=ref,
                )
            )
        else:
            rows.append(
                _row(
                    commit_time="2024-04-10T00:00:00+00:00",
                    state="VERIFIED",
                    reference=ref,
                )
            )

    records, _ = build_survival_dataset(rows)
    points = kaplan_meier_with_na(records)
    assert median_survival(points) == 20.0

    censoring = censoring_summary(records)
    assert censoring[OUTCOME_FIRST_MISSING] == 3
    assert censoring[OUTCOME_RIGHT_CENSORED] == 1


def test_repair_cumulative_incidence():
    rows = [
        _row(commit_time="2024-01-01T00:00:00+00:00", state="VERIFIED", reference="a"),
        _row(commit_time="2024-02-01T00:00:00+00:00", state="MISSING", reference="a"),
        _row(commit_time="2024-02-06T00:00:00+00:00", state="REPAIRED", reference="a"),
        _row(commit_time="2024-01-01T00:00:00+00:00", state="VERIFIED", reference="b"),
        _row(commit_time="2024-02-01T00:00:00+00:00", state="MISSING", reference="b"),
        _row(commit_time="2024-04-01T00:00:00+00:00", state="MISSING", reference="b"),
    ]
    records, _ = build_survival_dataset(rows)
    repair_points = repair_cumulative_incidence(records)
    assert repair_points
    assert repair_points[-1].cumulative_incidence == 0.5
