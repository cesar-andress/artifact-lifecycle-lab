# RQ5 v2 Factorial — Experiment Plan

**Infrastructure only. No agent runs executed.**

- Protocol: `RQ5_FACTORIAL_v1.0`
- Cases: **20** (12 repositories)
- Cells per case: **5** (T+L, F+L, T+P, F+P, N)
- Agents: **claude_code, codex, gemini_cli**
- Replicates: **3**
- Planned runs: **900** (expected 900)
- Execute allowed: **False**

## Factors

| Factor | Levels |
|--------|--------|
| A — Instruction | present, absent |
| B — Reference truth | truthful, false (when present) |
| C — Load-bearing | yes, no (when present) |

## Outputs

- `exports/rq5_v2_factorial/factorial_case_manifest.json`
- `exports/rq5_v2_factorial/run_plan.csv`
- `exports/rq5_v2_factorial/experiment_config.json`
