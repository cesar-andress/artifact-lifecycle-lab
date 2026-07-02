"""Abstract agent execution interface for RQ5."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from artifact_lab.experiments.truth_decay.rq5_experiment.models import AgentRunResult, ExperimentCase, TraceEvent


class AgentRunner(Protocol):
    """Vendor-neutral agent interface."""

    agent_id: str

    def run(
        self,
        *,
        case: ExperimentCase,
        condition: str,
        workspace: Path,
        replicate_id: int,
    ) -> AgentRunResult:
        """Execute one experimental run and return structured outcome + trace."""


def trace_from_events(events: list[TraceEvent]) -> dict[str, bool]:
    types = {event.event_type for event in events}
    return {
        "read_instruction": "read_instruction" in types,
        "followed_reference": "follow_reference" in types or "edit_file" in types,
        "ignored_reference": "ignore_reference" in types,
        "detected_inconsistency": "detect_inconsistency" in types,
        "repaired_reference": "repair_reference" in types or "edit_instruction" in types,
    }
