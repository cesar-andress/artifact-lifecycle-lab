# RQ5 Protocol Validation — Preparation Milestone

**Protocol:** `protocol/RQ5_AGENT_IMPACT_EXPERIMENT_v1.md`
**Milestone status:** Preparation only — case manifest generation, no agent execution

## Checklist vs frozen protocol

| Requirement | Status | Evidence |
|-------------|--------|----------|
| No artificial rot | PASS | All B-type snapshots use historical blobs at natural commits |
| Observed rot source | PASS | Degraded snapshots from `VERIFIED→MISSING` in longitudinal panel |
| Condition A truthful blob | PASS | `truthful` snapshots + `paired_truthful_*` for degraded |
| Condition B observed-rot blob | PASS | `born_stale` / `degraded` snapshots at integrity-loss commits |
| Fixed task context (design) | PARTIAL | `task_commit_sha` pinned; task prompt/rubric not implemented |
| Instruction text recoverable | PASS | 1427/1427 eligible rows |
| Verifiable rot reference | PASS | 27 eligible degraded snapshots |
| Repository build/test smoke | PENDING | Not executed — clone+test harness absent |
| Agent runs | N/A | Explicitly out of scope |
| Trace logging | N/A | Future implementation |

## Kill criteria (pre-flight)

| Criterion | Threshold | Current | Pass |
|-----------|-----------|---------|------|
| Valid observed-rot cases | ≥10 | 27 | YES |
| P1∩degraded eligible | ≥10 (pilot target) | 10 | YES |
| Truthful eligible specs | ≥10 | 770 | YES |

## Threats to validity (preparation)

1. **Issue availability proxy** — text-pattern heuristics, not live GitHub Issues API.
2. **Task availability proxy** — no compile/test execution; verified-reference anchors only.
3. **Born-stale vs degraded** — distinct snapshot types; do not merge in causal analysis.
4. **Mechanical VERIFIED** — tree membership, not semantic correctness.
5. **Pilot selection** — P1 sample is judgment sample; cluster by `repo_id` in analysis.
6. **Build gate absent** — eligible ≠ runnable until smoke checks implemented.

## Recommended pilot draw (deterministic)

1. Filter `experimental_eligible=true` AND `snapshot_type=degraded`.
2. Restrict to `p1_sample=true`.
3. Sort by `snapshot_id` ascending; take first 20–30 rows.
4. Join truthful snapshot for same `spec_id` (Condition A) via paired fields.
5. Record `build_check_pending` until CI harness lands.

## Corpus statistics

- Specifications in panel: 2,009
- Total snapshot rows: 2,490
- Experiment-eligible rows: 1,427
