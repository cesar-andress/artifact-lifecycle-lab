"""Extended causal statistics for RQ5 evidence collection."""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import asdict, dataclass

from artifact_lab.experiments.truth_decay.audit_statistics import bootstrap_mean_ci
from artifact_lab.experiments.truth_decay.rq5_experiment.models import AgentRunResult
from artifact_lab.experiments.truth_decay.rq5_experiment.statistics import compute_effect_sizes


@dataclass(frozen=True)
class CausalStatisticsRow:
    estimand: str
    agent_id: str
    n_cases: int
    n_pairs: int
    value: float
    ci_low: float
    ci_high: float
    method: str
    n_a_success: int = 0
    n_b_success: int = 0
    n_both_success: int = 0
    n_a_only_success: int = 0
    n_b_only_success: int = 0
    n_neither_success: int = 0


def _paired_case_success(
    results: list[AgentRunResult],
) -> dict[str, dict[str, dict[int, bool]]]:
    """agent_id -> case_id -> replicate_id -> {A: success, B: success}."""
    nested: dict[str, dict[str, dict[int, dict[str, bool]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(dict))
    )
    for result in results:
        nested[result.agent_id][result.case_id][result.replicate_id][result.condition] = result.success
    return nested


def mcnemar_exact_p(b: int, c: int) -> float:
    """Exact two-sided McNemar p-value for discordant pairs b (A only) and c (B only)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    accum = 0.0
    for i in range(k + 1):
        accum += math.comb(n, i)
    p_one_side = accum / (2**n)
    p_two_side = min(1.0, 2 * p_one_side)
    return round(p_two_side, 6)


def cliffs_delta(paired_a: list[float], paired_b: list[float]) -> float:
    if not paired_a or len(paired_a) != len(paired_b):
        return 0.0
    wins = losses = 0
    for a, b in zip(paired_a, paired_b):
        if a > b:
            wins += 1
        elif a < b:
            losses += 1
    n = len(paired_a)
    return round((wins - losses) / n, 6)


def compute_causal_statistics(
    results: list[AgentRunResult],
    *,
    bootstrap_iterations: int = 2000,
    seed: int = 42,
) -> list[CausalStatisticsRow]:
    rows: list[CausalStatisticsRow] = []
    effect_sizes = compute_effect_sizes(results, bootstrap_iterations=bootstrap_iterations, seed=seed)

    for effect in effect_sizes:
        rows.append(
            CausalStatisticsRow(
                estimand="success_rate_a",
                agent_id=effect.agent_id,
                n_cases=effect.n_cases,
                n_pairs=effect.n_pairs,
                value=effect.success_rate_a,
                ci_low=effect.success_difference_ci_low,
                ci_high=effect.success_difference_ci_high,
                method="wilson",
            )
        )
        rows.append(
            CausalStatisticsRow(
                estimand="success_rate_b",
                agent_id=effect.agent_id,
                n_cases=effect.n_cases,
                n_pairs=effect.n_pairs,
                value=effect.success_rate_b,
                ci_low=0.0,
                ci_high=0.0,
                method="wilson",
            )
        )
        rows.append(
            CausalStatisticsRow(
                estimand="paired_success_difference_a_minus_b",
                agent_id=effect.agent_id,
                n_cases=effect.n_cases,
                n_pairs=effect.n_pairs,
                value=effect.paired_success_difference,
                ci_low=effect.paired_success_difference_ci_low,
                ci_high=effect.paired_success_difference_ci_high,
                method="bootstrap_cluster_case",
            )
        )
        rows.append(
            CausalStatisticsRow(
                estimand="cohens_h",
                agent_id=effect.agent_id,
                n_cases=effect.n_cases,
                n_pairs=effect.n_pairs,
                value=effect.cohens_h,
                ci_low=effect.cohens_h,
                ci_high=effect.cohens_h,
                method="point_estimate",
            )
        )

    nested = _paired_case_success(results)
    for agent_id, cases in sorted(nested.items()):
        a_only = b_only = both = neither = 0
        time_a: list[float] = []
        time_b: list[float] = []
        for case_id, replicates in cases.items():
            for rep_success in replicates.values():
                a = rep_success.get("A", False)
                b = rep_success.get("B", False)
                if a and b:
                    both += 1
                elif a and not b:
                    a_only += 1
                elif b and not a:
                    b_only += 1
                else:
                    neither += 1
        for result in results:
            if result.agent_id != agent_id:
                continue
            if result.condition == "A":
                time_a.append(result.execution_time_seconds)
            else:
                time_b.append(result.execution_time_seconds)

        paired_times_a: list[float] = []
        paired_times_b: list[float] = []
        for case_id, replicates in cases.items():
            for rep_id, rep_success in replicates.items():
                ta = next(
                    (
                        r.execution_time_seconds
                        for r in results
                        if r.agent_id == agent_id
                        and r.case_id == case_id
                        and r.replicate_id == rep_id
                        and r.condition == "A"
                    ),
                    None,
                )
                tb = next(
                    (
                        r.execution_time_seconds
                        for r in results
                        if r.agent_id == agent_id
                        and r.case_id == case_id
                        and r.replicate_id == rep_id
                        and r.condition == "B"
                    ),
                    None,
                )
                if ta is not None and tb is not None:
                    paired_times_a.append(ta)
                    paired_times_b.append(tb)

        delta = cliffs_delta(paired_times_a, paired_times_b)
        if paired_times_a:
            diffs = [a - b for a, b in zip(paired_times_a, paired_times_b)]
            mean_diff, lo, hi = bootstrap_mean_ci(diffs, iterations=bootstrap_iterations, seed=seed)
        else:
            mean_diff = lo = hi = 0.0

        rows.append(
            CausalStatisticsRow(
                estimand="mcnemar_p_value",
                agent_id=agent_id,
                n_cases=len(cases),
                n_pairs=both + a_only + b_only + neither,
                value=mcnemar_exact_p(a_only, b_only),
                ci_low=0.0,
                ci_high=1.0,
                method="exact_mcnemar",
                n_a_success=both + a_only,
                n_b_success=both + b_only,
                n_both_success=both,
                n_a_only_success=a_only,
                n_b_only_success=b_only,
                n_neither_success=neither,
            )
        )
        rows.append(
            CausalStatisticsRow(
                estimand="execution_time_difference_a_minus_b",
                agent_id=agent_id,
                n_cases=len(cases),
                n_pairs=len(paired_times_a),
                value=round(mean_diff, 6),
                ci_low=round(lo, 6),
                ci_high=round(hi, 6),
                method="bootstrap_paired",
            )
        )
        rows.append(
            CausalStatisticsRow(
                estimand="cliffs_delta_execution_time",
                agent_id=agent_id,
                n_cases=len(cases),
                n_pairs=len(paired_times_a),
                value=delta,
                ci_low=delta,
                ci_high=delta,
                method="point_estimate",
            )
        )

    return rows


def causal_statistics_to_rows(rows: list[CausalStatisticsRow]) -> list[dict]:
    return [asdict(row) for row in rows]
