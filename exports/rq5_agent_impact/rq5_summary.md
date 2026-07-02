# RQ5 — Causal Agent Impact Experiment

## Design

- **Condition A:** repository pinned at `task_commit_sha` with truthful instruction blob.
- **Condition B:** same repository, same commit, same task; instruction blob swapped to
  naturally occurring confirmed-false snapshot (no synthetic perturbation).
- **Cases:** drawn deterministically from `rq5_candidate_dataset.csv` joined with
  `gfc_confirmatory_audit.csv` (`is_confirmed_false=true`).

## Execution

- Selected cases: **35**
- Agents: **stub**
- Replicates per (case × condition × agent): **1**
- Total runs recorded: **70** (A=35, B=35)
- Objective test execution: **disabled**
- Git workspaces: **disabled (local stub mode)**

## Outputs

- `rq5_dataset.csv` — run-level outcomes
- `rq5_effect_sizes.csv` — paired success contrasts and bootstrap CIs
- `rq5_trace_statistics.csv` — trace-coded behavior rates
- `rq5_case_manifest.csv` — selected experimental units
- `traces/` — JSONL interaction traces per run
- `figure_success_rate.pdf`, `figure_failure_modes.pdf`, `figure_trace_flow.pdf`

## Descriptive aggregates (no interpretation)

- Agent `stub_agent_v1`: success rate A=1.000, B=0.000, paired Δ=1.000 (bootstrap CI 1.000–1.000), Cohen's h=3.142

## Trace statistics rows

- Total trace statistic rows: **15**
