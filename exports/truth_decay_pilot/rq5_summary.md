# RQ5 — Experimental Preparation Corpus

## Scope

Deterministic preparation layer for future causal agent experiments.
**No LLM runs. No benchmarking. No perturbation synthesis.**

Each row in `rq5_candidate_dataset.csv` is a **natural snapshot** of one
machine-consumable specification (`repo_id`, `instruction_path`) paired with
repository state at a pinned `commit_sha`.

## Corpus size

- Machine-consumable specifications (instruction files): **2,009**
- Candidate snapshot rows: **2,490**

### Snapshots by type

| Snapshot type | Identified | Experiment-eligible |
|---------------|----------:|--------------------:|
| truthful | 770 | 770 |
| born_stale | 1,643 | 590 |
| repaired | 48 | 40 |
| degraded | 29 | 27 |

- Degraded snapshots with paired pre-rot truthful commit: **29**
- P1-sample eligible snapshots: **337**

## Snapshot definitions (natural, observational)

| Type | Selection rule | Protocol mapping |
|------|----------------|------------------|
| **truthful** | Latest commit maximizing verified/verifiable ratio (>0) | Condition A |
| **born_stale** | Earliest commit with verifiable ref never VERIFIED in panel | Condition B (integrity loss at birth) |
| **degraded** | Earliest `VERIFIED→MISSING` transition in panel | Condition B (post-verification loss) |
| **repaired** | Earliest `REPAIRED` state in panel | Post-repair observational stratum |

## Pairing fields

- **Repository state:** `commit_sha`, `task_commit_sha` (identical pin), `blob_sha`
- **Issue availability:** deterministic text/stale-reference heuristics (no GitHub API)
- **Task availability:** verified reference anchors + test-command/path signals in spec text
- **Truthful pair:** `paired_truthful_commit_sha` / `paired_truthful_blob_sha` for B-type snapshots

## Eligibility guardrails

- Requires recoverable L1b instruction blob
- Requires ≥1 verifiable reference at snapshot
- B-type snapshots require issue-availability heuristic pass
- All types require task-availability heuristic pass
- **Build/test smoke check:** not run in this milestone (`build_check_pending` in validation doc)

## Reproducibility

- Inputs: `reference_longitudinal.csv`, L1 events parquet, L1b blobs, P1 `reference_summary.csv`
- IDs: `spec_id = sha256(repo_id|instruction_path)[:16]`,
  `snapshot_id = sha256(spec_id|snapshot_type|commit_sha)[:16]`
- Re-run: `make truth-decay-rq5-prep`

## Outputs

- `rq5_candidate_dataset.csv`
- `rq5_summary.md` (this file)
- `rq5_protocol_validation.md`
