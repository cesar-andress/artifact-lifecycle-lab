# Novelty Audit — Evidence Only

**Scope:** Frozen exports (`exports/`), evidence CSV, protocol summaries. No manuscript prose. No invented citations.  
**Date:** 2026-07-03  
**Stance:** Hostile auditor. Flattery excluded.

---

## Executive answers

### What is genuinely new?

Only a narrow band of **first measurements on a new artifact class** (machine-consumed instruction files: AGENTS.md, skills, IDE rules) plus **one incomplete causal pilot** linking static referential manipulation to agent traces and outcomes. Concretely, from evidence:

1. **A longitudinal panel** at this scale on this document class (2,009 instruction files; 339,646 reference observations) with mechanical VERIFIED/MISSING states over git history.
2. **Quantified decomposition** showing born-at-birth missing mass dominates post-verification transitions in this cohort (17,747 never-VERIFIED vs 121 post-VERIFIED first-missing events; 0/121 adjusted genuine decay after audit).
3. **Confirmatory pass** on a born-false subset (1,200/1,405 confirmed mechanically false at creation; 6.76% adjusted cohort rate).
4. **First-party agent experiment** (in this lab) swapping truthful vs confirmed-false instruction blobs at pinned commits with trace-coded uptake and a null paired success contrast (Δ A−B = 0.00 pp, n = 63 triplets).
5. **Operational instruments** packaged together: born-stale autopsy taxonomy, GFC confirmatory audit, RQ2 failure audit, cited–uncited matched contrast, P4 maintenance attribution gate, RQ5 A/B/C protocol with condition C.

What is **not** new: the idea that docs go stale, that agents read context files, that broken links exist, that null experiments happen, or that survival analysis applies to software artifacts.

---

### What has already been shown in previous literature?

*Stated by mechanism/domain only—no paper titles invented here. These are established lines of work the evidence does not overturn.*

| Domain | What prior work already establishes | What this evidence adds (if anything) |
|--------|--------------------------------------|----------------------------------------|
| **Documentation decay / link rot** | Human-facing docs and wikis accumulate broken references over time; link rot is measurable. | Same phenomenon class, **different artifact** (agent instruction files); mechanical checks at commit granularity. |
| **Software traceability / reference integrity** | References between artifacts can be checked against repository state; drift detection is a known problem (incl. IaC/config drift analogies). | Applied to instruction-file regex extractions, not to deployment configs as primary object. |
| **Survival / event-history analysis in SE** | Time-to-failure models, censoring, and hazard framing are standard; left truncation and competing risks are known pitfalls. | RQ2 KM on VERIFIED→MISSING is **application**, not method invention. |
| **LLM agents + repository context** | Coding agents consume README, rules, and retrieved context; practitioner docs assume project instruction files matter. | Quantified uptake on **one** CLI agent under injection protocol—not ecosystem proof. |
| **Broken references vs task success** | Incorrect or missing context can hurt downstream tasks (RAG hallucination, wrong file paths)—**in principle**. | **Does not confirm harm** here: null A−B under pilot design. |
| **Bot/agent commit attribution** | Heuristic attribution from trailers, bots, and signatures is common in mining software repositories. | P4 validates one heuristic set on instruction-file commits (N = 200 gold). |
| **Selection on stable artifacts** | Documentation tends to cite stable entry points (README, main modules); matching studies exist for citation stability. | Cited vs depth/extension-matched uncited paths in **instruction files** specifically (85.4% paired ≤). |

**Bottom line:** The literature already supports “documentation can be wrong,” “links break,” “agents use files,” and “measure drift.” The evidence does **not** establish a new law of software engineering; it **localizes** known mechanisms to a new file class with fresh numbers.

---

### What is incremental?

Most of the program is incremental:

- RQ1 descriptive panel metrics (densities, transition counts).
- RQ2 survival curves on an RQ1 subset (2.7% post-verification failure among 4,521 verified-at-origin).
- RQ3 regime-stratified proportions (associations, not effects).
- RQ4 multi-state occupancy and transition tables.
- P5 feasibility counts (README/CONTRIBUTING comparability).
- GFC as second-pass labeling on an existing born-stale label set.
- Cited–uncited paired churn contrast with weak mean effect (CI crosses zero).
- RQ5 behavioral amplification (files modified) without outcome separation.
- Claim-to-export CSV indexing.

Incremental is not worthless—it is **necessary measurement**—but it is not paradigm shift.

---

### What is conceptual?

- **Late-binding model** (directive vs referential channel; static truth vs runtime resolution; load-bearing vs peripheral): organizing vocabulary, not an empirically validated theory.
- **Truth Decay vs Truth Debt separation**: definitional discipline motivated by null RQ5—conceptual, not a measured discovery.
- **Born-stale vs post-verification decay** as distinct constructs: conceptually right and supported descriptively, but structurally similar to left truncation / initial-condition vs failure in survival literature.

Conceptual contributions matter for **framing**; they are not **evidence** unless tied to tested predictions. Most model predictions remain untested (factorial channel separation, multi-agent replication, semantic falsehood).

---

### What is methodological?

| Methodological artifact | Evidence | Novelty of method |
|-------------------------|----------|-------------------|
| Longitudinal mechanical verifier on instruction-file extractions | RQ1 panel | **Incremental**—regex + git tree check pipeline |
| Born-stale autopsy (heuristic + dual LLM) | 17,747 cohort taxonomy | **Interesting** for this domain; not new adjudication theory |
| RQ2 post-verification failure audit | 121 events | **Interesting** audit layer; rules not independently validated |
| GFC confirmatory audit | 1,405 → 1,200 confirmed | **Incremental** confirmatory relabeling |
| Cited–uncited matched churn test | 2,259 pairs | **Incremental** matching design |
| P4 human-gold attribution gate | N = 200, F1 0.9617 | **Incremental** standard validation pattern |
| RQ5 A/B/C protocol v1.1 | design + partial execution | **Interesting** design; **incomplete** execution |
| Trace uptake funnel + mediation roles | 128 runs | **Interesting** instrumentation; heuristics unvalidated |
| Frozen evidence table / scientific freeze | process | **Incremental** reproducibility hygiene |

---

## Scoring rubric

| Score | Meaning |
|-------|---------|
| **Incremental** | Standard method or obvious extension; expected once someone looks at this artifact class. |
| **Interesting** | Worth publishing as a measurement note or pilot if framed honestly; would catch a specialist workshop’s attention. |
| **Novel** | First credible quantification or first controlled test in this **specific** setting; specialists would cite cautiously. |
| **Potentially field-changing** | Would alter how the field builds tools, standards, or research agendas **if** replicated at scale with clean identification. **None qualify at current evidence strength.** |

---

## Contribution-by-contribution scores

### Observational corpus (RQ1)

| # | Contribution (evidence) | Type | Score | Reasoning |
|---|-------------------------|------|-------|-----------|
| O1 | Longitudinal panel: 2,009 files, 339,646 observations (`rq1_feasibility.md`) | Empirical | **Interesting** | First large-scale **measurement object** on agent instruction files in this lab; not field-changing because cohort is enriched engineering sample (E1-100), not population, and “truth” is mechanical. |
| O2 | 51.9% UNVERIFIABLE observations (commands dominate) | Empirical | **Incremental** | Expected for instruction files full of shell snippets; mainly bounds interpretability of “staleness.” |
| O3 | 11.1% VERIFIED / 36.4% MISSING prevalence | Empirical | **Incremental** | Descriptive marginals without causal or comparative punchline. |
| O4 | State transition mass (e.g., 101,565 MISSING→MISSING) | Empirical | **Incremental** | Confirms persistent missing is absorbing; aligns with known panel dynamics. |

### Survival / post-verification decay (RQ2 + audit)

| # | Contribution | Type | Score | Reasoning |
|---|--------------|------|-------|-----------|
| S1 | 121/4,521 (2.7%) first MISSING after VERIFIED; S(365)≈0.848 (`rq2_summary.md`) | Empirical | **Incremental** | Standard survival application; rare events + heavy censoring; KM median not reached—weak headline. |
| S2 | 0/121 adjusted genuine post-verification decay (`rq2_failure_audit_summary.md`) | Empirical | **Interesting** | **Strong within-audit bound** that challenges decay-centric narrative **for this cohort**; fragile—73.6% reclassified as extractor artifacts by same pipeline family; only 1 LLM adjudication. |
| S3 | 73.6% post-verification failures = extractor artifacts | Empirical | **Interesting** | Suggests measurement dominates signal; undermines naive rot counts more than it proves “no decay ever.” |
| S4 | Born-stale exclusion (17,747 never VERIFIED) from RQ2 risk set | Methodological | **Interesting** | Correct estimand hygiene; conceptually standard left truncation, **newly applied** here with explicit counts. |

### Born-stale autopsy + GFC

| # | Contribution | Type | Score | Reasoning |
|---|--------------|------|-------|-----------|
| B1 | 17,747 born-stale references; 7-category taxonomy (`born_stale_summary.md`) | Empirical + method | **Novel** (narrow) | **Strongest observational novelty:** shows “missing” is heterogeneous templates/norms/anchors—not one decay process. Domain-specific first decomposition at this scale. |
| B2 | 1,405 raw `genuine_false_claim` (7.9%) | Empirical | **Incremental** | Upper bound before confirmatory pass; not reviewer-facing alone. |
| B3 | 1,200/1,405 (85.4%) GFC confirmed false at creation; 6.76% cohort rate (`gfc_confirmatory_summary.md`) | Empirical | **Interesting** | Quantifies **born-false** mass; still mechanical path absence, not semantic falsehood; deterministic audit only. |
| B4 | 135 LLM disagreements (0.8%) exported, not merged | Methodological | **Incremental** | Good practice; does not solve adjudication validity. |

### Selection / cited paths

| # | Contribution | Type | Score | Reasoning |
|---|--------------|------|-------|-----------|
| C1 | 85.4% pairs cited churn ≤ uncited (2,259 pairs, 78 repos) | Empirical | **Interesting** | Supports **selection** story (instructions cite stable paths); weak matching (extension/depth); mean diff CI includes zero—do not overclaim. |
| C2 | Mean churn difference 0.44 commits, CI crosses zero | Empirical | **Incremental** | Compatible with null average effect; paired fraction does the work. |

### Maintenance regimes (RQ3)

| # | Contribution | Type | Score | Reasoning |
|---|--------------|------|-------|-----------|
| R3-1 | Regime-stratified integrity proportions (human vs agent-assisted vs agent-dominated) | Empirical | **Incremental** | Ecological associations; RQ3 text forbids causal claims; confounding obvious. |
| R3-2 | 100% commit–attribution join on file commits | Methodological | **Incremental** | Engineering quality, not discovery. |

### Lifecycle dynamics (RQ4)

| # | Contribution | Type | Score | Reasoning |
|---|--------------|------|-------|-----------|
| R4-1 | 64,048 trajectories; 55.6% person-time integrity_loss | Empirical | **Incremental** | Descriptive multi-state table; complements RQ1; no new identification strategy. |
| R4-2 | Birth → 64.2% unverifiable / 28.6% integrity_loss | Empirical | **Incremental** | Quantifies that most life is non-operational at birth—supports born-stale narrative numerically. |

### Gates P4 / P5

| # | Contribution | Type | Score | Reasoning |
|---|--------------|------|-------|-----------|
| P4 | Agent maintenance attribution F1 0.9617, precision 0.958 (N = 200 gold) | Methodological | **Incremental** | Validates existing heuristics on a pilot sample; single reviewer; enables RQ3 labeling only. |
| P5 | Human doc baseline feasibility (66 repos, 105 files) | Methodological | **Incremental** | Gate passage; no comparative experiment. |

### Causal agent pilot (RQ5)

| # | Contribution | Type | Score | Reasoning |
|---|--------------|------|-------|-----------|
| A1 | Controlled A vs B referential truth swap at pinned commit | Methodological | **Interesting** | Right **idea** for identification; execution incomplete (22/35 A/B cases; 63 triplets). |
| A2 | Condition C no-instruction baseline (105 runs) | Methodological | **Interesting** | Design improvement over AB-only; confounds presence with both channels—still not factorial. |
| A3 | Δ A−B success = 0.00 pp; McNemar p = 1.0 | Empirical | **Interesting** | **Important null** under pilot—rules out **large** harm/benefit of referential swap here; indistinguishable from low power (~12% success, wide CIs). Not novel method; honest negative result. |
| A4 | Δ A−C / B−C +4.76 pp, CIs include zero | Empirical | **Incremental** | Noisy secondary contrast; 13 cases C-only. |
| A5 | 100% instruction_read (128/128) under injection | Empirical | **Incremental** | Tautological under protocol; documents compliance, not discovery. |
| A6 | 77.8% false_claim_used / instruction_followed on B | Empirical | **Interesting** | Shows agents **act** on false anchors—contradicts “robust ignore” story; trace heuristics unvalidated. |
| A7 | ~100 vs ~1.7 files modified (A/B vs C) | Empirical | **Interesting** | Large behavioral effect of **presence**; does not isolate directive channel; metric not manually audited. |
| A8 | Mediation: 19% false_claim_caused_failure vs null A−B | Empirical | **Incremental** | Post-hoc roles inconsistent with marginal null—heuristic taxonomy, not structural causal model. |
| A9 | tests_failed dominates unsuccessful runs | Empirical | **Incremental** | Confirms task hardness; expected for hard test suites. |
| A10 | Single agent (Claude Code CLI) | Limitation | **—** | Blocks generalization; keeps all RQ5 scores below **Novel**. |

### Conceptual / synthesis

| # | Contribution | Type | Score | Reasoning |
|---|--------------|------|-------|-----------|
| X1 | Late-binding two-channel model | Conceptual | **Interesting** | Useful **organizing frame** if labeled as hypothesis; not validated; partly tautological (runtime resolution = agents resolve at runtime). |
| X2 | Truth Decay vs Truth Debt split | Conceptual | **Interesting** | Methodological discipline; **supported negatively** (no Truth Debt promotion from RQ5). |
| X3 | Load-bearing vs peripheral referential claims | Conceptual | **Incremental** | Special case of causal salience; named post-hoc in mediation export. |
| X4 | Unsupported-claims inventory / evidence freeze | Methodological | **Incremental** | Good scientific hygiene; rare in industry labs, standard ambition for mature empirical SE. |

---

## Ranked headline contributions (evidence-only)

| Rank | Item | Score | Why it matters |
|------|------|-------|----------------|
| 1 | Born-stale heterogeneity + dominance over post-verification decay in cohort | **Novel** (narrow) | Changes **emphasis** from time-rot to initial validity + measurement mix—for this artifact class only. |
| 2 | RQ5 null referential-truth effect with non-null uptake/behavior | **Interesting** | Separates **consumption** from **outcome**; blocks naive “fix pointers → fix agents” story. |
| 3 | 0/121 genuine decay after audit | **Interesting** | Sharp bound, audit-dependent. |
| 4 | GFC 6.76% born-false rate | **Interesting** | Quantified mechanical false-at-birth mass. |
| 5 | Cited-path selection (85.4% paired stability) | **Interesting** | Explains weak coupling to outcomes without proving peripherality on tasks. |
| 6 | Longitudinal panel scale on instruction files | **Interesting** | Corpus asset, not conclusion. |
| 7 | Everything else listed | **Incremental** | Necessary scaffolding. |
| 8 | Late-binding model as “discovery” | **Interesting** (conceptual only) | Not an empirical contribution until pre-registered tests pass. |
| — | **Potentially field-changing** | **None** | Would require: complete ABC factorial, multi-agent replication, validated traces, semantic gold, representative cohort, and demonstrated tool/intervention effect. Current freeze meets none of these. |

---

## Honest novelty verdict

**Genuinely new (defensible):** First integrated **measurement + audit + partial causal pilot** program on **machine-consumed instruction files**, with the standout empirical finding that **born-stale / born-false and measurement artifacts dominate** post-verification decay signals in this cohort, plus a **pilot null** on referential-truth manipulation under high task difficulty.

**Not new:** Documentation rots; agents read project files; survival analysis applies; git heuristics attribute bots; broken references can exist without affecting a specific task.

**Overclaimed if sold as novel:** “Late binding” as a discovered mechanism; Truth Debt; channel factorial; cross-agent laws; semantic falsehood rates; decay is rare **in general** (only rare **after this audit in this cohort**).

**If the field cared only one sentence:** *You built the first serious ruler for a new file species and used it to show the ruler often measures birth defects and extractor noise more than time-decay—and a small agent experiment suggests fixing the pointer text may not move task success anyway.*

---

## Document control

| Field | Value |
|-------|--------|
| Version | v1 |
| Date | 2026-07-03 |
| Inputs | All `exports/**/**summary*.md`, `late_binding_evidence_table.csv`, `SCIENTIFIC_EVIDENCE_FREEZE.md` |
| Literature | Domain-level only; no bibliographic invention |
