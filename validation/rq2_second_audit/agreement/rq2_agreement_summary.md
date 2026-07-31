# RQ2 Independent Human Audit — Agreement Results

Primary frozen labels remain unchanged. Auditor files were not modified.

## Four estimators (binary YES counts as genuine decay)

| Estimator | Numerator / 121 | Notes |
|-----------|----------------:|-------|
| Original frozen (primary) | **0/121** | `is_genuine_decay` |
| Independent `juan` | **0/121** (0.0%; Wilson 0.0–3.1%) | NO=76, IE=45 |
| Independent `pepe` | **17/121** (14.0%; Wilson 9.0–21.4%) | NO=104, IE=0 |
| Adjudicated | — | pending completed adjudication |
| Decay-favoring sensitivity | **25/121** | prespecified scenario |

## Agreement vs primary

### Auditor `juan`

- Raw category agreement: **27/121** (0.223)
- Cohen's κ (categories): **0.178**
- Binary agreement (YES vs not-YES): **121/121** (1.000); TP=0 TN=121 FP=0 FN=0
- Positive agreement: **nan**
- Negative agreement: **1.000**
- Headline-changing disagreements (binary): **0** (all are primary=False → auditor YES or mapped)
- Confidence-stratified category agreement:
  - Low: 1/45
  - Medium: 26/76
- Category mix: {'rename_or_move': 19, 'normative_or_prescriptive': 18, 'ambiguous': 45, 'verification_anchor_issue': 38, 'extractor_artifact': 1}

### Auditor `pepe`

- Raw category agreement: **19/121** (0.157)
- Cohen's κ (categories): **0.073**
- Binary agreement (YES vs not-YES): **104/121** (0.860); TP=0 TN=104 FP=17 FN=0
- Positive agreement: **0.0**
- Negative agreement: **0.924**
- Headline-changing disagreements (binary): **17** (all are primary=False → auditor YES or mapped)
- Confidence-stratified category agreement:
  - High: 15/106
  - Low: 0/1
  - Medium: 4/14
- Category mix: {'verification_anchor_issue': 45, 'rename_or_move': 58, 'genuine_decay': 17, 'ambiguous': 1}

## Inter-auditor agreement

- `juan_vs_pepe`: category 43/121; genuine_decay raw 74/121; binary-mapped 104/121; κ(category)=0.199

## Interpretation notes

- κ alone is not validity evidence; interpret with prevalence and binary estimand.
- `INSUFFICIENT_EVIDENCE` is treated as **not** counting in the YES numerator (mapped to False for binary agreement with primary).
- If an auditor is non-expert / incomplete evidence review, treat their stream as provisional and invite revision before adjudication.
