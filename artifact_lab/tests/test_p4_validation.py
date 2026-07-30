"""Tests for P4 human-gold validation (read-only metrics)."""

from __future__ import annotations

import csv
from pathlib import Path

from artifact_lab.experiments.truth_pilots.p4_attribution_precision import PRECISION_KILL_THRESHOLD
from artifact_lab.experiments.truth_pilots.p4_validation import (
    compute_binary_metrics,
    load_human_gold,
    precision_by_signal,
    run_p4_validation,
)


def _write_gold(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def test_compute_binary_metrics_perfect_agreement(tmp_path: Path):
    rows = [
        {
            "human_label": "true_agent_maintenance",
            "counts_as_agent_maintenance": "yes",
            "signature_category": "claude_signature",
        },
        {
            "human_label": "generic_bot",
            "counts_as_agent_maintenance": "no",
            "signature_category": "bot_author",
        },
    ]
    m = compute_binary_metrics(rows)
    assert m.precision == 1.0
    assert m.recall == 1.0
    assert m.accuracy == 1.0
    assert m.cohen_kappa == 1.0


def test_run_p4_validation_writes_report(tmp_path: Path):
    rows = [
        {
            "worksheet_id": "1",
            "repo_id": "r1",
            "instruction_path": "AGENTS.md",
            "commit_sha": "abc",
            "human_label": "true_agent_maintenance",
            "counts_as_agent_maintenance": "yes",
            "signature_category": "co_authored_by_trailer",
            "reviewer_notes": "",
        },
        {
            "worksheet_id": "2",
            "repo_id": "r1",
            "instruction_path": "AGENTS.md",
            "commit_sha": "def",
            "human_label": "generic_bot",
            "counts_as_agent_maintenance": "no",
            "signature_category": "bot_author",
            "reviewer_notes": "",
        },
    ]
    gold = tmp_path / "gold.csv"
    _write_gold(gold, rows)
    out = tmp_path / "p4_validation.md"
    run_p4_validation(gold_csv=gold, output_md=out)
    text = out.read_text(encoding="utf-8")
    assert "PASS" in text
    assert "Cohen" in text


def test_precision_by_signal_groups_coauthored(tmp_path: Path):
    rows = [
        {
            "human_label": "true_agent_maintenance",
            "counts_as_agent_maintenance": "yes",
            "signature_category": "co_authored_by_trailer",
        },
        {
            "human_label": "human_only",
            "counts_as_agent_maintenance": "yes",
            "signature_category": "co_authored_by_trailer",
        },
    ]
    signal = precision_by_signal(rows)
    co = next(s for s in signal if s["signal"] == "Co-Authored-By")
    assert co["precision"] == 0.5
    assert co["n"] == 2


def test_human_gold_file_if_present():
    """Optional: full human labels are not redistributed in the archival worksheet."""
    gold_path = Path("exports/truth_pilot/agent_attribution_gold_worksheet.csv")
    if not gold_path.exists():
        return
    rows = load_human_gold(gold_path)
    if len(rows) < 200:
        return
    metrics = compute_binary_metrics(rows)
    assert metrics.precision >= PRECISION_KILL_THRESHOLD
