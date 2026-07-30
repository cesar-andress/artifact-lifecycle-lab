# RQ5 — Instruction Uptake Analysis

Post-hoc analysis of existing agent traces. No experiment protocol changes.

## Dataset

- Total runs classified: **128** (A=65, B=63)
- Agent(s): claude_code

## Uptake funnel (all runs)

| Stage | Condition A | Condition B |
|---|---:|---:|
| instruction_present | 65 (100.0%) | 63 (100.0%) |
| instruction_read | 65 (100.0%) | 63 (100.0%) |
| instruction_quoted | 65 (100.0%) | 63 (100.0%) |
| instruction_followed | 47 (72.3%) | 49 (77.8%) |
| task_success | 8 (12.3%) | 8 (12.7%) |

## Key questions

### 1. Did the agent actually read the instruction?

- Condition A: **65/65** runs (100.0%) show `instruction_read`.
- Condition B: **63/63** runs (100.0%) show `instruction_read`.
- The instruction file is injected before every run; uptake is near-universal at the read stage.

### 2. Did it act on the manipulated false claim?

- Condition B: **49/63** runs (77.8%) set `false_claim_used` (anchor reference appears in actionable trace events).
- Condition B: **14/63** runs (22.2%) encountered the claim but did not use or correct it (`false_claim_ignored`).

### 3. Are null effects caused by robustness or by non-use?

- Overall success: A=8/65 (12.3%), B=8/63 (12.7%).
- Among runs that **followed** the anchor reference: Δ success (A−B) = -0.014 (A=0.149, B=0.163).
- Among runs that **did not follow** the anchor: Δ success (A−B) = 0.056 (A=0.056, B=0.000).
- Among B runs that **used** the false claim: success rate = 0.163 (n=49).
- Among B runs that **ignored** the false claim: success rate = 0.000 (n=14).
- Interpretation: compare stratified A−B deltas. If effects appear only when `instruction_followed` or `false_claim_used` is true, null overall effects are consistent with **non-use** (decorative instruction) rather than agent robustness.

### 4. Is the instruction file executive or decorative in this experiment?

**Partially executive**: a majority of B runs act on the anchor reference, so the instruction enters the causal path for many tasks.

- Read → follow conversion (B): 77.8% of read runs follow the anchor.
- Follow → success conversion (B): 16.3% of follow runs succeed.

## Stratified A vs B comparison

Compare conditions only within uptake strata (see `rq5_uptake_by_condition.csv`).

| Stratum | Value | n_A | success_A | n_B | success_B | Δ (A−B) |
|---|---|---:|---:|---:|---:|---:|
| all | all | 65 | 0.123 | 63 | 0.127 | -0.004 |
| instruction_read | True | 65 | 0.123 | 63 | 0.127 | -0.004 |
| instruction_quoted | True | 65 | 0.123 | 63 | 0.127 | -0.004 |
| instruction_followed | True | 47 | 0.149 | 49 | 0.163 | -0.014 |
| instruction_followed | False | 18 | 0.056 | 14 | 0.000 | 0.056 |
| false_claim_used | False | 65 | 0.123 | 14 | 0.000 | 0.123 |
| false_claim_ignored | False | 65 | 0.123 | 49 | 0.163 | -0.040 |
| uptake_tier | followed_not_success | 40 | 0.000 | 41 | 0.000 | 0.000 |
| uptake_tier | full_uptake_success | 7 | 1.000 | 8 | 1.000 | 0.000 |
| uptake_tier | read_quoted_not_followed | 18 | 0.056 | 14 | 0.000 | 0.056 |

## Failure reasons (unsuccessful runs)

- Condition A: tests_failed=57
- Condition B: tests_failed=55
