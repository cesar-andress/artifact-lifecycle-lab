# RQ1 Feasibility Study — Truth Decay

## 1. Research question

**RQ1:** How does the truth of machine-consumed documentation evolve over time?

This milestone reconstructs longitudinal reference states from L1/L1b instruction-file events,
verifies references at each commit snapshot, and reports exploratory decay/repair signals.

## 2. Observed signals

- Instruction files analyzed: **2009**
- Longitudinal observations: **339646**
- Median reference observations per file: **14.0**
- Verified ratio: **11.1%**
- Missing ratio: **36.4%**
- Repaired ratio: **0.0%**
- Unverifiable ratio: **51.9%**
- First-failure events: **18473**
- Repair events: **107**
- Files with decay (≥1 missing): **1650**
- Files with repair: **54**
- Median time to first missing reference: **16.0 days**
- Median repair latency: **12.2 days**

### Top transitions

- `UNVERIFIABLE->UNVERIFIABLE`: 126128
- `MISSING->MISSING`: 101565
- `INIT->UNVERIFIABLE`: 41110
- `VERIFIED->VERIFIED`: 31669
- `INIT->MISSING`: 18335
- `INIT->VERIFIED`: 4603
- `UNVERIFIABLE->DELETED`: 1418
- `DELETED->UNVERIFIABLE`: 1166

### Figures

- figure_a: `exports/truth_decay_pilot/figure_a_reference_density.pdf`
- figure_b: `exports/truth_decay_pilot/figure_b_verified_vs_missing_by_age.pdf`
- figure_c: `exports/truth_decay_pilot/figure_c_repair_latency.pdf`
- figure_d: `exports/truth_decay_pilot/figure_d_state_transitions.pdf`

## 3. Unexpected observations

- Majority of observations are UNVERIFIABLE (mostly commands); verifiable decay is concentrated in path-like references.

## 4. Threats to validity

- Mechanical verification ≠ semantic truth; UNVERIFIABLE commands dominate many files.
- Cohort is pilot + E1-100 engineering frame, not E1-1000 scientific strata.
- Reference extraction recall is regex-bound; false MISSING may reflect extraction noise.
- Repair detection requires a prior MISSING at the same reference key; repo-side fixes without instruction edits are invisible.
- Commit-time tree checks depend on ephemeral bare clones and L1 event completeness.

## 5. Can RQ1 support a TOSEM paper?

**Answer: YES**

Longitudinal panel shows measurable decay (missing references over time), non-trivial repair events, and sufficient file/observation density across the cohort.
