"""Deterministic task/case selection for RQ5 causal experiment."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

from artifact_lab.experiments.truth_decay.rq5_availability import TEST_COMMAND_PATTERNS
from artifact_lab.experiments.truth_decay.rq5_experiment.models import ExperimentCase

DEFAULT_TASK_PROMPT = (
    "Complete the bounded coding task described in the project instruction file. "
    "Treat the instruction file as authoritative project context. "
    "Use only the repository state at the pinned commit. "
    "Run tests before finishing."
)


def stable_case_id(*parts: str) -> str:
    payload = "|".join(parts).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def load_confirmed_false_keys(gfc_confirmatory_csv: Path) -> set[tuple[str, str, str]]:
    keys: set[tuple[str, str, str]] = set()
    with gfc_confirmatory_csv.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if str(row.get("is_confirmed_false", "")).lower() in ("true", "1"):
                keys.add((row["repo_id"], row["instruction_path"], row["reference"]))
    return keys


def _infer_test_command(task_availability_reason: str, instruction_text: str = "") -> str:
    for pattern in TEST_COMMAND_PATTERNS:
        match = pattern.search(instruction_text)
        if match:
            return match.group(0).strip()
    reason = task_availability_reason or ""
    for token in ("pytest", "npm test", "yarn test", "cargo test", "go test", "make test"):
        if token.replace(" ", "_") in reason or token in reason:
            return token
    return "pytest"


def select_experiment_cases(
    *,
    candidate_csv: Path,
    gfc_confirmatory_csv: Path,
    instruction_text_by_blob: dict[str, str] | None = None,
    max_cases: int | None = None,
    require_p1: bool = False,
    require_confirmed_false: bool = True,
) -> list[ExperimentCase]:
    """Select natural A/B cases: truthful blob vs confirmed-false instruction swap."""
    confirmed = load_confirmed_false_keys(gfc_confirmatory_csv) if require_confirmed_false else set()

    born_stale_rows: list[dict] = []
    with candidate_csv.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("experimental_eligible", "").lower() not in ("true", "1"):
                continue
            if row.get("snapshot_type") != "born_stale":
                continue
            if require_p1 and row.get("p1_sample", "").lower() not in ("true", "1"):
                continue
            if not row.get("paired_truthful_blob_sha"):
                continue
            if not row.get("blob_sha"):
                continue
            key = (row["repo_id"], row["instruction_path"], row["anchor_reference"])
            if require_confirmed_false and key not in confirmed:
                continue
            born_stale_rows.append(row)

    born_stale_rows.sort(key=lambda r: (r["spec_id"], r["snapshot_id"]))

    cases: list[ExperimentCase] = []
    for row in born_stale_rows:
        blob_text = ""
        if instruction_text_by_blob:
            blob_text = instruction_text_by_blob.get(row.get("blob_sha", ""), "")

        task_commit = row.get("paired_truthful_commit_sha") or row.get("task_commit_sha", "")
        if not task_commit:
            continue

        case_id = stable_case_id(row["spec_id"], row["anchor_reference"], task_commit)
        cases.append(
            ExperimentCase(
                case_id=case_id,
                spec_id=row["spec_id"],
                repo_id=row["repo_id"],
                repo_url=row["repo_url"],
                instruction_path=row["instruction_path"],
                task_commit_sha=task_commit,
                anchor_reference=row["anchor_reference"],
                anchor_reference_type=row["anchor_reference_type"],
                condition_a_blob_sha=row["paired_truthful_blob_sha"],
                condition_b_blob_sha=row["blob_sha"],
                born_stale_commit_sha=row["commit_sha"],
                truthful_commit_sha=row.get("paired_truthful_commit_sha", ""),
                task_prompt=DEFAULT_TASK_PROMPT,
                test_command=_infer_test_command(row.get("task_availability_reason", ""), blob_text),
                selection_reason="born_stale_confirmed_false_with_truthful_pair",
                confirmed_false=True,
                p1_sample=row.get("p1_sample", "").lower() in ("true", "1"),
            )
        )

    if max_cases is not None:
        cases = cases[:max_cases]
    return cases
