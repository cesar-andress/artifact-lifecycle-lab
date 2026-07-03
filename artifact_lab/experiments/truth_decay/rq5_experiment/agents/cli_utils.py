"""Shared helpers for external CLI agent adapters."""

from __future__ import annotations

import json
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from artifact_lab.experiments.truth_decay.rq5_experiment.models import ExperimentCase, TraceEvent
from artifact_lab.ingest.git_utils import run_git


def build_experiment_prompt(case: ExperimentCase, *, condition: str = "A") -> str:
    if condition == "C":
        return (
            f"{case.task_prompt}\n\n"
            "No project instruction file is provided for this run.\n"
            f"Test command to run before finishing: `{case.test_command}`\n\n"
            "Constraints:\n"
            "- Use only files in this repository snapshot.\n"
            "- Do not fetch new commits or use network except running tests.\n"
            "- Make a small, bounded change verifiable by the test command.\n"
        )
    return (
        f"{case.task_prompt}\n\n"
        f"Instruction file (authoritative): `{case.instruction_path}`\n"
        f"Anchor reference from instructions: `{case.anchor_reference}`\n"
        f"Test command to run before finishing: `{case.test_command}`\n\n"
        "Constraints:\n"
        "- Use only files in this repository snapshot.\n"
        "- Do not fetch new commits or use network except running tests.\n"
        "- Make a small, bounded change verifiable by the test command.\n"
    )


def git_workspace_metrics(workspace: Path) -> dict[str, int]:
    root = workspace.resolve()
    if not root.is_dir():
        return {"files_modified": 0, "repository_changes": 0, "patch_size": 0}

    status = run_git(["git", "status", "--porcelain"], cwd=root, timeout=60)
    files_modified = 0
    if status.returncode == 0:
        files_modified = len([line for line in status.stdout.splitlines() if line.strip()])

    diff = run_git(["git", "diff", "--numstat", "HEAD"], cwd=root, timeout=60)
    patch_lines = 0
    if diff.returncode == 0:
        for line in diff.stdout.splitlines():
            parts = line.split("\t")
            if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                patch_lines += int(parts[0]) + int(parts[1])

    return {
        "files_modified": files_modified,
        "repository_changes": files_modified,
        "patch_size": patch_lines,
    }


def instruction_was_read(events: list[TraceEvent], instruction_path: str) -> bool:
    for event in events:
        if event.event_type in {"read_instruction", "Read", "read_file"}:
            return True
        payload = event.payload
        if instruction_path in str(payload.get("path", "")):
            return True
        if instruction_path in str(payload.get("command", "")):
            return True
    return False


def reference_followed(events: list[TraceEvent], reference: str) -> bool:
    ref_base = reference.rstrip("/").split("/")[-1]
    for event in events:
        if event.event_type in {"follow_reference", "follow_reference", "Edit", "Write", "Bash"}:
            blob = json.dumps(event.payload)
            if reference in blob or ref_base in blob:
                return True
    return False


def parse_claude_stream_json(stdout: str) -> tuple[list[TraceEvent], dict]:
    events: list[TraceEvent] = []
    meta: dict = {
        "iterations": 0,
        "tool_invocations": 0,
        "token_usage": None,
        "cost_usd": None,
        "tool_failures": 0,
    }
    now = lambda: datetime.now(timezone.utc).isoformat()

    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue

        if obj.get("type") == "assistant":
            message = obj.get("message") or {}
            for block in message.get("content") or []:
                if block.get("type") == "tool_use":
                    meta["tool_invocations"] += 1
                    name = block.get("name", "tool")
                    events.append(
                        TraceEvent(
                            timestamp=now(),
                            event_type=name,
                            payload={"tool": name, "input": block.get("input") or {}},
                        )
                    )
                    if name.lower() in {"bash", "run_terminal_cmd"}:
                        cmd = str((block.get("input") or {}).get("command", ""))
                        events.append(
                            TraceEvent(
                                timestamp=now(),
                                event_type="shell_command",
                                payload={"command": cmd},
                            )
                        )

        if obj.get("type") == "user":
            for block in (obj.get("message") or {}).get("content") or []:
                if block.get("type") == "tool_result" and block.get("is_error"):
                    meta["tool_failures"] += 1
                    events.append(
                        TraceEvent(
                            timestamp=now(),
                            event_type="tool_failure",
                            payload={"content": block.get("content")},
                        )
                    )

        if obj.get("type") == "result":
            meta["iterations"] = int(obj.get("num_turns") or 0)
            usage = obj.get("usage") or {}
            input_t = int(usage.get("input_tokens") or 0)
            output_t = int(usage.get("output_tokens") or 0)
            meta["token_usage"] = input_t + output_t
            if obj.get("total_cost_usd") is not None:
                meta["cost_usd"] = float(obj["total_cost_usd"])

    return events, meta


def parse_claude_json_result(stdout: str) -> tuple[list[TraceEvent], dict]:
    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("type") == "result":
            usage = obj.get("usage") or {}
            input_t = int(usage.get("input_tokens") or 0)
            output_t = int(usage.get("output_tokens") or 0)
            return [], {
                "iterations": int(obj.get("num_turns") or 1),
                "tool_invocations": 0,
                "token_usage": input_t + output_t,
                "cost_usd": float(obj["total_cost_usd"]) if obj.get("total_cost_usd") is not None else None,
                "tool_failures": 0,
            }
    return [], {"iterations": 1, "tool_invocations": 0, "token_usage": None, "cost_usd": None, "tool_failures": 0}


def run_subprocess(
    cmd: list[str],
    *,
    cwd: Path,
    timeout: int,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


def shell_commands_from_events(events: list[TraceEvent]) -> int:
    return sum(1 for event in events if event.event_type in {"shell_command", "Bash"})


def read_instruction_event(instruction_path: str) -> TraceEvent:
    return TraceEvent(
        timestamp=datetime.now(timezone.utc).isoformat(),
        event_type="read_instruction",
        payload={"path": instruction_path},
    )
