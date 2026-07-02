"""Unit tests for RQ1 truth-decay feasibility (no network)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from artifact_lab.experiments.truth_decay.longitudinal import load_instruction_file_events
from artifact_lab.experiments.truth_decay.report import assess_tosem_viability, generate_rq1_feasibility_report
from artifact_lab.experiments.truth_decay.states import (
    resolve_observation_state,
    transition_label,
)
from artifact_lab.experiments.truth_decay.stats import RQ1ExploratoryStats, compute_exploratory_stats


def test_resolve_observation_state_repair():
    state = resolve_observation_state(
        verify_status="verified",
        previous_state="MISSING",
        file_deleted=False,
    )
    assert state == "REPAIRED"


def test_resolve_observation_state_deleted():
    state = resolve_observation_state(
        verify_status="verified",
        previous_state="VERIFIED",
        file_deleted=True,
    )
    assert state == "DELETED"


def test_transition_label_init():
    assert transition_label(None, "VERIFIED") == "INIT->VERIFIED"


def test_compute_exploratory_stats_decay_and_repair():
    rows = [
        {
            "repo_id": "r1",
            "instruction_path": "AGENTS.md",
            "commit_time": "2024-01-01T00:00:00+00:00",
            "reference_type": "path",
            "reference": "src/a.py",
            "state": "VERIFIED",
            "transition": "INIT->VERIFIED",
            "reference_removed": False,
            "reference_added": True,
            "first_failure": False,
            "repair_event": False,
        },
        {
            "repo_id": "r1",
            "instruction_path": "AGENTS.md",
            "commit_time": "2024-02-01T00:00:00+00:00",
            "reference_type": "path",
            "reference": "src/a.py",
            "state": "MISSING",
            "transition": "VERIFIED->MISSING",
            "reference_removed": False,
            "reference_added": False,
            "first_failure": True,
            "repair_event": False,
        },
        {
            "repo_id": "r1",
            "instruction_path": "AGENTS.md",
            "commit_time": "2024-03-01T00:00:00+00:00",
            "reference_type": "path",
            "reference": "src/a.py",
            "state": "REPAIRED",
            "transition": "MISSING->REPAIRED",
            "reference_removed": False,
            "reference_added": False,
            "first_failure": False,
            "repair_event": True,
        },
    ]
    stats = compute_exploratory_stats(rows)
    assert stats.instruction_files == 1
    assert stats.first_failure_count == 1
    assert stats.repair_event_count == 1
    assert stats.median_time_to_first_missing_days == 31.0
    assert stats.median_repair_latency_days == 29.0
    assert stats.files_with_decay == 1
    assert stats.files_with_repair == 1


def test_assess_tosem_viability_yes():
    stats = RQ1ExploratoryStats(
        instruction_files=100,
        total_observations=5000,
        references_per_file_median=3.0,
        references_per_file_mean=4.0,
        verified_ratio=0.4,
        missing_ratio=0.15,
        repaired_ratio=0.05,
        unverifiable_ratio=0.4,
        deleted_ratio=0.0,
        state_counts={"VERIFIED": 2000, "MISSING": 750, "REPAIRED": 250},
        transition_counts={"VERIFIED->MISSING": 100},
        first_failure_count=80,
        repair_event_count=30,
        reference_additions=200,
        reference_removals=50,
        median_time_to_first_missing_days=45.0,
        median_repair_latency_days=14.0,
        files_with_decay=40,
        files_with_repair=15,
    )
    verdict, _ = assess_tosem_viability(stats)
    assert verdict == "YES"


def test_load_instruction_file_events(tmp_path: Path):
    ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
    path = tmp_path / "events.parquet"
    table = pa.Table.from_pylist(
        [
            {
                "repo_id": "r1",
                "repo_url": "https://github.com/o/r1",
                "family": "ai_conventions_v1",
                "path": "AGENTS.md",
                "commit_sha": "a",
                "commit_time": ts,
                "author_name": "x",
                "author_email_hash": "h",
                "change_type": "add",
                "blob_sha": "b1",
                "extraction_wave": "t",
                "detector_version": "1.0.0",
            }
        ],
        schema=pa.schema(
            [
                ("repo_id", pa.string()),
                ("repo_url", pa.string()),
                ("family", pa.string()),
                ("path", pa.string()),
                ("commit_sha", pa.string()),
                ("commit_time", pa.timestamp("us", tz="UTC")),
                ("author_name", pa.string()),
                ("author_email_hash", pa.string()),
                ("change_type", pa.string()),
                ("blob_sha", pa.string()),
                ("extraction_wave", pa.string()),
                ("detector_version", pa.string()),
            ]
        ),
    )
    pq.write_table(table, path)
    grouped = load_instruction_file_events([path])
    assert ("r1", "AGENTS.md") in grouped
    assert len(grouped[("r1", "AGENTS.md")]) == 1


def test_generate_rq1_feasibility_report(tmp_path: Path):
    stats = RQ1ExploratoryStats(
        instruction_files=10,
        total_observations=100,
        references_per_file_median=2.0,
        references_per_file_mean=2.5,
        verified_ratio=0.3,
        missing_ratio=0.1,
        repaired_ratio=0.02,
        unverifiable_ratio=0.58,
        deleted_ratio=0.0,
        state_counts={"VERIFIED": 30, "MISSING": 10, "UNVERIFIABLE": 58, "REPAIRED": 2},
        transition_counts={"VERIFIED->MISSING": 5},
        first_failure_count=8,
        repair_event_count=2,
        reference_additions=20,
        reference_removals=5,
        median_time_to_first_missing_days=30.0,
        median_repair_latency_days=7.0,
        files_with_decay=4,
        files_with_repair=2,
    )
    report = generate_rq1_feasibility_report(
        stats=stats,
        output_path=tmp_path / "rq1_feasibility.md",
        figure_paths={"figure_a": tmp_path / "figure_a.pdf"},
    )
    text = report.read_text(encoding="utf-8")
    assert "RQ1" in text
    assert "TOSEM" in text or "Answer:" in text
