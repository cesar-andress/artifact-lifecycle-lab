# RQ2 Audit-Rule Sensitivity Summary
Scenarios were locked in `docs/VALIDATION_EXTENSION_PROTOCOL.md` before aggregates were computed.
## Scenario estimates
| Scenario | Estimate | Wilson 95% CI | Available |
|----------|---------:|---------------|-----------|
| `primary_frozen` | 0/121 (0.00%) | 0.00–3.08% | yes |
| `decay_favoring` | 25/121 (20.66%) | 14.40–28.72% | yes |
| `high_specificity` | 0/121 (0.00%) | 0.00–3.08% | yes |
| `second_auditor` | — | — | no |
| `adjudicated` | — | — | no |

## Robust range (available scenarios)
- Minimum numerator: **0/121**
- Maximum numerator: **25/121**
- Primary frozen estimate remains **0/121**; sensitivity does not replace it.

## Case changes vs primary
- Total changed case-rows across scenarios: **25**
- `decay_favoring`: 25 events reclassified relative to primary

## Interpretation guardrail
If any available scenario is non-zero, report it plainly. The robust claim is the range across prespecified scenarios, not the literal zero alone.

**Note:** `second_auditor` and `adjudicated` scenarios await real human labels; they were not simulated.
