"""Orchestrate RQ1 truth-decay feasibility study."""

from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.truth_decay.figures import render_all_figures
from artifact_lab.experiments.truth_decay.longitudinal import (
    observations_to_rows,
    reconstruct_longitudinal_table,
)
from artifact_lab.experiments.truth_decay.report import generate_rq1_feasibility_report
from artifact_lab.experiments.truth_decay.stats import compute_exploratory_stats, stats_to_summary_rows

DEFAULT_L1_PATHS = (
    Path("data/l1/file_event_log/v1/events.parquet"),
    Path("data/l1/e1_100/v1/events.parquet"),
)
DEFAULT_EXPORT_DIR = Path("exports/truth_decay_pilot")


def _write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        atomic_write_text(path, "")
        return
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    atomic_write_text(path, buffer.getvalue())


def run_rq1_feasibility_study(
    *,
    l1_paths: list[Path],
    blobs_dir: Path,
    scratch_dir: Path,
    output_dir: Path,
    clone_timeout: int = 180,
    max_files: int | None = None,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    observations = reconstruct_longitudinal_table(
        l1_paths=l1_paths,
        blobs_dir=blobs_dir,
        scratch_dir=scratch_dir,
        clone_timeout=clone_timeout,
        max_files=max_files,
    )
    rows = observations_to_rows(observations)
    stats = compute_exploratory_stats(rows)

    longitudinal_csv = output_dir / "reference_longitudinal.csv"
    summary_csv = output_dir / "rq1_exploratory_stats.csv"
    report_md = output_dir / "rq1_feasibility.md"

    _write_csv(rows, longitudinal_csv)
    _write_csv(stats_to_summary_rows(stats), summary_csv)

    figure_paths = render_all_figures(rows, stats, output_dir)
    generate_rq1_feasibility_report(stats=stats, output_path=report_md, figure_paths=figure_paths)

    return {
        "longitudinal": longitudinal_csv,
        "summary": summary_csv,
        "report": report_md,
        **figure_paths,
    }
