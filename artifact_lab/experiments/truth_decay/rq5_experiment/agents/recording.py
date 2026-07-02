"""Trace recording wrapper for RQ5 agents."""

from __future__ import annotations

import json
from pathlib import Path

from artifact_lab.experiments.truth_decay.rq5_experiment.agents.base import AgentRunner
from artifact_lab.experiments.truth_decay.rq5_experiment.models import AgentRunResult, ExperimentCase


class RecordingAgent:
    """Persist full interaction traces for any AgentRunner implementation."""

    def __init__(self, inner: AgentRunner, traces_dir: Path) -> None:
        self.inner = inner
        self.agent_id = inner.agent_id
        self.traces_dir = traces_dir
        self.traces_dir.mkdir(parents=True, exist_ok=True)

    def run(
        self,
        *,
        case: ExperimentCase,
        condition: str,
        workspace: Path,
        replicate_id: int,
    ) -> AgentRunResult:
        result = self.inner.run(
            case=case,
            condition=condition,
            workspace=workspace,
            replicate_id=replicate_id,
        )
        trace_path = self.traces_dir / (
            f"{case.case_id}_{condition}_{self.agent_id}_r{replicate_id}.jsonl"
        )
        with trace_path.open("w", encoding="utf-8") as handle:
            for event in result.trace_events:
                handle.write(
                    json.dumps(
                        {
                            "timestamp": event.timestamp,
                            "event_type": event.event_type,
                            "payload": event.payload,
                        },
                        sort_keys=True,
                    )
                    + "\n"
                )
        return result
