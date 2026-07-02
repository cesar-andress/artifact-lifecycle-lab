# RQ5 Causal Experiment Infrastructure

**Status:** Implemented — agent execution harness and analysis pipeline  
**Protocol:** `protocol/RQ5_AGENT_IMPACT_EXPERIMENT_v1.md`  
**Preparation inputs (read-only):** `exports/truth_decay_pilot/rq5_candidate_dataset.csv`, `exports/truth_decay_pilot/gfc_confirmatory_audit.csv`

## Objective

Measure the practical impact of **confirmed false** machine-consumed instructions on software agents using a controlled A/B design:

| Condition | Instruction file | Repository state |
|-----------|------------------|------------------|
| **A** | Truthful natural blob (`paired_truthful_blob_sha`) | Pinned at `task_commit_sha` |
| **B** | Confirmed-false natural blob (`blob_sha` from born-stale snapshot) | Same commit, same task |

No synthetic perturbations. Only historically observed instruction snapshots.

## Commands

```bash
# Preparation corpus (unchanged)
make truth-decay-rq5-prep

# Causal experiment (stub agent, local workspaces — default for CI)
make truth-decay-rq5

# Full git workspaces + optional test execution
python -m artifact_lab.experiments.truth_decay rq5 \
  --use-git-workspaces \
  --run-tests \
  --agents stub
```

## Case selection

Deterministic filter on `rq5_candidate_dataset.csv`:

1. `experimental_eligible=true`
2. `snapshot_type=born_stale`
3. `paired_truthful_blob_sha` present
4. Anchor reference appears in `gfc_confirmatory_audit.csv` with `is_confirmed_false=true`
5. Sort by `(spec_id, snapshot_id)`; optional `--max-cases`, `--require-p1`

## Agent interface

Vendor-neutral protocol: `artifact_lab.experiments.truth_decay.rq5_experiment.agents.base.AgentRunner`

Register additional agents in `agents/registry.py`. All runs are wrapped by `RecordingAgent` and emit JSONL traces under `exports/rq5_agent_impact/traces/`.

## Outputs

Written to `exports/rq5_agent_impact/` (does not overwrite preparation artifacts in `exports/truth_decay_pilot/`):

| File | Content |
|------|---------|
| `rq5_dataset.csv` | Run-level outcomes |
| `rq5_summary.md` | Design and descriptive aggregates |
| `rq5_effect_sizes.csv` | Success contrasts, bootstrap CIs, Cohen's h |
| `rq5_trace_statistics.csv` | Trace-coded behavior rates |
| `rq5_case_manifest.csv` | Selected experimental units |
| `figure_success_rate.pdf` | Success by condition |
| `figure_failure_modes.pdf` | Failure mode counts |
| `figure_trace_flow.pdf` | Trace behavior by condition |

## Reproducibility

- Fixed case ordering and IDs (`stable_case_id`)
- Deterministic stub agent for infrastructure tests
- Bootstrap CIs with fixed seed (default 42)
- Git worktree isolation per run when `--use-git-workspaces` is enabled

## Tests

```bash
pytest artifact_lab/tests/test_rq5_experiment.py -q
```
