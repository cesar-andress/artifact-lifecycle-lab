# Task Difficulty Calibration

Pre-inclusion scoring pipeline for RQ5 v2. **No agent runs.**

- Candidates scored: **1524**
- Historical training cases (RQ5 v1): **22**
- v1 observed mean success: **12.1%** (too low; target 40–60%)
- Calibrated mean expected success (all): **54.2%**
- Mean in target band: **50.7%** (n=649)

## Inclusion tiers

| Tier | Count | Definition |
|------|------:|------------|
| target_band | 649 | Expected success ∈ [0.40, 0.60] |
| too_hard | 237 | Expected success < 0.40 |
| too_easy | 638 | Expected success > 0.60 |

## Scoring dimensions (0 = easy, 1 = hard)

1. **Compilation complexity** — build toolchain, monorepo, scoped packages
2. **Edited files estimate** — role, path type, v1 median files modified
3. **Test complexity** — test command tier, e2e paths, monorepo tests
4. **Dependency depth** — path depth, dependency anchors
5. **Historical failures** — case/spec/repo success from RQ5 v1 pilot

## Calibrator

- Weights: `(0.22, 0.18, 0.24, 0.16, 0.2)`
- Logistic intercept: **3.935**
- Logistic slope: **8.000**
- Training Brier score: **0.0370** (n=22)

## Outputs

- `exports/task_calibration/difficulty_scores.csv`
- `exports/task_calibration/difficulty_distribution.pdf`

Use `calibration_tier == target_band` rows for Phase 0 calibration pilot.
