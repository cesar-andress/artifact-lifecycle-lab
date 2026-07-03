"""Agent adapters: Claude Code, Codex, Gemini CLI."""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

from artifact_lab.experiments.rq5_v2.agents.base import FactorialAgent
from artifact_lab.experiments.rq5_v2.factors import levels_for_cell
from artifact_lab.experiments.rq5_v2.models import FactorialCase, FactorialRunResult
from artifact_lab.experiments.rq5_v2.prompts import build_factorial_prompt
from artifact_lab.experiments.truth_decay.rq5_experiment.agents.cli_utils import run_subprocess


def _base_result(
    *,
    case: FactorialCase,
    cell_code: str,
    agent_id: str,
    replicate_id: int,
    run_id: str,
    dry_run: bool,
) -> FactorialRunResult:
    levels = levels_for_cell(cell_code)
    return FactorialRunResult(
        run_id=run_id,
        case_id=case.case_id,
        cell_code=cell_code,
        agent_id=agent_id,
        replicate_id=replicate_id,
        factor_a=levels.factor_a,
        factor_b=levels.factor_b,
        factor_c=levels.factor_c,
        dry_run=dry_run,
    )


class ClaudeCodeAgent:
    agent_id = "claude_code"

    def __init__(self, *, command: str = "claude", timeout_seconds: int = 1200) -> None:
        self.command = command
        self.timeout_seconds = timeout_seconds

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
        case: FactorialCase,
        cell_code: str,
        workspace: Path,
        replicate_id: int,
        run_id: str,
    ) -> FactorialRunResult:
        started = time.perf_counter()
        prompt = build_factorial_prompt(case, cell_code=cell_code)
        cmd = [
            self.command,
            "-p",
            "--dangerously-skip-permissions",
            "--verbose",
            "--output-format",
            "stream-json",
            prompt,
        ]
        env = os.environ.copy()
        env["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] = "1"
        error = ""
        try:
            proc = run_subprocess(cmd, cwd=workspace, timeout=self.timeout_seconds, env=env)
            if proc.returncode != 0:
                error = proc.stderr.strip() or proc.stdout.strip() or f"exit {proc.returncode}"
        except subprocess.TimeoutExpired:
            error = "timeout"
        result = _base_result(
            case=case,
            cell_code=cell_code,
            agent_id=self.agent_id,
            replicate_id=replicate_id,
            run_id=run_id,
            dry_run=False,
        )
        result.execution_time_seconds = round(time.perf_counter() - started, 3)
        result.error_message = error
        result.read_instruction = levels_for_cell(cell_code).instruction_present
        return result


class CodexAgent:
    """OpenAI Codex CLI adapter."""

    agent_id = "codex"

    def __init__(self, *, command: str = "codex", timeout_seconds: int = 1200) -> None:
        self.command = command
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def is_available(command: str = "codex") -> bool:
        try:
            proc = run_subprocess([command, "--version"], cwd=Path.cwd(), timeout=30)
            return proc.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            return False

    def run(
        self,
        *,
        case: FactorialCase,
        cell_code: str,
        workspace: Path,
        replicate_id: int,
        run_id: str,
    ) -> FactorialRunResult:
        started = time.perf_counter()
        prompt = build_factorial_prompt(case, cell_code=cell_code)
        cmd = [self.command, "exec", "--full-auto", prompt]
        error = ""
        try:
            proc = run_subprocess(cmd, cwd=workspace, timeout=self.timeout_seconds)
            if proc.returncode != 0:
                error = proc.stderr.strip() or proc.stdout.strip() or f"exit {proc.returncode}"
        except subprocess.TimeoutExpired:
            error = "timeout"
        result = _base_result(
            case=case,
            cell_code=cell_code,
            agent_id=self.agent_id,
            replicate_id=replicate_id,
            run_id=run_id,
            dry_run=False,
        )
        result.execution_time_seconds = round(time.perf_counter() - started, 3)
        result.error_message = error
        result.read_instruction = levels_for_cell(cell_code).instruction_present
        return result


class GeminiCLIAgent:
    """Google Gemini CLI adapter."""

    agent_id = "gemini_cli"

    def __init__(self, *, command: str = "gemini", timeout_seconds: int = 1200) -> None:
        self.command = command
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def is_available(command: str = "gemini") -> bool:
        try:
            proc = run_subprocess([command, "--version"], cwd=Path.cwd(), timeout=30)
            return proc.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            return False

    def run(
        self,
        *,
        case: FactorialCase,
        cell_code: str,
        workspace: Path,
        replicate_id: int,
        run_id: str,
    ) -> FactorialRunResult:
        started = time.perf_counter()
        prompt = build_factorial_prompt(case, cell_code=cell_code)
        cmd = [self.command, "-p", prompt]
        error = ""
        try:
            proc = run_subprocess(cmd, cwd=workspace, timeout=self.timeout_seconds)
            if proc.returncode != 0:
                error = proc.stderr.strip() or proc.stdout.strip() or f"exit {proc.returncode}"
        except subprocess.TimeoutExpired:
            error = "timeout"
        result = _base_result(
            case=case,
            cell_code=cell_code,
            agent_id=self.agent_id,
            replicate_id=replicate_id,
            run_id=run_id,
            dry_run=False,
        )
        result.execution_time_seconds = round(time.perf_counter() - started, 3)
        result.error_message = error
        result.read_instruction = levels_for_cell(cell_code).instruction_present
        return result


REGISTERED_AGENTS: dict[str, type] = {
    "claude_code": ClaudeCodeAgent,
    "codex": CodexAgent,
    "gemini_cli": GeminiCLIAgent,
}


def discover_available_agents() -> list[str]:
    available: list[str] = []
    for name, cls in REGISTERED_AGENTS.items():
        if cls.is_available():
            available.append(name)
    return available


def build_agents(names: list[str], **kwargs) -> list[FactorialAgent]:
    agents: list[FactorialAgent] = []
    for name in names:
        if name not in REGISTERED_AGENTS:
            raise ValueError(f"unknown agent: {name}; available={sorted(REGISTERED_AGENTS)}")
        agents.append(REGISTERED_AGENTS[name](**kwargs))
    return agents
