"""Post-hoc RQ5 null-result mediation audit from existing traces."""

from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.truth_decay.rq5_experiment.mediation_analysis import (
    classify_all_mediation,
    mediation_by_condition_rows,
    mediation_summary_markdown,
)
from artifact_lab.experiments.truth_decay.rq5_experiment.mediation_figures import render_figure_rq5_mediation_flow
from artifact_lab.experiments.truth_decay.rq5_experiment.task_selection import select_experiment_cases
from artifact_lab.experiments.truth_decay.rq5_experiment.trace_classifier import apply_trace_classifications
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


def run_rq5_mediation_analysis(
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
    mediation_rows = classify_all_mediation(
        results=classified_results,
        cases=cases,
        traces_dir=traces_dir,
    )
    dataset = [row.to_row() for row in mediation_rows]
    by_condition = mediation_by_condition_rows(mediation_rows)

    paths = {
        "dataset_csv": output_dir / "rq5_mediation_dataset.csv",
        "summary_md": output_dir / "rq5_mediation_summary.md",
        "by_condition_csv": output_dir / "rq5_mediation_by_condition.csv",
        "figure_mediation_flow": output_dir / "figure_rq5_mediation_flow.pdf",
    }

    _write_csv(dataset, paths["dataset_csv"])
    _write_csv(by_condition, paths["by_condition_csv"])
    atomic_write_text(
        paths["summary_md"],
        mediation_summary_markdown(classifications=mediation_rows, by_condition_rows=by_condition),
    )
    render_figure_rq5_mediation_flow(mediation_rows, paths["figure_mediation_flow"])
    return paths
