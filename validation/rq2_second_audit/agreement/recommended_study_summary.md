# Recommended RQ2 Human-Validation Study

**Streams retained:** Pepe, Ana (primary independent pair); Rebeca (sensitivity).
**Excluded:** Juan (provisional / non-expert stream).
**Primary frozen labels:** unchanged (0/121).

## Estimators (do not collapse)

| Estimator | x/121 | Wilson 95% CI | Role |
|-----------|------:|---------------|------|
| `primary_frozen` | **0/121** (0.0%) | 0.0–3.1% | Frozen is_genuine_decay |
| `independent_pepe` | **17/121** (14.0%) | 9.0–21.4% | Primary independent stream |
| `independent_ana` | **18/121** (14.9%) | 9.6–22.3% | Primary independent stream (pair) |
| `pepe_ana_both_YES` | **13/121** (10.7%) | 6.4–17.5% | Conservative paired consensus (recommended adjudicated proxy) |
| `pepe_ana_either_YES` | **22/121** (18.2%) | 12.3–26.0% | Liberal paired union |
| `sensitivity_rebeca` | **27/121** (22.3%) | 15.8–30.5% | Independent upper-bound sensitivity stream |
| `decay_favoring_rules` | **25/121** (20.7%) | 14.4–28.7% | Prespecified audit-rule sensitivity |
| `high_specificity_rules` | **0/121** (0.0%) | 0.0–3.1% | Prespecified audit-rule sensitivity |

## Pepe ↔ Ana (primary independent pair)

- Category agreement: **111/121** (0.917); Cohen's κ = **0.866**
- Genuine-decay label agreement: **112/121**
- Binary YES agreement: **112/121** (0.926); κ = **0.699**
- Both YES: **13**; either YES: **22**
- Disagreement rows (category or binary): **10** (binary-only: 9; category: 10)

## Versus frozen primary

- `pepe`: category 19/121 (κ=0.073); binary 104/121; YES=17 (all FP vs primary zero)
- `ana`: category 20/121 (κ=0.080); binary 103/121; YES=18 (all FP vs primary zero)
- `rebeca`: category 24/121 (κ=0.136); binary 94/121; YES=27 (all FP vs primary zero)

## Robust reading

- Independent human YES numerators (Pepe/Ana): **17–18/121**.
- Conservative paired consensus (both YES): **13/121**.
- Rebeca sensitivity upper bound: **27/121**.
- Prespecified rule sensitivity: **0–25/121**.
- Across human + rule scenarios the adjusted numerator spans **0–27/121**, while naive detector-level 121/121 still substantially overstates genuine post-verification decay.
- Formal third-party adjudication of Pepe–Ana disagreements remains optional; the both-YES consensus is the transparent paired proxy used here.

## Outputs

- `recommended_estimators.csv`
- `pepe_ana_consensus_yes.csv`
- `pepe_ana_disagreements.csv` (adjudication worksheet)
