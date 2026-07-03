# Paper Synthesis Exports

Frozen evidentiary summaries for the late-binding model paper narrative. **No agent reruns** and **no modification** of upstream RQ1–RQ5 export directories.

## Contents

| File | Description |
|------|-------------|
| [`late_binding_evidence_table.csv`](late_binding_evidence_table.csv) | Claim → source → metric → value → limitation mapping |
| [`../docs/LATE_BINDING_MODEL_v1.md`](../docs/LATE_BINDING_MODEL_v1.md) | Full conceptual synthesis (directive/referential channels, DAG, threats, implications) |

## Primary upstream sources (read-only)

- `exports/truth_decay_pilot/` — RQ1–RQ4, born-stale, GFC, RQ2 failure, cited–uncited audits
- `exports/truth_pilot/p4_validation.md` — agent maintenance attribution validation
- `exports/rq5_agent_impact/` — A/B partial runs, uptake, mediation, ABC comparative analysis
- `exports/rq5_agent_impact_c/` — Condition C (no instruction) complete runs
- `protocol/RQ5_AGENT_IMPACT_EXPERIMENT_v1.md` — A/B/C redesign protocol

## Usage

1. Cite rows in `late_binding_evidence_table.csv` for reviewer-facing numeric claims.
2. Use `docs/LATE_BINDING_MODEL_v1.md` for narrative structure and construct definitions.
3. Do **not** treat observational prevalence rates (born-stale) as causal effect sizes from RQ5.

## Regeneration

This folder is **hand-curated synthesis**, not pipeline output. Update only when new frozen evidence is committed elsewhere; do not rerun agents from this directory.
