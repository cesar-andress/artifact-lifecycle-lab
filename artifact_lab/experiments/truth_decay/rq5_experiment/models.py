"""RQ5 causal agent-impact experiment — data models."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExperimentCase:
    case_id: str
    spec_id: str
    repo_id: str
    repo_url: str
    instruction_path: str
    task_commit_sha: str
    anchor_reference: str
    anchor_reference_type: str
    condition_a_blob_sha: str
    condition_b_blob_sha: str
    born_stale_commit_sha: str
    truthful_commit_sha: str
    task_prompt: str
    test_command: str
    selection_reason: str
    confirmed_false: bool
    p1_sample: bool


@dataclass(frozen=True)
class TraceEvent:
    timestamp: str
    event_type: str
    payload: dict[str, Any]


@dataclass
class AgentRunResult:
    agent_id: str
    condition: str
    case_id: str
    replicate_id: int
    success: bool
    tests_passing: bool
    compilation_success: bool
    execution_time_seconds: float
    files_modified: int
    tool_failures: int
    iterations: int
    commands_executed: int
    repository_changes: int
    read_instruction: bool
    followed_reference: bool
    ignored_reference: bool
    detected_inconsistency: bool
    repaired_reference: bool
    trace_events: list[TraceEvent] = field(default_factory=list)
    error_message: str = ""

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        row.pop("trace_events")
        return row
