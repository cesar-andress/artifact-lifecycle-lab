"""Tests for RQ5 v2 Phase 0 post-processing pipeline."""

from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path

from artifact_lab.experiments.rq5_v2.models import FactorialCase, FactorialCell
from artifact_lab.experiments.rq5_v2.phase0_analysis import (
    classify_failure,
    compute_funnel,
    evaluate_gates,
    funnel_transitions,
    power_update,
    run_phase0_analysis,
    write_gate_report,
)
from artifact_lab.experiments.rq5_v2.phase0_figures import render_success_rate
from artifact_lab.experiments.rq5_v2.phase0_provenance import collect_provenance, provenance_block
from artifact_lab.experiments.rq5_v2.phase0_run import PHASE0_CELL, compute_phase0_metrics


def _sample_row(**overrides) -> dict:
    base = {
        "run_id": "r1",
        "case_id": "c1",
        "cell_code": PHASE0_CELL,
        "success": "False",
        "tests_passing": "False",
        "compilation_success": "True",
        "execution_time_seconds": "120",
        "files_modified": "2",
        "tool_failures": "0",
        "read_instruction": "True",
        "anchor_path_touched": "True",
        "decoy_path_touched": "False",
        "bind_failure_detected": "False",
        "grounding_action": "False",
        "repair_success": "False",
        "dry_run": "False",
        "error_message": "",
        "trace_path": "",
        "cost_usd": "0.5",
        "token_usage": "1000",
        "commands_executed": "5",
        "iterations": "3",
        "anchor_attempted": "True",
        "instruction_read": "True",
        "timed_out": "False",
    }
    base.update(overrides)
    return base


def test_classify_failure_taxonomy():
    assert classify_failure(_sample_row(success="True")) == ""
    assert classify_failure(_sample_row(timed_out="True")) == "Timeout"
    assert classify_failure(_sample_row(error_message="Invalid API key")) == "Infrastructure"
    assert classify_failure(_sample_row(error_message="Vitest: not found")) == "Toolchain"
    assert classify_failure(_sample_row(instruction_read="False")) == "No instruction uptake"
    assert classify_failure(_sample_row(anchor_attempted="False", instruction_read="True")) == "No grounding"
    assert classify_failure(_sample_row(compilation_success="False")) == "Compilation"
    assert classify_failure(_sample_row(decoy_path_touched="True", anchor_path_touched="False")) == "Wrong edit"


def test_funnel_counts():
    rows = [
        _sample_row(anchor_attempted="True", bind_failure_detected="True", grounding_action="True"),
        _sample_row(anchor_attempted="False", instruction_read="False"),
    ]
    funnel = compute_funnel(rows)
    assert funnel["all_runs"] == 2
    assert funnel["M1_anchor_attempted"] == 1
    assert funnel["M2_bind_failure"] == 1
    assert funnel["M3_grounding_action"] == 1


def test_funnel_transitions():
    rows = [_sample_row(anchor_attempted="True", bind_failure_detected="True")]
    trans = funnel_transitions(rows)
    assert "read→M1→M2" in trans


def test_evaluate_gates_pass():
    rows = []
    for i in range(60):
        rows.append(
            _sample_row(
                run_id=f"r{i}",
                case_id=f"c{i // 3}",
                success="True" if i < 33 else "False",
                anchor_attempted="True",
                instruction_read="True",
            )
        )
    metrics = compute_phase0_metrics(rows)
    audit = {f"c{i}": {"repairability_score": "3"} for i in range(20)}
    manifest = Path("exports/rq5_v2_factorial/factorial_case_manifest.json")
    gates = evaluate_gates(rows=rows, metrics=metrics, audit=audit, manifest_path=manifest)
    cal = next(g for g in gates if "Calibration" in g.gate)
    assert cal.status == "PASS"
    read = next(g for g in gates if "Instruction read" in g.gate)
    assert read.status == "PASS"


def test_power_update_uses_observed_variance():
    rows = [_sample_row(success="True" if i % 2 == 0 else "False", case_id=f"c{i//3}") for i in range(12)]
    metrics = compute_phase0_metrics(rows)
    md = power_update(rows=rows, metrics=metrics)
    assert "observed" in md.lower()
    assert "Phase 1a" in md


def test_provenance_block_contains_fields(tmp_path: Path):
    prov = collect_provenance(
        manifest_path=tmp_path / "missing.json",
        script_paths=[Path(__file__)],
        cwd=tmp_path,
    )
    block = provenance_block(prov)
    assert "Git commit" in block
    assert "Manifest SHA-256" in block


def test_render_success_rate_pdf(tmp_path: Path):
    out = tmp_path / "success_rate.pdf"
    render_success_rate(success_rate=0.5, wilson_low=0.4, wilson_high=0.6, path=out)
    assert out.exists()
    assert out.stat().st_size > 100


def test_run_phase0_analysis_on_exports(tmp_path: Path):
    real = Path("exports/rq5_v2_factorial")
    if (real / "phase0_results.csv").exists():
        paths = run_phase0_analysis(output_dir=real)
    else:
        export_dir = tmp_path / "factorial"
        export_dir.mkdir()
        traces = export_dir / "phase0_traces"
        traces.mkdir()
        row = _sample_row(trace_path=str(traces / "r1.jsonl"))
        (traces / "r1.jsonl").write_text('{"type":"result","num_turns":1,"usage":{},"total_cost_usd":0.1}\n')
        buf = StringIO()
        w = csv.DictWriter(buf, fieldnames=list(row.keys()))
        w.writeheader()
        w.writerow(row)
        (export_dir / "phase0_results.csv").write_text(buf.getvalue())
        (export_dir / "phase0_case_audit.csv").write_text("case_id,repairability_score\nc1,3\n")
        (export_dir / "factorial_case_manifest.json").write_text("[]")
        paths = run_phase0_analysis(output_dir=export_dir)
    assert paths["dashboard"].exists()
    assert paths["gate_report"].exists()
    assert paths["fig_success"].exists()
    assert paths["provenance"].exists()


def test_write_gate_report(tmp_path: Path):
    from artifact_lab.experiments.rq5_v2.phase0_analysis import GateRow

    gates = [GateRow("Test gate", ">0.5", "0.6", "PASS")]
    prov = {"generated_at": "t", "git_commit": "abc", "manifest_sha256": "m", "python_version": "3.11", "platform": "x", "analysis_script_hashes": {}}
    out = tmp_path / "gates.md"
    write_gate_report(gates=gates, provenance=prov, path=out)
    text = out.read_text()
    assert "PASS" in text
    assert "Reproducibility" in text
