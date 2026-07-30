"""Tests for Phase 0 live status monitoring."""

from __future__ import annotations

from pathlib import Path

from artifact_lab.experiments.rq5_v2.phase0_status import (
    MIN_RUNS_FOR_RATE_WARNINGS,
    PHASE0_EXPECTED_CASES,
    build_status_snapshot,
    compute_warnings,
    load_results_csv,
    read_log_tail,
    render_status_markdown,
    run_phase0_status,
)


def _row(
    *,
    run_id: str = "r1",
    case_id: str = "c1",
    success: str = "False",
    instruction_read: str = "True",
    anchor_attempted: str = "True",
    error_message: str = "",
    cost_usd: str = "0.5",
    execution_time_seconds: str = "120",
    files_modified: str = "2",
    timed_out: str = "False",
) -> dict:
    return {
        "run_id": run_id,
        "case_id": case_id,
        "success": success,
        "instruction_read": instruction_read,
        "anchor_attempted": anchor_attempted,
        "compilation_success": "True",
        "tests_passing": "False",
        "error_message": error_message,
        "cost_usd": cost_usd,
        "token_usage": "1000",
        "execution_time_seconds": execution_time_seconds,
        "files_modified": files_modified,
        "timed_out": timed_out,
        "dry_run": "False",
    }


def test_load_results_empty(tmp_path: Path):
    assert load_results_csv(tmp_path / "missing.csv") == []


def test_read_log_tail(tmp_path: Path):
    log = tmp_path / "phase0_run.log"
    log.write_text("line1\n\nline2\n")
    tail = read_log_tail(log)
    assert "line2" in tail


def test_snapshot_progress_and_cost():
    rows = [
        _row(run_id="r1", case_id="c1", success="True"),
        _row(run_id="r2", case_id="c2", success="False", error_message="Vitest: not found"),
    ]
    snap = build_status_snapshot(rows=rows, log_tail="ok")
    assert snap.completed_runs == 2
    assert snap.completed_cases == 2
    assert snap.success_rate == 0.5
    assert snap.cumulative_cost == 1.0
    assert snap.provisional is True
    assert snap.estimated_remaining_cost > 0


def test_warnings_low_success_after_15_runs():
    rows = [
        _row(run_id=f"r{i}", success="False", error_message="test fail")
        for i in range(MIN_RUNS_FOR_RATE_WARNINGS)
    ]
    snap = build_status_snapshot(rows=rows)
    assert any("success rate" in w for w in snap.warnings)


def test_warnings_consecutive_infrastructure():
    rows = [
        _row(run_id=f"r{i}", error_message="Invalid API key")
        for i in range(4)
    ]
    snap = build_status_snapshot(rows=rows)
    assert any("consecutive infrastructure" in w for w in snap.warnings)


def test_warnings_infra_toolchain_rate():
    rows = [
        _row(run_id=f"r{i}", error_message="Vitest: not found")
        for i in range(MIN_RUNS_FOR_RATE_WARNINGS)
    ]
    snap = build_status_snapshot(rows=rows)
    assert any("infrastructure/toolchain" in w for w in snap.warnings)


def test_no_warnings_before_min_runs():
    rows = [_row(run_id=f"r{i}", success="False") for i in range(5)]
    warnings = compute_warnings(
        rows=rows,
        snapshot_metrics={
            "success_rate": 0.0,
            "anchor_attempt_rate": 0.0,
            "instruction_read_rate": 0.0,
            "infra_toolchain_rate": 1.0,
            "median_files_modified": 50.0,
        },
    )
    assert warnings == []


def test_run_phase0_status_writes_md(tmp_path: Path):
    export = tmp_path / "exports/rq5_v2_factorial"
    export.mkdir(parents=True)
    (export / "phase0_results.csv").write_text(
        "run_id,case_id,success,instruction_read,anchor_attempted,compilation_success,"
        "tests_passing,error_message,cost_usd,execution_time_seconds,files_modified,timed_out,dry_run\n"
        "r1,c1,True,True,True,True,True,,0.5,100,1,False,False\n"
    )
    (export / "phase0_run.log").write_text("run started\n")
    (export / "phase0_trace_audit.csv").write_text("run_id,trace_bytes\nr1,100\n")
    out = run_phase0_status(output_dir=export)
    assert out.exists()
    text = out.read_text()
    assert "1 / 60" in text
    assert "Provisional" in text


def test_render_includes_last_failure():
    rows = [_row(success="False", error_message="timeout_after_1200s")]
    snap = build_status_snapshot(rows=rows)
    md = render_status_markdown(snap)
    assert "timeout_after_1200s" in md
    assert f"/ {PHASE0_EXPECTED_CASES}" in md
