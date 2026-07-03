"""Post-hoc RQ5 uptake analysis from existing traces."""

from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.truth_decay.rq5_experiment.models import ExperimentCase
from artifact_lab.experiments.truth_decay.rq5_experiment.task_selection import select_experiment_cases
from artifact_lab.experiments.truth_decay.rq5_experiment.trace_classifier import apply_trace_classifications
from artifact_lab.experiments.truth_decay.rq5_experiment.uptake_analysis import (
    classify_all_uptake,
    uptake_analysis_markdown,
    uptake_by_condition_rows,
)
from artifact_lab.experiments.truth_decay.rq5_experiment.uptake_figures import render_figure_uptake_flow
from artifact_lab.experiments.truth_decay.run_rq5_causal_evidence import (
    DEFAULT_CANDIDATE_CSV,
    DEFAULT_GFC_CSV,
    DEFAULT_RQ5_CAUSAL_EXPORT,
    _load_existing_results,
)


def _write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        atomic_write_text(path, "")
        return
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    atomic_write_text(path, buffer.getvalue())


def run_rq5_uptake_analysis(
    *,
    candidate_csv: Path = DEFAULT_CANDIDATE_CSV,
    gfc_confirmatory_csv: Path = DEFAULT_GFC_CSV,
    output_dir: Path = DEFAULT_RQ5_CAUSAL_EXPORT,
    max_cases: int | None = None,
    require_p1: bool = False,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    results_csv = output_dir / "rq5_results.csv"
    traces_dir = output_dir / "traces"

    cases = select_experiment_cases(
        candidate_csv=candidate_csv,
        gfc_confirmatory_csv=gfc_confirmatory_csv,
        max_cases=max_cases,
        require_p1=require_p1,
    )
    results = _load_existing_results(results_csv, cases)
    if not results:
        raise RuntimeError(f"no results found in {results_csv}")

    classified_results = apply_trace_classifications(results=results, cases=cases)
    uptake_rows = classify_all_uptake(
        results=classified_results,
        cases=cases,
        traces_dir=traces_dir,
    )
    dataset = [row.to_row() for row in uptake_rows]
    by_condition = uptake_by_condition_rows(uptake_rows)

    paths = {
        "analysis_md": output_dir / "rq5_uptake_analysis.md",
        "dataset_csv": output_dir / "rq5_uptake_dataset.csv",
        "by_condition_csv": output_dir / "rq5_uptake_by_condition.csv",
        "figure_uptake_flow": output_dir / "figure_uptake_flow.pdf",
    }

    _write_csv(dataset, paths["dataset_csv"])
    _write_csv(by_condition, paths["by_condition_csv"])
    atomic_write_text(
        paths["analysis_md"],
        uptake_analysis_markdown(classifications=uptake_rows, by_condition_rows=by_condition),
    )
    render_figure_uptake_flow(uptake_rows, paths["figure_uptake_flow"])
    return paths
