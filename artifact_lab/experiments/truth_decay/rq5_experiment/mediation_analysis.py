"""Mediation audit for RQ5 null causal effects."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from artifact_lab.experiments.truth_decay.rq5_experiment.agents.cli_utils import (
    instruction_was_read,
    reference_followed,
)
from artifact_lab.experiments.truth_decay.rq5_experiment.models import AgentRunResult, ExperimentCase, TraceEvent
from artifact_lab.experiments.truth_decay.rq5_experiment.trace_classifier import failure_mode_rows
from artifact_lab.experiments.truth_decay.rq5_experiment.uptake_analysis import (
    instruction_quoted_in_trace,
    load_trace_events,
    reference_encountered,
    trace_path_for_run,
)

CAUSAL_ROLES_B = (
    "no_uptake",
    "uptake_but_not_load_bearing",
    "obstacle_recovered",
    "obstacle_unrecovered",
    "false_claim_caused_failure",
    "false_claim_irrelevant_to_failure",
    "ambiguous",
)

CAUSAL_ROLES_A = (
    "no_uptake",
    "uptake_but_not_load_bearing",
    "reference_used_and_succeeded",
    "reference_used_and_failed",
    "reference_ignored_after_reading",
    "ambiguous",
)

_OBSTACLE_PATTERNS = (
    r"does not exist",
    r"do not exist",
    r"not exist",
    r"no such file",
    r"no existe",
    r"cannot access",
    r"can't access",
    r"file has not been read",
    r"not found",
    r"absent:",
)


@dataclass(frozen=True)
class MediationClassification:
    agent_id: str
    condition: str
    case_id: str
    replicate_id: int
    anchor_reference: str
    task_success: bool
    failure_reason: str
    trace_classification: str
    false_claim_present_in_instruction: bool
    false_claim_read: bool
    false_claim_quoted_or_referenced: bool
    false_claim_used_in_tool_call: bool
    false_claim_encountered_as_obstacle: bool
    false_claim_corrected_by_agent: bool
    false_claim_ignored_after_reading: bool
    task_failed_before_false_claim_mattered: bool
    task_failed_because_of_false_claim: bool
    task_succeeded_despite_false_claim: bool
    causal_role: str

    def to_row(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "condition": self.condition,
            "case_id": self.case_id,
            "replicate_id": self.replicate_id,
            "anchor_reference": self.anchor_reference,
            "task_success": self.task_success,
            "failure_reason": self.failure_reason,
            "trace_classification": self.trace_classification,
            "false_claim_present_in_instruction": self.false_claim_present_in_instruction,
            "false_claim_read": self.false_claim_read,
            "false_claim_quoted_or_referenced": self.false_claim_quoted_or_referenced,
            "false_claim_used_in_tool_call": self.false_claim_used_in_tool_call,
            "false_claim_encountered_as_obstacle": self.false_claim_encountered_as_obstacle,
            "false_claim_corrected_by_agent": self.false_claim_corrected_by_agent,
            "false_claim_ignored_after_reading": self.false_claim_ignored_after_reading,
            "task_failed_before_false_claim_mattered": self.task_failed_before_false_claim_mattered,
            "task_failed_because_of_false_claim": self.task_failed_because_of_false_claim,
            "task_succeeded_despite_false_claim": self.task_succeeded_despite_false_claim,
            "causal_role": self.causal_role,
        }


def _event_blob(event: TraceEvent) -> str:
    return json.dumps(event.payload)


def _reference_tokens(reference: str) -> tuple[str, str]:
    ref = reference.rstrip("/")
    return ref, ref.split("/")[-1]


def reference_used_in_tool_call(events: list[TraceEvent], reference: str) -> bool:
    ref_full, ref_base = _reference_tokens(reference)
    actionable = {"Bash", "Edit", "Write", "Read", "follow_reference", "shell_command"}
    for event in events:
        if event.event_type not in actionable:
            continue
        blob = _event_blob(event)
        if ref_full in blob or ref_base in blob:
            return True
    return reference_followed(events, reference)


def reference_obstacle_encountered(events: list[TraceEvent], reference: str) -> bool:
    ref_full, ref_base = _reference_tokens(reference)
    used_before = False
    obstacle_re = re.compile("|".join(_OBSTACLE_PATTERNS), re.IGNORECASE)
    for event in events:
        if event.event_type in {"Bash", "Edit", "Write", "Read", "follow_reference", "shell_command"}:
            blob = _event_blob(event)
            if ref_full in blob or ref_base in blob:
                used_before = True
        if event.event_type == "tool_failure" and used_before:
            content = str(event.payload.get("content", ""))
            if obstacle_re.search(content) or ref_full in content or ref_base in content:
                return True
    return False


def reference_corrected_by_agent(
    *,
    result: AgentRunResult,
    events: list[TraceEvent],
    reference: str,
    obstacle: bool,
) -> bool:
    if result.repaired_reference or result.detected_inconsistency:
        return True
    if result.trace_classification == "manual_correction_by_agent":
        return True
    if not obstacle:
        return False
    ref_full, ref_base = _reference_tokens(reference)
    saw_obstacle = False
    for event in events:
        if event.event_type == "tool_failure":
            content = str(event.payload.get("content", ""))
            if re.search("|".join(_OBSTACLE_PATTERNS), content, re.IGNORECASE):
                saw_obstacle = True
        if saw_obstacle and event.event_type in {"Write", "Edit"}:
            blob = _event_blob(event)
            if ref_full not in blob and ref_base not in blob:
                return True
    return False


def _failure_reason(result: AgentRunResult) -> str:
    rows = failure_mode_rows([result])
    return rows[0].get("failure_mode", "unknown")


def _causal_role_b(
    *,
    read: bool,
    quoted: bool,
    used: bool,
    obstacle: bool,
    corrected: bool,
    ignored_after_reading: bool,
    success: bool,
    trace_classification: str,
) -> str:
    if not read:
        return "no_uptake"
    if not quoted and not used:
        return "no_uptake"
    if not used:
        return "uptake_but_not_load_bearing"
    if success:
        if obstacle and corrected:
            return "obstacle_recovered"
        if obstacle:
            return "ambiguous"
        return "uptake_but_not_load_bearing"
    if obstacle and corrected:
        return "obstacle_recovered"
    if obstacle:
        if trace_classification == "hallucinated_path":
            return "false_claim_caused_failure"
        return "obstacle_unrecovered"
    if ignored_after_reading:
        return "false_claim_irrelevant_to_failure"
    return "false_claim_irrelevant_to_failure"


def _causal_role_a(
    *,
    read: bool,
    quoted: bool,
    used: bool,
    ignored_after_reading: bool,
    success: bool,
) -> str:
    if not read:
        return "no_uptake"
    if not quoted and not used:
        return "no_uptake"
    if ignored_after_reading:
        return "reference_ignored_after_reading"
    if not used:
        return "uptake_but_not_load_bearing"
    if success:
        return "reference_used_and_succeeded"
    return "reference_used_and_failed"


def classify_mediation_b(
    *,
    result: AgentRunResult,
    case: ExperimentCase,
    events: list[TraceEvent],
) -> MediationClassification:
    anchor = case.anchor_reference
    read = instruction_was_read(events, case.instruction_path) or result.read_instruction
    quoted = (
        instruction_quoted_in_trace(events, case.instruction_path)
        or reference_encountered(events, anchor)
    )
    used = reference_used_in_tool_call(events, anchor) or result.followed_reference
    obstacle = reference_obstacle_encountered(events, anchor)
    corrected = reference_corrected_by_agent(
        result=result,
        events=events,
        reference=anchor,
        obstacle=obstacle,
    )
    ignored_after_reading = read and not used and not corrected
    success = result.success
    failed_before = not success and not used
    failed_because = not success and used and obstacle and not corrected
    succeeded_despite = success and used

    role = _causal_role_b(
        read=read,
        quoted=quoted,
        used=used,
        obstacle=obstacle,
        corrected=corrected,
        ignored_after_reading=ignored_after_reading,
        success=success,
        trace_classification=result.trace_classification or "",
    )

    return MediationClassification(
        agent_id=result.agent_id,
        condition=result.condition,
        case_id=result.case_id,
        replicate_id=result.replicate_id,
        anchor_reference=anchor,
        task_success=success,
        failure_reason=_failure_reason(result) if not success else "success",
        trace_classification=result.trace_classification or "",
        false_claim_present_in_instruction=True,
        false_claim_read=read,
        false_claim_quoted_or_referenced=quoted,
        false_claim_used_in_tool_call=used,
        false_claim_encountered_as_obstacle=obstacle,
        false_claim_corrected_by_agent=corrected,
        false_claim_ignored_after_reading=ignored_after_reading,
        task_failed_before_false_claim_mattered=failed_before,
        task_failed_because_of_false_claim=failed_because,
        task_succeeded_despite_false_claim=succeeded_despite,
        causal_role=role,
    )


def classify_mediation_a(
    *,
    result: AgentRunResult,
    case: ExperimentCase,
    events: list[TraceEvent],
) -> MediationClassification:
    anchor = case.anchor_reference
    read = instruction_was_read(events, case.instruction_path) or result.read_instruction
    quoted = (
        instruction_quoted_in_trace(events, case.instruction_path)
        or reference_encountered(events, anchor)
    )
    used = reference_used_in_tool_call(events, anchor) or result.followed_reference
    obstacle = reference_obstacle_encountered(events, anchor)
    corrected = reference_corrected_by_agent(
        result=result,
        events=events,
        reference=anchor,
        obstacle=obstacle,
    )
    ignored_after_reading = read and not used and not corrected
    success = result.success

    role = _causal_role_a(
        read=read,
        quoted=quoted,
        used=used,
        ignored_after_reading=ignored_after_reading,
        success=success,
    )

    return MediationClassification(
        agent_id=result.agent_id,
        condition=result.condition,
        case_id=result.case_id,
        replicate_id=result.replicate_id,
        anchor_reference=anchor,
        task_success=success,
        failure_reason=_failure_reason(result) if not success else "success",
        trace_classification=result.trace_classification or "",
        false_claim_present_in_instruction=False,
        false_claim_read=read,
        false_claim_quoted_or_referenced=quoted,
        false_claim_used_in_tool_call=used,
        false_claim_encountered_as_obstacle=obstacle,
        false_claim_corrected_by_agent=corrected,
        false_claim_ignored_after_reading=ignored_after_reading,
        task_failed_before_false_claim_mattered=not success and not used,
        task_failed_because_of_false_claim=False,
        task_succeeded_despite_false_claim=success and used,
        causal_role=role,
    )


def classify_mediation(
    *,
    result: AgentRunResult,
    case: ExperimentCase,
    events: list[TraceEvent] | None = None,
) -> MediationClassification:
    trace = events if events is not None else result.trace_events
    if result.condition == "B":
        return classify_mediation_b(result=result, case=case, events=trace)
    return classify_mediation_a(result=result, case=case, events=trace)


def classify_all_mediation(
    *,
    results: list[AgentRunResult],
    cases: list[ExperimentCase],
    traces_dir: Path,
) -> list[MediationClassification]:
    case_map = {case.case_id: case for case in cases}
    rows: list[MediationClassification] = []
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
        rows.append(classify_mediation(result=result, case=case, events=events))
    return rows


def mediation_by_condition_rows(classifications: list[MediationClassification]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def _metrics(bucket: list[MediationClassification]) -> dict[str, Any]:
        n = len(bucket) or 1
        return {
            "n_runs": len(bucket),
            "success_rate": round(sum(1 for r in bucket if r.task_success) / n, 6),
            "rate_read": round(sum(1 for r in bucket if r.false_claim_read) / n, 6),
            "rate_quoted_or_referenced": round(
                sum(1 for r in bucket if r.false_claim_quoted_or_referenced) / n, 6
            ),
            "rate_used_in_tool_call": round(
                sum(1 for r in bucket if r.false_claim_used_in_tool_call) / n, 6
            ),
            "rate_obstacle": round(
                sum(1 for r in bucket if r.false_claim_encountered_as_obstacle) / n, 6
            ),
            "rate_corrected": round(
                sum(1 for r in bucket if r.false_claim_corrected_by_agent) / n, 6
            ),
            "rate_ignored_after_reading": round(
                sum(1 for r in bucket if r.false_claim_ignored_after_reading) / n, 6
            ),
            "rate_failed_before_mattered": round(
                sum(1 for r in bucket if r.task_failed_before_false_claim_mattered) / n, 6
            ),
            "rate_failed_because_of_claim": round(
                sum(1 for r in bucket if r.task_failed_because_of_false_claim) / n, 6
            ),
            "rate_succeeded_despite_claim": round(
                sum(1 for r in bucket if r.task_succeeded_despite_false_claim) / n, 6
            ),
        }

    for condition in ("A", "B"):
        bucket = [r for r in classifications if r.condition == condition]
        row = {"row_type": "condition_summary", "condition": condition, **_metrics(bucket)}
        roles = sorted({r.causal_role for r in bucket})
        for role in roles:
            role_bucket = [r for r in bucket if r.causal_role == role]
            rows.append(
                {
                    "row_type": "causal_role",
                    "condition": condition,
                    "causal_role": role,
                    "count": len(role_bucket),
                    "frequency": round(len(role_bucket) / (len(bucket) or 1), 6),
                    "success_rate": round(
                        sum(1 for r in role_bucket if r.task_success) / (len(role_bucket) or 1), 6
                    ),
                }
            )
        rows.append(row)

    b_rows = [r for r in classifications if r.condition == "B"]
    a_rows = [r for r in classifications if r.condition == "A"]
    rows.append(
        {
            "row_type": "paired_comparison",
            "metric": "success_rate",
            "value_A": round(sum(1 for r in a_rows if r.task_success) / (len(a_rows) or 1), 6),
            "value_B": round(sum(1 for r in b_rows if r.task_success) / (len(b_rows) or 1), 6),
            "delta_A_minus_B": round(
                (sum(1 for r in a_rows if r.task_success) / (len(a_rows) or 1))
                - (sum(1 for r in b_rows if r.task_success) / (len(b_rows) or 1)),
                6,
            ),
        }
    )
    for metric in (
        "rate_used_in_tool_call",
        "rate_obstacle",
        "rate_failed_because_of_claim",
        "rate_succeeded_despite_claim",
    ):
        key_map = {
            "rate_used_in_tool_call": "false_claim_used_in_tool_call",
            "rate_obstacle": "false_claim_encountered_as_obstacle",
            "rate_failed_because_of_claim": "task_failed_because_of_false_claim",
            "rate_succeeded_despite_claim": "task_succeeded_despite_false_claim",
        }
        attr = key_map[metric]
        rows.append(
            {
                "row_type": "paired_comparison",
                "metric": metric,
                "value_A": round(sum(1 for r in a_rows if getattr(r, attr)) / (len(a_rows) or 1), 6),
                "value_B": round(sum(1 for r in b_rows if getattr(r, attr)) / (len(b_rows) or 1), 6),
                "delta_A_minus_B": round(
                    (sum(1 for r in a_rows if getattr(r, attr)) / (len(a_rows) or 1))
                    - (sum(1 for r in b_rows if getattr(r, attr)) / (len(b_rows) or 1)),
                    6,
                ),
            }
        )
    return rows


def mediation_flow_counts(classifications: list[MediationClassification]) -> dict[str, int]:
    b_rows = [r for r in classifications if r.condition == "B"]
    return {
        "present": sum(1 for r in b_rows if r.false_claim_present_in_instruction),
        "read": sum(1 for r in b_rows if r.false_claim_read),
        "quoted": sum(1 for r in b_rows if r.false_claim_quoted_or_referenced),
        "used": sum(1 for r in b_rows if r.false_claim_used_in_tool_call),
        "obstacle": sum(1 for r in b_rows if r.false_claim_encountered_as_obstacle),
        "corrected": sum(1 for r in b_rows if r.false_claim_corrected_by_agent),
        "failed_because": sum(1 for r in b_rows if r.task_failed_because_of_false_claim),
        "succeeded_despite": sum(1 for r in b_rows if r.task_succeeded_despite_false_claim),
    }


def _pct(n: int, total: int) -> str:
    if total == 0:
        return "0.0%"
    return f"{100 * n / total:.1f}%"


def mediation_summary_markdown(
    *,
    classifications: list[MediationClassification],
    by_condition_rows: list[dict[str, Any]],
) -> str:
    all_rows = classifications
    b_rows = [r for r in classifications if r.condition == "B"]
    a_rows = [r for r in classifications if r.condition == "A"]
    n_b = len(b_rows)
    n_a = len(a_rows)
    flow = mediation_flow_counts(classifications)

    role_counts_b = {role: sum(1 for r in b_rows if r.causal_role == role) for role in CAUSAL_ROLES_B}
    role_counts_a = {role: sum(1 for r in a_rows if r.causal_role == role) for role in CAUSAL_ROLES_A}

    enters_causal_path = sum(
        1 for r in b_rows if r.false_claim_used_in_tool_call or r.false_claim_encountered_as_obstacle
    )
    load_bearing = sum(
        1
        for r in b_rows
        if r.causal_role
        in {"false_claim_caused_failure", "obstacle_unrecovered", "obstacle_recovered"}
    )
    recovered = sum(1 for r in b_rows if r.causal_role == "obstacle_recovered")
    caused_failure = sum(1 for r in b_rows if r.causal_role == "false_claim_caused_failure")
    irrelevant = sum(1 for r in b_rows if r.causal_role == "false_claim_irrelevant_to_failure")
    not_load_bearing = sum(1 for r in b_rows if r.causal_role == "uptake_but_not_load_bearing")

    success_a = sum(1 for r in a_rows if r.task_success)
    success_b = sum(1 for r in b_rows if r.task_success)

    paired = [r for r in by_condition_rows if r.get("row_type") == "paired_comparison" and r.get("metric") == "success_rate"]
    success_delta = paired[0]["delta_A_minus_B"] if paired else 0.0

    lines = [
        "# RQ5 — Null-Result Mediation Audit",
        "",
        "Post-hoc trace audit only. Does not modify the experiment, agents, or datasets.",
        "",
        "## Scope",
        "",
        f"- Runs audited: **{len(all_rows)}** (A={n_a}, B={n_b})",
        f"- Overall success: A={success_a}/{n_a} ({_pct(success_a, n_a)}), "
        f"B={success_b}/{n_b} ({_pct(success_b, n_b)}), Δ(A−B)={success_delta:.3f}",
        "",
        "## B-condition mediation funnel",
        "",
        "| Stage | Count | Share of B runs |",
        "|---|---:|---:|",
    ]
    for stage, key in (
        ("false_claim_present_in_instruction", "present"),
        ("false_claim_read", "read"),
        ("false_claim_quoted_or_referenced", "quoted"),
        ("false_claim_used_in_tool_call", "used"),
        ("false_claim_encountered_as_obstacle", "obstacle"),
        ("false_claim_corrected_by_agent", "corrected"),
        ("task_failed_because_of_false_claim", "failed_because"),
        ("task_succeeded_despite_false_claim", "succeeded_despite"),
    ):
        lines.append(f"| {stage} | {flow[key]} | {_pct(flow[key], n_b)} |")

    lines.extend(["", "## Causal roles (B)", "", "| causal_role | count | frequency | success_rate |", "|---|---:|---:|---:|"])
    for row in by_condition_rows:
        if row.get("row_type") == "causal_role" and row.get("condition") == "B":
            lines.append(
                f"| {row['causal_role']} | {row['count']} | {row['frequency']:.3f} | {row['success_rate']:.3f} |"
            )

    lines.extend(["", "## Comparable reference usage (A)", "", "| causal_role | count | frequency | success_rate |", "|---|---:|---:|---:|"])
    for role in CAUSAL_ROLES_A:
        count = role_counts_a.get(role, 0)
        if count == 0:
            continue
        bucket = [r for r in a_rows if r.causal_role == role]
        rate = sum(1 for r in bucket if r.task_success) / len(bucket)
        lines.append(f"| {role} | {count} | {count / (n_a or 1):.3f} | {rate:.3f} |")

    lines.extend(
        [
            "",
            "## Audit questions",
            "",
            "### 1. How often does the false claim enter the causal path?",
            "",
            f"- Used in a tool call or followed as an actionable reference: **{flow['used']}/{n_b}** ({_pct(flow['used'], n_b)}).",
            f"- Broader path entry (used or obstacle after use): **{enters_causal_path}/{n_b}** ({_pct(enters_causal_path, n_b)}).",
            "",
            "### 2. How often is it load-bearing for the task?",
            "",
            f"- Runs classified as load-bearing (obstacle/recovery/failure roles): **{load_bearing}/{n_b}** ({_pct(load_bearing, n_b)}).",
            f"- Not load-bearing (read/referenced but not used, or failure unrelated): **{not_load_bearing + irrelevant}/{n_b}** "
            f"({_pct(not_load_bearing + irrelevant, n_b)}).",
            "",
            "### 3. How often does the agent recover from it?",
            "",
            f"- `obstacle_recovered`: **{recovered}/{n_b}** ({_pct(recovered, n_b)}).",
            f"- `task_succeeded_despite_false_claim`: **{flow['succeeded_despite']}/{n_b}** ({_pct(flow['succeeded_despite'], n_b)}).",
            "",
            "### 4. How often does it directly cause failure?",
            "",
            f"- `false_claim_caused_failure`: **{caused_failure}/{n_b}** ({_pct(caused_failure, n_b)}).",
            f"- `task_failed_because_of_false_claim` (heuristic): **{flow['failed_because']}/{n_b}** ({_pct(flow['failed_because'], n_b)}).",
            f"- `obstacle_unrecovered`: **{role_counts_b.get('obstacle_unrecovered', 0)}/{n_b}** "
            f"({_pct(role_counts_b.get('obstacle_unrecovered', 0), n_b)}).",
            "",
            "### 5. Does the null success effect reflect robustness or irrelevance?",
            "",
        ]
    )

    if abs(success_delta) < 0.05 and flow["used"] > n_b * 0.5:
        verdict = (
            "**Primarily irrelevance / low load-bearingness, not robustness.** "
            "Most B runs do act on the false claim, yet A and B success rates remain similar. "
            "Failures are dominated by cases where the false claim is used but not the "
            "identified proximal cause (`false_claim_irrelevant_to_failure`, `uptake_but_not_load_bearing`), "
            "or by shared task difficulty when following the anchor."
        )
    elif flow["used"] < n_b * 0.3:
        verdict = (
            "**Primarily non-use.** The false claim rarely enters tool-level behavior; "
            "the null effect is consistent with the manipulation not reaching task execution."
        )
    else:
        verdict = (
            "**Mixed / inconclusive.** Uptake is substantial but the null A−B success gap is small; "
            "trace evidence alone cannot separate robustness from irrelevance without stronger "
            "counterfactual labeling."
        )

    lines.append(verdict)
    lines.extend(
        [
            "",
            "Heuristic limits: obstacle and correction detection rely on trace substrings and "
            "event order; `ambiguous` runs should be interpreted cautiously.",
            "",
            f"- B `ambiguous`: {role_counts_b.get('ambiguous', 0)}",
            f"- B `no_uptake`: {role_counts_b.get('no_uptake', 0)}",
            "",
        ]
    )
    return "\n".join(lines)
