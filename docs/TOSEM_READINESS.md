# TOSEM Readiness Assessment

**Assumed submission date:** tomorrow  
**Manuscript:** `paper/` — *Late Binding in Machine-Consumed Instruction Files*  
**Evidence base:** Frozen exports only (no new experiments before submission)  
**Assessor stance:** ACM TOSEM associate editor, desk-reject threshold applied  
**Date:** 2026-07-03

---

## Scores (1–10)

| Dimension | Score | Brief justification |
|-----------|------:|---------------------|
| **Novelty** | **5** | First integrated measurement program on machine instruction files (AGENTS.md, skills, rules) is timely; standout empirical angle is born-stale dominance and audit decomposition—not a new theory. Survival framing, link rot, and agent-context use are known mechanism classes. See `docs/NOVELTY_AUDIT.md`. |
| **Technical depth** | **4** | Mechanical VERIFIED/MISSING pipeline, KM survival, multi-state tables, and matched churn are competent but standard. No new algorithms, formal models, or identification proofs. Conceptual DAG is placeholder (`paper/sections/03-conceptual-model.tex`). |
| **Empirical rigor** | **4** | Observational scale is real (339k observations). Audits (0/121 decay, GFC 1200/1405) depend on deterministic heuristics with minimal LLM/human escalation. RQ5 is incomplete (22/35 A/B cases, 63 triplets), single agent, ~12% success, wide CIs—null A−B is honest but inconclusive. |
| **Methodological rigor** | **3** | Multiple RQs without pre-registered primary estimand across the program; multiplicity uncontrolled. RQ5 protocol v1.1 exceeds execution (one agent vs 2–3 specified). Trace constructs unvalidated. Born-stale vs post-decay separation is good hygiene but not a registered SAP. |
| **Reproducibility** | **5** | Frozen exports, evidence CSV, and freeze discipline are strengths. Weakened by workspace-local artifacts (`p4_validation.md`, `rq5_results.csv`, `rq5_agent_impact_c/`), stale `rq5_summary.md`, empty `paper/figures/`, and Makefile TODO in §8. |
| **Generality** | **3** | E1-100 enriched engineering cohort (explicitly not population sample). Claude Code CLI only. Instruction injection protocol → 100% read tautology. No README arm, no IDE agents, no semantic gold. |
| **Writing** | **2** | Skeleton, not submission draft: `\todo{}` in §1–§4, §8; Figure 1 placeholder box; empty `references.bib`; no related work; authors/metadata TODO; §5 reads as export paste; `threats_revised.tex` not wired in. |
| **Conceptual contribution** | **4** | Late-binding two-channel frame is clarifying as **vocabulary** and motivates separating Truth Decay from Truth Debt. It is **not** empirically validated; channel factorial absent; risks sounding like post-hoc naming (Reviewer #2 simulation). |
| **Overall acceptance probability** | **~5%** | **Desk-reject likely** in current form (incomplete draft + overclaimed abstract vs evidence). Conditional on major reframe below, revising to a **single-RQ measurement paper** might reach **15–25%** at TOSEM; with completed RQ5 factorial + multi-agent replication, **35–45%** is plausible—not achievable by tomorrow without new runs. |

**Scale:** 1 = clearly below bar; 5 = borderline workshop/topical track; 7 = competitive TOSEM revise; 9 = strong accept; 10 = exceptional.

---

## Submission blockers (tomorrow)

| Severity | Issue |
|----------|--------|
| **Fatal** | Manuscript not compile-ready as a scientific article (TODOs, no bibliography, placeholder figure). |
| **Fatal** | Abstract claims a validated multi-RQ program + late-binding model; evidence supports **bounded measurement + exploratory null pilot** only. |
| **Fatal** | RQ5 causal arm incomplete and underpowered; cannot support central coupling claim at TOSEM bar. |
| **Major** | No related work section—unacceptable for TOSEM. |
| **Major** | Zero figures in `paper/figures/`; results section has figure TODO. |
| **Major** | Generality and construct validity threats dominate (single agent, mechanical truth, injection). |

---

## What is strong enough to build on

| Asset | TOSEM value |
|-------|-------------|
| Longitudinal panel on instruction files | Corpus + measurement contribution |
| Born-stale autopsy + GFC | **Primary publishable finding** if framed conservatively |
| RQ2 failure audit (0/121, 73.6% artifacts) | Sharp bound, audit-limited |
| RQ5 uptake + null A−B | Exploratory pilot; not headline |
| `threats_revised.tex`, evidence freeze, novelty audit | Mature internal discipline—not yet in paper |

---

## Score detail by TOSEM expectations

### Novelty (5/10)
TOSEM rewards new **phenomena** or **methods** with evidence. New **artifact class** measurement is mid-tier novelty. “Late binding” as discovery is weak; born-stale dominance in this cohort is the defensible hook.

### Technical depth (4/10)
Depth is in engineering of audits and panel, not in theory or algorithms. KM and multi-state are textbook applications.

### Empirical rigor (4/10)
Large-N observational work is solid; causal claims are not. Audits improve on raw counts but are not independently validated.

### Methodological rigor (3/10)
Protocol exists but execution diverges. No equivalence tests, no pre-registration, post-hoc mediation strata.

### Reproducibility (5/10)
Better than average intent; worse than average artifact packaging for ACM badge.

### Generality (3/10)
Specialized cohort, one agent, lab protocol—TOSEM will ask “so what for the field?”

### Writing (2/10)
Internal lab scaffold, not a submission.

### Conceptual contribution (4/10)
Useful distinction (static integrity vs runtime consumption vs outcome); needs “illustrative framework” labeling.

---

## Acceptance probability breakdown

| Scenario | P(accept) | Notes |
|----------|----------:|-------|
| **Submit `paper/` as-is tomorrow** | **~3–5%** | Desk reject or 1-page reject: incomplete + overclaim |
| **Tomorrow + full prose polish only** (TODOs, bib, figures copied, threats_revised) | **~8–12%** | Still fundamental identification/generality gaps |
| **Reframe to single-RQ measurement paper** (born-stale dominates; RQ5 appendix) | **~15–25%** | Honest TOSEM empirical note; still needs writing |
| **Complete RQ5 + multi-agent + committed artifact** (months) | **~35–45%** | Competitive if claims match evidence |
| **Field-changing late-binding theory paper** | **<2%** | Not supported by frozen evidence |

**Overall acceptance probability (tomorrow, as planned): ~5%.**

---

## The single change that would increase acceptance probability the most

**Reframe the submission as one primary empirical contribution—not a validated late-binding model—and demote everything else.**

Concretely:

1. **New title and thesis (example):** *Born-Stale References Dominate Static Integrity Signals in Machine-Consumed Instruction Files: A Longitudinal Measurement Study*  
2. **One primary RQ:** What is the decomposition of referential integrity failures (born-stale vs post-verification decay vs measurement artifact) in a longitudinal panel of agent instruction files?  
3. **Primary results:** 17,747 born-stale vs 121 post-verification events; 0/121 adjusted genuine decay; GFC 6.76% born-false; taxonomy + audits.  
4. **RQ5:** One short subsection or appendix titled *Exploratory pilot (incomplete)*—report uptake, null A−B, n=63, single agent, **no Truth Debt promotion**.  
5. **Late-binding model:** Move to §Discussion as *conceptual vocabulary*, explicitly **not tested**.  
6. **Drop or appendix:** RQ3/RQ4 unless one paragraph each serves the primary RQ.

**Why this one change dominates:**  
Tomorrow’s fatal risk is not missing a figure—it is **claim–evidence mismatch**. Reviewers will accept a narrow, honest measurement paper far sooner than a theory paper whose causal arm is incomplete, whose model is a placeholder, and whose abstract promises validation. Reframing aligns the manuscript with the **strongest frozen evidence** (born-stale audit line), sidesteps the weakest (validated two-channel model, Truth Debt, general agent law), and turns RQ5 from a liability into a bounded future-work hook.

**Expected ΔP(accept):** ~5% → **~15–25%** with accompanying writing completion; larger gains require experiments you cannot run before tomorrow.

**If reframing is impossible:** the single change with highest impact is **do not submit tomorrow**—acceptance probability of a future well-scoped paper exceeds near-certain desk reject.

---

## Minimum checklist if submitting anyway (does not replace reframe)

| Item | Status |
|------|--------|
| Remove all `\todo{}` | ❌ |
| Related work (≥30 citations) | ❌ |
| Figure 1 DAG + ≥4 results figures | ❌ |
| Swap in `threats_revised.tex` | ❌ |
| Abstract matches downgraded claims | ❌ |
| Artifact tarball at submission SHA | ❌ |
| Author metadata | ❌ |

---

## Document control

| Field | Value |
|-------|--------|
| Version | v1 |
| Date | 2026-07-03 |
| Inputs | `paper/`, frozen exports, `NOVELTY_AUDIT.md`, `REVIEWER2_SIMULATION.md`, `SCIENTIFIC_EVIDENCE_FREEZE.md` |
