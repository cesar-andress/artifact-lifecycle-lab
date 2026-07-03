# Paper Argument — ACM TOSEM

**Working title:** *Late Binding in Machine-Consumed Instruction Files*  
**Audience:** ACM Transactions on Software Engineering and Methodology  
**Mode:** Paper-writing — frozen evidence only  
**Sources:** `docs/LATE_BINDING_MODEL_v1.md`, `paper/main.tex`, `exports/paper_synthesis/late_binding_evidence_table.csv`, `docs/SCIENTIFIC_EVIDENCE_FREEZE.md`

**Format rule:** Each argumentative step is one logical unit; the final line cites supporting exports (no external literature).

---

## 1. What is the problem?

**P1.1** Teams now ship machine-consumed instruction files (AGENTS.md, skills manifests, IDE rule packs) alongside code; agents treat these artifacts as operational input, not optional prose.

**Evidence:** `paper/main.tex` (abstract, lines 39–40); `docs/LATE_BINDING_MODEL_v1.md` (§Core thesis, lines 12–15).

---

**P1.2** Practitioners and tooling implicitly assume a single documentation semantics: text is “true” if it matched the repository when written, and becomes harmful when it “rots” over time.

**Evidence:** `docs/LATE_BINDING_MODEL_v1.md` (§Core thesis, lines 17–22: static truth vs runtime resolution split); `paper/main.tex` (abstract, line 41: “resolved against the live repository at use time”).

---

**P1.3** Under that assumption, the engineering problem is framed as **truth decay**—keeping instruction-file references synchronized with the repository so agents do not fail on stale pointers.

**Evidence:** `exports/truth_decay_pilot/rq1_feasibility.md` (RQ1: “How does the truth of machine-consumed documentation evolve over time?”); `exports/truth_decay_pilot/rq2_summary.md` (RQ2 survival on VERIFIED→MISSING transitions, 4521 references, 121 failures).

---

**P1.4** The actual failure mode is underspecified: observational panels report large MISSING mass, but MISSING conflates born-false references, extractor noise, templates, anchor mismatches, and genuine post-verification decay.

**Evidence:** `exports/truth_decay_pilot/born_stale_summary.md` (17,747 born-stale references; 7 heterogeneous taxonomy categories); `exports/truth_decay_pilot/rq1_feasibility.md` (missing ratio 36.4%, unverifiable 51.9%, verified 11.1%).

---

**P1.5** Causal impact is also underspecified: even if static references are wrong, it is unknown whether agents **read**, **bind**, and **act** on them, or whether task environment dominates outcomes.

**Evidence:** `exports/rq5_agent_impact/rq5_redesign_plan.md` (AB_v1 incomplete without condition C baseline); `exports/paper_synthesis/late_binding_evidence_table.csv` (rows: instruction read, instruction followed, paired success difference).

---

**P1.6 — Problem statement (conclusion):** The field lacks a empirically grounded account of how machine-consumed instruction files combine **static referential integrity**, **runtime agent binding**, and **task environment**—and therefore misallocates research and tooling effort toward “decay” alone.

**Evidence:** `docs/LATE_BINDING_MODEL_v1.md` (§9 Synthesis, lines 221–223: separate integrity of static artifact from operational cost of consumption); `docs/SCIENTIFIC_EVIDENCE_FREEZE.md` (US-06: Truth Debt promotion unsupported).

---

## 2. Why does the community currently think differently?

**B2.1 — Belief A (static-documentation equivalence):** Instruction files are the same class of artifact as README/CONTRIBUTING: descriptive, human-audited, evaluated by whether text matched the repo at authoring time.

**Evidence:** `docs/LATE_BINDING_MODEL_v1.md` (§4 Alternative “Instruction files are static docs”, line 160); `exports/truth_pilot/p5_human_doc_baseline.md` (within-repo machine vs human doc comparison feasible—treated as comparable surfaces, not yet causally tested).

---

**B2.2 — Belief B (decay-centric narrative):** The dominant integrity failure is **post-verification reference decay**—references that were once VERIFIED and later go MISSING—because longitudinal panels surface VERIFIED→MISSING transitions.

**Evidence:** `exports/truth_decay_pilot/rq2_summary.md` (121 first-missing events among 4521 verified-at-origin references, 2.7%); `exports/truth_decay_pilot/rq1_feasibility.md` (18,473 first-failure events, 1,650 files with ≥1 missing).

---

**B2.3 — Belief C (operational harm from falsity):** Statically false referential content reliably **harms** agent task success; keeping references truthful **improves** success (Truth Debt as causal claim).

**Evidence:** `docs/LATE_BINDING_MODEL_v1.md` (§8 Unsupported: “False instructions reliably harm agent success”, “True instructions reliably help”, lines 207–209); `paper/main.tex` (abstract, line 41: tests whether static referential truth couples to outcomes).

---

**B2.4 — Belief D (decorative-instruction null):** Null causal effects in agent experiments mean agents **ignore** instruction files; instructions are non-executive decoration.

**Evidence:** `docs/LATE_BINDING_MODEL_v1.md` (§4 Alternative “Decorative instructions”, line 157); `exports/rq5_agent_impact/rq5_mediation_summary.md` (audit question 5: null success effect interpreted as irrelevance vs robustness).

---

**B2.5 — Belief E (robust binding):** When pointers are false, agents **detect and reject** them without acting—robustness explains null success differences between truthful and false referential content.

**Evidence:** `docs/LATE_BINDING_MODEL_v1.md` (§4 Alternative “Agent robustness to false refs”, line 158); `docs/SCIENTIFIC_EVIDENCE_FREEZE.md` (US-05: agents consistently reject false pointers—unsupported).

---

**B2.6 — Belief F (path instability drives staleness):** Instruction files cite paths that churn faster than the rest of the repository; decay is driven by unstable targets.

**Evidence:** `docs/LATE_BINDING_MODEL_v1.md` (§8 Unsupported: “Cited paths are less stable than uncited”, line 213); `exports/truth_decay_pilot/cited_uncited_summary.md` (mean paired churn difference CI crosses zero).

---

**B2.7 — Implicit community stance (synthesis):** Treat instruction files as static human documentation whose primary risk is time-based rot and whose primary remedy is keeping pointers synchronized—measured by longitudinal VERIFIED/MISSING panels and assumed to translate directly into agent failure cost.

**Evidence:** `docs/LATE_BINDING_MODEL_v1.md` (§Core thesis misattribution, line 22); `exports/paper_synthesis/late_binding_evidence_table.csv` (rows 1–6: observational integrity metrics without paired causal success rows).

---

## 3. What evidence overturns that belief?

### 3.1 Against Belief B (decay-centric narrative)

**E3.1a** Adjusted genuine post-verification decay is **0/121** audited failures; genuine-decay proportion among failures **0.0%** (Wilson 95% CI **0.0%–3.1%**).

**Evidence:** `exports/truth_decay_pilot/rq2_failure_audit_summary.md`; `exports/paper_synthesis/late_binding_evidence_table.csv` (row: Zero genuine post-verification decay).

---

**E3.1b** **73.6%** of post-verification failures are classified extractor artifacts (category D), not genuine decay.

**Evidence:** `exports/truth_decay_pilot/rq2_failure_audit_summary.md` (taxonomy table); `late_binding_evidence_table.csv` (row: Post-verification failures are mostly artifacts).

---

**E3.1c** The dominant static falsity mode is **born-stale / confirmed false at creation**, not time-decay: **1,200/1,405** (85.4%, Wilson CI **83.5%–87.2%**) confirmed false in GFC audit; adjusted cohort rate **6.76%**.

**Evidence:** `exports/truth_decay_pilot/gfc_confirmatory_summary.md`; `exports/truth_decay_pilot/born_stale_summary.md` (1,405 raw genuine_false_claim, 7.9% of 17,747); `late_binding_evidence_table.csv` (rows: Confirmed false claims at creation; Born-stale adjusted false-claim rate).

---

**E3.1d — Conclusion:** Post-verification decay is rare in this cohort; prevalence of static falsity is dominated by born-false and heterogeneous non-decay mechanisms—not ongoing rot after verification.

**Evidence:** `docs/SCIENTIFIC_EVIDENCE_FREEZE.md` (SS-01, SS-03, SS-04; US-01 contradicted); `docs/LATE_BINDING_MODEL_v1.md` (§3 mapping, rows 0 genuine decay + 1,200 confirmed false, lines 138–140).

---

### 3.2 Against Belief C (operational harm / help from referential truth)

**E3.2a** On **63** paired A/B/C triplets, success is **12.7%** (8/63) for both truthful (A) and false (B) referential content; paired Δ(A−B) = **0.00 pp**; McNemar **p = 1.0000**; cluster bootstrap 95% CI **[−6.35, +6.35] pp**.

**Evidence:** `exports/rq5_agent_impact/rq5_abc_comparative_analysis.md`; `late_binding_evidence_table.csv` (rows: No success difference A vs B paired; McNemar null A vs B; Success rate truthful/false on triplets).

---

**E3.2b** Truthful vs no-instruction contrast is not statistically reliable: Δ(A−C) = **+4.76 pp** (A **12.7%** vs C **7.9%**), cluster bootstrap CI **[−12.70, +22.22] pp**, McNemar **p = 0.5811**—CI includes zero.

**Evidence:** `exports/rq5_agent_impact/rq5_abc_comparative_analysis.md`; `late_binding_evidence_table.csv` (rows: A minus C paired difference; Success rate no instruction on triplets).

---

**E3.2c** Outcome failure is driven by tests, not compilation: compilation success **100%** (63/63) all conditions; unsuccessful A runs dominated by `tests_failed` (**57**).

**Evidence:** `exports/rq5_agent_impact/rq5_abc_comparative_analysis.md` (compilation_success 100%); `exports/rq5_agent_impact/rq5_uptake_analysis.md` (failure reasons); `late_binding_evidence_table.csv` (rows: Compile success all conditions; Baseline test failure dominates).

---

**E3.2d — Conclusion:** Static referential truth does not differentiate agent task success in this design; environmental task difficulty masks instruction manipulations—Truth Debt as causal claim is not supported.

**Evidence:** `docs/SCIENTIFIC_EVIDENCE_FREEZE.md` (SS-09, US-02, US-03, US-06); `docs/LATE_BINDING_MODEL_v1.md` (§8, lines 207–212).

---

### 3.3 Against Belief D (decorative instructions)

**E3.3a** When instruction files are present, agents exhibit `instruction_read` in **128/128** runs (100%): A **65/65**, B **63/63**.

**Evidence:** `exports/rq5_agent_impact/rq5_uptake_analysis.md`; `late_binding_evidence_table.csv` (row: Instruction read when present); `exports/rq5_agent_impact/figure_uptake_flow.pdf`.

---

**E3.3b** Agents follow anchor references in a majority of runs: `instruction_followed` **72.3%** (47/65) on A, **77.8%** (49/63) on B; false claim used on B **77.8%** (49/63).

**Evidence:** `exports/rq5_agent_impact/rq5_uptake_analysis.md`; `late_binding_evidence_table.csv` (rows: Instruction followed A/B; False claim acted upon condition B).

---

**E3.3c** Instruction presence amplifies behavioral scope even without success gain: mean files modified **99.7** (A), **103.0** (B) vs **1.7** (C) on paired triplets.

**Evidence:** `exports/rq5_agent_impact/rq5_abc_comparative_analysis.md`; `late_binding_evidence_table.csv` (rows: Files modified A/B/C); `docs/LATE_BINDING_MODEL_v1.md` (§3, A/B ~100 vs C ~2, line 147).

---

**E3.3d — Conclusion:** Instructions are executive (read, often followed, expand edit scope)—not ignored; null success effects therefore require a different explanation than non-use.

**Evidence:** `docs/SCIENTIFIC_EVIDENCE_FREEZE.md` (SS-08, SS-10; US-04 contradicted); `docs/LATE_BINDING_MODEL_v1.md` (§4 Decorative instructions **Weakened**, line 157).

---

### 3.4 Against Belief E (robust rejection of false pointers)

**E3.4a** On condition B, **77.8%** of runs use the false anchor in actionable traces; only **7.9%** (5/63) show agent correction in mediation audit.

**Evidence:** `exports/rq5_agent_impact/rq5_mediation_summary.md` (B mediation funnel); `late_binding_evidence_table.csv` (row: False claim acted upon condition B).

---

**E3.4b** Among runs that followed the anchor, success rates are similar across A and B (stratified Δ(A−B) = **−0.014**; B users success **0.163**, n=49)—suggesting non-robust following, not reliable rejection.

**Evidence:** `exports/rq5_agent_impact/rq5_uptake_analysis.md` (§Key questions 3, stratified table); `docs/LATE_BINDING_MODEL_v1.md` (§4 Agent robustness **Partially weakened**, line 158).

---

**E3.4c — Conclusion:** Agents frequently bind to statically false referential content without differential success penalty—robustness is not the explanation for null A−B effects.

**Evidence:** `docs/SCIENTIFIC_EVIDENCE_FREEZE.md` (MS-02, MS-03; US-05 contradicted).

---

### 3.5 Against Belief F (cited paths are unstable)

**E3.5a** In **85.4%** of **2,259** matched pairs (78 repos), cited path git churn ≤ uncited control churn (bootstrap CI **83.9%–86.9%**).

**Evidence:** `exports/truth_decay_pilot/cited_uncited_summary.md`; `late_binding_evidence_table.csv` (row: Cited paths disproportionately stable); `exports/truth_decay_pilot/figure_cited_uncited_churn.pdf`.

---

**E3.5b** Mean paired churn difference (cited − uncited) = **0.44** commits, 95% bootstrap CI **[−0.21, +1.15]**—includes zero; mean churn not significantly different.

**Evidence:** `exports/truth_decay_pilot/cited_uncited_summary.md` (§Interpretation); `docs/SCIENTIFIC_EVIDENCE_FREEZE.md` (MS-05).

---

**E3.5c — Conclusion:** Instruction files disproportionately cite intrinsically stable paths (selection effect)—not fast-churn targets that explain falsity.

**Evidence:** `docs/LATE_BINDING_MODEL_v1.md` (§4 Selection on stable paths **Supported**, line 161); `docs/SCIENTIFIC_EVIDENCE_FREEZE.md` (SS-05).

---

### 3.6 Against Belief A (static-documentation equivalence) — partial overturn

**E3.6a** Longitudinal mechanical verification (VERIFIED/MISSING at commit snapshots) diverges from runtime agent binding traces (`instruction_read` → `instruction_followed` → tool actions) measured only in RQ5.

**Evidence:** `docs/LATE_BINDING_MODEL_v1.md` (§2 Causal DAG: static layer vs runtime layer, lines 86–124); `exports/truth_decay_pilot/reference_longitudinal.csv` + `exports/rq5_agent_impact/rq5_uptake_dataset.csv`.

---

**E3.6b** Agent maintenance of instruction files is measurably attributable (F1 **0.9617**, precision **0.958**, N=200 human gold)—a maintenance regime distinct from human README editing and from runtime task success.

**Evidence:** `exports/truth_pilot/p4_validation.md` (workspace-local; see `docs/SCIENTIFIC_EVIDENCE_FREEZE.md` MS-01); `late_binding_evidence_table.csv` (rows: Agent maintenance attribution validated; precision gate); `exports/truth_decay_pilot/rq3_summary.md` (maintenance regime associations, observational).

---

**E3.6c — Conclusion:** Machine instruction files participate in agent maintenance and runtime consumption pipelines not captured by treating them as static human documentation alone—equivalence to README/CONTRIBUTING is not established causally.

**Evidence:** `docs/SCIENTIFIC_EVIDENCE_FREEZE.md` (US-09 untested); `exports/truth_pilot/p5_human_doc_baseline.md` (feasibility PASS only).

---

### 3.7 Evidence synthesis (overturning step — master conclusion)

| Prior belief | Overturning finding | Primary export |
|--------------|---------------------|----------------|
| Decay is the main integrity failure | 0/121 genuine post-verification decay; 85.4% born-false confirmed at creation | `rq2_failure_audit_summary.md`, `gfc_confirmatory_summary.md` |
| False refs harm agent success | Δ(A−B)=0.00 pp, p=1.0 | `rq5_abc_comparative_analysis.md` |
| Instructions are ignored | 100% read, ~78% follow on B | `rq5_uptake_analysis.md` |
| Agents reject false pointers | 77.8% false_claim_used on B | `rq5_uptake_analysis.md`, `rq5_mediation_summary.md` |
| Cited paths churn faster | 85.4% pairs cited ≤ uncited | `cited_uncited_summary.md` |

**Evidence:** `exports/paper_synthesis/late_binding_evidence_table.csv` (full inventory); `docs/SCIENTIFIC_EVIDENCE_FREEZE.md` (SS-/US- index).

---

## 4. What new conceptual model explains all observations?

### 4.1 Model definition

**M4.1** Machine-consumed instruction files are **late-binding artifacts** with two coupled channels: (1) **directive channel**—normative behavior-shaping text; (2) **referential channel**—pointers resolved against the **live workspace at consumption time**, not at authoring time.

**Evidence:** `docs/LATE_BINDING_MODEL_v1.md` (§Core thesis, §1.1 Two-channel artifact, lines 12–67); `paper/main.tex` (abstract, lines 40–41).

---

**M4.2** Truth splits into **static truth** (mechanical VERIFIED/MISSING at pinned commits in RQ1–RQ4) and **runtime resolution** (agent read/follow/act in RQ5 traces).

**Evidence:** `docs/LATE_BINDING_MODEL_v1.md` (§Core constructs, lines 28–37); `exports/truth_decay_pilot/reference_longitudinal.csv`; `exports/rq5_agent_impact/rq5_uptake_dataset.csv`.

---

### 4.2 Causal structure

**M4.3** Static referential state influences whether binding *can* succeed but does not directly cause task success; success is moderated by **environmental task difficulty** and whether a reference is **causally load-bearing**.

**Evidence:** `docs/LATE_BINDING_MODEL_v1.md` (§2 Causal DAG reading, lines 126–130); `exports/rq5_agent_impact/rq5_mediation_summary.md` (73.0% B runs non-load-bearing; 19.0% false_claim_caused_failure); `exports/rq5_agent_impact/rq5_uptake_analysis.md` (tests_failed dominates).

---

**M4.4** Directive channel can activate without referential grounding: instruction **presence** expands edit scope (~50× files modified) even when referential static truth is swapped (A≈B) or absent (C).

**Evidence:** `exports/rq5_agent_impact/rq5_abc_comparative_analysis.md` (mean files_modified A=99.7, B=103.0, C=1.7); `late_binding_evidence_table.csv` (rows: Files modified A/B/C); `docs/LATE_BINDING_MODEL_v1.md` (§1.1 key implication, lines 69–69).

---

### 4.3 Mapping observations → model (explanatory coverage)

**M4.5 — Observational layer (RQ1–RQ4):** Large born-stale mass + heterogeneous taxonomy + rare genuine post-verification decay ⇒ integrity problem is primarily **initial reference validity and measurement heterogeneity**, not ongoing rot.

**Evidence:** `exports/truth_decay_pilot/born_stale_summary.md` (17,747 cohort, 7 categories); `exports/truth_decay_pilot/gfc_confirmatory_summary.md` (1200 confirmed false); `exports/truth_decay_pilot/rq2_failure_audit_summary.md` (0 genuine decay); `exports/truth_decay_pilot/rq4_summary.md` (64,048 trajectories; 64.2% birth → unverifiable or integrity_loss).

---

**M4.6 — Selection layer:** Cited paths are disproportionately stable ⇒ many false referential claims sit on **peripheral, low-churn** pointers—consistent with weak coupling to task success.

**Evidence:** `exports/truth_decay_pilot/cited_uncited_summary.md` (85.4% paired stability fraction); `docs/LATE_BINDING_MODEL_v1.md` (§3 mapping, line 141).

---

**M4.7 — Runtime layer (RQ5):** Universal read + majority follow + large behavioral amplification + null A−B success ⇒ agents **consume** instructions through both channels, but **static referential truth is filtered** by late binding, load-bearingness, and environment.

**Evidence:** `exports/rq5_agent_impact/rq5_uptake_analysis.md`; `exports/rq5_agent_impact/rq5_abc_comparative_analysis.md`; `docs/LATE_BINDING_MODEL_v1.md` (§3 mapping table, lines 136–149).

---

**M4.8 — Maintenance layer (P4/RQ3):** Agent-attributed edits to instruction files are real and measurable separately from runtime task outcomes ⇒ **maintenance signal** must not be conflated with **consumption outcome**.

**Evidence:** `exports/truth_pilot/p4_validation.md` (F1 0.9617); `exports/truth_decay_pilot/rq3_summary.md` (regime-stratified birth/decay proportions, observational); `late_binding_evidence_table.csv` (P4 rows).

---

**M4.9 — Model conclusion:** The late-binding two-channel model unifies (i) rare post-verification decay, (ii) abundant born-false static claims, (iii) stable-path selection, (iv) executive agent uptake, (v) behavioral amplification without referential-truth success differentiation, and (vi) environment-gated outcomes—without requiring a single “documentation rot” mechanism.

**Evidence:** `docs/LATE_BINDING_MODEL_v1.md` (§9 Synthesis, lines 219–223); `paper/main.tex` (abstract, lines 41–42); `docs/SCIENTIFIC_EVIDENCE_FREEZE.md` (cross-reference index).

---

## 5. Why does this matter for software engineering?

### 5.1 Research methodology

**S5.1** Empirical studies must **separate constructs**: born-stale prevalence, post-verification decay rate, static panel integrity, runtime binding uptake, and causal task success—merging rates produces non-comparable “staleness” metrics.

**Evidence:** `docs/LATE_BINDING_MODEL_v1.md` (§6 implication 4, line 185; §8 lines 207–212); `late_binding_evidence_table.csv` (row: Born-stale adjusted false-claim rate limitation “not interchangeable with post-verification decay rate”); `exports/truth_decay_pilot/rq3_summary.md` (interpretation guardrails).

---

**S5.2** Agent impact experiments require a **no-instruction arm (C)** and **uptake funnel** reporting (read → follow → act → success); A/B alone is uninterpretable when presence changes behavior.

**Evidence:** `exports/rq5_agent_impact/rq5_redesign_plan.md`; `exports/rq5_agent_impact/rq5_abc_comparative_analysis.md` (63 triplets; A−C and A−B contrasts); `late_binding_evidence_table.csv` (row: RQ5 redesign requires condition C).

---

### 5.2 Tooling and practice

**S5.3** Validators should **split directive vs referential content**: lint pointers at **consumption time** (late-binding lint), not only at commit time; static VERIFIED/MISSING panels are insufficient for agent readiness.

**Evidence:** `docs/LATE_BINDING_MODEL_v1.md` (§7 implications 1–2, lines 194–195); `exports/truth_decay_pilot/rq1_feasibility.md` (mechanical verification ≠ semantic truth, threats).

---

**S5.4** Teams should mark **load-bearing vs peripheral references** and collect **read–repair telemetry**; many false claims are followed but non-load-bearing—accounting should not assume agents silently reject bad pointers.

**Evidence:** `docs/LATE_BINDING_MODEL_v1.md` (§7 implications 3–4, lines 196–197); `exports/rq5_agent_impact/rq5_mediation_summary.md` (uptake_but_not_load_bearing 30.2%; obstacle_recovered 7.9%).

---

**S5.5** Agent runtimes need **scope control**: directive-rich instruction presence inflated edit blast radius (~100 files vs ~2 without instruction)—increasing test failure risk independent of referential truth.

**Evidence:** `exports/rq5_agent_impact/rq5_abc_comparative_analysis.md` (files_modified); `docs/LATE_BINDING_MODEL_v1.md` (§7 implication 6, line 199); `docs/LATE_BINDING_MODEL_v1.md` (§5 threat 5: edit surface confound).

---

**S5.6** Maintenance analytics (P4/RQ3) can track **who changes instruction files** (human vs agent regimes) independently of whether those files **help agents succeed** on tasks—supporting governance of agent-generated specification debt without overclaiming runtime harm.

**Evidence:** `exports/truth_decay_pilot/rq3_summary.md` (observational regime differences; explicit no causal claims); `exports/truth_pilot/p4_validation.md` (precision gate PASS); `docs/LATE_BINDING_MODEL_v1.md` (§9: separate Truth Decay observational from Truth Debt conditional, lines 221–223).

---

**S5.7 — SE impact conclusion (for TOSEM):** Software engineering should treat machine-consumed instruction files as **late-binding, two-channel specifications**—subject to born-false static validity, agent maintenance dynamics, and runtime binding behavior—rather than as passive documentation whose primary metric is time-based truth decay.

**Evidence:** `paper/main.tex` (abstract conclusion, line 42); `docs/LATE_BINDING_MODEL_v1.md` (§9); `docs/SCIENTIFIC_EVIDENCE_FREEZE.md` (freeze rules); `exports/paper_synthesis/late_binding_evidence_table.csv` (29 frozen claim rows).

---

## Argument chain (single-page summary)

```
Problem:     Instruction files gate agent behavior, but integrity + impact mechanisms are conflated
             → Evidence: RQ1–RQ4 panel + RQ5 redesign gap (late_binding_evidence_table.csv)

Belief:      Static docs + decay narrative + falsity harms agents + instructions ignored if null
             → Evidence: LATE_BINDING_MODEL_v1.md §4 alternatives; rq2/rq5 summaries

Overturn:    0/121 genuine decay; 1200/1405 born-false; Δ(A−B)=0; 100% read; 77.8% follow false
             → Evidence: rq2_failure_audit, gfc_confirmatory, rq5_abc, rq5_uptake (CSV rows 1–24)

Model:       Directive + referential channels; late binding; static ≠ runtime; environment dominates
             → Evidence: LATE_BINDING_MODEL_v1.md §1–3; rq5_mediation; cited_uncited

SE matter:   Split metrics, ABC designs, split lint, load-bearing markers, scope control, maintenance vs outcome
             → Evidence: LATE_BINDING_MODEL_v1.md §6–7; rq3 guardrails; p4_validation; paper abstract
```

---

## Document control

| Field | Value |
|-------|-------|
| Version | v1 |
| Date | 2026-07-03 |
| Claim authority | `docs/SCIENTIFIC_EVIDENCE_FREEZE.md` |
| Manuscript scaffold | `paper/main.tex` |

**Constraint:** No external citations in this document; literature slots remain `\todo{}` in `paper/sections/`.
