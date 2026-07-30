"""Tests for selection observational study."""

from __future__ import annotations

import random

from artifact_lab.experiments.truth_decay.audit_statistics import (
    paired_cohens_d,
    permutation_test_sign_flip,
)
from artifact_lab.experiments.truth_decay.selection_study import (
    METRIC_CHURN,
    METRIC_SURVIVAL,
    PanelActivityCatalog,
    PathFeatures,
    SelectionMatchPair,
    _favorable_fraction,
    _match_score,
    _paired_differences,
    _path_panel_metrics_from_catalog,
    compute_selection_statistics,
)


def _sample_pair(**overrides) -> SelectionMatchPair:
    base = dict(
        repo_id="abc",
        repo_url="https://example.com/r",
        referenced_path="src/a.py",
        control_path="src/b.py",
        panel_start_commit="s",
        panel_end_commit="e",
        panel_start_time="2025-01-01T00:00:00+00:00",
        panel_end_time="2025-06-01T00:00:00+00:00",
        panel_duration_days=151.0,
        match_extension="py",
        match_depth_diff=0,
        match_size_ratio=1.0,
        match_creation_days_diff=10.0,
        match_score=1.5,
        ref_lifetime_days=140.0,
        ref_churn_commits=1,
        ref_rename_count=0,
        ref_deleted=False,
        ref_survived_panel=True,
        ctrl_lifetime_days=120.0,
        ctrl_churn_commits=3,
        ctrl_rename_count=1,
        ctrl_deleted=True,
        ctrl_survived_panel=False,
    )
    base.update(overrides)
    return SelectionMatchPair(**base)


def test_match_score_prefers_similar_candidates():
    target = PathFeatures(path="src/a.py", extension="py", depth=2, size_bytes=1000, creation_ts=1_700_000_000)
    close = PathFeatures(path="src/b.py", extension="py", depth=2, size_bytes=1100, creation_ts=1_700_100_000)
    far = PathFeatures(path="lib/x.py", extension="py", depth=1, size_bytes=50000, creation_ts=1_600_000_000)
    assert _match_score(target, close) < _match_score(target, far)


def test_favorable_fraction_for_churn():
    pairs = [
        _sample_pair(ref_churn_commits=1, ctrl_churn_commits=3),
        _sample_pair(ref_churn_commits=2, ctrl_churn_commits=2),
    ]
    flags = _favorable_fraction(pairs, METRIC_CHURN)
    assert flags == [1.0, 1.0]


def test_compute_selection_statistics_structure():
    pairs = [
        _sample_pair(ref_churn_commits=1, ctrl_churn_commits=4),
        _sample_pair(ref_churn_commits=0, ctrl_churn_commits=2),
    ]
    stats = compute_selection_statistics(pairs, seed=0)
    assert stats.n_pairs == 2
    assert len(stats.metrics) == 5
    churn = next(m for m in stats.metrics if m.metric == METRIC_CHURN)
    assert churn.mean_difference < 0
    survival = next(m for m in stats.metrics if m.metric == METRIC_SURVIVAL)
    assert survival.referenced_favorable_fraction == 1.0


def test_paired_cohens_d():
    diffs = [-2.0, -1.0, -1.0]
    assert paired_cohens_d(diffs) < 0


def test_permutation_test_sign_flip():
    diffs = [-5.0, -4.0, -3.0, -4.0, -2.0]
    p = permutation_test_sign_flip(diffs, iterations=2000, seed=0, alternative="less")
    assert p < 0.05


def test_paired_differences():
    pairs = [_sample_pair(ref_churn_commits=2, ctrl_churn_commits=5)]
    assert _paired_differences(pairs, METRIC_CHURN) == [-3.0]


def test_path_panel_metrics_from_catalog():
    catalog = PanelActivityCatalog(
        churn_commits={"src/a.py": 2},
        last_touch_ts={"src/a.py": 1_735_689_600},
        rename_count={"src/a.py": 1},
    )
    metrics = _path_panel_metrics_from_catalog(
        "src/a.py",
        catalog=catalog,
        panel_start_time="2025-01-01T00:00:00+00:00",
        panel_end_time="2025-06-01T00:00:00+00:00",
        panel_duration_days=151.0,
        tree_at_end={"src/a.py"},
    )
    assert metrics.churn_commits == 2
    assert metrics.rename_count == 1
    assert metrics.survived_panel is True
