# Review Response Plan — Manuscript Only

**Scope:** No new experiments, no dataset regeneration, no re-analysis scripts.  
**Goal:** Map every criticism in `docs/REVIEWER2_SIMULATION.md` to what the **current frozen exports** already support and which **manuscript edits** (text, figures copied from exports, tables transcribed from exports) address it.

**Legend — Can we already answer?**

| Code | Meaning |
|------|---------|
| **Yes** | Frozen export + honest framing fully addresses the criticism in prose/table/figure |
| **Partial** | We can bound, qualify, or transparency-report; cannot fully refute without new work |
| **No** | Criticism is valid; manuscript must downgrade claim and defer to future work |

**Figure naming:** `paper/figures/<name>.pdf` ← copy from cited export unless noted.

---

## Executive-level criticisms

| ID | Criticism (summary) | Already answer? | Figure | Table | Section change |
|----|---------------------|-----------------|--------|-------|----------------|
| EV-1 | Post-hoc vocabulary / model not validated | **Partial** | `model-dag.pdf` ← Mermaid in `docs/LATE_BINDING_MODEL_v1.md` | **New:** `tables/model-rq-mapping.tex` — transcribe §3 mapping from model doc + which RQ **illustrates** each edge (not tests) | **§1** reframe contributions as *conceptual framework + empirical bounds*; **§3** add “Illustrative implications (not pre-registered tests)”; **§6** delete “validates”; **§9** same |
| EV-2 | Observational + causal tracks disconnected | **Partial** | `trace-flow.pdf` ← `exports/rq5_agent_impact/figure_trace_flow.pdf` | **New:** `tables/bridge-cases.tex` — transcribe `rq5_case_manifest.csv` columns linking `anchor_reference`, `confirmed_false`, repo to panel cohort | **§4.2** add “Bridge cases” subsection; **§5** cross-reference case anchor to born-stale/GFC constructs |
| EV-3 | RQ5 incomplete / underpowered / confounded | **Yes** (transparency) | `abc-success.pdf` ← `figure_success_rate.pdf` | **New:** `tables/rq5-coverage.tex` — 35 cases, 128 A/B, 105 C, 63 triplets, 13 C-only (from `rq5_abc_comparative_analysis.md`, §4 design) | **Abstract**, **§4.3**, **§5.3**, **§7** internal validity; label RQ5 **exploratory pilot** |
| EV-4 | Key artifacts not in reproducibility bundle | **Partial** | — | **New:** `tables/artifact-index.tex` — list every cited path + git-tracked vs appendix-only note | **§8** replace TODO; add “Availability at submission” honesty box; cite `docs/SCIENTIFIC_EVIDENCE_FREEZE.md` inventory without pointing readers off-paper for core numbers |
| EV-5 | TODO stubs / not submission-ready | **Yes** | All figures copied per `paper/figures/README.md` | Complete `evidence-summary.tex` rows | **§2.1, §4.1, §4.2, §8.2, §1** organization — remove all `\todo{}` |

---

## Abstract + title (`paper/main.tex`)

| ID | Criticism | Already answer? | Figure | Table | Section change |
|----|-----------|-----------------|--------|-------|----------------|
| ABS-1 | “Late-binding model explains consumption” sounds like validated theory | **Partial** | `model-dag.pdf` | `model-rq-mapping.tex` | **Abstract**: “We *propose* a late-binding *framework*”; list bounded findings (i–v) as **observed**, not explained by model alone |
| ABS-2 | 0/121 genuine decay may be heuristic artifact | **Partial** | — | **New:** `tables/rq2-audit-taxonomy.tex` ← `rq2_failure_audit_summary.md` taxonomy | **Abstract** add “after deterministic+LLM audit”; **§5.1**, **§7** construct validity; report 73.6% extractor-artifact row |
| ABS-3 | 1200/1405 ≠ semantic falsehood | **Partial** | `born-stale-taxonomy.pdf`, `gfc-confirmatory.pdf` ← `figure_gfc_confirmatory.pdf` | **New:** `tables/gfc-taxonomy.tex` ← `gfc_confirmatory_summary.md` | **Abstract** replace “false” with “**mechanically confirmed missing at creation**”; **§5.2** define construct |
| ABS-4 | 100% read tautological under injection | **Yes** | `uptake-flow.pdf` | **New:** `tables/uptake-funnel.tex` ← `rq5_uptake_analysis.md` | **Abstract** “when instruction file is **injected per protocol**”; **§4.3** quote protocol injection rule; **§7** |
| ABS-5 | ~100 vs ~2 files = directive channel (unisolated) | **Partial** | `abc-success.pdf` + **New panel:** side-by-side `failure-modes.pdf` | **New:** `tables/abc-behavior.tex` ← `rq5_abc_comparative_analysis.md` aggregate row | **Abstract** “instruction **presence** associated with edit scope”; **§3** directive channel — “presence confound, not isolated manipulation”; **§6.2** |
| ABS-6 | Δ A−B = 0 indistinguishable from null power | **Partial** | `abc-success.pdf` | **New:** `tables/abc-contrasts.tex` — Wilson CIs + bootstrap CIs + McNemar from ABC analysis | **Abstract** add “on **63 paired triplets**; CIs include zero”; **§5.3**, **§7** statistical conclusion validity |

---

## §1 Introduction

| ID | Criticism | Already answer? | Figure | Table | Section change |
|----|-----------|-----------------|--------|-------|----------------|
| §1-F | Central claim stated as finding not definition | **Partial** | `model-dag.pdf` | `constructs.tex` (existing) | **§1** split into *Definition* (two channels) vs *Empirical bounds* (bullet list from exports); move strong causal wording to **§6** with limits |
| §1-1 | Not ordinary documentation — untested vs README | **Partial** | — | **New:** `tables/p5-baseline.tex` ← `p5_human_doc_baseline.md` (91.4% verifiable refs, feasibility PASS) | **§1**, **§2.1**: “P5 establishes comparability **feasibility only**”; **§7** external validity; **§9** future work — no claim of equivalence tested |
| §1-2 | Two-channel split = relabeling prose+links | **Partial** | `born-stale-taxonomy.pdf` | `constructs.tex` + **New:** `tables/channel-examples.tex` — 3–5 rows transcribed from `born_stale_examples.csv` / protocol | **§3** add operational **examples** from frozen exports; state classifier not validated |
| §1-3 | Multi-stage program doesn’t unify estimand | **Partial** | `model-dag.pdf` | `bridge-cases.tex`, `model-rq-mapping.tex` | **§1** contributions: “measurement program” not single estimand; **§4** add study architecture figure/table |
| §1-4 | Reproducibility bundle overstated | **Yes** | — | `artifact-index.tex`, expand `evidence-summary.tex` | **§1** contribution 4 → “claim-to-export index”; **§8** |

---

## §2 Background

| ID | Criticism | Already answer? | Figure | Table | Section change |
|----|-----------|-----------------|--------|-------|----------------|
| §2-M | §2.1 TODO | **Yes** | — | `p5-baseline.tex` | **§2.1** write: define AGENTS.md/skills/rules; contrast README/CONTRIBUTING using P5 numbers |
| §2-1 | Born-stale vs post-decay not novel | **Partial** | `survival.pdf` ← `figure_survival.pdf` | **New:** `tables/decay-definitions.tex` — RQ2 vs born-stale vs GFC | **§2.2** + **§3**; **E3** related work (literature placeholders only — titles TBD by authors, no invented citations) |
| §2-2 | P4 F1 optimistic / file not in artifact | **Partial** | — | **New:** `tables/p4-validation.tex` ← `p4_validation.md` confusion matrix | **§2.3**, **§5** P4: “N=200 pilot, single reviewer”; point to worksheet path in **§8**; do not claim population precision |
| §2-3 | Condition C confounds presence + both channels | **Yes** | `uptake-flow.pdf` | **New:** `tables/rq5-conditions.tex` — A/B/C definitions from `protocol/RQ5_AGENT_IMPACT_EXPERIMENT_v1.md` | **§2.4**, **§4.3**, **§6.2**: explicit confound; A−C is presence+content, not directive-only |

---

## §3 Conceptual Model

| ID | Criticism | Already answer? | Figure | Table | Section change |
|----|-----------|-----------------|--------|-------|----------------|
| §3-F | Model = glossary + missing DAG | **Yes** | **E2:** `model-dag.pdf` export from model doc Mermaid | `constructs.tex`, `model-rq-mapping.tex` | **§3** replace TODO box; add subsection “What the model does **not** claim” |
| §3-1 | Directive channel “strongly shapes” unisolated | **Partial** | `abc-behavior` panel: files_modified bar chart ← transcribe ABC table to `tables/abc-behavior.tex` | `abc-behavior.tex` | **§3** directive paragraph: “**associative** evidence under presence confound”; cite C arm |
| §3-2 | Referential resolved at use time = trivial | **Partial** | `trace-flow.pdf`, `uptake-flow.pdf` | `uptake-funnel.tex` | **§3** frame as **operational trace definition** aligned with protocol, not philosophical claim |
| §3-3 | Load-bearing post-hoc | **Partial** | `mediation-flow.pdf` ← `figure_rq5_mediation_flow.pdf` | **New:** `tables/mediation-roles.tex` ← `rq5_mediation_summary.md` | **§3** define load-bearing as **post-hoc trace taxonomy**; **§5.3** report strata; **§7** |
| §3-4 | 85.4% stability ⇒ peripheral false claims (invalid leap) | **Partial** | `cited-churn.pdf` ← `figure_cited_uncited_churn.pdf` | **New:** `tables/cited-uncited.tex` ← `cited_uncited_summary.md` | **§3** delete implication; move to **§6** as **selection effect only**; add case-level anchor types from `rq5_case_manifest.csv` in **§5** |

---

## §4 Study Design

| ID | Criticism | Already answer? | Figure | Table | Section change |
|----|-----------|-----------------|--------|-------|----------------|
| §4-F | Causal study incomplete | **Yes** | — | `rq5-coverage.tex` | **§4.3** primary analysis = **paired triplets only**; secondary = descriptive A/B, C cohort; stop implying full factorial |
| §4-1 | Corpus selection opaque | **Partial** | `reference-density.pdf` ← `figure_a_reference_density.pdf` | **New:** `tables/cohort-scale.tex` ← `rq1_feasibility.md`, `rq2_summary.md`, `e1_1000/cohort_design.md` if cited | **§4.1** cohort flow + threats from rq1 feasibility; **§7** |
| §4-2 | RQ1–4 multiplicity | **Partial** | — | **New:** `tables/endpoint-hierarchy.tex` — primary vs exploratory endpoints (transcribe from protocol + ABC doc) | **§4.2** label RQ1–4 **descriptive**; **§5** structure; **§7** multiplicity paragraph |
| §4-3 | Audits LLM-sparse | **Yes** | `gfc-confirmatory.pdf` | `rq2-audit-taxonomy.tex`, `gfc-taxonomy.tex` | **§4.2** audit protocol summary: LLM 1/121, 0/1405; **§7** |
| §4-4 | Single agent | **No** | — | `rq5-coverage.tex` (agent column) | **§4.3**, **Abstract**, **§7** external validity — Claude Code only; no generalization claim |
| §4-5 | Design TODOs | **Yes** | — | `cohort-scale.tex`, **New:** `tables/protocol-excerpt.tex` — prompt + test policy from `rq5_case_manifest.csv` / protocol | **§4.1, §4.2, §4.3** fill TODOs from protocol files |

---

## §5 Results

| ID | Criticism | Already answer? | Figure | Table | Section change |
|----|-----------|-----------------|--------|-------|----------------|
| §5-M | Reads like lab wiki | **Yes** | Curate 6–8 figures (see Figure Plan below) | Expand evidence table + domain tables | **§5** restructure: one narrative paragraph per subsection linking figure+table |
| §5-1 | RQ1 scale without extractor bounds | **Partial** | `reference-density.pdf`, `state-transitions.pdf` | `cohort-scale.tex` + **New:** `tables/p3-extraction-bound.tex` ← `p3_rot_incidence.md` | **§5.1** cite P3 bounds; soften VERIFIED/MISSING interpretation |
| §5-2 | 0/121 genuine decay | **Partial** | — | `rq2-audit-taxonomy.tex` | **§5.1** report taxonomy + CI; **§7** |
| §5-3 | 1200 confirmed false semantic overclaim | **Partial** | `born-stale-taxonomy.pdf`, `gfc-confirmatory.pdf` | `gfc-taxonomy.tex` | **§5.2** mechanical definition box |
| §5-4 | 85.4% stability + mean CI crosses 0 | **Yes** | `cited-churn.pdf`, `churn-hist.pdf` ← `figure_churn_difference_hist.pdf` | `cited-uncited.tex` | **§5.2** report **both** paired fraction and mean diff CI |
| §5-5 | RQ3 causal phrasing | **Partial** | `rq3-birth.pdf` ← `figure_rq3_birth_integrity.pdf` | **New:** `tables/rq3-regime.tex` ← `rq3_summary.md` / `rq3_tables.csv` | **§5** new RQ3 subsection; **association only** header; **§6** remove causal wording |
| §5-6 | 100% instruction_read | **Yes** | `uptake-flow.pdf` | `uptake-funnel.tex` | **§5.3** footnote: protocol injection |
| §5-7 | 77.8% followed heuristic | **Partial** | `trace-flow.pdf` | `uptake-funnel.tex` + mediation funnel rows | **§5.3** define heuristic; point to `rq5_uptake_analysis.md` |
| §5-8 | Δ A−B = 0 | **Partial** | `abc-success.pdf` | `abc-contrasts.tex` | **§5.3** primary pre-specified contrast A−B with full stats |
| §5-9 | ~100 files modified | **Partial** | — | `abc-behavior.tex` + cite metric definition from protocol/`rq5_dataset.csv` column description in **§4.3** | **§5.3** report median + mean; **§7** flag for manual validation as limitation (no new audit) |
| §5-10 | A vs C 12.7% vs 7.9% | **Partial** | `abc-success.pdf` | `abc-contrasts.tex` | **§5.3** report as **secondary**, underpowered |

---

## §6 Discussion

| ID | Criticism | Already answer? | Figure | Table | Section change |
|----|-----------|-----------------|--------|-------|----------------|
| §6-F | Reconciles despite null / incomplete | **Partial** | `model-dag.pdf` | **New:** `tables/supported-unsupported.tex` ← `LATE_BINDING_MODEL_v1.md` §8 + evidence CSV | **§6.1** replace “reconciles” with “**consistent with bounded observations**”; **§6.3** Truth Debt unsupported (keep) |
| §6-1 | Task difficulty dominates | **Partial** | `failure-modes.pdf` ← `figure_failure_modes.pdf` | **New:** `tables/failure-reasons.tex` ← `rq5_uptake_analysis.md` | **§6.1**, **§6.4** |
| §6-2 | Why TOSEM if Truth Debt dead | **Partial** | `born-stale-taxonomy.pdf` | `cohort-scale.tex`, `artifact-index.tex` | **§6** new “Contributions to SE measurement”: longitudinal corpus, audit instruments, ABC protocol, uptake funnel |
| §6-3 | Alternatives “weakened” too strong | **Partial** | `uptake-flow.pdf`, `mediation-flow.pdf` | `mediation-roles.tex` | **§6.4** replace “weakened” with “**inconsistent with**” / “**not supported as primary explanation**” |
| §6-4 | Tool implications unvalidated | **No** | — | — | **§6.5** retitle “**Hypothesized** implications”; cite model doc §7 as speculation; **§7** |

---

## §7 Threats to Validity

| ID | Criticism | Already answer? | Figure | Table | Section change |
|----|-----------|-----------------|--------|-------|----------------|
| §7-M | Threats justify rejection but unmitigated | **Partial** | — | `supported-unsupported.tex`, `endpoint-hierarchy.tex` | **§7** add “Mitigations attempted” column: transparency, overlap-only primary analysis, explicit unsupported table |
| §7-1 | Underpowered McNemar | **Partial** | — | `abc-contrasts.tex` | **§7** report discordant pairs 2/2 (A−B), n=63; cite wide CIs from ABC doc |
| §7-2 | instruction_followed heuristic | **Partial** | `trace-flow.pdf` | `uptake-funnel.tex` | **§7** construct validity — expand |

---

## §8 Reproducibility

| ID | Criticism | Already answer? | Figure | Table | Section change |
|----|-----------|-----------------|--------|-------|----------------|
| §8-F | Reproducibility bundle incomplete | **Partial** | — | `artifact-index.tex` | **§8** list all paths; mark “included in submission artifact” vs “available on request at freeze SHA”; do **not** claim full TOSEM artifact badge until committed |
| §8-1 | Makefile TODO | **Yes** | — | **New:** `tables/replication-commands.tex` ← Makefile targets (transcribe) | **§8.2** |
| §8-2 | No experiments → downgrade causal | **Yes** | — | `endpoint-hierarchy.tex` | **§8.3** freeze statement + **§4/Abstract** exploratory label |

---

## §9 Conclusion

| ID | Criticism | Already answer? | Figure | Table | Section change |
|----|-----------|-----------------|--------|-------|----------------|
| §9-1 | “Behave as late-binding” overstates | **Partial** | — | — | **§9** “evidence **is consistent with** a late-binding framing”; list **what was not shown** |
| §9-2 | Future work = paper should have done | **Partial** | — | `rq5-coverage.tex` | **§9** keep future work; add “**Scope of current submission**” bullet list mirroring what **is** complete |

---

## Ranked FATAL criticisms (F1–F9)

| ID | Already answer? | Figure | Table | Section change |
|----|-----------------|--------|-------|----------------|
| **F1** Model not tested | **Partial** | `model-dag.pdf` | `model-rq-mapping.tex`, `supported-unsupported.tex` | **§3** rename “Conceptual framework”; **§1, §6, §9** remove “validate/test”; add “Illustrative predictions” with status column (supported / unsupported / not tested) |
| **F2** RQ5 incomplete | **Yes** | — | `rq5-coverage.tex` | **Abstract, §4.3, §5.3, §7, §9** — primary analysis scope; figure caption notes n=63 |
| **F3** Single agent | **No** | — | `rq5-coverage.tex` | **§7** external validity; **§9** future work; strip multi-agent implication from **Abstract** |
| **F4** 100% read tautology | **Yes** | `uptake-flow.pdf` | `uptake-funnel.tex`, `protocol-excerpt.tex` | **§4.3, §5.3, §7** — relabel metric “protocol-attended instruction file” |
| **F5** Channels not isolated | **Partial** | `abc-behavior` (presence contrast only) | `rq5-conditions.tex`, `abc-behavior.tex` | **§3, §6.2** explicit: channels **defined**, not **factorially separated**; D/E conditions = future work |
| **F6** 0/121 audit circularity | **Partial** | — | `rq2-audit-taxonomy.tex` | **§5.1, §7** report rule pipeline + 73.6% artifact; “0 genuine **under audit rules**” |
| **F7** Artifact paths not git-tracked | **Partial** | — | `artifact-index.tex` | **§8** transparency; manuscript cites summaries that **are** tracked; defer raw CSV to artifact note |
| **F8** Weak coupling vs power | **Partial** | `abc-success.pdf` | `abc-contrasts.tex`, `mediation-roles.tex`, `endpoint-hierarchy.tex` | **§5.3** report load-bearing subset counts from mediation (descriptive); **§6, §7** “cannot distinguish null effect from low power” |
| **F9** Not TOSEM-shaped | **Partial** | Figure Plan (curated) | `endpoint-hierarchy.tex`, `supported-unsupported.tex` | **§1** single RQ: “How do static integrity, runtime uptake, and task outcomes relate in machine instruction files?”; **E3** related work; split optional online appendix for RQ3/RQ4 depth |

---

## Ranked MAJOR criticisms (M1–M12)

| ID | Already answer? | Figure | Table | Section change |
|----|-----------------|--------|-------|----------------|
| **M1** Mechanical ≠ semantic false | **Partial** | `gfc-confirmatory.pdf` | `gfc-taxonomy.tex` (template/normative rows) | **§5.2, §7** define “confirmed_false”; show 150 template (10.7%) in taxonomy |
| **M2** Trace heuristics unvalidated | **Partial** | `trace-flow.pdf` | `uptake-funnel.tex` + protocol trace definitions in `protocol-excerpt.tex` | **§4.3, §5.3, §7** |
| **M3** files_modified ~100 implausible | **Partial** | — | `abc-behavior.tex` | **§4.3** metric definition from frozen schema; **§5.3** mean+median; **§7** “metric not manually audited in this submission” |
| **M4** C confounds channels | **Yes** | `uptake-flow.pdf` | `rq5-conditions.tex` | **§2.4, §4.3, §6.2, §7** |
| **M5** Stability ≠ load-bearing | **Partial** | `cited-churn.pdf` | `bridge-cases.tex` (anchor_reference_type per case) | **§3, §6** remove leap; **§5** case table |
| **M6** RQ3 causal language | **Yes** | `rq3-birth.pdf` | `rq3-regime.tex` | **§5** new RQ3 results; **§6** association-only |
| **M7** P4 single reviewer / uncommitted | **Partial** | — | `p4-validation.tex` | **§2.3, §5, §8** pilot disclaimer |
| **M8** Mediation vs A−B inconsistency | **Partial** | `mediation-flow.pdf`, `failure-modes.pdf` | `mediation-roles.tex` | **§5.3** new mediation subsection; **§6.4** explain heuristic failure roles ≠ marginal success effect |
| **M9** No human doc arm | **No** | — | `p5-baseline.tex` | **§2.1, §7, §9** P5 feasibility only |
| **M10** Multiplicity | **Partial** | — | `endpoint-hierarchy.tex` | **§4.2, §5** designate **one** primary RQ5 contrast (A−B); RQ1–4 descriptive |
| **M11** Born-stale strata ignored in RQ5 | **Partial** | `born-stale-taxonomy.pdf` | **New:** `tables/rq5-by-ref-type.tex` — aggregate `rq5_case_manifest.csv` by `anchor_reference_type` | **§5.3** descriptive strata table (no new stats) |
| **M12** Niche corpus | **Partial** | `born-stale-by-repo.pdf` ← `figure_born_stale_by_repository.pdf` | `cohort-scale.tex` | **§4.1, §7** selection bias; `rq1_feasibility.md` threats |

---

## Ranked MINOR criticisms (m1–m9)

| ID | Already answer? | Figure | Table | Section change |
|----|-----------------|--------|-------|----------------|
| **m1** Abstract overclaims late binding | **Partial** | — | — | **Abstract** rewrite per ABS-1 |
| **m2** Repair definition mismatch | **Yes** | `repair-latency.pdf` ← `figure_c_repair_latency.pdf` | **New:** `tables/repair-definitions.tex` ← RQ1 vs RQ2 vs RQ4 definitions | **§5.1** paragraph “Repair constructs differ by RQ” |
| **m3** Missing CIs in prose | **Yes** | — | `abc-contrasts.tex`, `gfc-taxonomy.tex`, `rq2-audit-taxonomy.tex` | **§5** every proportion with CI from exports |
| **m4** Cohen's h narrative | **Yes** | — | `abc-contrasts.tex` | **§5.3** report h=0.1575 for A−C with “exploratory, CI includes zero” |
| **m5** Execution time ignored | **Yes** | — | Add rows to `abc-behavior.tex` from ABC analysis | **§5.3** one sentence or **§7** “no meaningful difference” |
| **m6** Stale rq5_summary.md | **Yes** | — | `artifact-index.tex` | **§8** “Deprecated exports” footnote; do not cite `rq5_summary.md` in paper |
| **m7** P4 path not in artifact | **Partial** | — | `p4-validation.tex`, `artifact-index.tex` | Cite `p4_attribution_precision.md` + worksheet path in **§8**; full metrics in **table** transcribed from local validation export |
| **m8** RQ4 occupancy underplayed | **Yes** | `rq4-occupancy.pdf` ← `figure_rq4_state_occupancy.pdf` | **New:** `tables/rq4-occupancy.tex` ← `rq4_summary.md` | **§5** add RQ4 subsection (short) |
| **m9** Cost transparency | **Partial** | — | **New:** `tables/rq5-cost.tex` — if `cost_usd` column in `rq5_results.csv` / traces, transcribe totals | **§4.3** or **§8** one row budget table; if absent, omit |

---

## EDITORIAL (E1–E8)

| ID | Already answer? | Figure | Table | Section change |
|----|-----------------|--------|-------|----------------|
| **E1** TODO placeholders | **Yes** | — | — | **§2.1, §4.1, §4.2, §8.2, §1** |
| **E2** Figure 1 TODO box | **Yes** | `model-dag.pdf` | — | **§3** `\includegraphics` |
| **E3** Empty bibliography | **No** (writing) | — | — | **§2** related work subsections; `references.bib` — **authors must add real citations** (plan lists topics only: doc drift, LLM context, traceability, survival bias) |
| **E4** Author metadata TODO | **Yes** | — | — | `main.tex` front matter |
| **E5** Organization TODO | **Yes** | — | — | **§1** roadmap paragraph |
| **E6** Empty paper/figures | **Yes** | Copy all from Figure Plan | — | **§5** `\includegraphics` |
| **E7** Internal doc paths in prose | **Yes** | — | — | Remove `\path{docs/LATE_BINDING_MODEL_v1.md}` from **§3, §6, §8**; inline minimal definitions |
| **E8** CCS/keywords | **Yes** | — | — | **main.tex** add keywords: empirical software engineering, measurement, pilot study, threats to validity |

---

## Occam narrative (reviewer synthesis)

| Criticism | Already answer? | Figure | Table | Section change |
|-----------|-----------------|--------|-------|----------------|
| Occam-1..6 simpler story fits all numbers | **Partial** | `model-dag.pdf` + RQ5 trio | `supported-unsupported.tex` | **§6** new subsection “Alternative: parsimonious account” — concede Occam fits; argue framework **organizes** measurements and **separates** constructs for tooling; do not claim Occam is falsified |

---

## Minimum bar items (reconsideration list) — manuscript-only stance

| Reviewer demand | Already answer? | Figure | Table | Section change |
|-----------------|-----------------|--------|-------|----------------|
| Complete ABC 35 cases | **No** | — | `rq5-coverage.tex` | **§9** future work; **§4** scope limitation |
| ≥2 agents | **No** | — | — | **§7, §9** |
| Human-validated traces | **No** | `trace-flow.pdf` (heuristic) | `uptake-funnel.tex` | **§7** |
| Factorial D/E | **No** | — | `rq5-conditions.tex` | **§3, §9** |
| Independent decay audit | **No** | — | `rq2-audit-taxonomy.tex` | **§7** |
| Committed artifact DOI | **Partial** | — | `artifact-index.tex` | **§8** |
| Related work | **No** | — | — | **§2**, `references.bib` |
| Downgrade “validated” | **Yes** | — | `supported-unsupported.tex` | **Abstract, §1, §6, §9** |

---

## Figure plan (copy-only, no regeneration)

| Paper fig | Export source | Primary criticisms addressed |
|-----------|---------------|------------------------------|
| `model-dag.pdf` | `docs/LATE_BINDING_MODEL_v1.md` §2 Mermaid | F1, §3-F, E2, EV-1 |
| `born-stale-taxonomy.pdf` | `exports/truth_decay_pilot/figure_born_stale_taxonomy.pdf` | ABS-3, §5-3, M11, M12 |
| `gfc-confirmatory.pdf` | `figure_gfc_confirmatory.pdf` | ABS-3, M1 |
| `cited-churn.pdf` | `figure_cited_uncited_churn.pdf` | §5-4, M5, §3-4 |
| `churn-hist.pdf` | `figure_churn_difference_hist.pdf` | §5-4 |
| `survival.pdf` | `figure_survival.pdf` | §2-1 |
| `reference-density.pdf` | `figure_a_reference_density.pdf` | §4-1, §5-1 |
| `state-transitions.pdf` | `figure_d_state_transitions.pdf` | §5-1 |
| `rq3-birth.pdf` | `figure_rq3_birth_integrity.pdf` | §5-5, M6 |
| `rq4-occupancy.pdf` | `figure_rq4_state_occupancy.pdf` | m8 |
| `uptake-flow.pdf` | `exports/rq5_agent_impact/figure_uptake_flow.pdf` | ABS-4, F4, §5-6, M4 |
| `trace-flow.pdf` | `figure_trace_flow.pdf` | §5-7, M2 |
| `mediation-flow.pdf` | `figure_rq5_mediation_flow.pdf` | §3-3, M8 |
| `failure-modes.pdf` | `figure_failure_modes.pdf` | §6-1 |
| `abc-success.pdf` | `figure_success_rate.pdf` | ABS-5, ABS-6, F8, §5-8 |
| `born-stale-by-repo.pdf` | `figure_born_stale_by_repository.pdf` | M12 |

---

## Table plan (new LaTeX fragments under `paper/tables/`)

| Table file | Source export | Primary criticisms |
|------------|---------------|-------------------|
| `constructs.tex` | model doc | existing |
| `evidence-summary.tex` | evidence CSV | existing — expand rows |
| `model-rq-mapping.tex` | `LATE_BINDING_MODEL_v1.md` §3 | F1, EV-1, §1-3 |
| `supported-unsupported.tex` | model doc §8 + evidence CSV | §6-F, F1, Occam |
| `endpoint-hierarchy.tex` | protocol + ABC doc | §4-2, M10, F8 |
| `cohort-scale.tex` | rq1, rq2 summaries | §4-1, §5-1, M12 |
| `rq2-audit-taxonomy.tex` | rq2_failure_audit_summary | ABS-2, F6, §5-2 |
| `gfc-taxonomy.tex` | gfc_confirmatory_summary | ABS-3, M1 |
| `cited-uncited.tex` | cited_uncited_summary | §5-4, M5 |
| `rq3-regime.tex` | rq3_summary / rq3_tables.csv | §5-5, M6 |
| `rq4-occupancy.tex` | rq4_summary | m8 |
| `p4-validation.tex` | p4_validation.md | §2-2, M7, m7 |
| `p5-baseline.tex` | p5_human_doc_baseline | §1-1, M9 |
| `rq5-conditions.tex` | protocol v1.1 | §2-3, M4, F5 |
| `rq5-coverage.tex` | rq5_abc + design section | F2, §4-F, m1 |
| `protocol-excerpt.tex` | protocol + case manifest | §4-5, F4, M2 |
| `uptake-funnel.tex` | rq5_uptake_analysis | ABS-4, §5-6, §5-7 |
| `abc-behavior.tex` | rq5_abc_comparative_analysis | ABS-5, §5-9, M3, F5 |
| `abc-contrasts.tex` | rq5_abc_comparative_analysis | ABS-6, F8, m3, m4 |
| `mediation-roles.tex` | rq5_mediation_summary | §3-3, M8, F8 |
| `failure-reasons.tex` | rq5_uptake_analysis | §6-1 |
| `bridge-cases.tex` | rq5_case_manifest.csv | EV-2, M5 |
| `rq5-by-ref-type.tex` | rq5_case_manifest.csv | M11 |
| `repair-definitions.tex` | rq1, rq2, rq4 summaries | m2 |
| `artifact-index.tex` | SCIENTIFIC_EVIDENCE_FREEZE inventory | F7, §8-F, m6 |
| `replication-commands.tex` | Makefile | §8-1 |
| `channel-examples.tex` | born_stale_examples.csv | §1-2 |

---

## Section edit checklist (ordered)

1. **`main.tex` (Abstract)** — ABS-1–6, m1, F2–F4 framing, E8 keywords  
2. **`01-introduction.tex`** — §1-F, §1-1–4, E5, F9 single RQ  
3. **`02-background.tex`** — E1 §2.1, §2-1–4, E3 related work skeleton  
4. **`03-conceptual-model.tex`** — E2, F1, F5, §3-1–4, E7 remove internal paths  
5. **`04-study-design.tex`** — E1 §4.1–4.2, §4-F, §4-1–5, endpoint hierarchy  
6. **`05-results.tex`** — §5-M restructure; add RQ3/RQ4/mediation subsections; all tables/figures  
7. **`06-discussion.tex`** — §6-F, Occam subsection, §6-1–4, downgrade §6.5  
8. **`07-threats.tex`** — §7-M, F3, F6, F8, all major threats explicit  
9. **`08-reproducibility.tex`** — §8-F, E1 §8.2, artifact index, m6  
10. **`09-conclusion.tex`** — §9-1–2, scope vs future work  
11. **`references.bib`** — E3 (real citations by authors)  
12. **`paper/figures/`** — E6 copy PDFs  

---

## What manuscript improvements **cannot** do (explicit non-answers)

These criticisms remain **open** after writing alone; paper must **not** imply otherwise:

- F2 complete 35-case A/B, F3 multi-agent, F5 factorial channel separation, F6 blind human audit, M2 trace κ, M9 README arm, M7 second P4 reviewer, independent decay replication, TOST/equivalence (unless numbers transcribed from existing `rq5_effect_sizes.csv` without new analysis — **omit** if not already computed in export).

For each, **§7 + §9 + endpoint-hierarchy table** must list as **out of scope for this submission**.

---

## Document control

| Field | Value |
|-------|-------|
| Version | v1 |
| Date | 2026-07-03 |
| Input | `docs/REVIEWER2_SIMULATION.md` |
| Constraint | Manuscript improvements only; no experiments |
