# RQ5 — Instruction Uptake Analysis

Post-hoc analysis of existing agent traces. No experiment protocol changes.

## Dataset

- Total runs classified: **125** (A=63, B=62)
- Agent(s): claude_code

## Uptake funnel (all runs)

| Stage | Condition A | Condition B |
|---|---:|---:|
| instruction_present | 63 (100.0%) | 62 (100.0%) |
| instruction_read | 63 (100.0%) | 62 (100.0%) |
| instruction_quoted | 63 (100.0%) | 62 (100.0%) |
| instruction_followed | 46 (73.0%) | 48 (77.4%) |
| task_success | 8 (12.7%) | 8 (12.9%) |

## Key questions

### 1. Did the agent actually read the instruction?

- Condition A: **63/63** runs (100.0%) show `instruction_read`.
- Condition B: **62/62** runs (100.0%) show `instruction_read`.
- The instruction file is injected before every run; uptake is near-universal at the read stage.

### 2. Did it act on the manipulated false claim?

- Condition B: **48/62** runs (77.4%) set `false_claim_used` (anchor reference appears in actionable trace events).
- Condition B: **14/62** runs (22.6%) encountered the claim but did not use or correct it (`false_claim_ignored`).

### 3. Are null effects caused by robustness or by non-use?

- Overall success: A=8/63 (12.7%), B=8/62 (12.9%).
- Among runs that **followed** the anchor reference: Δ success (A−B) = -0.014 (A=0.152, B=0.167).
- Among runs that **did not follow** the anchor: Δ success (A−B) = 0.059 (A=0.059, B=0.000).
- Among B runs that **used** the false claim: success rate = 0.167 (n=48).
- Among B runs that **ignored** the false claim: success rate = 0.000 (n=14).
- Interpretation: compare stratified A−B deltas. If effects appear only when `instruction_followed` or `false_claim_used` is true, null overall effects are consistent with **non-use** (decorative instruction) rather than agent robustness.

### 4. Is the instruction file executive or decorative in this experiment?

**Partially executive**: a majority of B runs act on the anchor reference, so the instruction enters the causal path for many tasks.

- Read → follow conversion (B): 77.4% of read runs follow the anchor.
- Follow → success conversion (B): 16.7% of follow runs succeed.

## Stratified A vs B comparison

Compare conditions only within uptake strata (see `rq5_uptake_by_condition.csv`).

| Stratum | Value | n_A | success_A | n_B | success_B | Δ (A−B) |
|---|---|---:|---:|---:|---:|---:|
| all | all | 63 | 0.127 | 62 | 0.129 | -0.002 |
| instruction_read | True | 63 | 0.127 | 62 | 0.129 | -0.002 |
| instruction_quoted | True | 63 | 0.127 | 62 | 0.129 | -0.002 |
| instruction_followed | True | 46 | 0.152 | 48 | 0.167 | -0.014 |
| instruction_followed | False | 17 | 0.059 | 14 | 0.000 | 0.059 |
| false_claim_used | False | 63 | 0.127 | 14 | 0.000 | 0.127 |
| false_claim_ignored | False | 63 | 0.127 | 48 | 0.167 | -0.040 |
| uptake_tier | followed_not_success | 39 | 0.000 | 40 | 0.000 | 0.000 |
| uptake_tier | full_uptake_success | 7 | 1.000 | 8 | 1.000 | 0.000 |
| uptake_tier | read_quoted_not_followed | 17 | 0.059 | 14 | 0.000 | 0.059 |

## Failure reasons (unsuccessful runs)

- Condition A: tests_failed=55
- Condition B: tests_failed=54
