"""Agent factory for RQ5 experiment runs."""

from __future__ import annotations

from artifact_lab.experiments.truth_decay.rq5_experiment.agents.base import AgentRunner
from artifact_lab.experiments.truth_decay.rq5_experiment.agents.claude_code import ClaudeCodeAgent
from artifact_lab.experiments.truth_decay.rq5_experiment.agents.copilot_cli import CopilotCLIAgent
from artifact_lab.experiments.truth_decay.rq5_experiment.agents.cursor_cli import CursorCLIAgent
from artifact_lab.experiments.truth_decay.rq5_experiment.agents.stub import StubAgent

REGISTERED_AGENTS: dict[str, type] = {
    "stub": StubAgent,
    "claude_code": ClaudeCodeAgent,
    "copilot_cli": CopilotCLIAgent,
    "cursor_cli": CursorCLIAgent,
}

REAL_AGENT_NAMES = ("claude_code", "copilot_cli", "cursor_cli")


def discover_available_agent_names() -> list[str]:
    available: list[str] = []
    if ClaudeCodeAgent.is_available():
        available.append("claude_code")
    if CopilotCLIAgent.is_available():
        available.append("copilot_cli")
    if CursorCLIAgent.is_available():
        available.append("cursor_cli")
    return available


def build_agents(names: list[str], **kwargs) -> list[AgentRunner]:
    agents: list[AgentRunner] = []
    for name in names:
        if name not in REGISTERED_AGENTS:
            raise ValueError(f"unknown agent: {name}; available={sorted(REGISTERED_AGENTS)}")
        agents.append(REGISTERED_AGENTS[name](**kwargs))
    return agents
