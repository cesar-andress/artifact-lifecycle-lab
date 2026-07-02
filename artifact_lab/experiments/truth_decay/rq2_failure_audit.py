"""RQ2 post-verification failure audit — taxonomy and deterministic classification."""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from artifact_lab.experiments.truth_decay.born_stale_audit import (
    is_likely_external,
    is_relative_path_candidate,
)
from artifact_lab.experiments.truth_decay.born_stale_taxonomy import (
    HeuristicVerdict,
    classify_heuristic,
    needs_llm_adjudication,
)
from artifact_lab.experiments.truth_decay.survival_dataset import OUTCOME_FIRST_MISSING
from artifact_lab.experiments.truth_pilots.gates_common import _csv_bool

FAILURE_CATEGORIES = (
    "genuine_decay",
    "rename_or_move",
    "verification_anchor_issue",
    "extractor_artifact",
    "normative_or_prescriptive",
    "external_or_environmental",
    "ambiguous",
)

CATEGORY_LETTERS = {
    "genuine_decay": "A",
    "rename_or_move": "B",
    "verification_anchor_issue": "C",
    "extractor_artifact": "D",
    "normative_or_prescriptive": "E",
    "external_or_environmental": "F",
    "ambiguous": "G",
}

BORN_STALE_TO_RQ2 = {
    "extraction_artifact": "extractor_artifact",
    "template_placeholder": "extractor_artifact",
    "normative_prescriptive": "normative_or_prescriptive",
    "verification_anchor_mismatch": "verification_anchor_issue",
    "external_reference": "external_or_environmental",
    "pre_observation_evolution": "ambiguous",
    "genuine_false_claim": "genuine_decay",
    "unresolved_disagreement": "ambiguous",
}


@dataclass(frozen=True)
class FailureAuditRecord:
    repo_id: str
    repo_url: str
    instruction_path: str
    reference_type: str
    reference: str
    time_origin: str
    time_end: str
    duration_days: float
    ever_repaired: bool
    post_failure_followup_days: float | None
    failure_commit: str
    failure_transition: str
    verified_before_failure: bool
    returned_after_missing: bool
    basename_collision_verified: bool
    n_observations: int
    repeated_repo_count: int
    repeated_file_count: int
    snippet_available: bool
    snippet: str
    born_stale_heuristic_category: str
    born_stale_heuristic_confidence: str
    born_stale_heuristic_rules: str
    heuristic_category: str
    heuristic_confidence: str
    heuristic_rules: str
    heuristic_rationale: str
    adjudication_status: str
    final_category: str
    category_letter: str
    is_genuine_decay: bool
    judge_a_model: str
    judge_a_category: str
    judge_a_rationale: str
    judge_b_model: str
    judge_b_category: str
    judge_b_rationale: str
    judge_agreement: str


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _trajectory_key(row: dict) -> tuple[str, str, str, str]:
    return (row["repo_id"], row["instruction_path"], row["reference_type"], row["reference"])


def load_survival_failures(survival_csv: Path) -> list[dict]:
    rows: list[dict] = []
    with survival_csv.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("outcome") == OUTCOME_FIRST_MISSING:
                rows.append(row)
    return rows


def _repetition_counts(longitudinal_rows: list[dict]) -> tuple[dict[str, int], dict[str, int]]:
    ref_counts: Counter[str] = Counter()
    file_counts: Counter[str] = Counter()
    for row in longitudinal_rows:
        if _csv_bool(row.get("reference_removed")):
            continue
        ref_key = f"{row['reference_type']}:{row['reference']}"
        ref_counts[ref_key] += 1
        file_counts[row["instruction_path"]] += 1
    return dict(ref_counts), dict(file_counts)


def _group_trajectories(longitudinal_rows: list[dict]) -> dict[tuple, list[dict]]:
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in longitudinal_rows:
        if _csv_bool(row.get("reference_removed")):
            continue
        grouped[_trajectory_key(row)].append(row)
    for events in grouped.values():
        events.sort(key=lambda r: r["commit_time"])
    return grouped


def _failure_event(events: list[dict], time_end: str) -> dict | None:
    end_dt = _parse_time(time_end)
    candidates = [e for e in events if _parse_time(e["commit_time"]) == end_dt and e["state"] == "MISSING"]
    if candidates:
        return candidates[0]
    for e in events:
        if e.get("transition") == "VERIFIED->MISSING":
            return e
    return None


def _returned_after_missing(events: list[dict], failure_time: str) -> bool:
    fail_dt = _parse_time(failure_time)
    seen_missing = False
    for ev in events:
        ts = _parse_time(ev["commit_time"])
        if ts < fail_dt:
            continue
        if ev["state"] == "MISSING":
            seen_missing = True
        if seen_missing and ev["state"] in ("VERIFIED", "REPAIRED"):
            return True
    return False


def _basename_collision_verified(
    *,
    events: list[dict],
    reference: str,
    failure_time: str,
) -> bool:
    basename = reference.rstrip("/").split("/")[-1]
    if not basename or basename == reference:
        return False
    fail_dt = _parse_time(failure_time)
    for ev in events:
        if _parse_time(ev["commit_time"]) != fail_dt:
            continue
        if ev["state"] != "VERIFIED":
            continue
        other = ev["reference"]
        if other != reference and other.rstrip("/").split("/")[-1] == basename:
            return True
    return False


def _post_verification_heuristic(
    *,
    reference_type: str,
    reference: str,
    instruction_path: str,
    n_observations: int,
    first_change_type: str,
    repeated_repo_count: int,
    repeated_file_count: int,
    snippet: str,
    ever_repaired: bool,
    returned_after_missing: bool,
    basename_collision: bool,
) -> tuple[str, str, tuple[str, ...], str]:
    """Return (category, confidence, rules, rationale) for RQ2 failure audit."""
    rules: list[str] = []

    if ever_repaired:
        rules.append("repair_event_after_first_missing")
        return (
            "rename_or_move",
            "medium",
            tuple(rules),
            "Reference returned to VERIFIED/REPAIRED after first MISSING — likely transient or path fix.",
        )
    if returned_after_missing:
        rules.append("verified_after_missing_same_trajectory")
        return (
            "rename_or_move",
            "medium",
            tuple(rules),
            "Post-failure observation shows reference verified again without new extraction key.",
        )
    if basename_collision:
        rules.append("same_basename_verified_at_failure_commit")
        return (
            "rename_or_move",
            "medium",
            tuple(rules),
            "Another verified reference shares basename at failure commit — possible rename/move.",
        )

    born = classify_heuristic(
        reference_type=reference_type,
        reference=reference,
        instruction_path=instruction_path,
        n_observations=n_observations,
        first_change_type=first_change_type,
        repeated_repo_count=repeated_repo_count,
        repeated_file_count=repeated_file_count,
        snippet=snippet,
    )
    if born.category:
        mapped = BORN_STALE_TO_RQ2.get(born.category, "ambiguous")
        if mapped == "genuine_decay" and born.confidence == "low":
            return (
                "ambiguous",
                "low",
                born.rules_fired + ("post_verification_low_confidence_genuine",),
                "Was VERIFIED then MISSING, but low-confidence path claim — may be verifier artifact.",
            )
        return mapped, born.confidence, born.rules_fired, born.rationale

    if is_relative_path_candidate(reference, reference_type):
        return (
            "verification_anchor_issue",
            "high",
            ("relative_or_single_segment_anchor",),
            "Relative path anchor may differ between verification and failure snapshot.",
        )
    if reference_type == "dependency" or is_likely_external(reference_type, reference):
        return (
            "external_or_environmental",
            "high",
            ("external_or_dependency_token",),
            "Reference depends on external package/tool state not pinned in repo tree.",
        )

    return (
        "ambiguous",
        "low",
        ("insufficient_heuristic_evidence",),
        "No deterministic RQ2 failure category met threshold.",
    )


def needs_rq2_llm_adjudication(*, category: str, confidence: str, born_verdict: HeuristicVerdict) -> bool:
    if category == "ambiguous":
        return True
    if confidence == "low":
        return True
    if category == "genuine_decay" and confidence != "high":
        return True
    return needs_llm_adjudication(born_verdict)


def map_llm_category_to_rq2(category: str | None) -> str:
    if not category:
        return "ambiguous"
    if category in FAILURE_CATEGORIES:
        return category
    return BORN_STALE_TO_RQ2.get(category, "ambiguous")


def _repo_url_map(longitudinal_rows: list[dict]) -> dict[str, str]:
    urls: dict[str, str] = {}
    for row in longitudinal_rows:
        rid = row["repo_id"]
        if rid not in urls and row.get("repo_url"):
            urls[rid] = row["repo_url"]
    return urls


def _first_event_meta(events: list[dict]) -> dict:
    if not events:
        return {"first_commit": "", "first_change_type": ""}
    return {
        "first_commit": events[0].get("commit", ""),
        "first_change_type": events[0].get("change_type", ""),
    }


def build_failure_audit_records(
    *,
    survival_failures: list[dict],
    longitudinal_rows: list[dict],
) -> list[dict]:
    """Prepare per-failure context rows before snippet load and adjudication."""
    trajectories = _group_trajectories(longitudinal_rows)
    ref_counts, file_counts = _repetition_counts(longitudinal_rows)
    repo_urls = _repo_url_map(longitudinal_rows)
    prepared: list[dict] = []

    for row in survival_failures:
        key = (row["repo_id"], row["instruction_path"], row["reference_type"], row["reference"])
        events = trajectories.get(key, [])
        meta = _first_event_meta(events)
        fail_ev = _failure_event(events, row["time_end"])
        ref_key = f"{row['reference_type']}:{row['reference']}"
        prepared.append(
            {
                "survival_row": row,
                "events": events,
                "first_commit": meta["first_commit"],
                "first_change_type": meta["first_change_type"],
                "failure_commit": (fail_ev or {}).get("commit", ""),
                "failure_transition": (fail_ev or {}).get("transition", "VERIFIED->MISSING"),
                "returned_after_missing": _returned_after_missing(events, row["time_end"]),
                "basename_collision_verified": _basename_collision_verified(
                    events=events,
                    reference=row["reference"],
                    failure_time=row["time_end"],
                ),
                "repeated_repo_count": ref_counts.get(ref_key, 1),
                "repeated_file_count": file_counts.get(row["instruction_path"], 1),
                "repo_url": repo_urls.get(row["repo_id"], ""),
            }
        )
    return prepared


def classify_failure_context(
    *,
    reference_type: str,
    reference: str,
    instruction_path: str,
    n_observations: int,
    first_change_type: str,
    repeated_repo_count: int,
    repeated_file_count: int,
    snippet: str,
    ever_repaired: bool,
    returned_after_missing: bool,
    basename_collision_verified: bool,
) -> tuple[str, str, tuple[str, ...], str, HeuristicVerdict]:
    born = classify_heuristic(
        reference_type=reference_type,
        reference=reference,
        instruction_path=instruction_path,
        n_observations=n_observations,
        first_change_type=first_change_type,
        repeated_repo_count=repeated_repo_count,
        repeated_file_count=repeated_file_count,
        snippet=snippet,
    )
    category, confidence, rules, rationale = _post_verification_heuristic(
        reference_type=reference_type,
        reference=reference,
        instruction_path=instruction_path,
        n_observations=n_observations,
        first_change_type=first_change_type,
        repeated_repo_count=repeated_repo_count,
        repeated_file_count=repeated_file_count,
        snippet=snippet,
        ever_repaired=ever_repaired,
        returned_after_missing=returned_after_missing,
        basename_collision=basename_collision_verified,
    )
    return category, confidence, rules, rationale, born


def record_to_row(record: FailureAuditRecord) -> dict:
    return asdict(record)
