# Paper Synthesis Exports

**Mode:** Paper-writing — agent experiments frozen.

Evidentiary summaries for the ACM TOSEM submission *Late Binding in Machine-Consumed Instruction Files*.

## Contents

| File | Description |
|------|-------------|
| [`late_binding_evidence_table.csv`](late_binding_evidence_table.csv) | Claim → source → metric → value → limitation |
| [`../docs/LATE_BINDING_MODEL_v1.md`](../docs/LATE_BINDING_MODEL_v1.md) | Conceptual model synthesis |
| [`../../paper/README.md`](../../paper/README.md) | LaTeX skeleton |

## Rules

1. Every numeric claim in `paper/` must trace to a row in `late_binding_evidence_table.csv`.
2. Do not rerun agents during paper iteration.
3. Do not modify upstream RQ export directories; cite paths as read-only.

## Primary upstream sources

- `exports/truth_decay_pilot/` — RQ1–RQ4, audits
- `exports/truth_pilot/p4_validation.md` — P4 attribution
- `exports/rq5_agent_impact/` — A/B partial, uptake, ABC analysis
- `exports/rq5_agent_impact_c/` — Condition C complete (105 runs)
