"""GitHub Copilot CLI adapter for RQ5."""

from __future__ import annotations

import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from artifact_lab.experiments.truth_decay.rq5_experiment.agents.base import trace_from_events
from artifact_lab.experiments.truth_decay.rq5_experiment.agents.cli_utils import (
    build_experiment_prompt,
    git_workspace_metrics,
    instruction_was_read,
    read_instruction_event,
    reference_followed,
    run_subprocess,
)
from artifact_lab.experiments.truth_decay.rq5_experiment.models import AgentRunResult, ExperimentCase, TraceEvent


class CopilotCLIAgent:
    agent_id = "copilot_cli"

    def __init__(
        self,
        *,
        command: list[str] | None = None,
        timeout_seconds: int = 1800,
    ) -> None:
        self.command = command or ["npx", "@github/copilot"]
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def is_available(command: list[str] | None = None) -> bool:
        cmd = command or ["npx", "@github/copilot"]
        try:
            proc = run_subprocess(
                [*cmd, "-p", "Reply OK", "--allow-all-tools"],
                cwd=Path.cwd(),
                timeout=90,
            )
            combined = (proc.stdout or "") + (proc.stderr or "")
            if "Authentication failed" in combined:
                return False
            return proc.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            return False

    def run(
        self,
        *,
        case: ExperimentCase,
        condition: str,
        workspace: Path,
        replicate_id: int,
    ) -> AgentRunResult:
        started = time.perf_counter()
        prompt = build_experiment_prompt(case)
        cmd = [
            *self.command,
            "-p",
            prompt,
            "--allow-all-tools",
            "--add-dir",
            str(workspace),
        ]
        events: list[TraceEvent] = [read_instruction_event(case.instruction_path)]
        error_message = ""
        tool_invocations = 0
        tool_failures = 0

        try:
            proc = run_subprocess(cmd, cwd=workspace, timeout=self.timeout_seconds)
            stdout = proc.stdout or ""
            stderr = proc.stderr or ""
            if proc.returncode != 0:
                error_message = stderr.strip() or stdout.strip() or f"exit_code={proc.returncode}"
                tool_failures += 1
            events.append(
                TraceEvent(
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    event_type="copilot_response",
                    payload={"stdout_len": len(stdout), "stderr_len": len(stderr)},
                )
            )
            tool_invocations = stdout.lower().count("tool") + stderr.lower().count("tool")
        except subprocess.TimeoutExpired:
            error_message = f"timeout_after_{self.timeout_seconds}s"
            tool_failures += 1
        except OSError as exc:
            error_message = str(exc)
            tool_failures += 1

        git_metrics = git_workspace_metrics(workspace)
        trace_flags = trace_from_events(events)
        elapsed = time.perf_counter() - started

        return AgentRunResult(
            agent_id=self.agent_id,
            condition=condition,
            case_id=case.case_id,
            replicate_id=replicate_id,
            success=not error_message,
            tests_passing=False,
            compilation_success=True,
            execution_time_seconds=round(elapsed, 3),
            files_modified=git_metrics["files_modified"],
            tool_failures=tool_failures,
            iterations=1,
            commands_executed=tool_invocations,
            repository_changes=git_metrics["repository_changes"],
            read_instruction=instruction_was_read(events, case.instruction_path),
            followed_reference=reference_followed(events, case.anchor_reference),
            ignored_reference=not reference_followed(events, case.anchor_reference),
            detected_inconsistency=False,
            repaired_reference=trace_flags["repaired_reference"],
            trace_events=events,
            error_message=error_message,
            tool_invocations=tool_invocations,
            patch_size=int(git_metrics["patch_size"]),
            token_usage=None,
            cost_usd=None,
        )
