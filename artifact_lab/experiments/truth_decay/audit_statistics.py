"""Shared statistics helpers for truth-decay validation audits."""

from __future__ import annotations

import math
import random


def wilson_interval(successes: int, trials: int, z: float = 1.96) -> tuple[float, float]:
    if trials == 0:
        return 0.0, 0.0
    p = successes / trials
    denom = 1 + z**2 / trials
    center = (p + z**2 / (2 * trials)) / denom
    margin = (z / denom) * math.sqrt((p * (1 - p) / trials) + (z**2 / (4 * trials**2)))
    return max(0.0, center - margin), min(1.0, center + margin)


def bootstrap_mean_ci(
    values: list[float],
    *,
    iterations: int = 2000,
    seed: int = 42,
) -> tuple[float, float, float]:
    if not values:
        return 0.0, 0.0, 0.0
    mean = sum(values) / len(values)
    if len(values) == 1:
        return mean, mean, mean
    rng = random.Random(seed)
    samples: list[float] = []
    for _ in range(iterations):
        draw = [rng.choice(values) for _ in range(len(values))]
        samples.append(sum(draw) / len(draw))
    samples.sort()
    lo = samples[int(0.025 * len(samples))]
    hi = samples[int(0.975 * len(samples))]
    return mean, lo, hi


def paired_cohens_d(differences: list[float]) -> float:
    """Cohen's d for paired samples (mean diff / SD of diffs)."""
    if len(differences) < 2:
        return 0.0
    mean = sum(differences) / len(differences)
    variance = sum((d - mean) ** 2 for d in differences) / (len(differences) - 1)
    if variance <= 0:
        return 0.0
    return mean / math.sqrt(variance)


def permutation_test_sign_flip(
    differences: list[float],
    *,
    iterations: int = 10000,
    seed: int = 42,
    alternative: str = "two-sided",
) -> float:
    """Sign-flip permutation test for paired mean difference."""
    if not differences:
        return 1.0
    observed = sum(differences) / len(differences)
    if observed == 0.0:
        return 1.0
    rng = random.Random(seed)
    extreme = 0
    for _ in range(iterations):
        flipped = [d * rng.choice([-1, 1]) for d in differences]
        perm_mean = sum(flipped) / len(flipped)
        if alternative == "less":
            if perm_mean <= observed:
                extreme += 1
        elif alternative == "greater":
            if perm_mean >= observed:
                extreme += 1
        else:
            if abs(perm_mean) >= abs(observed):
                extreme += 1
    return (extreme + 1) / (iterations + 1)
