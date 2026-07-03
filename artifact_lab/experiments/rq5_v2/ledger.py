"""Run ledger for checkpoint/resume (no execution in default build)."""

from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.rq5_v2.models import FactorialRunResult, RunPlanEntry


def completed_run_keys(results_csv: Path) -> set[str]:
    if not results_csv.exists():
        return set()
    keys: set[str] = set()
    with results_csv.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            keys.add(row.get("run_id", ""))
    return {k for k in keys if k}


def pending_entries(
    *,
    plan: list[RunPlanEntry],
    results_csv: Path,
) -> list[RunPlanEntry]:
    done = completed_run_keys(results_csv)
    return [entry for entry in plan if entry.run_id not in done]


def append_result(path: Path, result: FactorialRunResult) -> None:
    row = result.to_row()
    exists = path.exists() and path.stat().st_size > 0
    buffer = StringIO()
    fieldnames = list(row.keys())
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
    if not exists:
        writer.writeheader()
    writer.writerow(row)
    mode = "a" if exists else "w"
    with path.open(mode, encoding="utf-8") as handle:
        handle.write(buffer.getvalue())
