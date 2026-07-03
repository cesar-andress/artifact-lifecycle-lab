"""Claude Code CLI adapter for RQ5."""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

from artifact_lab.experiments.truth_decay.rq5_experiment.agents.base import trace_from_events
from artifact_lab.experiments.truth_decay.rq5_experiment.agents.cli_utils import (
    build_experiment_prompt,
    git_workspace_metrics,
    instruction_was_read,
    parse_claude_json_result,
    parse_claude_stream_json,
    read_instruction_event,
    reference_followed,
    run_subprocess,
    shell_commands_from_events,
)
from artifact_lab.experiments.truth_decay.rq5_experiment.models import AgentRunResult, ExperimentCase


class ClaudeCodeAgent:
    agent_id = "claude_code"

    def __init__(
        self,
        *,
        command: str = "claude",
        timeout_seconds: int = 1800,
        use_stream_json: bool = True,
    ) -> None:
        self.command = command
        self.timeout_seconds = timeout_seconds
        self.use_stream_json = use_stream_json

    @staticmethod
    def is_available(command: str = "claude") -> bool:
        try:
            proc = run_subprocess([command, "--version"], cwd=Path.cwd(), timeout=30)
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
        prompt = build_experiment_prompt(case, condition=condition)
        cmd = [
            self.command,
            "-p",
            "--dangerously-skip-permissions",
        ]
        if self.use_stream_json:
            cmd.extend(["--verbose", "--output-format", "stream-json"])
        else:
            cmd.extend(["--output-format", "json"])
        cmd.append(prompt)

        env = os.environ.copy()
        env["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] = "1"

        error_message = ""
        events = [read_instruction_event(case.instruction_path)]
        meta = {
            "iterations": 0,
            "tool_invocations": 0,
            "token_usage": None,
            "cost_usd": None,
            "tool_failures": 0,
        }

        try:
            proc = run_subprocess(cmd, cwd=workspace, timeout=self.timeout_seconds, env=env)
            stdout = proc.stdout or ""
            stderr = proc.stderr or ""
            if proc.returncode != 0:
                error_message = stderr.strip() or stdout.strip() or f"exit_code={proc.returncode}"
            if self.use_stream_json:
                parsed_events, parsed_meta = parse_claude_stream_json(stdout)
            else:
                parsed_events, parsed_meta = parse_claude_json_result(stdout)
            events.extend(parsed_events)
            meta.update({k: parsed_meta.get(k, meta[k]) for k in meta})
        except subprocess.TimeoutExpired:
            error_message = f"timeout_after_{self.timeout_seconds}s"
        except OSError as exc:
            error_message = str(exc)

        if not instruction_was_read(events, case.instruction_path):
            events.append(read_instruction_event(case.instruction_path))

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
            tool_failures=int(meta["tool_failures"]),
            iterations=int(meta["iterations"] or 1),
            commands_executed=shell_commands_from_events(events),
            repository_changes=git_metrics["repository_changes"],
            read_instruction=instruction_was_read(events, case.instruction_path),
            followed_reference=reference_followed(events, case.anchor_reference),
            ignored_reference=not reference_followed(events, case.anchor_reference),
            detected_inconsistency=False,
            repaired_reference=trace_flags["repaired_reference"],
            trace_events=events,
            error_message=error_message,
            tool_invocations=int(meta["tool_invocations"]),
            patch_size=int(git_metrics["patch_size"]),
            token_usage=meta["token_usage"],
            cost_usd=meta["cost_usd"],
        )
