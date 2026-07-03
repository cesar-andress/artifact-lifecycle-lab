"""Deterministic stub agent for RQ5 infrastructure tests."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path

from artifact_lab.experiments.truth_decay.rq5_experiment.agents.base import trace_from_events
from artifact_lab.experiments.truth_decay.rq5_experiment.models import AgentRunResult, ExperimentCase, TraceEvent


class StubAgent:
    """Simulates agent behavior without external LLM calls."""

    agent_id = "stub_agent_v1"

    def __init__(self, *, fail_on_condition_b: bool = True) -> None:
        self.fail_on_condition_b = fail_on_condition_b

    def run(
        self,
        *,
        case: ExperimentCase,
        condition: str,
        workspace: Path,
        replicate_id: int,
    ) -> AgentRunResult:
        started = time.perf_counter()
        instruction = workspace / case.instruction_path
        events: list[TraceEvent] = []
        now = lambda: datetime.now(timezone.utc).isoformat()

        if condition == "C" or not instruction.exists():
            success = True
            tests_passing = True
            tool_failures = 0
            trace_flags = {
                "read_instruction": False,
                "followed_reference": False,
                "ignored_reference": True,
                "detected_inconsistency": False,
                "repaired_reference": False,
            }
        else:
            events.append(
                TraceEvent(
                    timestamp=now(),
                    event_type="read_instruction",
                    payload={"path": case.instruction_path},
                )
            )

            anchor_present = case.anchor_reference in instruction.read_text(encoding="utf-8", errors="replace")
            if anchor_present:
                events.append(
                    TraceEvent(
                        timestamp=now(),
                        event_type="follow_reference",
                        payload={"reference": case.anchor_reference},
                    )
                )

            if condition == "B" and self.fail_on_condition_b and anchor_present:
                events.append(
                    TraceEvent(
                        timestamp=now(),
                        event_type="tool_failure",
                        payload={"reference": case.anchor_reference, "reason": "missing_path"},
                    )
                )
                success = False
                tests_passing = False
                tool_failures = 1
            else:
                success = True
                tests_passing = True
                tool_failures = 0

            trace_flags = trace_from_events(events)
        elapsed = time.perf_counter() - started
        return AgentRunResult(
            agent_id=self.agent_id,
            condition=condition,
            case_id=case.case_id,
            replicate_id=replicate_id,
            success=success,
            tests_passing=tests_passing,
            compilation_success=True,
            execution_time_seconds=round(elapsed, 3),
            files_modified=0,
            tool_failures=tool_failures,
            iterations=1,
            commands_executed=1,
            repository_changes=0,
            read_instruction=trace_flags["read_instruction"],
            followed_reference=trace_flags["followed_reference"],
            ignored_reference=trace_flags["ignored_reference"],
            detected_inconsistency=trace_flags["detected_inconsistency"],
            repaired_reference=trace_flags["repaired_reference"],
            trace_events=events,
        )
