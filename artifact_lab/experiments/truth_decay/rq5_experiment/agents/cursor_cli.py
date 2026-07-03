"""Cursor CLI adapter — headless agent mode unavailable."""

from __future__ import annotations

import time
from pathlib import Path

from artifact_lab.experiments.truth_decay.rq5_experiment.models import AgentRunResult, ExperimentCase


class CursorCLIAgent:
    """Cursor desktop CLI does not expose a headless coding agent in this environment."""

    agent_id = "cursor_cli"

    @staticmethod
    def is_available() -> bool:
        return False

    def run(
        self,
        *,
        case: ExperimentCase,
        condition: str,
        workspace: Path,
        replicate_id: int,
    ) -> AgentRunResult:
        return AgentRunResult(
            agent_id=self.agent_id,
            condition=condition,
            case_id=case.case_id,
            replicate_id=replicate_id,
            success=False,
            tests_passing=False,
            compilation_success=False,
            execution_time_seconds=0.0,
            files_modified=0,
            tool_failures=1,
            iterations=0,
            commands_executed=0,
            repository_changes=0,
            read_instruction=False,
            followed_reference=False,
            ignored_reference=True,
            detected_inconsistency=False,
            repaired_reference=False,
            trace_events=[],
            error_message="cursor_cli_headless_unavailable",
        )
