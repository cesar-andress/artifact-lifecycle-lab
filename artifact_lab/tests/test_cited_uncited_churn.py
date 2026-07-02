"""Tests for cited vs uncited churn contrast."""

from __future__ import annotations

from artifact_lab.experiments.truth_decay.cited_uncited_churn import (
    PathChurnPair,
    _eligible_cited_reference,
    _pick_uncited_control,
    collect_cited_path_trajectories,
    compute_churn_contrast_statistics,
)
import random


def test_eligible_cited_reference_rejects_glob():
    assert not _eligible_cited_reference("packages/*/", "directory")
    assert _eligible_cited_reference("src/main.py", "path")


def test_collect_cited_trajectories():
    rows = [
        {
            "repo_id": "abc",
            "repo_url": "https://example.com/r",
            "reference": "src/foo.py",
            "reference_type": "path",
            "reference_removed": False,
            "state": "VERIFIED",
            "commit": "c1",
            "commit_time": "2025-01-01T00:00:00+00:00",
        },
        {
            "repo_id": "abc",
            "repo_url": "https://example.com/r",
            "reference": "src/foo.py",
            "reference_type": "path",
            "reference_removed": False,
            "state": "MISSING",
            "commit": "c2",
            "commit_time": "2025-02-01T00:00:00+00:00",
        },
    ]
    trajectories = collect_cited_path_trajectories(rows)
    meta = trajectories[("abc", "src/foo.py")]
    assert meta["verified_rate"] == 0.5
    assert meta["panel_start_commit"] == "c1"
    assert meta["panel_end_commit"] == "c2"


def test_pick_uncited_control_matches_extension():
    rng = random.Random(0)
    control = _pick_uncited_control(
        tree_paths={"src/foo.py", "src/bar.py", "docs/readme.md"},
        cited_paths={"src/foo.py"},
        target_path="src/foo.py",
        rng=rng,
    )
    assert control == "src/bar.py"


def test_compute_churn_statistics():
    pairs = [
        PathChurnPair(
            repo_id="abc",
            repo_url="u",
            cited_path="a.py",
            uncited_path="b.py",
            panel_start_commit="s",
            panel_end_commit="e",
            cited_churn_commits=1,
            uncited_churn_commits=3,
            cited_verified_rate=1.0,
            match_extension="py",
            match_depth=1,
        ),
        PathChurnPair(
            repo_id="abc",
            repo_url="u",
            cited_path="c.py",
            uncited_path="d.py",
            panel_start_commit="s",
            panel_end_commit="e",
            cited_churn_commits=2,
            uncited_churn_commits=2,
            cited_verified_rate=0.5,
            match_extension="py",
            match_depth=1,
        ),
    ]
    stats = compute_churn_contrast_statistics(pairs)
    assert stats.n_pairs == 2
    assert stats.mean_difference < 0
    assert stats.cited_more_stable_fraction == 1.0
