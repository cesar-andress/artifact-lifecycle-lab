# RQ5 Agent Impact Experiment Protocol v1

**Status:** Frozen — design only; not implemented  
**Protocol version:** `RQ5_AGENT_IMPACT_EXPERIMENT_v1`  
**Parent protocol:** `protocol/TRUTH_DECAY_PROTOCOL_v1.md`  
**Prerequisite gates:** P3 (rot incidence), P4 (attribution precision), P5 (human doc baseline)

---

## Purpose

Close the TOSEM reviewer objection: *"Truth decay may exist, but does it matter?"*

This protocol defines a **controlled agent task experiment** measuring whether **observed documentation rot** (from P3 longitudinal data) causes measurable downstream cost when agents consume instruction files.

**Truth Decay** remains the primary phenomenon unless RQ5 demonstrates sufficient **operational cost**. **Truth Debt** (accumulated stale-reference burden) is promoted to a first-class claim **only if** RQ5 shows cost.

---

## Research question

**RQ5 (impact):** When machine-consumed documentation contains references that have **observed rot** (mechanically verified as missing at a fixed commit), do coding agents suffer degraded task success compared to truthful documentation at the same commit?

**Comparative baseline (P5):** Within the same repository, do README/CONTRIBUTING human-facing docs show different reference density and ambiguity? This is descriptive only; the causal experiment uses instruction files.

---

## Design principles

| Principle | Rule |
|-----------|------|
| **No artificial rot** | Perturbations sampled from **observed rot events** in `exports/truth_pilot/p3_rot_events.csv` or longitudinal panel |
| **Fixed task context** | Same repo, same commit SHA, same task prompt across conditions |
| **Repeated runs** | Multiple stochastic replicates per (agent × condition × case) |
| **Blind conditions** | Agents receive either truthful docs or observed-rotted docs; evaluators blind to condition |
| **No scaling** | Pilot on ≤10 case repos drawn from P1/P3 sample until design validated |

---

## Experimental units

**Case** = one `(repo_id, instruction_path, commit_sha, reference_set)` drawn from P3 rot events where:

1. Instruction file text is recoverable from L1b at or before `commit_sha`.
2. At least one verifiable reference transitioned VERIFIED → MISSING (observed rot).
3. Repository builds/tests at `commit_sha` (smoke check).

**Conditions:**

| Condition | Documentation |
|-----------|---------------|
| **A — Truthful** | Instruction file blob at last snapshot where target references were VERIFIED |
| **B — Observed rot** | Instruction file blob at snapshot where target references are MISSING (from P3) |
| **C — Human baseline** (optional) | README.md or CONTRIBUTING.md at same commit (no rot injection) |

No synthetic path invention. Condition B uses **real historical stale text** from the laboratory.

---

## Agents and models

**Pilot:** 2–3 agents/models (minimum for reviewer objection closure):

| Agent slot | Example class | Role |
|------------|---------------|------|
| **Agent 1** | IDE-integrated (e.g. Cursor-class) | Primary consumer of `.cursor/rules`, AGENTS.md |
| **Agent 2** | CLI/API agent (e.g. Claude Code-class) | Primary consumer of CLAUDE.md, skills |
| **Agent 3** | Copilot-class (optional) | Consumer of copilot-instructions |

Exact product versions pinned per run manifest. Same tool access policy across agents (read, edit, shell, test).

---

## Task specification

**Fixed task** (same natural-language spec for all runs):

> Implement a small, well-bounded change in the repository at the pinned commit (e.g. add a unit test, fix a typed function, update a CLI flag) using the provided instruction file as authoritative project context.

**Constraints:**

- Task must require consulting instruction file (references paths/commands in file).
- Task must be completable without network beyond dependency install.
- Timeout: 30 minutes wall per run.
- Agents may not fetch newer commits.

---

## Perturbation sampling (from observed rot)

Source: `p3_rot_events.csv` + longitudinal rows for text blobs.

For each selected rot event:

1. Identify `reference` that went MISSING.
2. Load instruction file at **pre-rot** commit (Condition A) and **post-rot** commit (Condition B).
3. Record which references are stale in B (must include the P3 rot reference).
4. Do **not** edit text manually except to select historical snapshots.

Target: **20–30 rot cases** from P1/P3 sample for pilot; expand only after kill criteria review.

---

## Replication plan

| Factor | Levels |
|--------|--------|
| Condition | A (truthful), B (observed rot) |
| Agent | 2–3 models |
| Replicates | **≥3 runs** per (case × condition × agent) |

**Total pilot runs (estimate):** 20 cases × 2 conditions × 2 agents × 3 replicates ≈ **240 runs** (upper bound; prune after variance review).

Randomization: case order randomized; condition order counterbalanced across replicates.

---

## Metrics

### Primary (task outcome)

| Metric | Definition |
|--------|------------|
| **success** | Task rubric pass (binary): required files changed, tests pass, no scope violation |
| **tests_pass** | Project test command exit 0 |
| **compile_pass** | Build/typecheck exit 0 (if applicable) |
| **time_to_completion** | Wall seconds until agent stop or timeout |

### Secondary (process)

| Metric | Definition |
|--------|------------|
| **files_changed** | Count of modified files |
| **tool_failures** | Count of failed shell/tool invocations |
| **reference_follow_attempts** | Agent tried path/command from instruction file |

### Tool-use traces (mandatory logging)

For each run, capture structured trace:

| Trace field | Values |
|-------------|--------|
| `read_reference` | Agent opened/read instruction file |
| `followed_reference` | Agent invoked path/command from file |
| `corrected_reference` | Agent edited instruction file or substituted path after failure |
| `failed_on_reference` | Agent error aligned with stale reference in Condition B |

Traces stored under `exports/rq5_agent_impact/traces/` (future); not implemented in this milestone.

---

## Analysis plan (pilot — no full survival)

**Primary estimand:** Δ success rate = P(success | A) − P(success | B) averaged across cases and agents.

**Secondary:** Δ median time, Δ test pass rate, trace-coded `failed_on_reference` rate in B only.

**Power / variance concerns:**

- Agent stochasticity dominates; **≥3 replicates** required to estimate run-level variance.
- Case clustering by repo inflates SE; analyze with repo random effect or cluster-robust SE.
- Expect low power at n=20 cases; pilot goal is **variance decomposition**, not definitive significance.
- If success is ceiling-rated in both conditions, experiment cannot support cost claim → kill.

---

## Kill criteria

| Criterion | Threshold | Action |
|-----------|-----------|--------|
| **No measurable cost** | Δ success ≤ 5pp and Δ time ≤ 10% across agents | Truth Debt **not promoted**; Truth Decay remains observational primary |
| **Rot cases insufficient** | <10 valid observed-rot cases after sampling | Delay RQ5; do not scale |
| **Trace logging failure** | <90% runs with parseable tool traces | Fix instrumentation before any paper claim |
| **Attribution gate fail** | P4 human precision <0.80 | Do not link rot to agent-maintenance RQ3 |
| **Artificial rot detected** | Any manual reference falsification | Protocol violation; discard run |

---

## Outputs (future implementation)

| Artifact | Path |
|----------|------|
| Case manifest | `exports/rq5_agent_impact/case_manifest.csv` |
| Run results | `exports/rq5_agent_impact/run_results.csv` |
| Trace summary | `exports/rq5_agent_impact/trace_summary.csv` |
| Pilot report | `exports/rq5_agent_impact/rq5_pilot_report.md` |

**This milestone:** design document only. No agent runs.

---

## Relationship to Truth Decay protocol

```
P3 rot incidence ──► case sampling (observed rot, not synthetic)
P4 attribution ────► agent-maintenance claims (separate from impact)
P5 human baseline ► within-repo descriptive comparison
RQ5 experiment ───► causal cost of rot (Truth Debt conditional)
```

**Primary phenomenon (default):** Truth Decay (staleness over time)  
**Conditional phenomenon:** Truth Debt (operational cost of stale machine-consumed docs) — requires RQ5 cost evidence

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| v1 | 2026-07-02 | Initial RQ5 agent impact experiment design (not implemented) |
