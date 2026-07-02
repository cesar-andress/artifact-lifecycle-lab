"""Agent factory for RQ5 experiment runs."""

from __future__ import annotations

from artifact_lab.experiments.truth_decay.rq5_experiment.agents.base import AgentRunner
from artifact_lab.experiments.truth_decay.rq5_experiment.agents.stub import StubAgent

REGISTERED_AGENTS: dict[str, type] = {
    "stub": StubAgent,
}


def build_agents(names: list[str], **kwargs) -> list[AgentRunner]:
    agents: list[AgentRunner] = []
    for name in names:
        if name not in REGISTERED_AGENTS:
            raise ValueError(f"unknown agent: {name}; available={sorted(REGISTERED_AGENTS)}")
        agents.append(REGISTERED_AGENTS[name](**kwargs))
    return agents
