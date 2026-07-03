# RQ5 v2 Phase 0 Plan Audit

**Status:** Design-only audit (no agent execution)
**Manifest:** `exports/rq5_v2_factorial/factorial_case_manifest.json`
**Protocol:** `docs/RQ5_V2_PROTOCOL.md` v2.1 (Phase 0 = 20 calibration cases, T+L band)

## Verdict

**PASS** — `20` / `20` cases valid for Phase 0 calibration.

| Threshold | Result |
|-----------|--------|
| PASS (≥ 20 valid) | ✓ |
| WARN (12–19 valid) | — |
| FAIL (< 12 valid) | — |

## Summary counts

- **valid_phase0_cases:** 20
- **invalid_cases:** 0
- **reviewer_accept_cases:** 20

### Reasons for invalidity

- (none)

### Ecosystem distribution (all / valid)

- **node:** 8 total, 8 valid
- **other:** 6 total, 6 valid
- **python:** 6 total, 6 valid
- **Cohort balance gate:** PASS — ok

### Repository distribution

- `agentwrapper/agent-orchestrator`: 3 case(s)
- `alphabitcore/nexus-gateway`: 3 case(s)
- `fixmyberlin/tilda-geo`: 2 case(s)
- `vercel/next.js`: 2 case(s)
- `azure/oav`: 2 case(s)
- `microsoft/vscode`: 2 case(s)
- `myriad-dreamin/tinymist`: 1 case(s)
- `astral-sh/ruff`: 1 case(s)
- `langgenius/dify`: 1 case(s)
- `automattic/wp-calypso`: 1 case(s)
- `goldenpotato137/potatovn`: 1 case(s)
- `datadog/dd-trace-js`: 1 case(s)

### Difficulty distribution (`calibrated_expected_success`)

- min: 0.4025
- max: 0.5142
- mean: 0.4746
- in band [0.4, 0.6]: 20/20

### Repairability distribution

- cases with `repairability_score`: 20/20

### Load-bearing role distribution

- `edit`: 20

## Per-case results

| case_id | repo | valid | reviewer | top failure |
|---------|------|-------|----------|-------------|
| `d2578b858cfe326f` | `fixmyberlin/tilda-geo` | True | True | — |
| `3ff980d65c78fd63` | `agentwrapper/agent-orchestrator` | True | True | — |
| `1e1131e99f590b53` | `vercel/next.js` | True | True | — |
| `abced8248ab90fb1` | `fixmyberlin/tilda-geo` | True | True | — |
| `d5303ea5b426c7be` | `agentwrapper/agent-orchestrator` | True | True | — |
| `6aab689b93e84025` | `vercel/next.js` | True | True | — |
| `150fbfaadda24570` | `azure/oav` | True | True | — |
| `ea5545b3e36e5c4b` | `alphabitcore/nexus-gateway` | True | True | — |
| `67c22d7f97cdb50d` | `microsoft/vscode` | True | True | — |
| `9040e7f7272a3e24` | `myriad-dreamin/tinymist` | True | True | — |
| `1bf1e91d4777d875` | `astral-sh/ruff` | True | True | — |
| `fa545f0a92aa171d` | `microsoft/vscode` | True | True | — |
| `1f69fffb4fb41600` | `azure/oav` | True | True | — |
| `4f7981489a817e80` | `agentwrapper/agent-orchestrator` | True | True | — |
| `b929f379e955a660` | `alphabitcore/nexus-gateway` | True | True | — |
| `ba9ebf91f505caac` | `langgenius/dify` | True | True | — |
| `e6e06694f4d15f4f` | `automattic/wp-calypso` | True | True | — |
| `c2e719f548713d54` | `goldenpotato137/potatovn` | True | True | — |
| `5c319b36368735a7` | `datadog/dd-trace-js` | True | True | — |
| `8921c9d4e98fba03` | `alphabitcore/nexus-gateway` | True | True | — |

## Reviewer-facing notes

1. **False-reference construct:** Non-resolving plausible sibling paths per RQ5 v2.1.
2. **Phase 0 scope:** Full 5-cell factorial is planned in infrastructure; Phase 0 execution uses **T+L only** per protocol — this audit validates case *construction* for the full battery.
3. **Success gate:** `calibrated_expected_success` is authoritative; raw `estimated_success_rate` is informational only.
4. **Operational load-bearing gate** (≥ 60% anchor attempt) requires agent runs and is out of scope for this design audit.

