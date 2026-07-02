"""Statistics for RQ2 post-verification failure audit."""

from __future__ import annotations

import csv
import math
import random
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from artifact_lab.experiments.truth_decay.rq2_failure_audit import FailureAuditRecord


@dataclass(frozen=True)
class AuditStatistics:
    n_failures: int
    n_genuine_adjusted: int
    genuine_proportion: float
    genuine_proportion_ci_low: float
    genuine_proportion_ci_high: float
    verified_cohort_size: int
    adjusted_decay_rate: float
    adjusted_decay_rate_ci_low: float
    adjusted_decay_rate_ci_high: float
    born_stale_raw: int
    born_stale_genuine_adjusted: int
    raw_ratio_born_to_post: float
    adjusted_ratio_born_to_post: float
    bootstrap_ratio_ci_low: float
    bootstrap_ratio_ci_high: float
    category_counts: dict[str, int]


def wilson_interval(successes: int, trials: int, z: float = 1.96) -> tuple[float, float]:
    if trials == 0:
        return 0.0, 0.0
    p = successes / trials
    denom = 1 + z**2 / trials
    center = (p + z**2 / (2 * trials)) / denom
    margin = (z / denom) * math.sqrt((p * (1 - p) / trials) + (z**2 / (4 * trials**2)))
    return max(0.0, center - margin), min(1.0, center + margin)


def load_born_stale_repo_counts(
    taxonomy_csv: Path,
) -> tuple[int, int, dict[str, int], dict[str, int]]:
    """Return total born-stale rows, genuine-false count, and per-repo maps."""
    by_repo_raw: Counter[str] = Counter()
    by_repo_genuine: Counter[str] = Counter()
    total = 0
    genuine = 0
    with taxonomy_csv.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            total += 1
            repo = row["repo_id"]
            by_repo_raw[repo] += 1
            if row.get("final_category") == "genuine_false_claim":
                genuine += 1
                by_repo_genuine[repo] += 1
    return total, genuine, dict(by_repo_raw), dict(by_repo_genuine)


def _bootstrap_adjusted_ratio(
    *,
    records: list[FailureAuditRecord],
    born_by_repo_genuine: dict[str, int],
    bootstrap_iterations: int,
    seed: int,
) -> tuple[float, float]:
    by_repo_post_genuine: Counter[str] = Counter()
    by_repo_post_total: Counter[str] = Counter()
    for record in records:
        by_repo_post_total[record.repo_id] += 1
        if record.is_genuine_decay:
            by_repo_post_genuine[record.repo_id] += 1

    repos = sorted(set(born_by_repo_genuine) | set(by_repo_post_total))
    if not repos:
        return 0.0, 0.0

    rng = random.Random(seed)
    samples: list[float] = []
    for _ in range(bootstrap_iterations):
        drawn = [rng.choice(repos) for _ in range(len(repos))]
        post_g = sum(by_repo_post_genuine.get(r, 0) for r in drawn)
        born_g = sum(born_by_repo_genuine.get(r, 0) for r in drawn)
        if post_g == 0:
            continue
        samples.append(born_g / post_g)

    if not samples:
        return 0.0, 0.0
    samples.sort()
    lo = samples[int(0.025 * len(samples))]
    hi = samples[int(0.975 * len(samples))]
    return lo, hi


def compute_audit_statistics(
    *,
    records: list[FailureAuditRecord],
    verified_cohort_size: int,
    born_stale_raw: int,
    born_stale_genuine_adjusted: int,
    born_by_repo_raw: dict[str, int] | None = None,
    born_by_repo_genuine: dict[str, int] | None = None,
    bootstrap_iterations: int = 2000,
    seed: int = 42,
) -> AuditStatistics:
    n = len(records)
    n_genuine = sum(1 for r in records if r.is_genuine_decay)
    prop = n_genuine / n if n else 0.0
    prop_lo, prop_hi = wilson_interval(n_genuine, n)

    decay_rate = n_genuine / verified_cohort_size if verified_cohort_size else 0.0
    dr_lo, dr_hi = wilson_interval(n_genuine, verified_cohort_size)

    raw_ratio = born_stale_raw / n if n else 0.0
    adj_ratio = born_stale_genuine_adjusted / n_genuine if n_genuine else float("inf")

    if born_by_repo_genuine:
        lo, hi = _bootstrap_adjusted_ratio(
            records=records,
            born_by_repo_genuine=born_by_repo_genuine,
            bootstrap_iterations=bootstrap_iterations,
            seed=seed,
        )
    else:
        lo = hi = adj_ratio if math.isfinite(adj_ratio) else 0.0

    return AuditStatistics(
        n_failures=n,
        n_genuine_adjusted=n_genuine,
        genuine_proportion=round(prop, 6),
        genuine_proportion_ci_low=round(prop_lo, 6),
        genuine_proportion_ci_high=round(prop_hi, 6),
        verified_cohort_size=verified_cohort_size,
        adjusted_decay_rate=round(decay_rate, 6),
        adjusted_decay_rate_ci_low=round(dr_lo, 6),
        adjusted_decay_rate_ci_high=round(dr_hi, 6),
        born_stale_raw=born_stale_raw,
        born_stale_genuine_adjusted=born_stale_genuine_adjusted,
        raw_ratio_born_to_post=round(raw_ratio, 4),
        adjusted_ratio_born_to_post=round(adj_ratio, 4) if math.isfinite(adj_ratio) else 0.0,
        bootstrap_ratio_ci_low=round(lo, 4),
        bootstrap_ratio_ci_high=round(hi, 4),
        category_counts=dict(Counter(r.final_category for r in records)),
    )
