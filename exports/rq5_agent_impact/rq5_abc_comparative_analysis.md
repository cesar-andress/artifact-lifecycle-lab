# RQ5 Comparative Analysis — A / B / C

**Scope:** Paired triplets where the same `(case_id, replicate_id)` has runs in A, B, and C.
**Overlap cases:** 22 confirmed-false cases with partial A/B and complete C.
**Paired triplets:** 63 (of max 66).
**Agent:** claude_code only.

> Descriptive/paired statistics only. No post-hoc pruning. C from `exports/rq5_agent_impact_c/`; A/B from `exports/rq5_agent_impact/`.

## Aggregate metrics on paired triplets

| Metric | Truthful (A) | False (B) | No instruction (C) |
|--------|-------------:|----------:|-------------------:|
| success | 12.7% (8/63) | 12.7% (8/63) | 7.9% (5/63) |
| tests_passing | 12.7% (8/63) | 12.7% (8/63) | 7.9% (5/63) |
| compilation_success | 100.0% (63/63) | 100.0% (63/63) | 100.0% (63/63) |
| execution_time_seconds | 139.9 (med 97.3) | 137.5 (med 106.5) | 162.4 (med 123.8) |
| files_modified | 99.7 (med 100.0) | 103.0 (med 103.0) | 1.7 (med 1.0) |
| commands_executed | 17.0 (med 13.0) | 17.3 (med 15.0) | 24.4 (med 21.0) |
| tool_failures | 1.4 (med 1.0) | 1.3 (med 1.0) | 1.4 (med 1.0) |
| token_usage | 11024.8 (med 8635.0) | 10612.7 (med 8998.0) | 11733.6 (med 10351.0) |

## Paired contrasts (primary)

### truthful vs no instruction (A − C)

| Statistic | Value |
|-----------|------:|
| n triplets | 63 |
| n cases | 21 |
| success rate A | 12.7% (8/63) |
| success rate C | 7.9% (5/63) |
| Wilson 95% CI A | [6.6%, 23.1%] |
| Wilson 95% CI C | [3.4%, 17.3%] |
| paired success difference | +4.76 pp |
| bootstrap 95% CI (triplet) | [-6.35, +15.87] pp |
| bootstrap 95% CI (cluster case) | [-12.70, +22.22] pp |
| McNemar exact p | 0.5811 |
| discordant (A only / C only) | 8 / 5 |
| both success / neither | 0 / 50 |
| Cohen's h | 0.1575 |
| execution time diff mean (s) | -22.5 |
| execution time diff bootstrap CI | [-54.1, +8.0] s |
| Cliff's delta (time) | -0.0476 |

### false vs no instruction (B − C)

| Statistic | Value |
|-----------|------:|
| n triplets | 63 |
| n cases | 21 |
| success rate B | 12.7% (8/63) |
| success rate C | 7.9% (5/63) |
| Wilson 95% CI B | [6.6%, 23.1%] |
| Wilson 95% CI C | [3.4%, 17.3%] |
| paired success difference | +4.76 pp |
| bootstrap 95% CI (triplet) | [-6.35, +15.87] pp |
| bootstrap 95% CI (cluster case) | [-12.70, +22.22] pp |
| McNemar exact p | 0.5811 |
| discordant (B only / C only) | 8 / 5 |
| both success / neither | 0 / 50 |
| Cohen's h | 0.1575 |
| execution time diff mean (s) | -24.8 |
| execution time diff bootstrap CI | [-57.9, +8.9] s |
| Cliff's delta (time) | -0.0476 |

### truthful vs false (A − B)

| Statistic | Value |
|-----------|------:|
| n triplets | 63 |
| n cases | 21 |
| success rate A | 12.7% (8/63) |
| success rate B | 12.7% (8/63) |
| Wilson 95% CI A | [6.6%, 23.1%] |
| Wilson 95% CI B | [6.6%, 23.1%] |
| paired success difference | +0.00 pp |
| bootstrap 95% CI (triplet) | [-6.35, +6.35] pp |
| bootstrap 95% CI (cluster case) | [-6.35, +6.35] pp |
| McNemar exact p | 1.0000 |
| discordant (A only / B only) | 2 / 2 |
| both success / neither | 6 / 53 |
| Cohen's h | 0.0000 |
| execution time diff mean (s) | +2.4 |
| execution time diff bootstrap CI | [-21.7, +26.3] s |
| Cliff's delta (time) | -0.0476 |

## Interpretation (conservative)

- **A−B (truth vs false):** paired Δ = +0.00 pp, CI [-6.35, +6.35], McNemar p = 1.0000.
- **A−C (truth vs none):** paired Δ = +4.76 pp, CI [-12.70, +22.22], McNemar p = 0.5811.
- **B−C (false vs none):** paired Δ = +4.76 pp, CI [-12.70, +22.22], McNemar p = 0.5811.

- All three cluster-bootstrap CIs for success difference **include zero**: no statistically reliable paired effect at n=63 triplets / 21 cases.
- **13 cases** have C only (no matching A/B yet); full 35-case ABC analysis requires completing A/B on remaining cases or restricting to overlap.
- High baseline failure rate (~88%) limits power; instruction manipulation may not be the binding constraint on these tasks.
