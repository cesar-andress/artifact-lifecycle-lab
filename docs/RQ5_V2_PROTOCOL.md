# RQ5 v2 — Causal Agent Experiment Protocol

**Status:** Design only (not implemented)  
**Version:** `RQ5_AGENT_IMPACT_EXPERIMENT_v2.1`  
**Supersedes for causal inference:** `protocol/RQ5_AGENT_IMPACT_EXPERIMENT_v1.md` (v1 remains frozen as historical evidence)  
**Parent framework:** Late-binding model v1 (`docs/LATE_BINDING_MODEL_v1.md`)  
**Date:** 2026-07-03

---

## 0. Executive summary

RQ5 v1 lacked causal power because (i) tasks were decoupled from cited anchors in most runs, (ii) the primary estimand treated referential truth as a main effect without a pre-specified **truth × load-bearing** interaction, (iii) baseline success was ~12% so outcome variance was dominated by environmental difficulty, and (iv) the effective sample was 63 paired triplets on a single agent.

RQ5 v2 is a **pre-registered factorial experiment** whose **primary scientific hypothesis is H4**: task success depends on the **interaction** of referential truth and causal load-bearing status. H1 (instruction presence) is a **manipulation check only**; the paper is **not** centered on whether instructions matter.

Design commitments that address TOSEM reviewer concerns:

1. **False reference is defined narrowly** (Section 4): a **syntactically plausible but non-resolving path** at the pinned commit. Typo, deleted, renamed, external, and semantic falsehood classes are **excluded** from the primary experiment.
2. **Staged execution gates** (Section 11): Phase 0 (calibration) → Phase 1a (40 cases, primary agent) → gate → Phase 1b (120 cases) → Phase 2 (second-agent replication). No scaling without passing gates.
3. **Operational load-bearing gate** (Section 8.6): in T+L and F+L cells, `anchor_attempted` must occur in ≥ 60% of runs; otherwise the case is excluded or redesigned.
4. **Primary causal claim** (Section 2.1): not “instructions matter” and not “false instructions do not matter,” but **“referential truth matters as a function of causal load-bearing status.”**

**Primary analysis agent runs (if all phases complete):** 120 cases × 5 within-case cells × 3 replicates = 1,800 (Agent A), plus 600 replication runs (Agent B, 50% of cases).

No code, runner changes, or agent executions are in scope for this document.

---

## 1. Why v1 failed the causal bar

| v1 limitation | Consequence for inference |
|---------------|---------------------------|
| Load-bearing stratum inferred post hoc; 73% of B runs classified non-load-bearing | Truth main effect diluted; interaction untestable |
| Generic pytest task not coupled to anchor path | Agents read and follow false anchors without outcome change |
| ~12% marginal success (88% failure ceiling) | Wide CIs; Type II error on any instruction effect |
| 63 paired triplets, 1 agent (Claude Code) | Underpowered; no cross-agent robustness |
| A/B/C present but incomplete A/B; C added mid-stream | Messy factorial; stratification not balanced |
| “False” reference mixed typo/deleted/semantic classes | Construct validity unclear; reviewers reject estimand |

v1 remains valid evidence for **consumption** (read/follow) and **directive-driven edit scope**. v2 is required for **causal claims** about the truth × load-bearing interaction on outcomes.

---

## 2. Research question and primary causal claim

### 2.1 Primary causal claim (paper center)

The v2 paper tests **one primary causal claim**:

> **Referential truth affects task success as a function of causal load-bearing status** — i.e., truth effects are **conditional** on whether the cited path is required to complete the task, not unconditional on instruction presence or falsity alone.

**Explicit non-claims (even if results are null):**

| Non-claim | Why excluded |
|-----------|--------------|
| “Instructions matter” | H1 is a manipulation check; presence is not the primary estimand |
| “False instructions do not matter” | A null H4 does not license a blanket falsity-irrelevance claim; it may indicate failed load-bearing manipulation, low power, or narrow false-reference construct |
| “Agents ignore instruction files” | v1 already falsified; not re-tested as headline |
| “Truth debt is widespread” | Observational panel claim; out of v2 scope |

### 2.2 Research question (v2)

**RQ5 (causal v2):** Under controlled instruction injection at a pinned commit, does **referential truth** interact with **causal load-bearing status** to affect task success — and through what behavioral mediation path when references are false and load-bearing?

Sub-questions map to hypotheses (Section 3). **H4 is primary**; H1–H3 are supporting.

---

## 3. Hypotheses and estimands

**Hypothesis priority:**

| Priority | ID | Role |
|----------|-----|------|
| **Primary** | **H4** | Truth × load-bearing interaction on task success |
| Secondary | H2 | Stratum-specific decomposition of H4 |
| Mechanistic | H3 | Mediation chain in false, load-bearing cells |
| Manipulation check | H1 | Instruction presence modifies behavior (not paper center) |

---

### H4 — Task outcome depends on truth × load-bearing interaction *(PRIMARY)*

**Claim:** Task success is driven by the **interaction** of referential truth and causal load-bearing status. Referential truth affects outcomes **primarily when** the cited path is load-bearing; in the peripheral stratum, true and false references yield equivalent outcomes (H2 restates this decomposition).

**Primary estimand (H4):**

```
logit P(success) = β0 + β1·Truth + β2·LoadBearing + β3·(Truth × LoadBearing) + controls + random effects
```

**Primary coefficient:** β3 (interaction).  
**Secondary:** β1 (truth main effect) reported but **not primary**; preregistered expectation is β1 ≈ 0 when β2 and β3 are included.

**Success criterion:** β3 > 0 with two-sided p < 0.05 (cluster-robust) OR 95% CI for Δ(success) in LB stratum excludes 0 while PB stratum CI includes 0.

**Paper framing:** All introduction, methods, and discussion sections lead with H4. H1 results appear in a “Manipulation checks” subsection only.

---

### H2 — Reference truth matters only when references are load-bearing *(secondary decomposition of H4)*

**Claim:** Referential truth affects outcomes **only** in the load-bearing stratum; in the peripheral stratum, true and false references yield equivalent outcomes.

**Operationalization:** 2 × 2 subset when instruction is present: {True, False} × {Load-bearing, Peripheral}.

**Primary estimands (H2):**

| ID | Estimand | Test |
|----|----------|------|
| H2a | Simple effect of truth in load-bearing stratum | P(success \| true, LB) − P(success \| false, LB) |
| H2b | Simple effect of truth in peripheral stratum | P(success \| true, PB) − P(success \| false, PB) |

**Success criterion:** |H2a| > |H2b| and H2b CI includes 0; equivalently, a **smaller Bayes factor or non-significant z-test** for truth in PB while truth in LB exceeds minimum detectable effect (Section 12).

---

### H3 — Agents repair false references by grounding against the repository *(mechanistic)*

**Claim:** When agents encounter a **non-resolving false reference** (Section 4) on a load-bearing path, a substantial fraction **detects failure** and **attempts grounding** (search, list, read alternative paths, edit instruction text, or substitute targets) before task completion.

**Operationalization:** Trace-coded mediation chain on **false, load-bearing** cells only.

**Primary estimands (H3):**

| Stage | Variable | Definition |
|-------|----------|------------|
| M1 | `anchor_attempted` | Tool event targets the cited path or command derived from it |
| M2 | `bind_failure_detected` | Explicit error, retry, or verbalized missing-target in trace |
| M3 | `grounding_action` | Repo search / glob / read of sibling paths / instruction self-edit within 10 tool steps after M2 |
| M4 | `repair_success` | Subsequent tool call succeeds on a semantically equivalent target OR task proceeds without anchor |

**Success criterion:** P(M3 \| M2, false, LB) ≥ 0.40 on preregistered trace rubric; inter-rater κ ≥ 0.75 on 10% human audit subsample.

---

### H1 — Instructions modify agent behaviour *(manipulation check only)*

**Claim:** Injecting a machine-consumed instruction file changes agent behaviour relative to absence. This confirms the presence manipulation worked; it is **not** a primary scientific contribution.

**Operationalization:** Presence vs. absence of the instruction file at the pinned commit.

**Estimands (H1 — manipulation check):**

| ID | Estimand | Comparison | Gate threshold |
|----|----------|------------|----------------|
| H1a | Instruction read rate | P(read \| present) − P(read \| absent) | > 0.90 pooled (Phase 0/1a) |
| H1b | Edit scope | E[files modified \| present] − E[files modified \| absent] | CI excludes 0 on ≥ 80% of calibration cases |
| H1c | Tool-call profile | Distribution shift (shell/read/write counts) | Descriptive only |

**Failure action:** If H1a gate fails after two injection revisions, halt Phase 1a and fix injection mechanism before any causal inference. **Do not** reframe a failed H1 as a substantive finding.

**Reporting:** H1 appears under “Manipulation checks” in the paper; not in abstract conclusions.

---

## 4. False reference definition (construct validity)

### 4.1 Primary experiment: one false-reference class only

A **false reference** in the primary experiment is defined **narrowly** as:

> A **syntactically plausible path string** cited in the instruction file that **does not resolve** to any file or directory at the **pinned commit** under the preregistered mechanical verifier (`git ls-tree` / path existence rules).

**Properties required:**

| Property | Requirement |
|----------|-------------|
| Syntax | Valid relative or repo-root path format for the ecosystem (e.g. `src/utils/helpers.py`, not `http://...`) |
| Plausibility | Path resembles real paths in the repo (same directory prefix, naming convention) |
| Non-resolution | `MISSING` at pinned SHA — no blob at that path |
| Stability | Same false path string used in F+L and F+P cells for a given case |

### 4.2 Excluded falsehood classes (primary experiment)

The following classes are **explicitly excluded** from the primary factorial. They may be reserved for a **future extension study** with separate pre-registration.

| Class | Example | Exclusion rationale |
|-------|---------|---------------------|
| **Typo** | `utils/helper.py` vs `utils/helpers.py` | Confounds spelling error with missing target |
| **Deleted** | Path existed in parent commit, removed at pin | Confounds history narrative with static non-resolution |
| **Renamed** | Path moved to new name at pin | Confounds rename discovery with absence |
| **External** | URL, package registry, MCP endpoint | Different resolution semantics |
| **Semantic falsehood** | Path exists but describes wrong behavior | Mechanical verifier cannot detect; different estimand |

**Construction rule:** For each case, `{anchor_path_false}` is authored at design time as a **never-existing sibling path** in the same directory as `{anchor_path_true}` (e.g. `src/foo/bar_helper.py` when true target is `src/foo/bar_utils.py`). It must never have existed in the repo history at the pinned commit.

### 4.3 True reference definition

A **true reference** is a path string that **resolves** at the pinned commit (`VERIFIED` under mechanical rules) and points to the file the task requires (LB) or cites in the peripheral section only (PB).

---

## 5. Experimental design overview

### 5.1 Design type

**Split-plot factorial** with:

- **Between-case factors:** repository, task template, anchor path class (fixed at case construction).
- **Within-case repeated measures:** full 2 × 2 × 2 core factorial + absence cell.

### 5.2 Core factorial (instruction present cells)

| Cell | Truth | Load-bearing | Instruction content |
|------|-------|--------------|---------------------|
| **T+L** | True | Load-bearing | Anchor path exists; task requires that path |
| **F+L** | False | Load-bearing | Non-resolving plausible path; task requires that logical target |
| **T+P** | True | Peripheral | Anchor path exists; task solvable without it |
| **F+P** | False | Peripheral | Non-resolving plausible path; task solvable without it |

### 5.3 Presence control (H1 manipulation check)

| Cell | Truth | Load-bearing | Instruction |
|------|-------|--------------|-------------|
| **N** | — | — | File removed from workspace (v1 Condition C, redesigned) |

Each **case** contributes up to **five cells**: T+L, F+L, T+P, F+P, N.

### 5.4 Blocking and randomization

- Cases blocked by **language/ecosystem** (Python/pytest, Node/npm, mixed).
- **Latin square** on cell order across replicates to reduce scheduling artifacts.
- **Truth and peripheral/load-bearing** are crossed within case; the same natural-language task stem is used; only the instruction blob and anchor sentence differ per cell.

---

## 6. Experimental factors (summary table)

| Factor | Type | Levels | Role |
|--------|------|--------|------|
| **Referential truth** | Within-case (if present) | True, False | **H4 (primary)**, H2 |
| **Load-bearing** | Within-case (if present) | Load-bearing (LB), Peripheral (PB) | **H4 (primary)**, H2 |
| **Instruction presence** | Within-case | Present, Absent | **H1 manipulation check only** |
| **Agent product** | Between-run | Agent A (primary), Agent B (replication) | Robustness (Phase 2) |
| **Replicate** | Within (case × cell × agent) | r = 1…R | Stochastic variation |
| **Case** | Between | i = 1…N | Cluster unit |

**Not experimental factors (held constant or covariates):** pinned commit SHA, task prompt template, timeout (20 min v2), network policy (no new commits), test command, instruction file path convention, false-reference class (always non-resolving plausible path).

---

## 7. Independent variables (IVs)

### 7.1 Manipulated IVs

| IV | Values | Manipulation mechanism |
|----|--------|------------------------|
| `truth` | 0 = false, 1 = true | Swap path string to **non-resolving plausible path** vs. **existing target** at commit (Section 4) |
| `load_bearing` | 0 = peripheral, 1 = load-bearing | Task spec requires editing anchor file (LB) vs. editing decoy file while anchor only in "see also" (PB) |
| `presence` | 0, 1 | Remove instruction file from workspace vs. inject frozen blob (**H1 check only**) |

### 7.2 Derived factorial indicators

- `truth_x_lb` = truth × load_bearing (interaction term for **H4**)
- `false_lb` = (1 − truth) × load_bearing (domain for H3 mediation)

### 7.3 Design IVs (blocking)

- `ecosystem` ∈ {python, node, other}
- `repo_id` (random intercept)
- `case_id` (random intercept)

### 7.4 Non-manipulated covariates (pre-specified)

| Covariate | Source | Rationale |
|-----------|--------|-----------|
| `baseline_test_pass` | Smoke at commit | Environmental difficulty |
| `instruction_token_count` | Blob | Directive density |
| `anchor_depth` | Path depth from root | Discovery difficulty |
| `prior_agent_exposure` | Run index | Learning (should be 0 if fresh session) |

---

## 8. Dependent variables (DVs)

### 8.1 Primary DV (H4)

| DV | Type | Definition |
|----|------|------------|
| `task_success` | Binary | Required edit applied **and** test command exit 0 **and** no scope violation |

### 8.2 Secondary DVs (behaviour — H1 check, mechanism)

| DV | Type | Definition |
|----|------|------------|
| `instruction_read` | Binary | Trace shows instruction file opened or quoted |
| `files_modified` | Count | Distinct files written |
| `anchor_path_touched` | Binary | Edit or read on anchor path (true path for T cells; attempted false path for F cells) |
| `decoy_path_touched` | Binary | Edit on task-required decoy path (PB cells) |
| `time_to_first_test` | Seconds | Latency |
| `test_exit_code` | Ordinal | 0 vs. non-zero |

### 8.3 Mechanism DVs (H3)

| DV | Type | Definition |
|----|------|------------|
| `anchor_attempted` | Binary | Tool call path matches cited anchor (M1) |
| `bind_failure_detected` | Binary | Rubric-coded from trace (M2) |
| `grounding_action` | Binary | Search/list/read/repair within window after failure (M3) |
| `repair_success` | Binary | Subsequent successful bind or task continuation (M4) |
| `instruction_self_repair` | Binary | Agent edits instruction file to fix path |

### 8.4 Manipulation-check DVs

| DV | Type | Definition |
|----|------|------------|
| `mechanical_truth_at_commit` | Binary | Independent verifier: path resolves at SHA |
| `load_bearing_label_agreement` | Binary | Author checklist vs. blind human audit (10% sample) |

---

## 9. Manipulation checks and operational gates

Checks run **before** main analysis and **between phases**. Failure triggers case exclusion, redesign, or protocol halt — not silent continuation.

### 9.1 Mechanical truth check (automated)

At pinned commit, for each case:

- **True cells:** cited path must resolve (`VERIFIED` under mechanical rules).
- **False cells:** cited path must not resolve (`MISSING`) and must satisfy Section 4 (non-resolving plausible path only).

**Gate:** 100% of injected blobs pass mechanical check. Any failure → case dropped from analysis set.

### 9.2 Load-bearing construct check (design-time + audit)

**Design-time checklist (author):**

1. LB: task rubric names anchor path as **only** valid edit target for the required change.
2. PB: identical rubric names **decoy path**; anchor appears only in non-actionable section (e.g. "Related files").
3. PB: decoy path exists at commit; required tests do not import anchor path.

**Blind audit:** 10% of cases (min 12) rated by two annotators: {LB confirmed, PB confirmed, ambiguous}.

**Gate:** κ ≥ 0.75; ambiguous ≤ 5%. Otherwise refine task templates before scaling.

### 9.3 Instruction presence check (H1)

- **Present:** SHA256 of injected blob matches frozen manifest.
- **Absent:** instruction path absent from workspace listing; agent prompt unchanged (still mentions "if present, follow project instructions").

### 9.4 Uptake check (H1 manipulation)

On **present** cells, instruction read rate must exceed **0.90** pooled across Phase 0 and Phase 1a. If not, revise injection mechanism (prompt, path, IDE config) before scaling to Phase 1b.

### 9.5 Environmental difficulty calibration

**Phase 0** (Section 11): target marginal success in **T+L** cell ∈ [0.45, 0.75]. If success < 0.30 or > 0.85 after two template iterations, adjust task difficulty (not truth/load-bearing labels).

### 9.6 Operational load-bearing gate *(NEW — mandatory)*

Load-bearing status is not only a **design-time label** but an **operational property** verified at runtime.

**Definition:** A case is **operationally load-bearing** in LB cells (T+L, F+L) if the agent **attempts the cited anchor path** in a sufficient fraction of runs.

**Measurement:** `anchor_attempted` (M1) — tool event targets the cited path or a command derived from it.

**Gate (per case, evaluated after Phase 1a):**

| Cell | Requirement |
|------|-------------|
| T+L | P(`anchor_attempted`) ≥ **0.60** across replicates |
| F+L | P(`anchor_attempted`) ≥ **0.60** across replicates |

**Failure actions:**

| Outcome | Action |
|---------|--------|
| Case fails gate in T+L or F+L | **Exclude** from primary H4 analysis set OR **redesign** task until gate passes in a re-pilot (max 2 redesign attempts) |
| > 20% of Phase 1a cases fail gate | **Halt** Phase 1b; revise LB task template globally before scaling |
| F+L passes but T+L fails | Case invalid (true path should be easier to attempt); exclude |
| Both fail | Strong evidence task is decoupled from anchor; exclude and log as v1 failure mode |

**Rationale:** If the agent never attempts the anchor, the task is **not operationally load-bearing** regardless of author intent. Without this gate, H4 is uninterpretable (v1 failure mode).

**Reporting:** Report operational LB rate per case in supplementary table; primary analysis uses only cases passing gate.

---

## 10. Mediation model (H3)

### 10.1 Prespecified path (false, load-bearing cells only)

```
Non-resolving false ref → Anchor attempt → Bind failure → Grounding → Repair success → Task success
                              M1              M2            M3           M4
```

### 10.2 Mediation variables

| Variable | Role | Coding |
|----------|------|--------|
| `anchor_attempted` | M1 | Tool call path matches cited anchor |
| `bind_failure_detected` | M2 | Error or explicit retry on missing target |
| `grounding_action` | M3 | Repo exploration or instruction edit after M2 |
| `repair_success` | M4 | Successful alternative bind OR task proceeds |
| `task_success` | Outcome | Section 8.1 |

### 10.3 Estimands

- **Natural direct effect (NDE):** effect of false anchor on success when grounding is disabled (hypothetical).
- **Natural indirect effect (NIE):** effect transmitted through M2→M3→M4.
- **Report:** proportion of false-LB failures with M2=1; proportion with M3=1 given M2; success rate given M4=1 vs. 0.

### 10.4 Analysis method

- Primary: **cluster bootstrap mediation** (cases as clusters, 5,000 resamples, seed 42).
- Secondary: **Baron-Kenny logistic steps** with cluster-robust SEs (exploratory, FDR-controlled).
- **Not claimed:** causal mediation without no-unmeasured-confounding assumption; document as **mechanistic evidence** supporting H3.

---

## 11. Staged execution phases and gates

Execution proceeds in **strict stages**. Each stage must pass its gate before the next begins. **No optional stopping on significant β3.**

### 11.1 Phase 0 — Calibration (mandatory)

| Parameter | Value |
|-----------|-------|
| Cases | **20** |
| Cells per case | **T+L only** (truth true, load-bearing) |
| Replicates | 3 |
| Agent | Primary agent (Agent A) only |
| Goal | Marginal T+L success ∈ [0.45, 0.75]; validate task templates |

**Phase 0 gate (all required):**

| Check | Pass criterion | Fail action |
|-------|----------------|-------------|
| T+L success rate | ∈ [0.45, 0.75] | Revise task difficulty (max 2 iterations); halt if still out of band |
| Instruction read rate (present) | ≥ 0.90 | Revise injection mechanism |
| Mechanical truth | 100% | Fix case construction |

**Phase 0 does not estimate H4.** It calibrates difficulty and confirms basic protocol viability.

---

### 11.2 Phase 1a — Primary factorial pilot (mandatory before scale-up)

| Parameter | Value |
|-----------|-------|
| Cases | **40** (complete 5-cell factorial) |
| Cells | T+L, F+L, T+P, F+P, N |
| Replicates | 3 |
| Agent | **Agent A only** |
| Runs | 40 × 5 × 3 = **600** |

**Phase 1a gate (all required to proceed to Phase 1b):**

| Check | Pass criterion | Fail action |
|-------|----------------|-------------|
| **Success rate (T+L)** | ∈ [0.40, 0.80] pooled | Revise difficulty; do not scale |
| **Anchor attempt rate (T+L, F+L)** | ≥ **0.60** per case (Section 9.6) | Exclude/redesign failing cases; if > 20% fail, halt and revise LB template |
| **Truth × LB effect direction** | Point estimate of (success_T+L − success_F+L) > 0 OR interaction OR > 0 in prespecified model | See Section 21 (Risk register) if null or reversed |
| **Instruction read (H1 check)** | ≥ 0.90 on present cells | Fix injection; do not scale |
| **Mechanical truth** | 100% | Fix construction |

**Phase 1a purpose:** Confirm the factorial is **causally identified** (operational load-bearing + non-trivial success variance) before committing to 120 cases and Agent B costs.

**Phase 1a analysis:** Run primary H4 model on present cells (n = 40 cases). This is **interim** — not the final confirmatory test — but informs the go/no-go decision.

---

### 11.3 Phase 1b — Main factorial (conditional on Phase 1a gate)

| Parameter | Value |
|-----------|-------|
| Cases | **120** total (40 from 1a + **80 new**, or full fresh 120 if 1a cases redesigned) |
| Cells | 5 |
| Replicates | 3 |
| Agent | Agent A |
| Runs | 120 × 5 × 3 = **1,800** |

**Entry condition:** Phase 1a gate passed (Section 11.2).

**Phase 1b gate (before Phase 2):**

| Check | Pass criterion |
|-------|----------------|
| Operational LB gate | ≥ 80% of cases pass Section 9.6 |
| Exclusions | Document all excluded cases with reason code |

**Primary confirmatory analysis** runs on Phase 1b complete dataset (Agent A, present cells for H4).

---

### 11.4 Phase 2 — Second-agent replication (conditional on Phase 1b)

| Parameter | Value |
|-----------|-------|
| Cases | **50%** of Phase 1b cases (stratified by ecosystem), min 40 |
| Cells | 5 |
| Replicates | 2 |
| Agent | **Agent B** (different vendor/model class) |
| Runs | ~60 × 5 × 2 = **600** (exact N depends on stratification) |

**Entry condition:** Phase 1b complete; primary H4 analysis script frozen.

**Phase 2 purpose:** External validity — does β3 direction replicate on Agent B?

**Analysis:** Same H4 model on Agent B subset; report compatibility interval overlap on β3; **do not pool** agents in primary model.

---

### 11.5 Phase summary diagram

```
Phase 0 (20 cases, T+L)
    │ gate: success band, read rate, mechanical truth
    ▼
Phase 1a (40 cases, full factorial, Agent A)
    │ gate: success, anchor_attempt ≥ 60%, truth×LB direction, H1 read
    ▼
Phase 1b (120 cases, Agent A)          Phase 2 (50% cases, Agent B)
    │ confirmatory H4                       │ replication
    └───────────────────────────────────────┘
```

### 11.6 Task constraints (all phases)

- Wall timeout: **20 minutes**.
- No `git fetch`, no checkout of other commits.
- Success requires **passing preregistered test command** (pytest, npm test, etc.).
- Agents receive identical system prompt except instruction blob manipulation.

---

## 12. Power analysis

### 12.1 Primary test

**H4 interaction:** mixed-effects logistic regression

```
task_success ~ truth * load_bearing + (1 | case) + (1 | repo)
```

Two-sided α = 0.05, power 1 − β = 0.80.

**Analysis sample:** Present cells only (T+L, F+L, T+P, F+P); cases passing operational LB gate (Section 9.6).

### 12.2 Assumed effect sizes (preregistered planning values)

| Parameter | Symbol | Planning value | Rationale |
|-----------|--------|----------------|-----------|
| Success \| true, LB (T+L) | p₁₁ | **0.60** | Calibration target mid-range |
| Success \| false, LB (F+L) | p₀₁ | **0.35** | Truth matters when load-bearing |
| Success \| true, PB (T+P) | p₁₀ | **0.55** | Peripheral: slightly easier |
| Success \| false, PB (F+P) | p₀₀ | **0.52** | Truth irrelevant (H2) |
| Odds ratio (LB truth effect) | OR_LB | **2.8** | log-OR ≈ 1.03 |
| Odds ratio (PB truth effect) | OR_PB | **1.1** | near null (H2) |
| Intraclass correlation (case) | ICC | **0.15** | Conservative cluster correlation |

**Interaction contrast:** Δ = (p₁₁ − p₀₁) − (p₁₀ − p₀₀) = (0.60 − 0.35) − (0.55 − 0.52) = **0.28**

### 12.3 Sample size derivation

| Quantity | Phase 1a (interim) | Phase 1b (confirmatory) |
|----------|-------------------|-------------------------|
| Cases | 40 | **120** |
| Replicates | 3 | 3 |
| Present-cell runs (Agent A) | 480 | **1,440** |
| Absent-cell runs (Agent A) | 120 | 360 |
| **MDE interaction (80% power)** | ~0.35 (wide; directional only) | **~0.22** |

Phase 1a is **underpowered for confirmatory H4** by design; it tests viability and effect direction only. Confirmatory power targets N = 120 cases at R = 3.

### 12.4 Multiplicity

| Family | Tests | Control |
|--------|-------|---------|
| **Primary (H4)** | β3 interaction | α = 0.05 (no adjustment) |
| Secondary (H2, H3) | 4 tests | Benjamini-Hochberg FDR @ 0.10 |
| Manipulation check (H1) | 2 tests | Descriptive; gate thresholds pre-specified |
| Exploratory | Agent B replication | Descriptive + CI overlap |

---

## 13. Statistical analysis plan

### 13.1 Primary analysis (H4)

**Model:**

```r
glmer(
  task_success ~ truth * load_bearing + ecosystem + baseline_test_pass +
    (1 | repo_id) + (1 | case_id),
  family = binomial,
  data = present_cells_passing_lb_gate
)
```

**Report:** OR, 95% CI, z-test for β3; marginal predicted probabilities for all four cells.

**Cluster-robust sensitivity:** GEE with exchangeable correlation within case.

### 13.2 H2 analysis (secondary)

Stratum-specific truth effects in LB vs. PB cells; Wald contrast for |β_truth,LB| > |β_truth,PB|.

### 13.3 H3 analysis (mechanistic)

Descriptive funnel M1→M2→M3→M4 in F+L; cluster bootstrap NIE.

### 13.4 H1 analysis (manipulation check — not in abstract)

Compare present vs. absent on `instruction_read` and `files_modified`. Report in supplementary "Manipulation checks" only.

### 13.5 Agent replication (Phase 2)

Same H4 model on Agent B subset; compatibility interval overlap on β3.

### 13.6 Missing data

- **Primary estimand:** available-case analysis (cases passing operational LB gate).
- **Sensitivity:** complete-case (all 5 cells × R replicates).

---

## 14. Case construction protocol

Each case is a tuple:

```
(repo_id, commit_sha, instruction_path, task_id, anchor_path_true, anchor_path_false, decoy_path, test_command)
```

### 14.1 False path construction (Section 4 compliance)

- `{anchor_path_false}` = syntactically plausible, **never existed** at pinned commit, same directory prefix as true path.
- **Do not** use typos, deleted files, renamed paths, URLs, or semantically misleading existing files.
- Verify: `mechanical_truth_at_commit` = MISSING for false path, VERIFIED for true path.

### 14.2 Load-bearing (LB) template

Instruction (present tense):

> To complete this task, modify `{anchor_path}`: {specific_change}. Run `{test_command}` before finishing.

- **True (T+L):** `{anchor_path}` = `{anchor_path_true}` (exists).
- **False (F+L):** `{anchor_path}` = `{anchor_path_false}` (non-resolving plausible path); task rubric still requires that logical file.

### 14.3 Peripheral (PB) template

Anchor moved to **Related documentation** section; task rubric:

> Modify `{decoy_path}` only: {specific_change}. Do not edit other files.

- **True (T+P):** Related section cites `{anchor_path_true}`.
- **False (F+P):** Related section cites `{anchor_path_false}`.

### 14.4 Case inclusion / exclusion

| Criterion | Rule |
|-----------|------|
| False-reference class | Non-resolving plausible path only (Section 4) |
| Operational LB gate | Pass Section 9.6 after Phase 1a |
| Mechanical truth | 100% pass |
| Diversity | ≤ 3 cases per repo; ≥ 20 unique repos in final N |

---

## 15. Agents and execution

| Slot | Requirement | Role |
|------|-------------|------|
| **Agent A** | IDE-integrated or CLI agent with read/edit/shell | Primary inference (Phases 0, 1a, 1b) |
| **Agent B** | Different vendor/model class | Replication (Phase 2 only) |

**Version pinning:** model ID, CLI version, tool policy JSON in run manifest.

**Blinding:** automated outcome scoring (test harness); trace coders blind to cell label.

---

## 16. Pre-registration and governance

Before Phase 0 first run:

1. Register on OSF/AsPredicted: **H4 as primary**, staged gates, N=120 target, operational LB gate, false-reference definition.
2. Freeze case manifest schema.
3. Freeze trace coding rubric for M1–M4.
4. Publish analysis plan separate from this design doc.

**Stop rules:**

- Phase 0 T+L success < 0.25 after 2 iterations → halt.
- Phase 1a: > 20% cases fail operational LB gate → halt before 1b.
- Mechanical truth gate fails on > 5% cases → halt construction.
- **No optional stopping** on significant β3.

---

## 17. Mapping to late-binding model

| Model construct | v2 operationalization |
|-----------------|----------------------|
| Referential channel | Truth manipulation (non-resolving plausible path) |
| Causal load-bearing | LB vs. PB task design + operational gate |
| Directive channel | Present vs. absent (**H1 check only**) |
| Runtime resolution | M1–M4 mediation |
| Truth Debt claim | Licensed **only** if H4 interaction significant **and** H2 stratum pattern holds |

---

## 18. Explicit non-claims (v2 scope boundaries)

Even if H4 holds, v2 does **not** support:

- GitHub-wide prevalence of truth debt
- Typo-, deleted-, renamed-, external-, or semantic-falsehood effects (excluded from primary experiment)
- Human documentation equivalence
- Unpinned / live IDE sessions without commit pin
- "Instructions matter" as primary causal conclusion (H1 is manipulation check)
- "False instructions do not matter" as blanket null claim

---

## 19. Comparison to v1 (summary)

| Dimension | v1 | v2 |
|-----------|----|----|
| **Primary estimand** | A−B truth main effect | **Truth × load-bearing interaction (H4)** |
| **Paper center** | Instruction consumption | **Conditional referential truth effect** |
| False reference | Mixed classes | **Non-resolving plausible path only** |
| Load-bearing | Post-hoc trace stratum | Design-time + **operational gate (≥ 60% anchor attempt)** |
| Execution | Single batch | **Staged: Phase 0 → 1a → 1b → 2** |
| Cases | 35 rot-sampled | 120 constructed + panel |
| H1 role | Implicit primary | **Manipulation check only** |

---

## 20. Risk register — outcomes and responses

This section pre-specifies **what the study means** under each outcome. Reviewers should not need to infer post hoc narratives.

### 20.1 H4 positive (β3 > 0, p < 0.05; H2 pattern consistent)

**Interpretation:** Referential truth affects task success **conditionally** on causal load-bearing status. The primary causal claim (Section 2.1) is **supported**.

**Paper framing:**

- Title/abstract center on **conditional truth effect**, not instruction presence.
- Report H2 stratum decomposition, H3 mediation as mechanism.
- Phase 2 Agent B replication strengthens external validity claim.
- **Venue target:** ICSE/FSE (empirical); TOSEM only if Agent B replicates and H3 mediation is robust.

**Claims licensed:** Conditional referential truth effect in machine-consumed instruction files at pinned commits, for non-resolving plausible false paths.

**Claims not licensed:** Ecosystem-wide truth debt; semantic falsehood; other false-reference classes.

---

### 20.2 H4 null (β3 CI includes 0; adequately powered at N = 120)

**Interpretation:** No detectable interaction between referential truth and load-bearing status on task success under this design.

**Paper framing:**

- **Honest null paper** — "Referential truth and load-bearing status do not interact on agent task success under calibrated, operationally load-bearing tasks."
- Emphasize: operational LB gate passed (tasks were coupled); success rate was in band (not ceiling/floor); false-reference construct was narrow and verified.
- Report H2 stratum effects with CIs; report H3 funnel descriptively.
- **Do not** claim "false instructions do not matter" globally.
- **Do not** collapse into "instructions do not matter" (H1 may still pass).

**Scientific value:** Rules out a **specific conditional causal claim** under rigorous design. Contributes methodology (benchmark + gates) even if null.

**Venue target:** FSE/ICSE (SEIP or research track); EMSE for methods-heavy null.

**Follow-up:** Extension study with alternate false-reference classes (Section 4.2) if reviewers ask about construct breadth.

---

### 20.3 H4 opposite to prediction (β3 < 0 significant, or success_F+L > success_T+L in LB)

**Interpretation:** Unexpected reversal — false non-resolving references **outperform** true references in load-bearing stratum.

**Paper framing:**

- **Surprise finding paper** — investigate mechanisms before claiming.
- Mandatory analyses: (a) trace audit for spurious success paths (agent skips anchor, edits wrong file that passes tests); (b) case-level leverage diagnostics; (c) test suite validity (does passing test not require anchor edit?).
- If reversal is artifact → exclude cases, re-run; document transparently.
- If reversal is real → report as **"agents succeed despite false references when task-test coupling is weak"** — a construct validity finding about task design, not support for false instructions.

**Stop rule:** Do not publish reversal without completing forensic case audit (min 10 cases hand-reviewed).

**Venue target:** FSE (surprising empirical result + methodology caution).

---

### 20.4 H1 fails (instruction read rate < 0.90 after injection revisions)

**Interpretation:** Presence manipulation failed. Agents do not consume injected instruction files at sufficient rate.

**Response:**

1. **Halt** Phase 1b and Phase 2 until injection mechanism is fixed.
2. H4 results from Phase 1a (if any) are **invalid for causal inference** — consumption precondition not met.
3. Publish **protocol/methods note** on injection failure modes; do not publish H4 as primary result.
4. Investigate: prompt wording, instruction path convention, agent config, IDE discovery of instruction file.

**Paper option:** Short SEIP paper on "replicating v1 consumption under v2 injection" if root cause is informative.

**This is not a substantive null on truth effects** — it is a **failed experiment** (Type III error / manipulation failure).

---

### 20.5 Load-bearing manipulation fails (operational gate: < 60% anchor attempt in T+L/F+L)

**Interpretation:** Tasks are **decoupled** from cited anchors despite author intent. Same failure mode as v1.

**Response:**

| Scope | Action |
|-------|--------|
| Single case | Exclude; redesign task; re-pilot in Phase 0 |
| > 20% of Phase 1a cases | **Halt** scale-up; global LB template revision |
| Gate passes in T+L but not F+L | Expected partially (false path harder); if F+L < 0.40, consider whether F+L is interpretable; document |

**Paper option if widespread failure persists after redesign:**

- Methods paper: "Design-time vs. operational load-bearing in agent instruction experiments."
- Report v1 and v2 coupling failure rates; prescriptive task design guidelines.
- **Do not** interpret as evidence that truth does not matter.

**Scientific value:** High — identifies a **construct validity bottleneck** the field has ignored.

---

## 21. Deliverables (documentation only; no code in this phase)

| Artifact | Path (planned) |
|----------|----------------|
| This protocol | `docs/RQ5_V2_PROTOCOL.md` |
| Case manifest schema | `protocol/RQ5_V2_CASE_MANIFEST.schema.json` (future) |
| Trace coding rubric | `protocol/RQ5_V2_TRACE_RUBRIC.md` (future) |
| Pre-registration snapshot | OSF link (future) |
| Power analysis notebook | `docs/RQ5_V2_POWER_SIM.ipynb` (future) |

---

## 22. Checklist before implementation phase

- [ ] Approve LB/PB task templates on 5 exemplar repos
- [ ] Confirm false-reference construction follows Section 4 (non-resolving plausible path only)
- [ ] Run Phase 0 calibration (20 cases)
- [ ] Finalize trace rubric with dual coding pilot (M1 `anchor_attempted` critical for gate)
- [ ] Pre-register on OSF with H4 primary, staged gates, operational LB gate
- [ ] Implement runner v2 (out of scope for this document)
- [ ] Cost estimate: Phase 0 (180 runs) + Phase 1a (600) + Phase 1b (1,800) + Phase 2 (600)
- [ ] IRB / AI disclosure alignment with target venue

---

*End of RQ5 v2 protocol v2.1 (design only).*
