# RQ2 Post-Verification Failure Audit

## Purpose

Validate whether the **121** RQ2 `first_missing` events after at least one
`VERIFIED` observation are genuine reference decay or verification/measurement artifacts.

## Cohort

- Post-verification failures audited: **121**
- Verified-at-least-once cohort (RQ2 denominator): **4521**
- LLM dual-judge enabled: **yes**
- References sent to LLM judges: **1**
- Judge disagreements (unresolved): **0**

## Adjusted decay metrics

- Raw post-verification failures: **121**
- Adjusted genuine post-verification decay: **0**
- Genuine-decay proportion among failures: **0.0%**
  (Wilson 95% CI: 0.0%–3.1%)
- Adjusted decay rate (vs verified cohort): **0.00%**
  (Wilson 95% CI: 0.00%–0.08%)

## Born-false vs post-verification decay ratio

- Born-stale raw cohort: **17747**
- Born-stale adjusted genuine-false: **1405**
- Raw ratio (born-stale raw / post failures): **146.67**
- Adjusted ratio (born genuine-false / post genuine decay): **0.00**
- Bootstrap 95% CI (clustered by repository): **0.00–0.00**

## Taxonomy (deterministic first, dual LLM for ambiguous)

| Letter | Category | Count | % |
|--------|----------|------:|--:|
| A | `genuine_decay` | 0 | 0.0% |
| B | `rename_or_move` | 19 | 15.7% |
| C | `verification_anchor_issue` | 5 | 4.1% |
| D | `extractor_artifact` | 89 | 73.6% |
| E | `normative_or_prescriptive` | 7 | 5.8% |
| F | `external_or_environmental` | 0 | 0.0% |
| G | `ambiguous` | 1 | 0.8% |

## Adjudication status

- **deterministic_medium:** 114 (94.2%)
- **deterministic_high:** 6 (5.0%)
- **llm_inconclusive:** 1 (0.8%)

## Protocol

1. **Deterministic heuristics** reuse born-stale taxonomy with post-verification signals
   (`ever_repaired`, `returned_after_missing`, basename collision at failure commit).
2. **Dual LLM judges** (`deepseek-coder-v2:lite`, `devstral:latest`) only when
   heuristic confidence is insufficient or category is `ambiguous`.
3. **Disagreements** remain `ambiguous`; rows copied to `rq2_failure_audit_disagreements.csv`.

## Limitations

- Does not modify RQ2 survival outputs or prior datasets.
- Snippet context depends on L1/L1b blob availability at first observation commit.
- Genuine decay requires semantic judgment for path moves vs deletions.

## Outputs

- `rq2_failure_audit.csv`
- `rq2_failure_audit_summary.md`
- `rq2_failure_audit_disagreements.csv`
