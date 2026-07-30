# RQ5 v2 — Factorial Experiment Protocol (Implementation)

**Version:** `RQ5_FACTORIAL_v1.0`  
**Status:** Infrastructure implemented; **no agent execution** until explicitly enabled  
**Code:** `artifact_lab/experiments/rq5_v2/`  
**Design reference:** `docs/RQ5_V2_PROTOCOL.md`  
**Date:** 2026-07-03

---

## 1. Purpose

This document specifies the **implemented** factorial design for RQ5 v2 causal agent experiments. It maps experimental factors to code artifacts, run identifiers, and analysis fields.

v1 pilot success (~12%) was too low for causal inference. Case selection uses the **task calibration pipeline** (`exports/task_calibration/`) to prefer tasks with expected success ∈ [40%, 60%].

---

## 2. Experimental factors

### Factor A — Instruction presence

| Level | Code value | Workspace treatment |
|-------|------------|---------------------|
| **Present** | `present` | Inject frozen instruction blob at `instruction_path` |
| **Absent** | `absent` | Remove `instruction_path` from workspace (cell `N`) |

**Hypothesis:** H1 (instructions modify behaviour vs. absence)

### Factor B — Referential truth (when A = present)

| Level | Code value | Instruction content |
|-------|------------|---------------------|
| **Truthful** | `truthful` | Cited anchor path **exists** at pinned commit |
| **False** | `false` | Cited anchor path **does not exist** at commit |

**Hypothesis:** H2, H4 (truth effects; interaction with load-bearing)

When A = absent, B = `na`.

### Factor C — Load-bearing (when A = present)

| Level | Code value | Task + instruction coupling |
|-------|------------|-------------------------------|
| **Yes** | `yes` | Task requires editing the cited anchor (cells `T+L`, `F+L`) |
| **No** | `no` | Task requires editing **decoy path** only; anchor in Related files (cells `T+P`, `F+P`) |

**Hypothesis:** H2, H3, H4

When A = absent, C = `na`.

---

## 3. Within-case cells

Each **case** contributes five cells:

| Cell | A | B | C | Description |
|------|---|---|---|-------------|
| `T+L` | present | truthful | yes | True anchor, load-bearing |
| `F+L` | present | false | yes | False anchor, load-bearing |
| `T+P` | present | truthful | no | True anchor, peripheral |
| `F+P` | present | false | no | False anchor, peripheral |
| `N` | absent | — | — | No instruction file |

Implementation: `artifact_lab/experiments/rq5_v2/factors.py` (`CellCode`, `FactorLevels`).

---

## 4. Agent platforms

| Agent ID | CLI | Module |
|----------|-----|--------|
| `claude_code` | `claude` | `agents/registry.py` → `ClaudeCodeAgent` |
| `codex` | `codex` | `CodexAgent` |
| `gemini_cli` | `gemini` | `GeminiCLIAgent` |

Discovery: `python -m artifact_lab.experiments.rq5_v2 agents`

**Execution is blocked by default.** To run agents (not enabled in this milestone):

```bash
export RQ5_V2_ALLOW_EXECUTE=1
# and set ExperimentConfig.allow_execute=True in code
```

---

## 5. Case construction pipeline

```
load_bearing_candidates.csv
        ↓ filter recommended_for_pilot (calibration)
difficulty_scores.csv
        ↓
case_builder.build_factorial_cases()
        ↓ instruction_variants.build_factorial_cells()
factorial_case_manifest.json
```

Each case includes:

- `anchor_path_true`, `anchor_path_false`, `decoy_path`
- Per-cell `instruction_blob_sha`, `cited_anchor`, `mechanical_truth`, `task_prompt`
- Metadata: ecosystem, calibrated expected success

---

## 6. Run matrix

```
cases × cells × agents × replicates
```

Default (pilot plan):

- 20 cases (configurable `--max-cases`)
- 5 cells
- 3 agents (Claude Code, Codex, Gemini CLI)
- 3 replicates
- **900 planned runs** (20 × 5 × 3 × 3)

Planning: `plan.build_run_plan()` with seeded Latin-square cell ordering.

---

## 7. Outputs (infrastructure)

| Path | Description |
|------|-------------|
| `exports/rq5_v2_factorial/factorial_case_manifest.json` | Frozen cases + cell blobs |
| `exports/rq5_v2_factorial/run_plan.csv` | Full run matrix |
| `exports/rq5_v2_factorial/experiment_config.json` | Agents, replicates, flags |
| `exports/rq5_v2_factorial/experiment_plan_summary.md` | Human-readable plan |
| `exports/rq5_v2_factorial/results_dry_run.csv` | Planned-only stubs (optional) |

After execution (future):

| Path | Description |
|------|-------------|
| `exports/rq5_v2_factorial/results.csv` | Run-level outcomes |
| `exports/rq5_v2_factorial/traces/` | JSONL traces per run |

---

## 8. CLI commands

```bash
# Build manifest + run plan (NO agent execution)
python -m artifact_lab.experiments.rq5_v2 build-plan \
  --output-dir exports/rq5_v2_factorial \
  --max-cases 20

# Write dry-run ledger stubs
python -m artifact_lab.experiments.rq5_v2 dry-run-ledger \
  --output-dir exports/rq5_v2_factorial

# List agents
python -m artifact_lab.experiments.rq5_v2 agents
```

Makefile:

```bash
make rq5-v2-factorial-plan
```

---

## 9. Manipulation checks

Pre-analysis gates (`validation.py`):

1. **Mechanical truth:** `git ls-tree` at commit; true cells VERIFIED, false cells MISSING
2. **Instruction presence:** file exists (present) / absent (N)
3. **Decoy exists:** peripheral cells only

---

## 10. Primary analysis mapping

| Hypothesis | Estimand | Fields |
|------------|----------|--------|
| H1 | P(read \| present) − P(read \| absent) | `read_instruction`, `factor_a` |
| H2 | Truth effect in LB vs PB | `factor_b`, `factor_c`, `success` |
| H3 | Mediation on false+LB | `bind_failure_detected`, `grounding_action`, `repair_success` |
| H4 | Truth × load-bearing interaction | `factor_b`, `factor_c`, `success` |

Run-level CSV columns include: `run_id`, `case_id`, `cell_code`, `factor_a`, `factor_b`, `factor_c`, `agent_id`, `replicate_id`, `success`, `tests_passing`, `files_modified`, `dry_run`.

---

## 11. Module index

```
artifact_lab/experiments/rq5_v2/
├── __init__.py
├── __main__.py           # CLI
├── models.py             # FactorialCase, RunPlanEntry, ExperimentConfig
├── factors.py            # Cell codes, factor levels
├── instruction_variants.py
├── case_builder.py
├── prompts.py
├── workspace.py
├── plan.py
├── manifest.py
├── ledger.py
├── validation.py
├── evaluation.py
├── runner.py             # Gated execution
├── run.py                # build_experiment_plan()
└── agents/
    ├── base.py
    └── registry.py       # claude_code, codex, gemini_cli
```

Related (upstream):

- `artifact_lab/experiments/truth_decay/rq5_v2/load_bearing.py` — candidate identification
- `artifact_lab/experiments/task_calibration/` — difficulty scoring

---

## 12. What is explicitly out of scope

- Agent execution in this milestone (infrastructure only)
- Main-study analysis scripts (planned after pilot data)
- Human load-bearing audit UI

---

## 13. Checklist before first live run

- [ ] `build-plan` completes with ≥ 20 calibration-band cases
- [ ] Manipulation checks pass on 100% of cells (sample validation)
- [ ] `RQ5_V2_ALLOW_EXECUTE=1` documented in runbook
- [ ] Trace storage and cost caps configured
- [ ] Pre-registration filed
