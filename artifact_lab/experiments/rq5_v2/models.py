"""Data models for RQ5 v2 factorial experiment."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from artifact_lab.experiments.rq5_v2.factors import ALL_CELLS, CellCode

DEFAULT_AGENTS: tuple[str, ...] = ("claude_code", "codex", "gemini_cli")
DEFAULT_REPLICATES: int = 3
DEFAULT_CELLS: tuple[str, ...] = tuple(c.value for c in ALL_CELLS)
RUN_TIMEOUT_SECONDS: int = 1200


@dataclass(frozen=True)
class FactorialCell:
    """Frozen instruction variant for one within-case cell."""

    cell_code: str
    instruction_blob_sha: str
    cited_anchor: str
    mechanical_truth: bool
    task_prompt: str
    load_bearing: bool


@dataclass(frozen=True)
class FactorialCase:
    """Experimental unit: one repo × commit × instruction file × anchor pair."""

    case_id: str
    candidate_id: str
    repo_id: str
    repo_url: str
    repository: str
    instruction_path: str
    commit_sha: str
    anchor_path_true: str
    anchor_path_false: str
    decoy_path: str
    test_command: str
    reference_type: str
    load_bearing_role: str
    ecosystem: str
    calibrated_expected_success: float
    cells: dict[str, FactorialCell]
    repairability_score: int = 0
    repairability_reason: str = ""
    selection_reason: str = "calibration_target_band"

    def get_cell(self, cell_code: str) -> FactorialCell:
        if cell_code not in self.cells:
            raise KeyError(f"cell {cell_code} not defined for case {self.case_id}")
        return self.cells[cell_code]


@dataclass(frozen=True)
class RunPlanEntry:
    """One scheduled agent run (may be dry-run only)."""

    run_id: str
    case_id: str
    cell_code: str
    agent_id: str
    replicate_id: int
    factor_a: str
    factor_b: str
    factor_c: str
    repo_url: str
    commit_sha: str
    instruction_path: str
    test_command: str
    status: str = "planned"


@dataclass
class FactorialRunResult:
    """Outcome of one executed (or stub) agent run."""

    run_id: str
    case_id: str
    cell_code: str
    agent_id: str
    replicate_id: int
    factor_a: str
    factor_b: str
    factor_c: str
    success: bool = False
    tests_passing: bool = False
    compilation_success: bool = True
    execution_time_seconds: float = 0.0
    files_modified: int = 0
    tool_failures: int = 0
    read_instruction: bool = False
    anchor_path_touched: bool = False
    decoy_path_touched: bool = False
    bind_failure_detected: bool = False
    grounding_action: bool = False
    repair_success: bool = False
    dry_run: bool = True
    error_message: str = ""
    trace_path: str = ""

    def to_row(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ExperimentConfig:
    """Top-level experiment configuration (frozen at manifest build)."""

    protocol_version: str = "RQ5_FACTORIAL_v1.0"
    agents: tuple[str, ...] = DEFAULT_AGENTS
    cells: tuple[str, ...] = DEFAULT_CELLS
    replicates: int = DEFAULT_REPLICATES
    primary_agent: str = "claude_code"
    replication_agents: tuple[str, ...] = ("codex", "gemini_cli")
    run_timeout_seconds: int = RUN_TIMEOUT_SECONDS
    allow_execute: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def expected_runs(self, n_cases: int) -> int:
        return n_cases * len(self.cells) * len(self.agents) * self.replicates
