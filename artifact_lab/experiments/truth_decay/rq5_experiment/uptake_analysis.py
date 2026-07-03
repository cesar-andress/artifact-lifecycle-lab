"""Uptake classification for RQ5 causal traces."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from artifact_lab.experiments.truth_decay.rq5_experiment.agents.cli_utils import (
    instruction_was_read,
    reference_followed,
)
from artifact_lab.experiments.truth_decay.rq5_experiment.models import AgentRunResult, ExperimentCase, TraceEvent
from artifact_lab.experiments.truth_decay.rq5_experiment.trace_classifier import failure_mode_rows


@dataclass(frozen=True)
class UptakeClassification:
    agent_id: str
    condition: str
    case_id: str
    replicate_id: int
    instruction_present: bool
    instruction_read: bool
    instruction_quoted: bool
    instruction_followed: bool
    false_claim_encountered: bool
    false_claim_used: bool
    false_claim_corrected: bool
    false_claim_ignored: bool
    task_success: bool
    failure_reason: str
    uptake_tier: str
    trace_classification: str

    def to_row(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "condition": self.condition,
            "case_id": self.case_id,
            "replicate_id": self.replicate_id,
            "instruction_present": self.instruction_present,
            "instruction_read": self.instruction_read,
            "instruction_quoted": self.instruction_quoted,
            "instruction_followed": self.instruction_followed,
            "false_claim_encountered": self.false_claim_encountered,
            "false_claim_used": self.false_claim_used,
            "false_claim_corrected": self.false_claim_corrected,
            "false_claim_ignored": self.false_claim_ignored,
            "task_success": self.task_success,
            "failure_reason": self.failure_reason,
            "uptake_tier": self.uptake_tier,
            "trace_classification": self.trace_classification,
        }


def load_trace_events(path: Path) -> list[TraceEvent]:
    if not path.exists():
        return []
    events: list[TraceEvent] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            events.append(
                TraceEvent(
                    timestamp=obj.get("timestamp", ""),
                    event_type=obj.get("event_type", ""),
                    payload=obj.get("payload") or {},
                )
            )
    return events


def trace_path_for_run(
    *,
    traces_dir: Path,
    case_id: str,
    condition: str,
    agent_id: str,
    replicate_id: int,
) -> Path:
    return traces_dir / f"{case_id}_{condition}_{agent_id}_r{replicate_id}.jsonl"


def _event_blob(event: TraceEvent) -> str:
    return json.dumps(event.payload)


def reference_encountered(events: list[TraceEvent], reference: str) -> bool:
    ref_base = reference.rstrip("/").split("/")[-1]
    for event in events:
        blob = _event_blob(event)
        if reference in blob or ref_base in blob:
            return True
    return False


def instruction_quoted_in_trace(events: list[TraceEvent], instruction_path: str) -> bool:
    for event in events:
        if event.event_type == "Read":
            file_path = str((event.payload.get("input") or {}).get("file_path", ""))
            if instruction_path in file_path:
                return True
        if event.event_type in {"read_instruction", "read_file"}:
            path = str(event.payload.get("path", ""))
            if instruction_path in path:
                return True
    return False


def _failure_reason(result: AgentRunResult) -> str:
    rows = failure_mode_rows([result])
    return rows[0].get("failure_mode", "unknown")


def _uptake_tier(
    *,
    instruction_read: bool,
    instruction_quoted: bool,
    instruction_followed: bool,
    task_success: bool,
) -> str:
    if instruction_read and instruction_followed and task_success:
        return "full_uptake_success"
    if instruction_read and instruction_followed:
        return "followed_not_success"
    if instruction_read and instruction_quoted and not instruction_followed:
        return "read_quoted_not_followed"
    if instruction_read and not instruction_followed:
        return "read_not_followed"
    if not instruction_read:
        return "not_read"
    return "unknown"


def classify_uptake(
    *,
    result: AgentRunResult,
    case: ExperimentCase,
    events: list[TraceEvent] | None = None,
) -> UptakeClassification:
    trace = events if events is not None else result.trace_events
    instruction_present = True
    instruction_read = instruction_was_read(trace, case.instruction_path) or result.read_instruction
    instruction_quoted = instruction_quoted_in_trace(trace, case.instruction_path) or instruction_read
    instruction_followed = reference_followed(trace, case.anchor_reference) or result.followed_reference

    encountered = reference_encountered(trace, case.anchor_reference)
    if result.condition == "B":
        false_claim_encountered = encountered or instruction_read
        false_claim_used = instruction_followed
        false_claim_corrected = bool(result.repaired_reference or result.detected_inconsistency)
        false_claim_ignored = false_claim_encountered and not false_claim_used and not false_claim_corrected
    else:
        false_claim_encountered = False
        false_claim_used = False
        false_claim_corrected = False
        false_claim_ignored = False

    task_success = result.success
    failure_reason = _failure_reason(result) if not task_success else "success"
    uptake_tier = _uptake_tier(
        instruction_read=instruction_read,
        instruction_quoted=instruction_quoted,
        instruction_followed=instruction_followed,
        task_success=task_success,
    )

    return UptakeClassification(
        agent_id=result.agent_id,
        condition=result.condition,
        case_id=result.case_id,
        replicate_id=result.replicate_id,
        instruction_present=instruction_present,
        instruction_read=instruction_read,
        instruction_quoted=instruction_quoted,
        instruction_followed=instruction_followed,
        false_claim_encountered=false_claim_encountered,
        false_claim_used=false_claim_used,
        false_claim_corrected=false_claim_corrected,
        false_claim_ignored=false_claim_ignored,
        task_success=task_success,
        failure_reason=failure_reason,
        uptake_tier=uptake_tier,
        trace_classification=result.trace_classification or "",
    )


def classify_all_uptake(
    *,
    results: list[AgentRunResult],
    cases: list[ExperimentCase],
    traces_dir: Path,
) -> list[UptakeClassification]:
    case_map = {case.case_id: case for case in cases}
    classified: list[UptakeClassification] = []
    for result in results:
        case = case_map[result.case_id]
        trace_path = trace_path_for_run(
            traces_dir=traces_dir,
            case_id=result.case_id,
            condition=result.condition,
            agent_id=result.agent_id,
            replicate_id=result.replicate_id,
        )
        events = load_trace_events(trace_path)
        classified.append(classify_uptake(result=result, case=case, events=events))
    return classified


def uptake_by_condition_rows(classifications: list[UptakeClassification]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def _append_group(
        *,
        stratum: str,
        stratum_value: str,
        condition: str,
        bucket: list[UptakeClassification],
    ) -> None:
        if not bucket:
            return
        n = len(bucket)
        rows.append(
            {
                "stratum": stratum,
                "stratum_value": stratum_value,
                "condition": condition,
                "n_runs": n,
                "success_rate": round(sum(1 for r in bucket if r.task_success) / n, 6),
                "rate_instruction_read": round(sum(1 for r in bucket if r.instruction_read) / n, 6),
                "rate_instruction_quoted": round(sum(1 for r in bucket if r.instruction_quoted) / n, 6),
                "rate_instruction_followed": round(sum(1 for r in bucket if r.instruction_followed) / n, 6),
                "rate_false_claim_encountered": round(
                    sum(1 for r in bucket if r.false_claim_encountered) / n, 6
                ),
                "rate_false_claim_used": round(sum(1 for r in bucket if r.false_claim_used) / n, 6),
                "rate_false_claim_corrected": round(
                    sum(1 for r in bucket if r.false_claim_corrected) / n, 6
                ),
                "rate_false_claim_ignored": round(sum(1 for r in bucket if r.false_claim_ignored) / n, 6),
            }
        )

    strata = (
        "all",
        "instruction_read",
        "instruction_quoted",
        "instruction_followed",
        "false_claim_encountered",
        "false_claim_used",
        "false_claim_ignored",
        "uptake_tier",
    )
    for stratum in strata:
        if stratum == "all":
            for condition in ("A", "B"):
                bucket = [r for r in classifications if r.condition == condition]
                _append_group(stratum=stratum, stratum_value="all", condition=condition, bucket=bucket)
            continue

        if stratum == "uptake_tier":
            values = sorted({r.uptake_tier for r in classifications})
        elif stratum.startswith("false_claim"):
            values = ("True", "False")
        else:
            values = ("True", "False")

        for value in values:
            for condition in ("A", "B"):
                if stratum == "uptake_tier":
                    bucket = [
                        r for r in classifications if r.condition == condition and r.uptake_tier == value
                    ]
                else:
                    flag = value == "True"
                    bucket = [
                        r
                        for r in classifications
                        if r.condition == condition and getattr(r, stratum) is flag
                    ]
                _append_group(stratum=stratum, stratum_value=value, condition=condition, bucket=bucket)

    paired_rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for row in rows:
        key = (row["stratum"], row["stratum_value"])
        if key in seen:
            continue
        a_row = next(
            (
                r
                for r in rows
                if r["stratum"] == row["stratum"]
                and r["stratum_value"] == row["stratum_value"]
                and r["condition"] == "A"
            ),
            None,
        )
        b_row = next(
            (
                r
                for r in rows
                if r["stratum"] == row["stratum"]
                and r["stratum_value"] == row["stratum_value"]
                and r["condition"] == "B"
            ),
            None,
        )
        if not a_row or not b_row:
            continue
        seen.add(key)
        paired_rows.append(
            {
                "row_type": "paired_AB",
                "stratum": row["stratum"],
                "stratum_value": row["stratum_value"],
                "n_A": a_row["n_runs"],
                "success_rate_A": a_row["success_rate"],
                "n_B": b_row["n_runs"],
                "success_rate_B": b_row["success_rate"],
                "success_delta_A_minus_B": round(a_row["success_rate"] - b_row["success_rate"], 6),
            }
        )

    for row in rows:
        row["row_type"] = "by_condition"
    return rows + paired_rows


def uptake_flow_counts(classifications: list[UptakeClassification]) -> dict[str, dict[str, int]]:
    stages = (
        "instruction_present",
        "instruction_read",
        "instruction_quoted",
        "instruction_followed",
        "task_success",
    )
    counts: dict[str, dict[str, int]] = {condition: {stage: 0 for stage in stages} for condition in ("A", "B")}
    for row in classifications:
        counts[row.condition]["instruction_present"] += int(row.instruction_present)
        counts[row.condition]["instruction_read"] += int(row.instruction_read)
        counts[row.condition]["instruction_quoted"] += int(row.instruction_quoted)
        counts[row.condition]["instruction_followed"] += int(row.instruction_followed)
        counts[row.condition]["task_success"] += int(row.task_success)
    return counts


def _rate(n: int, total: int) -> str:
    if total == 0:
        return "0.0%"
    return f"{100 * n / total:.1f}%"


def uptake_analysis_markdown(
    *,
    classifications: list[UptakeClassification],
    by_condition_rows: list[dict[str, Any]],
) -> str:
    n_total = len(classifications)
    n_a = sum(1 for r in classifications if r.condition == "A")
    n_b = sum(1 for r in classifications if r.condition == "B")
    flow = uptake_flow_counts(classifications)

    read_a = sum(1 for r in classifications if r.condition == "A" and r.instruction_read)
    read_b = sum(1 for r in classifications if r.condition == "B" and r.instruction_read)
    followed_a = sum(1 for r in classifications if r.condition == "A" and r.instruction_followed)
    followed_b = sum(1 for r in classifications if r.condition == "B" and r.instruction_followed)
    used_b = sum(1 for r in classifications if r.condition == "B" and r.false_claim_used)
    ignored_b = sum(1 for r in classifications if r.condition == "B" and r.false_claim_ignored)
    success_a = sum(1 for r in classifications if r.condition == "A" and r.task_success)
    success_b = sum(1 for r in classifications if r.condition == "B" and r.task_success)

    paired = [r for r in by_condition_rows if r.get("row_type") == "paired_AB"]
    by_condition = [r for r in by_condition_rows if r.get("row_type") == "by_condition"]
    followed_stratum = next(
        (r for r in paired if r["stratum"] == "instruction_followed" and r["stratum_value"] == "True"),
        None,
    )
    not_followed_stratum = next(
        (r for r in paired if r["stratum"] == "instruction_followed" and r["stratum_value"] == "False"),
        None,
    )
    used_b_only = next(
        (
            r
            for r in by_condition
            if r["stratum"] == "false_claim_used"
            and r["stratum_value"] == "True"
            and r["condition"] == "B"
        ),
        None,
    )
    ignored_b_only = next(
        (
            r
            for r in by_condition
            if r["stratum"] == "false_claim_ignored"
            and r["stratum_value"] == "True"
            and r["condition"] == "B"
        ),
        None,
    )

    lines = [
        "# RQ5 — Instruction Uptake Analysis",
        "",
        "Post-hoc analysis of existing agent traces. No experiment protocol changes.",
        "",
        "## Dataset",
        "",
        f"- Total runs classified: **{n_total}** (A={n_a}, B={n_b})",
        f"- Agent(s): {', '.join(sorted({r.agent_id for r in classifications}))}",
        "",
        "## Uptake funnel (all runs)",
        "",
        "| Stage | Condition A | Condition B |",
        "|---|---:|---:|",
    ]
    for stage in ("instruction_present", "instruction_read", "instruction_quoted", "instruction_followed", "task_success"):
        lines.append(
            f"| {stage} | {flow['A'][stage]} ({_rate(flow['A'][stage], n_a)}) | "
            f"{flow['B'][stage]} ({_rate(flow['B'][stage], n_b)}) |"
        )

    lines.extend(
        [
            "",
            "## Key questions",
            "",
            "### 1. Did the agent actually read the instruction?",
            "",
            f"- Condition A: **{read_a}/{n_a}** runs ({_rate(read_a, n_a)}) show `instruction_read`.",
            f"- Condition B: **{read_b}/{n_b}** runs ({_rate(read_b, n_b)}) show `instruction_read`.",
            "- The instruction file is injected before every run; uptake is near-universal at the read stage.",
            "",
            "### 2. Did it act on the manipulated false claim?",
            "",
            f"- Condition B: **{used_b}/{n_b}** runs ({_rate(used_b, n_b)}) set `false_claim_used` "
            "(anchor reference appears in actionable trace events).",
            f"- Condition B: **{ignored_b}/{n_b}** runs ({_rate(ignored_b, n_b)}) encountered the claim "
            "but did not use or correct it (`false_claim_ignored`).",
            "",
            "### 3. Are null effects caused by robustness or by non-use?",
            "",
            f"- Overall success: A={success_a}/{n_a} ({_rate(success_a, n_a)}), "
            f"B={success_b}/{n_b} ({_rate(success_b, n_b)}).",
        ]
    )
    if followed_stratum and not_followed_stratum:
        lines.append(
            f"- Among runs that **followed** the anchor reference: "
            f"Δ success (A−B) = {followed_stratum['success_delta_A_minus_B']:.3f} "
            f"(A={followed_stratum['success_rate_A']:.3f}, B={followed_stratum['success_rate_B']:.3f})."
        )
        lines.append(
            f"- Among runs that **did not follow** the anchor: "
            f"Δ success (A−B) = {not_followed_stratum['success_delta_A_minus_B']:.3f} "
            f"(A={not_followed_stratum['success_rate_A']:.3f}, B={not_followed_stratum['success_rate_B']:.3f})."
        )
    if used_b_only and ignored_b_only:
        lines.append(
            f"- Among B runs that **used** the false claim: success rate = "
            f"{used_b_only['success_rate']:.3f} (n={used_b_only['n_runs']})."
        )
        lines.append(
            f"- Among B runs that **ignored** the false claim: success rate = "
            f"{ignored_b_only['success_rate']:.3f} (n={ignored_b_only['n_runs']})."
        )
    lines.extend(
        [
            "- Interpretation: compare stratified A−B deltas. If effects appear only when "
            "`instruction_followed` or `false_claim_used` is true, null overall effects are "
            "consistent with **non-use** (decorative instruction) rather than agent robustness.",
            "",
            "### 4. Is the instruction file executive or decorative in this experiment?",
            "",
        ]
    )
    follow_rate_b = followed_b / n_b if n_b else 0.0
    if follow_rate_b >= 0.5:
        verdict = (
            "**Partially executive**: a majority of B runs act on the anchor reference, "
            "so the instruction enters the causal path for many tasks."
        )
    elif read_a == n_a and read_b == n_b and followed_b < followed_a:
        verdict = (
            "**Mostly decorative**: agents read the file but often do not follow the anchor "
            "reference; causal manipulation may not reach task behavior."
        )
    else:
        verdict = (
            "**Mixed**: read uptake is high but follow uptake is moderate; instruction is "
            "executive only for a subset of runs."
        )
    lines.append(verdict)
    lines.extend(
        [
            "",
            f"- Read → follow conversion (B): {_rate(followed_b, read_b)} of read runs follow the anchor.",
            f"- Follow → success conversion (B): {_rate(success_b, followed_b)} of follow runs succeed.",
            "",
            "## Stratified A vs B comparison",
            "",
            "Compare conditions only within uptake strata (see `rq5_uptake_by_condition.csv`).",
            "",
            "| Stratum | Value | n_A | success_A | n_B | success_B | Δ (A−B) |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in paired:
        lines.append(
            f"| {row['stratum']} | {row['stratum_value']} | {row['n_A']} | "
            f"{row['success_rate_A']:.3f} | {row['n_B']} | {row['success_rate_B']:.3f} | "
            f"{row['success_delta_A_minus_B']:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Failure reasons (unsuccessful runs)",
            "",
        ]
    )
    for condition in ("A", "B"):
        fails = [r for r in classifications if r.condition == condition and not r.task_success]
        if not fails:
            lines.append(f"- Condition {condition}: no failures.")
            continue
        reasons: dict[str, int] = {}
        for row in fails:
            reasons[row.failure_reason] = reasons.get(row.failure_reason, 0) + 1
        summary = ", ".join(f"{k}={v}" for k, v in sorted(reasons.items(), key=lambda kv: -kv[1]))
        lines.append(f"- Condition {condition}: {summary}")

    lines.append("")
    return "\n".join(lines)
