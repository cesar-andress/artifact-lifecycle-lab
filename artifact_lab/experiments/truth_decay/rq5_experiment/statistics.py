"""Statistical analysis for RQ5 causal experiment."""

from __future__ import annotations

import math
import random
from collections import defaultdict
from dataclasses import asdict, dataclass

from artifact_lab.experiments.truth_decay.audit_statistics import bootstrap_mean_ci, wilson_interval
from artifact_lab.experiments.truth_decay.rq5_experiment.models import AgentRunResult


@dataclass(frozen=True)
class EffectSizeRow:
    estimand: str
    agent_id: str
    n_cases: int
    n_pairs: int
    success_rate_a: float
    success_rate_b: float
    success_difference: float
    success_difference_ci_low: float
    success_difference_ci_high: float
    paired_success_difference: float
    paired_success_difference_ci_low: float
    paired_success_difference_ci_high: float
    cohens_h: float
    bootstrap_iterations: int


def _cohens_h(p1: float, p2: float) -> float:
    p1 = min(max(p1, 0.0), 1.0)
    p2 = min(max(p2, 0.0), 1.0)
    return 2.0 * math.asin(math.sqrt(p1)) - 2.0 * math.asin(math.sqrt(p2))


def _paired_differences(results: list[AgentRunResult]) -> dict[str, dict[str, list[float]]]:
    """Map agent_id -> case_id -> {A: success, B: success}."""
    by_agent_case: dict[str, dict[str, dict[str, float]]] = defaultdict(lambda: defaultdict(dict))
    for result in results:
        by_agent_case[result.agent_id][result.case_id][result.condition] = 1.0 if result.success else 0.0
    return by_agent_case


def compute_effect_sizes(
    results: list[AgentRunResult],
    *,
    bootstrap_iterations: int = 2000,
    seed: int = 42,
) -> list[EffectSizeRow]:
    by_agent: dict[str, list[AgentRunResult]] = defaultdict(list)
    for result in results:
        by_agent[result.agent_id].append(result)

    rows: list[EffectSizeRow] = []
    paired_map = _paired_differences(results)

    for agent_id, bucket in sorted(by_agent.items()):
        a_runs = [r for r in bucket if r.condition == "A"]
        b_runs = [r for r in bucket if r.condition == "B"]
        a_success = sum(1 for r in a_runs if r.success)
        b_success = sum(1 for r in b_runs if r.success)
        rate_a = a_success / len(a_runs) if a_runs else 0.0
        rate_b = b_success / len(b_runs) if b_runs else 0.0
        diff = rate_a - rate_b
        diff_lo, diff_hi = wilson_interval(a_success, len(a_runs))
        diff_b_lo, diff_b_hi = wilson_interval(b_success, len(b_runs))
        # Difference CI via bootstrap on paired case means when possible
        paired_diffs: list[float] = []
        for case_id, conds in paired_map[agent_id].items():
            if "A" in conds and "B" in conds:
                paired_diffs.append(conds["A"] - conds["B"])

        if paired_diffs:
            paired_mean, paired_lo, paired_hi = bootstrap_mean_ci(
                paired_diffs,
                iterations=bootstrap_iterations,
                seed=seed,
            )
        else:
            paired_mean = paired_lo = paired_hi = 0.0

        rows.append(
            EffectSizeRow(
                estimand="success_rate_difference_A_minus_B",
                agent_id=agent_id,
                n_cases=len(paired_map[agent_id]),
                n_pairs=len(paired_diffs),
                success_rate_a=round(rate_a, 6),
                success_rate_b=round(rate_b, 6),
                success_difference=round(diff, 6),
                success_difference_ci_low=round(diff_lo - diff_b_hi, 6),
                success_difference_ci_high=round(diff_hi - diff_b_lo, 6),
                paired_success_difference=round(paired_mean, 6),
                paired_success_difference_ci_low=round(paired_lo, 6),
                paired_success_difference_ci_high=round(paired_hi, 6),
                cohens_h=round(_cohens_h(rate_a, rate_b), 6),
                bootstrap_iterations=bootstrap_iterations,
            )
        )
    return rows


def effect_sizes_to_rows(rows: list[EffectSizeRow]) -> list[dict]:
    return [asdict(row) for row in rows]
