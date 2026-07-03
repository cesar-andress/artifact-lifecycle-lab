# RQ5 v2 Phase 0 Plan Audit

**Status:** Design-only audit (no agent execution)
**Manifest:** `exports/rq5_v2_factorial/factorial_case_manifest.json`
**Protocol:** `docs/RQ5_V2_PROTOCOL.md` v2.1 (Phase 0 = 20 calibration cases, T+L band)

## Verdict

**FAIL** — `0` / `20` cases valid for Phase 0 calibration.

| Threshold | Result |
|-----------|--------|
| PASS (≥ 20 valid) | ✗ |
| WARN (12–19 valid) | — |
| FAIL (< 12 valid) | ✓ |

## Summary counts

- **valid_phase0_cases:** 0
- **invalid_cases:** 20
- **reviewer_accept_cases:** 0

### Reasons for invalidity

- `false_anchor_plausible`: 20 case(s)
- `estimated_success_rate_in_band`: 20 case(s)
- `repairability_score_present`: 20 case(s)
- `decoy_resolves`: 5 case(s)
- `all_cells_feasible`: 5 case(s)
- `not_duplicated_repo_path`: 2 case(s)
- `lb_by_construction`: 1 case(s)

### Ecosystem distribution (all / valid)

- **python:** 9 total, 0 valid
- **node:** 8 total, 0 valid
- **other:** 3 total, 0 valid
- **Cohort balance gate:** PASS — ok

### Repository distribution

- `alphabitcore/nexus-gateway`: 3 case(s)
- `datadog/dd-trace-js`: 3 case(s)
- `microsoft/vscode`: 3 case(s)
- `automattic/wp-calypso`: 2 case(s)
- `fixmyberlin/tilda-geo`: 2 case(s)
- `1password/scam`: 1 case(s)
- `agents2agentsai/ata`: 1 case(s)
- `agentwrapper/agent-orchestrator`: 1 case(s)
- `all-hands-ai/openhands`: 1 case(s)
- `azure/oav`: 1 case(s)
- `goldenpotato137/potatovn`: 1 case(s)
- `langgenius/dify`: 1 case(s)

### Difficulty distribution (`calibrated_expected_success`)

- min: 0.4242
- max: 0.5995
- mean: 0.5017
- in band [0.4, 0.6]: 20/20

### Repairability distribution

- cases with `repairability_score`: 0/20

### Load-bearing role distribution

- `edit`: 20

## Per-case results

| case_id | repo | valid | reviewer | top failure |
|---------|------|-------|----------|-------------|
| `99b797ea6a6deac7` | `1password/scam` | False | False | false_anchor_plausible |
| `944220ccb9aadf46` | `agents2agentsai/ata` | False | False | false_anchor_plausible |
| `3ff980d65c78fd63` | `agentwrapper/agent-orchestrator` | False | False | false_anchor_plausible |
| `96808285059cf23c` | `all-hands-ai/openhands` | False | False | false_anchor_plausible |
| `6258a18544a5225c` | `alphabitcore/nexus-gateway` | False | False | false_anchor_plausible |
| `b929f379e955a660` | `alphabitcore/nexus-gateway` | False | False | false_anchor_plausible |
| `ea5545b3e36e5c4b` | `alphabitcore/nexus-gateway` | False | False | false_anchor_plausible |
| `e6e06694f4d15f4f` | `automattic/wp-calypso` | False | False | false_anchor_plausible |
| `4419c0ae8c4ef36f` | `automattic/wp-calypso` | False | False | false_anchor_plausible |
| `1f69fffb4fb41600` | `azure/oav` | False | False | false_anchor_plausible |
| `95030e45b4415001` | `datadog/dd-trace-js` | False | False | false_anchor_plausible |
| `5582c9ab02a349f0` | `datadog/dd-trace-js` | False | False | false_anchor_plausible |
| `5c319b36368735a7` | `datadog/dd-trace-js` | False | False | false_anchor_plausible |
| `abced8248ab90fb1` | `fixmyberlin/tilda-geo` | False | False | false_anchor_plausible |
| `d2578b858cfe326f` | `fixmyberlin/tilda-geo` | False | False | false_anchor_plausible |
| `c2e719f548713d54` | `goldenpotato137/potatovn` | False | False | false_anchor_plausible |
| `4f4de58388a20bee` | `langgenius/dify` | False | False | false_anchor_plausible |
| `81d53fc9366a97dd` | `microsoft/vscode` | False | False | false_anchor_plausible |
| `e435bdab8fbfa2e2` | `microsoft/vscode` | False | False | false_anchor_plausible |
| `8e4537290b0d3085` | `microsoft/vscode` | False | False | false_anchor_plausible |

## Reviewer-facing notes

1. **False-reference construct:** Cases using `_*.missing` suffix fail RQ5 v2.1 narrow definition (non-resolving *plausible* sibling path).
2. **Phase 0 scope:** Full 5-cell factorial is planned in infrastructure; Phase 0 execution uses **T+L only** per protocol — this audit validates case *construction* for the full battery.
3. **repairability_score:** Not present in current calibration pipeline; all cases fail criterion 10 until the field is added to `difficulty_scores.csv`.
4. **Operational load-bearing gate** (≥ 60% anchor attempt) requires agent runs and is out of scope for this design audit.

