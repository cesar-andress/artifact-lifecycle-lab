"""Run matrix planning for RQ5 v2 factorial experiment."""

from __future__ import annotations

import hashlib
import random

from artifact_lab.experiments.rq5_v2.factors import levels_for_cell
from artifact_lab.experiments.rq5_v2.models import ExperimentConfig, FactorialCase, RunPlanEntry


def _run_id(case_id: str, cell_code: str, agent_id: str, replicate_id: int) -> str:
    raw = f"{case_id}|{cell_code}|{agent_id}|{replicate_id}"
    return hashlib.sha256(raw.encode()).hexdigest()[:20]


def build_run_plan(
    *,
    cases: list[FactorialCase],
    config: ExperimentConfig,
    seed: int = 42,
) -> list[RunPlanEntry]:
    """
    Expand case × cell × agent × replicate matrix with Latin-square cell ordering.
    """
    rng = random.Random(seed)
    entries: list[RunPlanEntry] = []

    for case in cases:
        cell_order = list(config.cells)
        rng.shuffle(cell_order)

        for agent_id in config.agents:
            for replicate_id in range(1, config.replicates + 1):
                rep_cells = cell_order[:]
                rng.shuffle(rep_cells)
                for cell_code in rep_cells:
                    levels = levels_for_cell(cell_code)
                    entries.append(
                        RunPlanEntry(
                            run_id=_run_id(case.case_id, cell_code, agent_id, replicate_id),
                            case_id=case.case_id,
                            cell_code=cell_code,
                            agent_id=agent_id,
                            replicate_id=replicate_id,
                            factor_a=levels.factor_a,
                            factor_b=levels.factor_b,
                            factor_c=levels.factor_c,
                            repo_url=case.repo_url,
                            commit_sha=case.commit_sha,
                            instruction_path=case.instruction_path,
                            test_command=case.test_command,
                        )
                    )
    return entries
