"""Load RQ5 v1 pilot runs for calibration fitting."""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from artifact_lab.experiments.task_calibration.scoring import (
    DifficultyDimensions,
    TaskFeatures,
    score_all_dimensions,
)


def _bool(value: object) -> bool:
    return str(value).lower() in ("true", "1", "yes")


@dataclass
class HistoricalCaseStats:
    case_id: str
    repo_id: str
    repository: str
    instruction_path: str
    anchor_reference: str
    test_command: str
    n_runs: int
    success_rate: float
    test_failure_rate: float
    median_files_modified: float
    compilation_failure_rate: float


@dataclass
class HistoricalIndex:
    global_failure_rate: float
    by_case: dict[tuple[str, str, str], HistoricalCaseStats]
    by_spec: dict[tuple[str, str], HistoricalCaseStats]
    by_repo: dict[str, HistoricalCaseStats]
    cases: list[HistoricalCaseStats]


def _repo_display(repo_url: str, repo_id: str) -> str:
    if repo_url and "github.com/" in repo_url:
        tail = repo_url.rstrip("/").split("github.com/")[-1]
        parts = tail.split("/")
        if len(parts) >= 2:
            return f"{parts[0]}/{parts[1]}"
    return repo_id


def load_historical_index(
    *,
    results_csv: Path,
    manifest_csv: Path,
    failure_modes_csv: Path | None = None,
) -> HistoricalIndex:
    manifest: dict[str, dict] = {}
    if manifest_csv.exists():
        with manifest_csv.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                manifest[row["case_id"]] = row

    failure_by_run: dict[tuple[str, str, str], str] = {}
    if failure_modes_csv and failure_modes_csv.exists():
        with failure_modes_csv.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                key = (row["case_id"], row["condition"], row["replicate_id"])
                failure_by_run[key] = row.get("failure_mode", "")

    grouped: dict[str, list[dict]] = defaultdict(list)
    if results_csv.exists():
        with results_csv.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                grouped[row["case_id"]].append(row)

    cases: list[HistoricalCaseStats] = []
    for case_id, runs in grouped.items():
        meta = manifest.get(case_id, runs[0] if runs else {})
        repo_id = meta.get("repo_id", runs[0].get("repo_id", "")) if runs else meta.get("repo_id", "")
        repo_url = meta.get("repo_url", runs[0].get("repo_url", "")) if runs else meta.get("repo_url", "")
        instruction_path = meta.get("instruction_path", runs[0].get("instruction_path", ""))
        anchor = meta.get("anchor_reference", runs[0].get("anchor_reference", ""))
        test_command = meta.get("test_command", runs[0].get("test_command", "pytest"))

        n = len(runs)
        successes = sum(1 for r in runs if _bool(r.get("success")))
        tests_fail = sum(1 for r in runs if not _bool(r.get("tests_passing")))
        compile_fail = sum(1 for r in runs if not _bool(r.get("compilation_success")))
        files = sorted(int(r.get("files_modified") or 0) for r in runs)
        median_files = float(files[len(files) // 2]) if files else 0.0

        cases.append(
            HistoricalCaseStats(
                case_id=case_id,
                repo_id=repo_id,
                repository=_repo_display(repo_url, repo_id),
                instruction_path=instruction_path,
                anchor_reference=anchor,
                test_command=test_command,
                n_runs=n,
                success_rate=successes / n if n else 0.0,
                test_failure_rate=tests_fail / n if n else 0.0,
                median_files_modified=median_files,
                compilation_failure_rate=compile_fail / n if n else 0.0,
            )
        )

    by_case: dict[tuple[str, str, str], HistoricalCaseStats] = {}
    by_spec: dict[tuple[str, str], HistoricalCaseStats] = {}
    by_repo: dict[str, HistoricalCaseStats] = {}

    for case in cases:
        key = (case.repo_id, case.instruction_path, case.anchor_reference)
        by_case[key] = case
        spec_key = (case.repo_id, case.instruction_path)
        if spec_key not in by_spec or case.n_runs > by_spec[spec_key].n_runs:
            by_spec[spec_key] = case
        if case.repo_id not in by_repo or case.n_runs > by_repo[case.repo_id].n_runs:
            by_repo[case.repo_id] = case

    total_runs = sum(c.n_runs for c in cases)
    total_success = sum(c.success_rate * c.n_runs for c in cases)
    global_failure = 1.0 - (total_success / total_runs) if total_runs else 0.87

    return HistoricalIndex(
        global_failure_rate=global_failure,
        by_case=by_case,
        by_spec=by_spec,
        by_repo=by_repo,
        cases=cases,
    )


def lookup_historical(
    index: HistoricalIndex,
    *,
    repo_id: str,
    instruction_path: str,
    anchor_reference: str,
) -> tuple[float | None, float | None, float | None, float | None]:
    """Return (case_success, spec_success, repo_success, median_files)."""
    case = index.by_case.get((repo_id, instruction_path, anchor_reference))
    if case:
        return case.success_rate, None, None, case.median_files_modified
    spec = index.by_spec.get((repo_id, instruction_path))
    repo = index.by_repo.get(repo_id)
    return (
        None,
        spec.success_rate if spec else None,
        repo.success_rate if repo else None,
        spec.median_files_modified if spec else (repo.median_files_modified if repo else None),
    )


def historical_training_rows(index: HistoricalIndex) -> list[tuple[DifficultyDimensions, float]]:
    """Dimension vectors + observed success for calibrator fitting."""
    rows: list[tuple[DifficultyDimensions, float]] = []
    for case in index.cases:
        features = TaskFeatures(
            repository=case.repository,
            reference=case.anchor_reference,
            instruction_path=case.instruction_path,
            reference_type="path",
            role="edit",
            test_command=case.test_command,
            context_snippet="",
            repo_id=case.repo_id,
        )
        dims = score_all_dimensions(
            features,
            historical_median_files=case.median_files_modified,
            case_success_rate=case.success_rate,
            global_failure_rate=index.global_failure_rate,
        )
        rows.append((dims, case.success_rate))
    return rows
