"""Unit tests for pre-scaling validation gates P3–P5 (no network)."""

from __future__ import annotations

from datetime import datetime, timezone

from artifact_lab.experiments.truth_pilots.p3_rot_incidence import (
    RotTrajectory,
    build_rot_trajectories,
    compute_rot_metrics,
    kaplan_meier_median_estimable,
)
from artifact_lab.experiments.truth_pilots.p4_attribution_precision import (
    build_gold_worksheet,
    categorize_signature,
    sample_candidates,
)


def _row(**kwargs) -> dict:
    base = {
        "repo_id": "r1",
        "instruction_path": "AGENTS.md",
        "reference_type": "path",
        "reference": "src/a.py",
        "commit_time": "2024-01-01T00:00:00+00:00",
        "state": "VERIFIED",
        "transition": "INIT->VERIFIED",
        "reference_removed": False,
        "first_failure": False,
    }
    base.update(kwargs)
    return base


def test_build_rot_trajectories_detects_failure():
    rows = [
        _row(commit_time="2024-01-01T00:00:00+00:00", state="VERIFIED"),
        _row(
            commit_time="2024-02-01T00:00:00+00:00",
            state="MISSING",
            transition="VERIFIED->MISSING",
            first_failure=True,
        ),
    ]
    trajectories = build_rot_trajectories(rows)
    assert len(trajectories) == 1
    assert trajectories[0].rot_event is True
    assert trajectories[0].censored is False


def test_compute_rot_metrics_and_km():
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    trajectories = [
        RotTrajectory(
            repo_id="r1",
            instruction_path="AGENTS.md",
            reference_type="path",
            reference="a.py",
            start_time=start,
            end_time=datetime(2024, 2, 1, tzinfo=timezone.utc),
            event_time=datetime(2024, 2, 1, tzinfo=timezone.utc),
            censored=False,
            rot_event=True,
        ),
        RotTrajectory(
            repo_id="r1",
            instruction_path="AGENTS.md",
            reference_type="path",
            reference="b.py",
            start_time=start,
            end_time=datetime(2024, 6, 1, tzinfo=timezone.utc),
            event_time=None,
            censored=True,
            rot_event=False,
        ),
    ]
    metrics = compute_rot_metrics(trajectories, p1_files=1)
    assert metrics["references_ever_missing"] == 1
    assert metrics["verifiable_references"] == 2
    assert metrics["right_censoring_rate"] == 0.5


def test_kaplan_meier_insufficient_events():
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    trajectories = [
        RotTrajectory(
            repo_id="r1",
            instruction_path="AGENTS.md",
            reference_type="path",
            reference=f"f{i}.py",
            start_time=start,
            end_time=datetime(2024, 6, 1, tzinfo=timezone.utc),
            event_time=None,
            censored=True,
            rot_event=False,
        )
        for i in range(3)
    ]
    ok, _, note = kaplan_meier_median_estimable(trajectories)
    assert ok is False
    assert "insufficient" in note


def test_categorize_dependabot_excluded():
    cat, counts = categorize_signature(
        attribution_class="bot_author",
        signature_type="bot_account",
        author_name="dependabot[bot]",
        author_email="49699333+dependabot[bot]@users.noreply.github.com",
        evidence="author=dependabot[bot]",
    )
    assert cat == "dependabot"
    assert counts is False


def test_categorize_claude_coauthored():
    cat, counts = categorize_signature(
        attribution_class="agent_coauthored",
        signature_type="co_authored_by",
        author_name="Dev",
        author_email="dev@example.com",
        evidence="co_authored_by:claude:Claude Opus 4.6",
    )
    assert cat == "co_authored_by_claude"
    assert counts is True


def test_sample_candidates_deterministic():
    candidates = [
        {
            "repo_id": f"r{i}",
            "commit_sha": f"sha{i}",
            "attribution_class": "agent_coauthored",
            "signature_type": "co_authored_by",
            "author_name": "Dev",
            "author_email": "d@e.com",
            "evidence": "co_authored_by:claude:Claude",
            "instruction_path": "AGENTS.md",
        }
        for i in range(50)
    ]
    s1 = sample_candidates(candidates, n=10, seed=42)
    s2 = sample_candidates(candidates, n=10, seed=42)
    assert [c["commit_sha"] for c in s1] == [c["commit_sha"] for c in s2]


def test_load_longitudinal_rows_parses_csv_booleans(tmp_path):
    import csv
    from artifact_lab.experiments.truth_pilots.gates_common import load_longitudinal_rows

    path = tmp_path / "long.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "repo_id",
                "instruction_path",
                "reference_type",
                "reference",
                "reference_removed",
                "reference_added",
                "first_failure",
                "repair_event",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "repo_id": "r1",
                "instruction_path": "AGENTS.md",
                "reference_type": "path",
                "reference": "a.py",
                "reference_removed": "False",
                "reference_added": "True",
                "first_failure": "False",
                "repair_event": "False",
            }
        )
    rows = load_longitudinal_rows(path)
    assert rows[0]["reference_removed"] is False
    assert rows[0]["reference_added"] is True


def test_build_gold_worksheet_columns():
    sampled = [
        {
            "repo_id": "r1",
            "repo_url": "https://github.com/o/r1",
            "instruction_path": "AGENTS.md",
            "commit_sha": "abc",
            "commit_time": "1",
            "author_name": "Dev",
            "author_email": "d@e.com",
            "attribution_class": "agent_coauthored",
            "signature_type": "co_authored_by",
            "evidence": "co_authored_by:cursor:Cursor",
        }
    ]
    rows = build_gold_worksheet(sampled)
    assert rows[0]["worksheet_id"] == 1
    assert rows[0]["signature_category"] == "co_authored_by_cursor"
    assert rows[0]["counts_as_agent_maintenance"] == "yes"
    assert rows[0]["human_label"] == ""
