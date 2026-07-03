# RQ5 Redesign Plan — A/B/C with Load-Bearing Strata

**Status:** Experiment paused at partial A/B execution; do not resume A/B-only runs without Condition C.

## Why the current A/B design is insufficient

- Partial results (128 runs, 22 cases) show **near-null aggregate difference**: success A=8/65 vs B=8/63.
- A null A−B result is **uninterpretable** without a no-instruction baseline: we cannot distinguish
  (i) instruction truth having no effect from (ii) agents ignoring instructions entirely.
- Task failure rates are high in both conditions (~87%), suggesting instruction content may not be the binding constraint.
- Without Condition C, observed A≈B could mean false claims are peripheral, not load-bearing.

## How A/B/C fixes the inference problem

| Condition | Treatment | Identifies |
|-----------|-----------|------------|
| **A** | Truthful instruction | Upper bound when agents read and follow docs |
| **B** | Confirmed-false instruction | Cost of false content *given instruction presence* |
| **C** | No instruction / file removed | Baseline without machine-consumed doc |

Primary contrasts:
- **A − C:** effect of providing *any* truthful instruction vs none.
- **B − C:** effect of providing a false instruction vs none.
- **A − B:** effect of instruction *truth* holding presence fixed.

Optional strata (pre-registered, not post-hoc):
- **Load-bearing:** anchor on task-critical path (issue cue + verified-reference task coupling).
- **Peripheral:** stale reference unlikely to bind agent behavior.

Hypothesis ordering:
1. If B≈C and A>C → false instructions ignored; truth matters only via presence.
2. If B<C and A≈B≈C → false claims peripheral.
3. If B<C and A>C → load-bearing false claims impose cost beyond missing instructions.

## Candidate selection (current corpus)

- Total confirmed-false cases: **35**
- Load-bearing stratum: **34**
- Peripheral stratum: **0**
- Unknown stratum: **1**

Load-bearing flags use task/issue availability metadata plus partial trace uptake from completed runs.

## Minimum sample size (pilot guidance)

- Full A/B/C matrix: **35 cases × 3 conditions × 3 replicates × 1 agent(s) = 315 runs**.
- Minimum for stratified pilot (≥12 cases per stratum): **≈414 runs**.
- McNemar / paired bootstrap on A−B requires **≥3 paired replicates** per case (already specified).
- Condition C adds **50% more runs** vs A/B-only design but is required for identifiability.

## Existing runs that can be reused

- **Reusable A/B runs:** 128 ({'A': 65, 'B': 63})
- **Paired A/B replicates:** 63
- **Cases with partial coverage:** 22 / 35
- **Spend to date (partial):** $62.52

Reuse policy:
- Condition **A** and **B** runs in `rq5_results.csv` remain valid under frozen protocol (same commit, task, tests).
- Do **not** discard; mark as `design_version=AB_v1` when merging into A/B/C analysis.
- Condition **C** runs are **entirely new** (instruction file absent).

## New runs required

- **Condition C only (complete current case set):** 105 runs
- **Remaining A/B to finish AB_v1 matrix:** up to 82 runs (if completing all 35 cases before pivot)
- **Recommended pivot:** stop new A/B-only runs; collect **105** Condition C runs + stratified top-up to 12 cases per stratum.

## Implementation status

- Protocol updated: `protocol/RQ5_AGENT_IMPACT_EXPERIMENT_v1.md` (v1.1 A/B/C)
- Runner supports Condition C via instruction file removal (`workspace.py`)
- Default runner conditions remain **A/B only**; C is opt-in via `--conditions A B C`
- Load-bearing flags on `ExperimentCase`: `load_bearing_stratum`, `likely_load_bearing`

## Next steps (manual)

1. Review stratum counts; optionally prune to balanced load-bearing/peripheral panels.
2. Run Condition C only: `rq5-run --conditions C --no-resume` (separate results file recommended).
3. Analyze A−C, B−C, A−B with paired/cluster bootstrap; stratify by load_bearing_stratum.
4. Do not interpret AB_v1 null result as evidence of no effect.
