# TOSEM Go/No-Go — Half-Life of Truth

**Overall recommendation:** **GO**

## P1 — Reference density

- Files sampled: **400**
- Files with ≥1 verifiable reference: **72.0%**
- Median verifiable references per file: **3.0**
- Extraction failures: **0**
- Density sufficient for truth-decay study? **Yes**

### RQs supported by P1
- **RQ_truth_decay:** Do machine-consumed instruction files encode verifiable claims that go stale?
- **RQ_reference_half_life:** What fraction of path/directory/script/dependency references fail at HEAD?

### RQs to drop or defer (P1)
- Adoption prevalence at ecosystem scale (original E1 census) — defer unless reframed as covariate.
- Semantic truth / LLM-judged correctness — not validated here; defer to L5.

## P2 — Agent attribution

- Commits scanned: **11187**
- Candidate agent-authored: **1210**
- Candidate agent-co-authored: **1606**
- Signal rate: **25.2%**
- Files with agent signal: **989** (30.4%)
- Attribution sufficient for self-maintenance RQ? **Yes**

### RQs supported by P2
- **RQ_self_maintenance:** Are instruction-file changes disproportionately agent-co-authored?
- **RQ_agent_vs_human_decay:** Do agent-maintained files show different reference staleness?

### RQs to drop or defer (P2)
- Binary agent/human without attribution metadata — signal too weak alone.

## Recommended next step
1. Design longitudinal protocol: resample instruction files at T+Δ, remeasure reference verification.
2. Join P1 audit rows with P2 attribution on (repo_id, instruction_path).
3. Keep E1-1000 frozen; extend only via targeted re-extraction for longitudinal panel.
