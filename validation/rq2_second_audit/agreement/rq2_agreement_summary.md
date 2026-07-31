# RQ2 Independent Human Audit — Agreement Results

Primary frozen labels remain unchanged. Auditor files were not modified.

## Four estimators (binary YES counts as genuine decay)

| Estimator | Numerator / 121 | Notes |
|-----------|----------------:|-------|
| Original frozen (primary) | **0/121** | `is_genuine_decay` |
| Independent `ana` | **18/121** (14.9%; Wilson 9.6–22.3%) | NO=103, IE=0 |
| Independent `pepe` | **17/121** (14.0%; Wilson 9.0–21.4%) | NO=104, IE=0 |
| Independent `rebeca` | **27/121** (22.3%; Wilson 15.8–30.5%) | NO=94, IE=0 |
| Adjudicated | — | pending completed adjudication |
| Decay-favoring sensitivity | **25/121** | prespecified scenario |

## Agreement vs primary

### Auditor `ana`

- Raw category agreement: **20/121** (0.165)
- Cohen's κ (categories): **0.080**
- Binary agreement (YES vs not-YES): **103/121** (0.851); TP=0 TN=103 FP=18 FN=0
- Positive agreement: **0.0**
- Negative agreement: **0.920**
- Headline-changing disagreements (binary): **18** (all are primary=False → auditor YES or mapped)
- Confidence-stratified category agreement:
  - High: 9/89
  - Medium: 11/32
- Category mix: {'verification_anchor_issue': 41, 'rename_or_move': 60, 'genuine_decay': 18, 'normative_or_prescriptive': 2}

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

### Auditor `rebeca`

- Raw category agreement: **24/121** (0.198)
- Cohen's κ (categories): **0.136**
- Binary agreement (YES vs not-YES): **94/121** (0.777); TP=0 TN=94 FP=27 FN=0
- Positive agreement: **0.0**
- Negative agreement: **0.874**
- Headline-changing disagreements (binary): **27** (all are primary=False → auditor YES or mapped)
- Confidence-stratified category agreement:
  - High: 15/102
  - Medium: 9/19
- Category mix: {'rename_or_move': 42, 'verification_anchor_issue': 51, 'genuine_decay': 27, 'external_or_environmental': 1}

## Inter-auditor agreement

- `ana_vs_pepe`: category 111/121; genuine_decay raw 112/121; binary-mapped 112/121; κ(category)=0.866
- `ana_vs_rebeca`: category 87/121; genuine_decay raw 110/121; binary-mapped 110/121; κ(category)=0.569
- `pepe_vs_rebeca`: category 88/121; genuine_decay raw 111/121; binary-mapped 111/121; κ(category)=0.578

## Interpretation notes

- κ alone is not validity evidence; interpret with prevalence and binary estimand.
- `INSUFFICIENT_EVIDENCE` is treated as **not** counting in the YES numerator (mapped to False for binary agreement with primary).
- If an auditor is non-expert / incomplete evidence review, treat their stream as provisional and invite revision before adjudication.
