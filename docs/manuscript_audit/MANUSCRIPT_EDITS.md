# Manuscript Edits — RQ5 Feasibility Failure Refactor

**Binding facts:** Blind LB/material-necessity annotation NOT FEASIBLE (35/35 circular); v2 kit DO NOT DISTRIBUTE; 73% mediation must not explain the null; prefer deletion over soft unsupported rewrites.

Companion docs: `RQ5_DEPENDENCY_MAP.md`, `RQ5_CLAIM_AUDIT.md`, `MANUSCRIPT_CHANGE_PLAN.md`.

---

## Title / framing recommendation (Phase 9)

| Item | Decision |
|------|----------|
| Title | **KEEP** `Late Binding in Machine-Consumed Instruction Files` |
| Justification | Surviving evidence still supports late binding as the organizing model: static panel integrity ≠ runtime resolution; directive presence expands edit scope; referential-truth swaps need not move pytest-gated success in the exploratory pilot. Shifting the title to “reference decay” alone would understate the directive/runtime layer and over-emphasize a rot narrative the audits already demote. Optional subtitle (not applied): observational characterization of instruction-reference integrity. |

---

## Edit log

For each edit: **old** → **new**, reason, scientific justification.

### E1 — `paper/main.tex` (Abstract)

| Field | Text |
|-------|------|
| **Old** | Controlled A/B/C “experiment”; contribution separates observational truth decay from **causal** operational cost; no statement that LB validation failed. |
| **New** | “exploratory A/B/C agent pilot”; contribution keeps mechanical misalignment separate from **unestablished** operational harm; explicitly states material-necessity (load-bearing) validation was **not achievable** under the frozen task design. |
| **Reason** | Abstract must not imply confirmatory causal RQ5 or validated LB. |
| **Scientific justification** | Class A pilot metrics retained; Class C/D confirmatory framing removed (Claim Audit A2 / D). |

### E2 — `sections/01-introduction.tex`

| Field | Text |
|-------|------|
| **Old** | “null **causal** contrast”; program promised confirmatory causal contrasts; contributions included causal load-bearing as delivered vocabulary/result. |
| **New** | “null **paired success** contrast in an exploratory pilot”; descriptive agent-run contrasts; contributions drop validated LB / causal load-bearing as delivered; Truth Debt labeled unestablished. |
| **Reason** | Intro must not promise confirmatory RQ5 or measured LB. |
| **Scientific justification** | Estimand separation (A3) kept; measured LB (C/D) removed. |

### E3 — `sections/02-background.tex`

| Field | Text |
|-------|------|
| **Old** | G3: withhold Truth Debt unless controlled experimentation **demonstrates** downstream cost; presupposed “causal results.” |
| **New** | G3: withhold unless construct-valid evidence shows cost; pilot does **not** establish cost; material-necessity validation not achievable; cross-ref `sec:threats-lb-validation`. |
| **Reason** | Avoid “demonstrates”; record failed validation as design fact. |
| **Scientific justification** | Withholding Truth Debt remains Class A; positive cost demonstration is D. |

### E4 — `sections/03-conceptual-model.tex` + `tables/constructs.tex`

| Field | Text |
|-------|------|
| **Old** | C4/C5 and table row treated **causal load-bearing** / non-LB anchors as evidenced moderators (null A−B as LB evidence). |
| **New** | Task difficulty + **hypothesized** task-critical path; table row “Task-critical (hypothesized) … not independently validated here”; non-LB explanatory clause deleted. |
| **Reason** | Moderator must not be presented as measured. |
| **Scientific justification** | Human LB infeasible (C); mediation LB is B→D for explanatory use. |

### E5 — `sections/04-study-design.tex`

| Field | Text |
|-------|------|
| **Old** | “**causal track** (RQ5) **tests**…”; unrealized “blind human … stratified load-bearing contrasts.” |
| **New** | “**exploratory agent track** … **probes**…” without validated material necessity; planned blinded validation **abandoned** (35/35 no independent task oracle); freeze gaps list “construct-valid load-bearing annotation.” |
| **Reason** | Design must state abandonment, not “pending annotation.” |
| **Scientific justification** | Feasibility report NOT_FEASIBLE; process fact Class A; confirmatory track Class D. |

### E6 — `sections/05-results.tex`

| Field | Text |
|-------|------|
| **Old** | RQ5 framed as operational-harm / Truth Debt bridge; mediation **46/63 (73%) non-load-bearing which explains** null coexistence with follow/use. |
| **New** | Exploratory pilot; descriptive rates and null Δ retained; mediation sentence **deleted as explanation** — retained only as unvalidated heuristic artifact with threats cross-ref; “causal track” → exploratory agent track. |
| **Reason** | Mandatory deletion of 73% explanatory claim. |
| **Scientific justification** | Claim Audit D2 / B1; Rule 2–4. |

### E7 — `sections/06-discussion.tex`

| Field | Text |
|-------|------|
| **Old** | Arguments treating LB mediation / stratified uptake as mechanism; future-work rescue of LB annotation; causal bridge language. |
| **New** | Explicit “what remains / what does not remain” after withdrawing construct-invalid LB validation; Truth Debt not promoted; no RQ5 rescue promises; redirect open questions to new task sampling. |
| **Reason** | Discussion must not depend on Class B/C/D claims. |
| **Scientific justification** | Phases 5 rules; surviving evidence = observational + exploratory pilot only. |

### E8 — `sections/threats_revised.tex`

| Field | Text |
|-------|------|
| **Old** | S-6 soft “exploratory” mediation; E-5 “load-bearing stratum defined but not analyzed”; closing claims omitted LB validation failure; no dedicated abandonment subsection. |
| **New** | New `\paragraph{T-LB}` `\label{sec:threats-lb-validation}` (circularity, non-distribution, integrity argument, observational still valid / LB estimate not independently validated); S-6 forbids confirmatory 73% use; E-5/S-2 demote LB strata; closing claims block validated LB and mediation strata; table 45 threats / +1 Mitigated. |
| **Reason** | Phase 4 mandatory threats rewrite. |
| **Scientific justification** | Feasibility audit; Rule 1; strengthens integrity by non-claim. |

### E9 — `sections/08-reproducibility.tex`

| Field | Text |
|-------|------|
| **Old** | Makefile listed `truth-decay-rq5-mediation` alongside uptake as ordinary regen. |
| **New** | Uptake remains primary; mediation called out as archived heuristic only; note that blind LB kits are not distribution targets. |
| **Reason** | Avoid implying mediation is manuscript-supported evidence. |
| **Scientific justification** | Class B export hygiene. |

### E10 — `sections/09-conclusion.tex`

| Field | Text |
|-------|------|
| **Old** | Late-binding wrap including “causal load on task outcomes”; open questions that invite LB annotation rescue. |
| **New** | Conclusion stands without validated LB: observational audits + exploratory pilot coexistence facts; material necessity not part of supported contributions; open questions require **new task sampling**, not reinterpretation of withdrawn annotation. |
| **Reason** | Phase 8: every sentence must survive if RQ5-LB never existed. |
| **Scientific justification** | Class A only. |

### E11 — `paper/archive/current_claims.md`

| Field | Text |
|-------|------|
| **Old** | Listed causal track and causal load-bearing as contributions. |
| **New** | Aligned with post-feasibility claim set (exploratory track; LB unvalidated; 73% not confirmatory). |
| **Reason** | Archive claim ledger must match live manuscript. |
| **Scientific justification** | Consistency with Claim Audit. |

### E12 — Archive sync

| Field | Text |
|-------|------|
| **Old** | `paper/archive/tex/sections/` held pre-refactor wording. |
| **New** | Synced from live `paper/sections/` (+ `constructs.tex`, `main.tex`). |
| **Reason** | Prevent divergent archive snapshot. |
| **Scientific justification** | Editorial hygiene only. |

---

## Sentence-level abstract audit (Phase 6)

| Sentence theme | Keep? | Class |
|----------------|-------|-------|
| Agents resolve refs at run time; static ≠ runtime | Yes | A |
| Late-binding model + frozen program including exploratory RQ5 | Yes (wording fixed) | A |
| 0/121 genuine decay; 1200/1405 GFC | Yes | A |
| Pilot: read/follow/edit scope; Δ A−B = 0 | Yes as exploratory | A2 |
| Contribution: boundaries; LB validation not achievable; replication package | Yes | A / process |

Removed/avoided: human validation of LB; confirmed material necessity; 73% mediation; “causal operational cost” as identified.

---

## Contribution list after rewrite (Phase 7)

1. Operational vocabulary (directive/referential, static truth, runtime resolution).  
2. Observational evidence: birth-time/classification misalignment >> audited post-verification rot.  
3. Exploratory agent pilot separating presence from referential-truth swaps **without** independently validated material necessity.  
4. Public replication package with claim boundaries.

**Removed contribution:** validated / causal load-bearing analysis.

---

## Checklist (post-edit)

- [x] No confirmatory “causal track proves…” for RQ5.  
- [x] No 73% as explanation in abstract/results/discussion/conclusion.  
- [x] No implication humans validated LB/material necessity.  
- [x] Threats subsection documents abandonment + integrity rationale.  
- [x] Conclusion stands without RQ5-LB.  
- [x] Title retained with justification.
