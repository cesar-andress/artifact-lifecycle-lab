# RQ5 — Null-Result Mediation Audit

Post-hoc trace audit only. Does not modify the experiment, agents, or datasets.

## Scope

- Runs audited: **128** (A=65, B=63)
- Overall success: A=8/65 (12.3%), B=8/63 (12.7%), Δ(A−B)=-0.004

## B-condition mediation funnel

| Stage | Count | Share of B runs |
|---|---:|---:|
| false_claim_present_in_instruction | 63 | 100.0% |
| false_claim_read | 63 | 100.0% |
| false_claim_quoted_or_referenced | 63 | 100.0% |
| false_claim_used_in_tool_call | 49 | 77.8% |
| false_claim_encountered_as_obstacle | 17 | 27.0% |
| false_claim_corrected_by_agent | 5 | 7.9% |
| task_failed_because_of_false_claim | 12 | 19.0% |
| task_succeeded_despite_false_claim | 8 | 12.7% |

## Causal roles (B)

| causal_role | count | frequency | success_rate |
|---|---:|---:|---:|
| false_claim_caused_failure | 12 | 0.190 | 0.000 |
| false_claim_irrelevant_to_failure | 27 | 0.429 | 0.000 |
| obstacle_recovered | 5 | 0.079 | 0.600 |
| uptake_but_not_load_bearing | 19 | 0.302 | 0.263 |

## Comparable reference usage (A)

| causal_role | count | frequency | success_rate |
|---|---:|---:|---:|
| reference_used_and_succeeded | 7 | 0.108 | 1.000 |
| reference_used_and_failed | 40 | 0.615 | 0.000 |
| reference_ignored_after_reading | 18 | 0.277 | 0.056 |

## Audit questions

### 1. How often does the false claim enter the causal path?

- Used in a tool call or followed as an actionable reference: **49/63** (77.8%).
- Broader path entry (used or obstacle after use): **49/63** (77.8%).

### 2. How often is it load-bearing for the task?

- Runs classified as load-bearing (obstacle/recovery/failure roles): **17/63** (27.0%).
- Not load-bearing (read/referenced but not used, or failure unrelated): **46/63** (73.0%).

### 3. How often does the agent recover from it?

- `obstacle_recovered`: **5/63** (7.9%).
- `task_succeeded_despite_false_claim`: **8/63** (12.7%).

### 4. How often does it directly cause failure?

- `false_claim_caused_failure`: **12/63** (19.0%).
- `task_failed_because_of_false_claim` (heuristic): **12/63** (19.0%).
- `obstacle_unrecovered`: **0/63** (0.0%).

### 5. Does the null success effect reflect robustness or irrelevance?

**Primarily irrelevance / low load-bearingness, not robustness.** Most B runs do act on the false claim, yet A and B success rates remain similar. Failures are dominated by cases where the false claim is used but not the identified proximal cause (`false_claim_irrelevant_to_failure`, `uptake_but_not_load_bearing`), or by shared task difficulty when following the anchor.

Heuristic limits: obstacle and correction detection rely on trace substrings and event order; `ambiguous` runs should be interpreted cautiously.

- B `ambiguous`: 0
- B `no_uptake`: 0
