# TOSEM Gap Analysis — Scientific Program Review

**Reviewer stance:** ACM TOSEM Associate Editor (desk review of the **research program**, not the manuscript prose)  
**Scope:** `artifact-lifecycle-lab/` evidence, protocols, exports, and forward program (RQ5 v2, LATE_BINDING_MODEL v2)  
**Date:** 2026-07-03  
**Verdict on program today:** Strong **measurement audit** on a new artifact class; weak **identification** and **generalization**; causal layer **exploratory and incomplete**. Not yet a TOSEM-scale **theory + validation** contribution.

---

## 1. Current scientific contribution

What the program actually establishes, stripped of narrative:

### A. Primary contribution (defensible at TOSEM if scoped honestly)

**First large-scale longitudinal measurement of referential integrity in machine-consumed instruction files** (AGENTS.md, skills, IDE rules, copilot instructions), with explicit separation of:

| Finding | Evidence | Scale |
|---------|----------|-------|
| Born-stale mass dominates never-verified references | `born_stale_taxonomy.csv` | **17,747** references never VERIFIED |
| Post-verification first-missing is rare among verified-at-origin | `rq2_survival.csv` | **121 / 4,521** (2.7%) |
| Adjusted genuine post-verification decay is zero in audited sample | `rq2_failure_audit_summary.md` | **0 / 121** |
| Confirmed mechanically false at creation (confirmatory pass) | `gfc_confirmatory_summary.md` | **1,200 / 1,405** (85.4%); **6.76%** of born-stale cohort |
| Post-verification failures mostly extractor artifacts | `rq2_failure_audit_summary.md` | **73.6%** category D |
| Instruction files cite paths that are not more volatile than matched uncited controls (paired fraction) | `cited_uncited_summary.md` | **85.4%** of **2,259** pairs |

This is **empirical reframing**, not a new mechanism: it localizes known documentation-integrity and survival-bias issues to a **new artifact class** with audit discipline. The standout scientific product is **decomposition + bounds** (what is rot vs birth-time false vs measurement artifact), not “late binding” as discovery.

### B. Secondary contribution (methodological packaging)

- **Audit stack** reusable for other labs: born-stale autopsy → GFC confirmatory → RQ2 failure audit → cited–uncited contrast (`docs/SCIENTIFIC_EVIDENCE_FREEZE.md` SS-01–SS-07).
- **Pre-scaling gates P1–P5** executed with PASS on pilot exports (reference density, attribution signal, rot incidence, classifier precision, human-doc feasibility).
- **P4 attribution validator** on human gold: precision **0.958**, F1 **0.962** (`p4_validation.md`, N=200 — workspace-local).
- **Claim-to-evidence inventory** (`late_binding_evidence_table.csv`, 29 rows) — unusual internal rigor; not yet external artifact badge.

### C. Exploratory contribution (causal track — not headline-grade)

**RQ5 v1 partial factorial** (Claude Code CLI only):

| Result | n | Interpretation |
|--------|---|----------------|
| Instruction read when injected | **128/128** | Protocol artifact, not organic uptake |
| Null paired truth effect | **63** triplets, Δ(A−B)=**0.00 pp**, McNemar **p=1.0** | Honest null; **inconclusive** (power + design) |
| Behavioral amplification (files touched) | A≈**100**, C≈**2** | Presence changes scope; not channel-validated |
| ~**12%** marginal success | 233 total runs | Environmental ceiling; masks any instruction effect |
| Incomplete A/B coverage | **22/35** cases | Factorial imbalanced; 13 cases C-only |

**Net:** The program **disproves** several naive hypotheses (common post-verification decay; agents ignore files; agents reject false refs) and **fails to support** operational harm (Truth Debt). That asymmetry is scientifically valuable but **not** a positive causal theory result.

### D. Not a contribution (yet)

- **Late-binding two-channel model** — vocabulary + DAG; **zero prospective tests passed** (`LATE_BINDING_MODEL_v1.md` descriptive; `LATE_BINDING_MODEL_V2.md` pre-registered but **0 runs**).
- **RQ3/RQ4 regime and lifecycle tables** — descriptive occupancy; **no causal or predictive claims** justified beyond supporting the primary decomposition story.
- **E1-1000 cohort** — pre-registered, **not extracted** — no scientific weight.
- **RQ5 v2 factorial** — infrastructure + 900-run plan; **allow_execute: false** — contributes **protocol**, not **evidence**.

---

## 2. Biggest remaining weakness

**Single sentence:** The program conflates a **strong observational audit** with a **failed causal identification strategy**, then labels the gap with a **conceptual model that has not been tested**.

**Why this is fatal at TOSEM:**

1. **Estimand confusion.** Static panel integrity (VERIFIED/MISSING), runtime binding (trace follow), and task success are measured on **different designs** and merged narratively. No unified dataset links panel references to powered causal outcomes.

2. **Causal arm is scientifically incomplete, not merely underpowered.**  
   - 63/105 planned paired triplets; 13 cases never received A/B.  
   - Load-bearing was **post-hoc** (73% of B runs non-load-bearing in mediation).  
   - Generic pytest task **decoupled** from anchor in most runs.  
   - One agent, ~12% success → **Type II error is guaranteed**, not informative null.

3. **Construct validity of “truth.”** Mechanical path existence ≠ semantic falsehood. Reviewers will reject any claim that “false instructions” were manipulated when the manipulation is **missing file at commit**, not **wrong guidance**.

4. **Generalization is unearned.** E1-100 is an enriched engineering frame (98 repos), not a population sample. RQ5 is one CLI product. **100% read** under injection cannot support ecosystem claims.

5. **Forward program (v2) is not evidence.** Excellent protocol hygiene (`RQ5_V2_PROTOCOL.md`, factorial infra, calibration) **increases reviewer expectations** without delivering runs. A TOSEM AE will ask: “Why should I believe v2 will succeed when v1 failed for structural reasons you already documented?”

**Bottom line:** The weakness is not missing prose — it is **claim tier mismatch**. The strongest tier (measurement + audit) is buried under a weaker tier (model + causal law) that the data do not support.

---

## 3. Experiments that would materially increase acceptance probability

Ranked by **ROI** = (expected Δ acceptance probability) / (cost × risk × calendar time).  
Baseline P(accept) today: **~5%** as full late-binding theory paper; **~15–25%** as narrow measurement paper (`TOSEM_READINESS.md`).

| Rank | Experiment | Expected ΔP(accept) | Cost / time | Why ROI is high |
|------|------------|----------------------:|-------------|-----------------|
| **1** | **Reframe + commit observational artifact only** (born-stale decomposition paper; RQ5 → appendix; model → discussion vocabulary) | **+10–20 pp** | Low / weeks | Uses **existing** SS-01–SS-07; removes falsified causal headline; matches TOSEM empirical note bar |
| **2** | **RQ5 v2 calibration pilot** — 20 cases × 5 cells × 1 agent × 3 reps = **300 runs**, success band 40–60%, pre-registered **P-I1** (truth×load-bearing interaction) | **+8–15 pp** *if interaction detected*; **−5 pp** if null again without power proof | Medium / 4–8 weeks | Only path to salvage causal track; infra already built; failure is also publishable **if** pre-registered |
| **3** | **Human validation sample** — 100 stratified references (born-false vs template vs normative vs genuine path) with 2 raters, κ reported | **+5–8 pp** | Low–medium / 2–4 weeks | Directly addresses mechanical-truth attack; cheap vs agent runs |
| **4** | **Cross-agent replication (minimum 2/3)** on **same 20 calibration cases**, primary endpoints P-D1/P-I1 only | **+5–10 pp** | Medium / parallel to #2 | US-08 (single agent) is automatic reject phrase |
| **5** | **Commit + Zenodo entire export bundle** (including workspace-local RQ5 CSVs, traces, checksums, agent version pins) | **+3–5 pp** | Low / days | TOSEM artifact badge; currently **fatal** reproducibility gap |
| **6** | **Held-out panel replication** — P-S1/P-S2 on fresh repo sample (not E1-100 train) | **+3–6 pp** | Medium / 2–3 weeks compute | Shows decomposition is not single-cohort overfit |
| **7** | **Trace construct validation** — 50 runs double-coded by humans for `instruction_followed`, `bind_failure`, `load_bearing` | **+3–5 pp** | Medium / 2–3 weeks | Mediation (H3) unusable without this |
| **8** | **Directive-only vs referential-only factorial arms** (2 extra cells) on micro-task repos | **+5–8 pp** *if channels separable* | High / new design + runs | Tests core model mechanism; only if #2 shows signal |
| **9** | **Complete RQ5 v1 A/B** on remaining 13 cases (39 runs) | **+1–3 pp** | Low / days | Fixes incompleteness narrative; **does not fix** power or load-bearing design flaw |
| **10** | **E1-1000 full extraction** | **+2–4 pp** | High / months | Scale alone without new identification **does not** move causal claims |
| **11** | **P5 human-doc consumption comparison** (README vs AGENTS.md agent arm) | **+2–4 pp** | Medium | Nice boundary; not core to current strongest claims |
| **12** | **Semantic falsehood LLM adjudication at scale** | **+1–3 pp** | Medium | Incremental on GFC; reviewers still skeptical |

**Realistic ceiling without #2 succeeding:** **~25–35%** at TOSEM (strong measurement + exploratory causal appendix).  
**Realistic ceiling with #2 + #4 positive:** **~40–50%**.  
**>70%** requires #2 **plus** external replication or community adoption evidence (see §8).

---

## 4. Experiments that are unnecessary (for TOSEM acceptance at current claim tier)

Do **not** fund these before reframing claims:

| Experiment | Why unnecessary |
|------------|-----------------|
| **More RQ3/RQ4 stratifications** without new estimand | Descriptive tables already sufficient; multiplicity risk |
| **E1-1000 extraction** before causal identification works | Scale amplifies audit findings marginally; does not validate model |
| **Additional born-stale taxonomy categories** | 17,747 cohort already typed; diminishing returns |
| **More post-hoc mediation on v1 traces** | Load-bearing labels post-hoc; constructs unvalidated; unpublishable as causal |
| **LLM re-audit of all 121 RQ2 events** | Deterministic rules dominate; sample human audit (#3) sufficient |
| **IDE/browser agent runs without protocol parity** | Uncontrolled confound; wait until CLI factorial is stable |
| **Synthetic micro-repo-only battery** without panel anchor | Reviewers will dismiss as toy; only useful as **supplement** to #2 |
| **Human reader study of instruction prose quality** | Off-estimand for integrity measurement paper |
| **Re-running v1 A/B on same 35 cases with more replicates** | ~12% success ceiling; more n repeats imprecision, not new science |
| **Building more infrastructure without `allow_execute`** | RQ5 v2 infra is sufficient; next dollar is **runs**, not code |

**Rule:** Any experiment that produces **another descriptive CSV** without a **pre-registered falsifiable prediction** is waste at this stage.

---

## 5. Threats reviewers will attack (expect verbatim)

### Threats to external validity

- **Convenience cohort:** E1-100 = 17 pilot + 83 VSDLC engineering repos; not representative of GitHub, npm, or enterprise monorepos.
- **Single agent family:** Claude Code CLI only; Codex/Gemini are **planned**, not evidenced.
- **Injection protocol:** Instruction file materialized before run → **100% read** is tautological; not ecological validity.
- **Task battery:** Generic “bounded change + pytest” decoupled from real maintainer intent.

### Threats to construct validity

- **Mechanical truth ≠ semantic truth:** MISSING path ≠ “false claim”; VERIFIED path ≠ “correct guidance.”
- **Born-stale heterogeneity collapsed:** 7.9% raw `genuine_false_claim` mixes template, anchor, normative, extraction artifacts — GFC helps but is still mechanical.
- **Load-bearing inferred from traces** in v1; **designed** in v2 but **untested**.
- **Trace classifiers** (`instruction_followed`, `false_claim_used`) unvalidated against human coding.

### Threats to internal validity (causal)

- **Incomplete factorial:** 63 triplets, 22/35 A/B, 13 C-only.
- **Ceiling/floor effects:** ~88% failure → null A−B uninformative.
- **Confounding:** Presence expands edit scope (~100 files) → test failure independent of truth.
- **No manipulation check** that B blob was semantically the **only** difference agents acted on.
- **Multiple comparisons** across RQ1–RQ5 without family-wise control.

### Threats to statistical conclusion validity

- **Post-hoc strata** (mediation, load-bearing) after seeing null main effect.
- **Wide CIs** on all causal contrasts (e.g. A−C CI spans 35 pp).
- **McNemar with sparse cells** (8 successes in A and B).
- **Survival analysis left-truncation** — authors acknowledge but reviewers will probe immortal-time bias.

### Threats to reproducibility

- **Workspace-local exports** not git-tracked: `rq5_results.csv`, `rq5_agent_impact_c/`, `p4_validation.md`.
- **Stale summaries** (`rq5_summary.md` says 9 runs).
- **Agent version unpinned** across time.
- **No Zenodo DOI** at submission (planned only).

### Threats to novelty

- “Agents read context files” — known.  
- “Docs go stale” — known.  
- “Survival analysis on software artifacts” — known application.  
- **Novelty rests on artifact class + audit decomposition**, not on late-binding vocabulary (`NOVELTY_AUDIT.md`).

---

## 6. Claims that are currently unsupported

From `SCIENTIFIC_EVIDENCE_FREEZE.md` (US-*) and program logic. **Do not publish as findings:**

| ID | Claim | Status |
|----|-------|--------|
| US-01 | Post-verification decay is common | **Contradicted** (0/121 adjusted) |
| US-02 | False referential content reliably **harms** success | **Contradicted** (Δ A−B = 0) |
| US-03 | Truthful referential content reliably **helps** success vs absent | **Not demonstrated** (A−C CI includes 0) |
| US-06 | Truth Debt — operational cost of static falsity | **Not demonstrated** |
| US-07 | Cited paths **less** stable than uncited (mean) | **Not demonstrated** (Δ CI includes 0) |
| US-08 | Cross-agent generalization | **Not tested** |
| US-09 | IDE-integrated consumption equals CLI | **Not tested** |
| US-10 | Semantic falsehood rate equals mechanical false rate | **Not tested** |
| US-11 | Full 35-case ABC factorial complete | **Contradicted** (63 triplets) |
| — | Late-binding **model validated** | **Not tested** (v2 predictions unfired) |
| — | Directive vs referential **channels independently causal** | **Not tested** (no D/E arms) |
| — | Load-bearing stratum **pre-specified** causal effect | **Not tested** in v1; v2 not run |
| — | Read–repair pathway **≥40%** grounding rate | **Not tested** (H3 unfired) |
| — | E1-1000 confirms E1-100 patterns | **No data** |
| — | Human docs behave like machine instruction files under agent consumption | **Not tested** (P5 = feasibility only) |

**Narrative claims that sound supported but are not:**

- “Agents consume instruction files in the wild” — only under **lab injection**.  
- “False anchors are peripheral” — selection on churn **≠** task load-bearing.  
- “Model explains null result” — explanation **post-hoc** until v2 runs.

---

## 7. Claims that are already publication-ready

Ready for a **conservative TOSEM empirical paper** (measurement + audit). Wording should match SS-* limits.

### Tier 1 — Headline-ready (High confidence)

| ID | Claim | Key limit to state |
|----|-------|-------------------|
| SS-01 | 0/121 adjusted genuine post-verification decay | Audit heuristics; 1 LLM case in RQ2 audit |
| SS-02 | 73.6% post-verification failures are extractor artifacts | Taxonomy not independently validated |
| SS-03 | 17,747 born-stale; 7.9% raw `genuine_false_claim` | Heterogeneous taxonomy |
| SS-04 | 1,200/1,405 GFC confirmed false at creation | Mechanical confirmation |
| SS-05 | 6.76% born-false rate in born-stale cohort (adjusted) | Cohort-specific |
| SS-06 | 85.4% paired cited ≤ uncited churn | Mean Δ CI includes 0 |
| SS-07 | Panel scale: 2,009 files, 339,646 obs. | E1-100 frame |

### Tier 2 — Results-ready with caveats (Medium confidence)

| ID | Claim | Caveat |
|----|-------|--------|
| SS-08 | 100% instruction read when present (128/128) | Injection design |
| SS-09 | Null paired A−B success (63 triplets) | Incomplete, underpowered |
| SS-10 | ~100 vs ~2 files modified (A/B vs C) | Not channel-decomposed |
| MS-03 | 77.8% false-claim use on B | Trace heuristic |
| MS-08 | Test failure dominates unsuccessful runs | Not isolated causally |
| MS-11 | P5 human-doc baseline feasible | Not comparative experiment |
| MS-04 | A−C +4.76 pp, not significant | Wide CI |

### Tier 3 — Discussion-only (conceptual, not findings)

- Late-binding **vocabulary** (directive vs referential; static vs runtime) — label as **framework**, cite v2 predictions as future work.  
- Truth Decay vs Truth Debt **distinction** — definitional, motivated by null causal pilot.  
- Implications for tool builders (lint at consumption, load-bearing markers) — **opinion** unless tied to user study.

---

## 8. Roadmap: current state → >70% P(accept) at TOSEM

**Honest assessment:** **>70%** at TOSEM is **aspirational** for any single empirical SE paper unless the contribution becomes **field-defining** (standard dataset + benchmark + multi-site replication) or the causal result is **large, replicated, and surprising**. Internal assessment tops out at **~40–50%** with excellent v2 execution (`TOSEM_READINESS.md`). The roadmap below states what **would** be required—not what is likely.

### Phase 0 — Stop the bleeding (weeks 0–4) | Target P ≈ 20–30%

1. **Split the program into two papers mentally:**  
   - **Paper A (submit first):** Born-stale decomposition + audits (SS-01–SS-07 only).  
   - **Paper B (later):** Causal factorial — do not mention in Paper A abstract except “future work.”
2. Commit all workspace-local exports; pin agent versions; Zenodo DOI.
3. Human validation sample (§3 rank #3) for mechanical labels.
4. **Kill** Truth Debt, validated model, and cross-agent claims from Paper A.

*Without Phase 0, do not submit.*

### Phase 1 — Powered causal identification (months 1–4) | Target P ≈ 35–45%

1. Execute RQ5 v2 **calibration pilot** (300 runs, 1 agent) with pre-registered gates (`LATE_BINDING_MODEL_V2.md` P-M1, P-E1, P-I1).
2. If success band wrong: **stop** and adjust calibration — do not interpret null.
3. If interaction **null** with adequate power (≥80% for pre-specified MDE): publish **negative result** as separate short paper or TOSEM appendix — **do not** rescue with post-hoc strata.
4. Trace validation (§3 rank #7) before any mediation claim.

### Phase 2 — Generalization (months 4–8) | Target P ≈ 45–55%

1. Replicate primary estimands on **Codex + Gemini CLI** (§3 rank #4).
2. Held-out repo panel replication (§3 rank #6).
3. Optional: directive-only / referential-only arms **only if** Phase 1 shows truth×LB interaction.

### Phase 3 — Community anchor (months 6–12) | Required for >70%

TOSEM rarely exceeds **~50–55%** for “we ran an experiment on N repos” without **community uptake**. To reach **>70%**, the program needs **at least one** of:

| Anchor | Requirement |
|--------|-------------|
| **Benchmark adoption** | Public leaderboard + ≥3 external teams reproduce primary effect on shared cases |
| **Industry/tool integration** | Consumption-time linter shipped in a major agent product with evaluation |
| **Multi-site study** | ≥2 independent labs replicate SS-01 decomposition + v2 interaction sign |
| **Foundational dataset paper** | Curated longitudinal corpus becomes **the** reference for instruction-file research (citations, not just GitHub stars) |

Without Phase 3, **realistic ceiling ≈ 45–55%** even with perfect Phase 1–2.

### Decision tree (brutal)

```
Today
 ├─ Submit full late-binding theory now → P ≈ 5% (desk reject)
 ├─ Paper A (measurement only) + Phase 0 → P ≈ 20–30%
 ├─ Paper A + Phase 1 positive interaction + Phase 2 replication → P ≈ 40–50%
 └─ Above + Phase 3 community anchor → P ≈ 60–75% (still not guaranteed)
```

### What **not** to do on the roadmap

- Do not merge v1 and v2 evidence in one narrative without clear “pilot” vs “confirmatory” labels.  
- Do not add RQ6 observational tracks before causal estimand is identified.  
- Do not publish LATE_BINDING_MODEL v2 predictions **after** seeing v2 data (registration timestamp matters).

---

## 9. AE summary judgment

| Question | Answer |
|----------|--------|
| Is there a TOSEM-worthy scientific core? | **Yes** — born-stale dominance + audit-limited bounds on post-verification decay in machine instruction files. |
| Is the late-binding model a contribution today? | **No** — untested vocabulary. |
| Is the causal program complete? | **No** — v1 incomplete; v2 unexecuted. |
| What should the authors do first? | **Reframe and submit measurement**; **run** v2 factorial or **stop claiming** causal law. |
| Is >70% realistic without external anchor? | **No.** |

---

## Document control

| Field | Value |
|-------|--------|
| Version | v1 |
| Inputs | Frozen exports, `SCIENTIFIC_EVIDENCE_FREEZE.md`, `TOSEM_READINESS.md`, `NOVELTY_AUDIT.md`, `REVIEWER2_SIMULATION.md`, `LATE_BINDING_MODEL_V2.md`, RQ5 v1/v2 protocols |
| Excludes | Manuscript prose quality, LaTeX, figure polish |
