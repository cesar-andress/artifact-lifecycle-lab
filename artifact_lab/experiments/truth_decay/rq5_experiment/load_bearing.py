"""Load-bearing vs peripheral stratum flags for RQ5 candidate cases."""

from __future__ import annotations

import csv
from pathlib import Path

PERIPHERAL_ANCHOR_HINTS = (
    "readme",
    "contributing",
    "changelog",
    "license",
    "docs/",
    ".github/",
)

LOAD_BEARING_PATH_HINTS = (
    "agents.md",
    "claude.md",
    "copilot",
    "skill",
    ".cursor/rules",
    "config.toml",
    "package.json",
    "pyproject",
    "makefile",
)


def classify_load_bearing_stratum(
    *,
    anchor_reference: str,
    anchor_reference_type: str,
    instruction_path: str,
    task_availability: bool,
    task_availability_reason: str,
    issue_availability: bool,
    issue_availability_reason: str,
    n_missing_verifiable: int,
    n_verifiable: int,
    instruction_text: str = "",
    trace_follow_rate_b: float | None = None,
    trace_read_rate_a: float | None = None,
) -> tuple[str, bool, str]:
    """Return (stratum, likely_load_bearing, reason)."""
    anchor_lower = anchor_reference.lower()
    path_lower = instruction_path.lower()
    text_lower = instruction_text.lower()

    missing_ratio = n_missing_verifiable / n_verifiable if n_verifiable else 0.0
    anchor_in_text = anchor_lower in text_lower or anchor_reference in instruction_text
    path_is_agent_surface = any(h in path_lower for h in LOAD_BEARING_PATH_HINTS)
    anchor_is_peripheral = any(h in anchor_lower for h in PERIPHERAL_ANCHOR_HINTS)

    score = 0
    reasons: list[str] = []

    if task_availability and "verified_reference" in task_availability_reason:
        score += 2
        reasons.append("task_requires_verified_reference_anchors")
    if issue_availability:
        score += 2
        reasons.append("issue_cue_present")
    if anchor_in_text:
        score += 2
        reasons.append("anchor_in_instruction_text")
    if path_is_agent_surface:
        score += 1
        reasons.append("agent_instruction_surface")
    if anchor_reference_type in {"path", "command"} and not anchor_is_peripheral:
        score += 1
        reasons.append("verifiable_non_peripheral_anchor")
    if missing_ratio >= 0.5:
        score += 1
        reasons.append("high_missing_ratio")
    if trace_follow_rate_b is not None and trace_follow_rate_b >= 0.5:
        score += 1
        reasons.append("agents_follow_false_reference_in_B")
    if trace_read_rate_a is not None and trace_read_rate_a >= 0.5:
        score += 1
        reasons.append("agents_read_instruction_in_A")

    if anchor_is_peripheral and not anchor_in_text:
        score -= 2
        reasons.append("peripheral_anchor_hint")

    if score >= 4:
        return "load_bearing", True, ";".join(reasons)
    if score <= 1:
        return "peripheral", False, ";".join(reasons) or "low_task_coupling"
    return "unknown", score >= 3, ";".join(reasons) or "ambiguous_coupling"


def trace_rates_by_case(results_csv: Path) -> dict[str, dict[str, float]]:
    """Aggregate follow/read rates from completed RQ5 runs."""
    if not results_csv.exists():
        return {}
    grouped: dict[str, dict[str, list[bool]]] = {}
    with results_csv.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            case_id = row["case_id"]
            grouped.setdefault(case_id, {"read_a": [], "follow_b": []})
            if row["condition"] == "A":
                grouped[case_id]["read_a"].append(row.get("read_instruction") in ("True", "true", "1"))
            if row["condition"] == "B":
                grouped[case_id]["follow_b"].append(row.get("followed_reference") in ("True", "true", "1"))

    rates: dict[str, dict[str, float]] = {}
    for case_id, buckets in grouped.items():
        rates[case_id] = {}
        if buckets["read_a"]:
            rates[case_id]["trace_read_rate_a"] = sum(buckets["read_a"]) / len(buckets["read_a"])
        if buckets["follow_b"]:
            rates[case_id]["trace_follow_rate_b"] = sum(buckets["follow_b"]) / len(buckets["follow_b"])
    return rates
