"""Build factorial cases from calibrated load-bearing candidates."""

from __future__ import annotations

import csv
from pathlib import Path

from artifact_lab.experiments.task_calibration.scoring import extract_test_command_from_task
from artifact_lab.experiments.truth_decay.born_stale_context import build_blob_index
from artifact_lab.experiments.truth_pilots.gates_common import DEFAULT_L1_PATHS
from artifact_lab.experiments.rq5_v2.instruction_variants import (
    build_factorial_cells,
    case_id_from_candidate,
    derive_decoy_path,
    derive_false_path,
)
from artifact_lab.experiments.rq5_v2.models import FactorialCase
from artifact_lab.store.blobs import BlobStore

DEFAULT_CANDIDATES_CSV = Path("exports/rq5_v2/load_bearing_candidates.csv")
DEFAULT_CALIBRATION_CSV = Path("exports/task_calibration/difficulty_scores.csv")


def _ecosystem(test_command: str, instruction_path: str) -> str:
    cmd = test_command.lower()
    path = instruction_path.lower()
    if any(x in cmd for x in ("npm", "yarn", "pnpm", "jest", "vitest")) or "package.json" in path:
        return "node"
    if any(x in cmd for x in ("cargo", "go test", "mvn")):
        return "other"
    return "python"


def _load_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _calibration_index(rows: list[dict]) -> dict[str, dict]:
    return {row["candidate_id"]: row for row in rows if row.get("candidate_id")}


def _bool(value: object) -> bool:
    return str(value).lower() in ("true", "1", "yes")


def build_factorial_cases(
    *,
    candidates_csv: Path = DEFAULT_CANDIDATES_CSV,
    calibration_csv: Path = DEFAULT_CALIBRATION_CSV,
    blobs_dir: Path = Path("data/blobs"),
    l1_paths: list[Path] | None = None,
    max_cases: int | None = None,
    require_calibration_band: bool = True,
) -> list[FactorialCase]:
    """
    Construct factorial cases from load-bearing candidates + calibration scores.

    By default only includes rows with `recommended_for_pilot=True`.
    """
    candidates = _load_csv(candidates_csv)
    calibration = _calibration_index(_load_csv(calibration_csv))
    blob_store = BlobStore(blobs_dir)
    blob_index = build_blob_index(list(l1_paths or DEFAULT_L1_PATHS))

    cases: list[FactorialCase] = []
    for row in candidates:
        cid = row.get("candidate_id", "")
        cal = calibration.get(cid, {})
        if require_calibration_band and cal and not _bool(cal.get("recommended_for_pilot")):
            continue
        if require_calibration_band and not cal:
            continue

        repo_id = row["repo_id"]
        instruction_path = row["instruction_path"]
        commit = row["commit_sha"]
        anchor_true = row["reference"]

        blob_sha = blob_index.get((repo_id, instruction_path, commit), "")
        if not blob_sha:
            continue
        try:
            base_text = blob_store.get_text(blob_sha).decode("utf-8", errors="replace")
        except OSError:
            continue
        if not base_text.strip():
            continue

        test_command = extract_test_command_from_task(row.get("task", ""))
        false_path = derive_false_path(anchor_true)
        decoy = derive_decoy_path(anchor_true, instruction_path)

        cells = build_factorial_cells(
            base_instruction_text=base_text,
            anchor_true=anchor_true,
            test_command=test_command,
            blob_store=blob_store,
            anchor_false=false_path,
            decoy_path=decoy,
        )

        case_id = case_id_from_candidate(cid, commit)
        expected = float(cal.get("calibrated_expected_success", row.get("estimated_success_rate", 0.5)))

        cases.append(
            FactorialCase(
                case_id=case_id,
                candidate_id=cid,
                repo_id=repo_id,
                repo_url=row.get("repo_url", ""),
                repository=row.get("repository", ""),
                instruction_path=instruction_path,
                commit_sha=commit,
                anchor_path_true=anchor_true,
                anchor_path_false=false_path,
                decoy_path=decoy,
                test_command=test_command,
                reference_type=row.get("reference_type", "path"),
                load_bearing_role=row.get("role", "edit"),
                ecosystem=_ecosystem(test_command, instruction_path),
                calibrated_expected_success=expected,
                cells=cells,
            )
        )
        if max_cases is not None and len(cases) >= max_cases:
            break

    return cases
