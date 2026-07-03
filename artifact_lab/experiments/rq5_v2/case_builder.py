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
)
from artifact_lab.experiments.rq5_v2.models import FactorialCase
from artifact_lab.experiments.rq5_v2.path_derivation import derive_case_paths
from artifact_lab.experiments.rq5_v2.repo_tree import RepoTreeCache
from artifact_lab.experiments.truth_pilots.verify_refs import _path_exists
from artifact_lab.store.blobs import BlobStore

DEFAULT_CANDIDATES_CSV = Path("exports/rq5_v2/load_bearing_candidates.csv")
DEFAULT_CALIBRATION_CSV = Path("exports/task_calibration/difficulty_scores.csv")
MAX_CASES_PER_REPO = 3
TARGET_SUCCESS = 0.50


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


def _float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def _dedupe_key(row: dict) -> tuple[str, str, str]:
    return (row["repo_id"], row["reference"], row["commit_sha"])


def _selection_tuple(row: dict, calibration: dict[str, dict]) -> tuple[float, float, float, str]:
    cid = row.get("candidate_id", "")
    cal = calibration.get(cid, {})
    confidence = _float(row.get("confidence"))
    calibrated = _float(cal.get("calibrated_expected_success"), _float(row.get("estimated_success_rate"), 0.5))
    repair = _float(row.get("repairability_score") or cal.get("repairability_score"))
    return (
        confidence,
        -abs(calibrated - TARGET_SUCCESS),
        repair,
        cid,
    )


def _predict_ecosystem(row: dict) -> str:
    test_command = extract_test_command_from_task(row.get("task", ""))
    return _ecosystem(test_command, row.get("instruction_path", ""))


def _round_robin_candidates(candidates: list[dict]) -> list[dict]:
    """Prefer node/other candidates before python to keep Phase 0 cohort balanced."""
    buckets: dict[str, list[dict]] = {"node": [], "other": [], "python": []}
    for row in candidates:
        buckets[_predict_ecosystem(row)].append(row)

    ordered: list[dict] = []
    indices = {key: 0 for key in buckets}
    priority = ("node", "other", "python")
    remaining = sum(len(v) for v in buckets.values())
    while remaining > 0:
        progressed = False
        for eco in priority:
            idx = indices[eco]
            if idx < len(buckets[eco]):
                ordered.append(buckets[eco][idx])
                indices[eco] += 1
                remaining -= 1
                progressed = True
        if not progressed:
            break
    return ordered


def deduplicate_candidates(
    candidates: list[dict],
    calibration: dict[str, dict],
) -> list[dict]:
    """Keep best row per (repo_id, true_anchor_path, commit_sha)."""
    groups: dict[tuple[str, str, str], list[dict]] = {}
    for row in candidates:
        groups.setdefault(_dedupe_key(row), []).append(row)

    selected: list[dict] = []
    for group in groups.values():
        best = max(group, key=lambda r: _selection_tuple(r, calibration))
        selected.append(best)
    selected.sort(key=lambda r: _selection_tuple(r, calibration), reverse=True)
    return selected


def build_factorial_cases(
    *,
    candidates_csv: Path = DEFAULT_CANDIDATES_CSV,
    calibration_csv: Path = DEFAULT_CALIBRATION_CSV,
    blobs_dir: Path = Path("data/blobs"),
    l1_paths: list[Path] | None = None,
    scratch_dir: Path = Path("scratch"),
    max_cases: int | None = None,
    require_calibration_band: bool = True,
    max_cases_per_repo: int = MAX_CASES_PER_REPO,
) -> list[FactorialCase]:
    """
    Construct factorial cases from load-bearing candidates + calibration scores.

    Uses commit-aware false/decoy derivation and deduplicates by repo/anchor/commit.
    """
    candidates = _load_csv(candidates_csv)
    calibration = _calibration_index(_load_csv(calibration_csv))
    blob_store = BlobStore(blobs_dir)
    blob_index = build_blob_index(list(l1_paths or DEFAULT_L1_PATHS))
    tree_cache = RepoTreeCache(scratch_dir=scratch_dir, clone_prefix="rq5v2_build")

    filtered: list[dict] = []
    for row in candidates:
        cid = row.get("candidate_id", "")
        cal = calibration.get(cid, {})
        if require_calibration_band and cal and not _bool(cal.get("recommended_for_pilot")):
            continue
        if require_calibration_band and not cal:
            continue
        filtered.append(row)

    candidates = _round_robin_candidates(deduplicate_candidates(filtered, calibration))

    # Scan more rows than max_cases because path derivation rejects some candidates.
    scan_limit = (max_cases or 20) * 8

    cases: list[FactorialCase] = []
    repo_counts: dict[str, int] = {}

    for row in candidates:
        if max_cases is not None and len(cases) >= max_cases:
            break
        if scan_limit <= 0:
            break
        scan_limit -= 1

        cid = row.get("candidate_id", "")
        cal = calibration.get(cid, {})
        repo_id = row["repo_id"]
        if repo_counts.get(repo_id, 0) >= max_cases_per_repo:
            continue

        instruction_path = row["instruction_path"]
        commit = row["commit_sha"]
        anchor_true = row["reference"]
        repo_url = row.get("repo_url", "")
        if not repo_url:
            continue

        blob_sha = blob_index.get((repo_id, instruction_path, commit), "")
        if not blob_sha:
            continue
        try:
            base_text = blob_store.get_text(blob_sha).decode("utf-8", errors="replace")
        except OSError:
            continue
        if not base_text.strip():
            continue

        tree_paths = tree_cache.paths_at(repo_id=repo_id, repo_url=repo_url, commit_sha=commit)
        if not _path_exists(anchor_true, tree_paths):
            continue

        derived = derive_case_paths(anchor_true, tree_paths)
        if derived is None:
            continue

        test_command = extract_test_command_from_task(row.get("task", ""))
        cells = build_factorial_cells(
            base_instruction_text=base_text,
            anchor_true=anchor_true,
            test_command=test_command,
            blob_store=blob_store,
            anchor_false=derived.false_path,
            decoy_path=derived.decoy_path,
        )

        case_id = case_id_from_candidate(cid, commit)
        expected = _float(cal.get("calibrated_expected_success"), _float(row.get("estimated_success_rate"), 0.5))

        cases.append(
            FactorialCase(
                case_id=case_id,
                candidate_id=cid,
                repo_id=repo_id,
                repo_url=repo_url,
                repository=row.get("repository", ""),
                instruction_path=instruction_path,
                commit_sha=commit,
                anchor_path_true=anchor_true,
                anchor_path_false=derived.false_path,
                decoy_path=derived.decoy_path,
                test_command=test_command,
                reference_type=row.get("reference_type", "path"),
                load_bearing_role=row.get("role", "edit"),
                ecosystem=_ecosystem(test_command, instruction_path),
                calibrated_expected_success=expected,
                repairability_score=derived.repairability_score,
                repairability_reason=derived.repairability_reason,
                cells=cells,
            )
        )
        repo_counts[repo_id] = repo_counts.get(repo_id, 0) + 1

    return cases
