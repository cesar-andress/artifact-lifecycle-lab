# Scientific Evidence Freeze

**Status:** FROZEN — paper-writing mode  
**Freeze date:** 2026-07-03  
**Working title:** *Late Binding in Machine-Consumed Instruction Files*

## Purpose

This document enumerates every empirical claim currently supported by **existing, read-only laboratory outputs**. It is the authoritative claim inventory for the ACM TOSEM submission. No new experiments, no regeneration of datasets, and no modification of export directories are permitted after this freeze.

## Provenance policy

1. Each claim cites **primary export paths** relative to the repository root (`artifact-lifecycle-lab/`).
2. **Statistical evidence** reproduces values exactly as reported in those exports (summaries preferred over re-aggregation).
3. Claims are classified by evidential strength, not narrative importance.
4. **Git-tracking status** is noted where a supporting file exists on disk but is not yet indexed in `git` (see §Inventory).

### Confidence levels (operational definitions)

| Level | Meaning |
|-------|---------|
| **High** | Direct count or estimate from a primary export; audit or paired design; large *N*; CI or *p*-value reported where applicable; minimal inferential leap. |
| **Medium** | Trace/heuristic classification, observational association, subset overlap, CI includes zero, single-agent pilot, or supporting file not git-tracked at freeze time. |
| **None** | Claim explicitly contradicted by frozen outputs or not empirically tested. |

---

## Output inventory (read-only)

### Git-tracked primary exports

| Domain | Key summaries | Key datasets | Key figures |
|--------|---------------|--------------|-------------|
| RQ1 | `exports/truth_decay_pilot/rq1_feasibility.md` | `exports/truth_decay_pilot/reference_longitudinal.csv`, `rq1_exploratory_stats.csv` | `figure_a_reference_density.pdf`, `figure_b_verified_vs_missing_by_age.pdf`, `figure_c_repair_latency.pdf`, `figure_d_state_transitions.pdf` |
| RQ2 survival | `exports/truth_decay_pilot/rq2_summary.md` | `exports/truth_decay_pilot/rq2_survival.csv` | `figure_survival.pdf`, `figure_cumulative_hazard.pdf`, `figure_censoring.pdf` |
| RQ2 audit | `exports/truth_decay_pilot/rq2_failure_audit_summary.md` | `exports/truth_decay_pilot/rq2_failure_audit.csv` | — |
| Born-stale | `exports/truth_decay_pilot/born_stale_summary.md` | `born_stale_taxonomy.csv`, `born_stale_statistics.csv`, `born_stale_disagreements.csv` | `figure_born_stale_taxonomy.pdf`, `figure_born_stale_by_reference_type.pdf`, `figure_born_stale_by_repository.pdf` |
| GFC confirmatory | `exports/truth_decay_pilot/gfc_confirmatory_summary.md` | `gfc_confirmatory_audit.csv`, `gfc_confirmatory_examples.csv` | `figure_gfc_confirmatory.pdf` |
| Cited vs uncited | `exports/truth_decay_pilot/cited_uncited_summary.md` | `cited_uncited_comparison.csv` | `figure_cited_uncited_churn.pdf`, `figure_churn_difference_hist.pdf` |
| RQ3 | `exports/truth_decay_pilot/rq3_summary.md` | `rq3_dataset.csv`, `rq3_tables.csv` | `figure_rq3_birth_integrity.pdf`, `figure_rq3_repair_probability.pdf`, `figure_rq3_transition_matrix.pdf` |
| RQ4 | `exports/truth_decay_pilot/rq4_summary.md` | `rq4_multistate.csv` | `figure_rq4_*.pdf` (5 figures) |
| P4 gate (auto) | `exports/truth_pilot/p4_attribution_precision.md` | `agent_attribution_gold_worksheet.csv`, `agent_commit_candidates.csv` | — |
| P5 baseline | `exports/truth_pilot/p5_human_doc_baseline.md` | `human_doc_reference_examples.csv` | — |
| RQ5 A/B uptake | `exports/rq5_agent_impact/rq5_uptake_analysis.md` | `rq5_uptake_dataset.csv`, `rq5_uptake_by_condition.csv` | `figure_uptake_flow.pdf` |
| RQ5 A/B mediation | `exports/rq5_agent_impact/rq5_mediation_summary.md` | `rq5_mediation_dataset.csv`, `rq5_mediation_by_condition.csv` | `figure_rq5_mediation_flow.pdf`, `figure_trace_flow.pdf`, `figure_failure_modes.pdf` |
| RQ5 A/B/C paired | `exports/rq5_agent_impact/rq5_abc_comparative_analysis.md` | `rq5_dataset.csv`, `rq5_effect_sizes.csv` | `figure_success_rate.pdf` |
| Paper synthesis | `exports/paper_synthesis/late_binding_evidence_table.csv` | — | — |
| Conceptual model | `docs/LATE_BINDING_MODEL_v1.md` | — | — |

### Workspace-local outputs (exist on disk; not git-tracked at freeze)

| Path | Used for |
|------|----------|
| `exports/truth_pilot/p4_validation.md` | Human gold validation metrics (P4 PASS) |
| `exports/rq5_agent_impact/rq5_results.csv` | Full A/B run ledger (128 runs) |
| `exports/rq5_agent_impact/rq5_statistics.csv` | Descriptive RQ5 statistics |
| `exports/rq5_agent_impact/rq5_failure_modes.csv` | Failure-mode counts |
| `exports/rq5_agent_impact_c/` | Condition C complete cohort (105 runs) |

Claims citing workspace-local files are classified **Moderately supported** until those exports are committed unchanged.

### Stale / superseded summaries (do not cite for counts)

| File | Issue |
|------|-------|
| `exports/rq5_agent_impact/rq5_summary.md` | Reports 9 total runs; superseded by `rq5_uptake_analysis.md` (128 runs) |
| `exports/rq5_agent_impact_c/rq5_summary.md` | Template header still lists A/B design; use `rq5_results.csv` row count |

---

## Strongly supported claims

Direct measurements from git-tracked exports with high confidence. No causal language unless the export explicitly supports it.

---

### SS-01 — Zero adjusted genuine post-verification decay

| Field | Value |
|-------|-------|
| **Claim ID** | SS-01 |
| **Exact wording** | After audit adjustment, **0 of 121** post-verification `first_missing` events are classified as genuine reference decay. |
| **Supporting datasets** | `exports/truth_decay_pilot/rq2_failure_audit.csv` |
| **Supporting figures** | — |
| **Supporting tables** | Taxonomy table in `rq2_failure_audit_summary.md` (§Taxonomy) |
| **Statistical evidence** | Adjusted genuine decay: **0/121** (0.0%); Wilson 95% CI among failures: **0.0%–3.1%**; adjusted decay rate vs verified cohort (4521): **0.00%** (Wilson 95% CI: **0.00%–0.08%**). Category A `genuine_decay`: **0** (0.0%). |
| **Limitations** | Single audit pass; deterministic heuristics first; only **1** reference sent to LLM judges; snippet context depends on L1/L1b blob availability. |
| **Confidence** | High |

---

### SS-02 — Post-verification failures are predominantly measurement artifacts

| Field | Value |
|-------|-------|
| **Claim ID** | SS-02 |
| **Exact wording** | **73.6%** (89/121) of post-verification failures are classified as extractor artifacts (category D). |
| **Supporting datasets** | `exports/truth_decay_pilot/rq2_failure_audit.csv` |
| **Supporting figures** | — |
| **Supporting tables** | Taxonomy table in `rq2_failure_audit_summary.md` |
| **Statistical evidence** | Category D count **89**; proportion **73.6%**. Secondary categories: B rename_or_move **19** (15.7%), C verification_anchor_issue **5** (4.1%), E normative_or_prescriptive **7** (5.8%), G ambiguous **1** (0.8%). |
| **Limitations** | Taxonomy depends on deterministic heuristics; semantic judgment required for path moves vs deletions. |
| **Confidence** | High |

---

### SS-03 — Born-stale cohort size and raw false-claim upper bound

| Field | Value |
|-------|-------|
| **Claim ID** | SS-03 |
| **Exact wording** | The born-stale autopsy classifies **17,747** verifiable references that never reach `VERIFIED`; **1,405** (7.9%) are labeled `genuine_false_claim` (raw upper bound before confirmatory audit). |
| **Supporting datasets** | `exports/truth_decay_pilot/born_stale_taxonomy.csv`, `born_stale_statistics.csv` |
| **Supporting figures** | `exports/truth_decay_pilot/figure_born_stale_taxonomy.pdf`, `figure_born_stale_by_reference_type.pdf`, `figure_born_stale_by_repository.pdf` |
| **Supporting tables** | Taxonomy table in `born_stale_summary.md` |
| **Statistical evidence** | Cohort **17,747**; `genuine_false_claim` **1,405** (**7.9%**). LLM judges adjudicated **1,540** references; **135** unresolved disagreements (0.8%). |
| **Limitations** | Born-stale is heterogeneous (12.6% extraction artifact, 32.9% normative, 29.9% anchor mismatch, etc.); raw `genuine_false_claim` is not reviewer-facing without GFC confirmatory pass. |
| **Confidence** | High |

---

### SS-04 — Confirmed false claims at creation (GFC audit)

| Field | Value |
|-------|-------|
| **Claim ID** | SS-04 |
| **Exact wording** | Of **1,405** prior `genuine_false_claim` references, **1,200** (**85.4%**) are confirmed false at creation in the GFC confirmatory audit. |
| **Supporting datasets** | `exports/truth_decay_pilot/gfc_confirmatory_audit.csv`, `gfc_confirmatory_examples.csv` |
| **Supporting figures** | `exports/truth_decay_pilot/figure_gfc_confirmatory.pdf` |
| **Supporting tables** | Confirmatory taxonomy in `gfc_confirmatory_summary.md` |
| **Statistical evidence** | Confirmed false (A): **1200/1405** (**85.4%**); Wilson 95% CI: **83.5%–87.2%**. Adjusted born-stale false-claim rate vs 17,747 cohort: **6.76%**. Template category E: **150** (10.7%); artifact B: **4** (0.3%). |
| **Limitations** | **0** references sent to LLM judges (all deterministic); does not prove semantic incorrectness beyond path existence checks. |
| **Confidence** | High |

---

### SS-05 — Cited paths are disproportionately stable vs matched uncited controls (paired fraction)

| Field | Value |
|-------|-------|
| **Claim ID** | SS-05 |
| **Exact wording** | In **85.4%** of **2,259** matched pairs across **78** repositories, cited path git churn is less than or equal to uncited control churn. |
| **Supporting datasets** | `exports/truth_decay_pilot/cited_uncited_comparison.csv` |
| **Supporting figures** | `exports/truth_decay_pilot/figure_cited_uncited_churn.pdf`, `figure_churn_difference_hist.pdf` |
| **Supporting tables** | Results block in `cited_uncited_summary.md` |
| **Statistical evidence** | Paired fraction **85.4%** (95% bootstrap CI: **83.9%–86.9%**). Mean cited churn **1.99** (CI: 1.49–2.61); mean uncited **1.54** (CI: 1.18–1.99). |
| **Limitations** | Matching uses extension and depth only; selection effect interpretation, not causal stability intervention. |
| **Confidence** | High |

---

### SS-06 — RQ2 post-verification failure rate among verified references

| Field | Value |
|-------|-------|
| **Claim ID** | SS-06 |
| **Exact wording** | Among **4,521** references entering at `VERIFIED`, **121** (**2.7%**) experience a first `MISSING` event; **4,263** (**94.3%**) are right-censored. |
| **Supporting datasets** | `exports/truth_decay_pilot/rq2_survival.csv` |
| **Supporting figures** | `exports/truth_decay_pilot/figure_survival.pdf`, `figure_cumulative_hazard.pdf` |
| **Supporting tables** | Cohort block in `rq2_summary.md` |
| **Statistical evidence** | Primary failures **121/4521** (**2.7%**). Kaplan–Meier: **S(365 days) = 0.848**; median survival not reached. Conditional median time to first MISSING among failures: **34.5 days**. |
| **Limitations** | Repo clustering not adjusted (naive Greenwood CI); engineering cohort; zero-day failures common at commit granularity. |
| **Confidence** | High |

---

### SS-07 — RQ1 longitudinal panel descriptive scale

| Field | Value |
|-------|-------|
| **Claim ID** | SS-07 |
| **Exact wording** | The RQ1 longitudinal panel comprises **2,009** instruction files and **339,646** reference observations with median **14.0** observations per file. |
| **Supporting datasets** | `exports/truth_decay_pilot/reference_longitudinal.csv`, `rq1_exploratory_stats.csv` |
| **Supporting figures** | `exports/truth_decay_pilot/figure_a_reference_density.pdf`, `figure_b_verified_vs_missing_by_age.pdf`, `figure_d_state_transitions.pdf` |
| **Supporting tables** | §Observed signals in `rq1_feasibility.md` |
| **Statistical evidence** | Verified ratio **11.1%**; missing **36.4%**; unverifiable **51.9%**; first-failure events **18,473**; files with ≥1 missing **1,650**. |
| **Limitations** | Mechanical verification ≠ semantic truth; UNVERIFIABLE commands dominate; pilot + E1-100 cohort. |
| **Confidence** | High |

---

### SS-08 — Agents read instruction files whenever present (RQ5 A/B)

| Field | Value |
|-------|-------|
| **Claim ID** | SS-08 |
| **Exact wording** | In **128** Claude Code runs with instruction files injected (A=65, B=63), **100%** exhibit `instruction_read` and `instruction_quoted` trace events. |
| **Supporting datasets** | `exports/rq5_agent_impact/rq5_uptake_dataset.csv`, `rq5_uptake_by_condition.csv` |
| **Supporting figures** | `exports/rq5_agent_impact/figure_uptake_flow.pdf` |
| **Supporting tables** | Uptake funnel in `rq5_uptake_analysis.md`; `paper/tables/evidence-summary.tex` (row: instruction read) |
| **Statistical evidence** | Condition A: **65/65** (100.0%) read; Condition B: **63/63** (100.0%) read. |
| **Limitations** | Single agent (Claude Code CLI); instruction file injected pre-run; trace classifier heuristic. |
| **Confidence** | High |

---

### SS-09 — No paired success difference between truthful and false referential content

| Field | Value |
|-------|-------|
| **Claim ID** | SS-09 |
| **Exact wording** | On **63** paired A/B/C triplets (22 overlap cases), task success is **12.7%** (8/63) for both A and B; paired Δ(A−B) = **0.00 pp**. |
| **Supporting datasets** | `exports/rq5_agent_impact/rq5_dataset.csv`, `rq5_effect_sizes.csv` |
| **Supporting figures** | `exports/rq5_agent_impact/figure_success_rate.pdf` |
| **Supporting tables** | Aggregate metrics + A−B contrast in `rq5_abc_comparative_analysis.md`; `paper/tables/evidence-summary.tex` |
| **Statistical evidence** | Wilson 95% CI A and B: **[6.6%, 23.1%]** each. Bootstrap 95% CI (cluster case) for Δ(A−B): **[−6.35, +6.35] pp**. McNemar exact **p = 1.0000**; discordant pairs **2 / 2**; Cohen's **h = 0.0000**. |
| **Limitations** | **63** triplets / **21** cases only; **13** cases have C without matching A/B; high baseline failure (~88%); low power. |
| **Confidence** | High (for null paired contrast on overlap subset) |

---

### SS-10 — Instruction presence amplifies files modified (behavioral)

| Field | Value |
|-------|-------|
| **Claim ID** | SS-10 |
| **Exact wording** | On paired triplets, mean files modified is **99.7** (A), **103.0** (B), and **1.7** (C). |
| **Supporting datasets** | `exports/rq5_agent_impact/rq5_dataset.csv` |
| **Supporting figures** | — |
| **Supporting tables** | Aggregate metrics in `rq5_abc_comparative_analysis.md` |
| **Statistical evidence** | Medians: A **100.0**, B **103.0**, C **1.0**. Compilation success **100%** (63/63) all conditions on triplets. |
| **Limitations** | Behavioral metric, not task success; does not isolate directive vs referential channel without further design. |
| **Confidence** | High |

---

### SS-11 — RQ4 lifecycle occupancy and birth transitions (descriptive)

| Field | Value |
|-------|-------|
| **Claim ID** | SS-11 |
| **Exact wording** | Among **64,048** reference trajectories, birth transitions are predominantly to `unverifiable` (**41,110**; **P = 0.642**) or `integrity_loss` (**18,335**; **P = 0.286**); only **4,603** (**P = 0.072**) reach operational at birth. |
| **Supporting datasets** | `exports/truth_decay_pilot/rq4_multistate.csv` |
| **Supporting figures** | `exports/truth_decay_pilot/figure_rq4_state_occupancy.pdf`, `figure_rq4_transition_matrix.pdf`, `figure_rq4_lifecycle_diagram.pdf` |
| **Supporting tables** | First-transition and occupancy tables in `rq4_summary.md`  |
| **Statistical evidence** | State occupancy person-time: integrity_loss **55.6%**, unverifiable **34.5%**, operational **9.2%**. Post-birth P(operational→integrity_loss) **0.492**; P(integrity_loss→deletion) **0.830**. |
| **Limitations** | Mechanical states ≠ semantic lifecycle; irregular panel spacing; no competing-risks adjustment. |
| **Confidence** | High (descriptive proportions only) |

---

## Moderately supported claims

Supported by existing outputs but requiring heuristics, observational design, subset restrictions, non-significant contrasts, or workspace-local files.

---

### MS-01 — P4 agent-maintenance classifier passes human gold gate

| Field | Value |
|-------|-------|
| **Claim ID** | MS-01 |
| **Exact wording** | On **N = 200** human-reviewed commits, the frozen P4 classifier achieves precision **0.958**, recall **0.965**, F1 **0.9617**, accuracy **0.945**, Cohen's κ **0.8643** for `true_agent_maintenance`. |
| **Supporting datasets** | `exports/truth_pilot/agent_attribution_gold_worksheet.csv` |
| **Supporting figures** | — |
| **Supporting tables** | Confusion matrix in `exports/truth_pilot/p4_validation.md` (**workspace-local**) |
| **Statistical evidence** | Gate threshold precision ≥ **80%**; observed **95.8%** → **PASS**. TP/FP/FN: **138/6/5** on binary collapse. |
| **Limitations** | Supporting summary not git-tracked at freeze; single human review pass; worksheet is pilot sample not exhaustive; κ collapses three-level human taxonomy. |
| **Confidence** | Medium |

---

### MS-02 — Agents follow anchor references in a majority of runs

| Field | Value |
|-------|-------|
| **Claim ID** | MS-02 |
| **Exact wording** | `instruction_followed` is observed in **72.3%** (47/65) of condition A runs and **77.8%** (49/63) of condition B runs. |
| **Supporting datasets** | `exports/rq5_agent_impact/rq5_uptake_dataset.csv` |
| **Supporting figures** | `exports/rq5_agent_impact/figure_uptake_flow.pdf` |
| **Supporting tables** | Uptake funnel in `rq5_uptake_analysis.md` |
| **Statistical evidence** | Read→follow conversion (B): **77.8%** of read runs. |
| **Limitations** | Inferred from trace events, not ground-truth binding to repository paths. |
| **Confidence** | Medium |

---

### MS-03 — False anchor reference enters actionable trace path on B

| Field | Value |
|-------|-------|
| **Claim ID** | MS-03 |
| **Exact wording** | On condition B, **49/63** runs (**77.8%**) set `false_claim_used` (anchor appears in actionable trace events). |
| **Supporting datasets** | `exports/rq5_agent_impact/rq5_uptake_dataset.csv`, `rq5_mediation_dataset.csv` |
| **Supporting figures** | `exports/rq5_agent_impact/figure_trace_flow.pdf`, `figure_rq5_mediation_flow.pdf` |
| **Supporting tables** | B mediation funnel in `rq5_mediation_summary.md` |
| **Statistical evidence** | `false_claim_used_in_tool_call`: **49/63** (**77.8%**). `false_claim_ignored`: **14/63** (**22.2%**). |
| **Limitations** | Actionable-trace heuristic; does not prove incorrect repo mutation. |
| **Confidence** | Medium |

---

### MS-04 — Truthful vs no-instruction paired contrast is not statistically reliable

| Field | Value |
|-------|-------|
| **Claim ID** | MS-04 |
| **Exact wording** | Paired Δ(A−C) success = **+4.76 pp** (A **12.7%** vs C **7.9%** on triplets); cluster bootstrap 95% CI **[−12.70, +22.22] pp**; McNemar **p = 0.5811**. |
| **Supporting datasets** | `exports/rq5_agent_impact/rq5_dataset.csv`, `rq5_effect_sizes.csv` |
| **Supporting figures** | `exports/rq5_agent_impact/figure_success_rate.pdf` |
| **Supporting tables** | A−C contrast in `rq5_abc_comparative_analysis.md` |
| **Statistical evidence** | B−C identical to A−C on overlap (**+4.76 pp**, same CI, **p = 0.5811**). All three cluster-bootstrap success CIs **include zero**. |
| **Limitations** | Directional point estimate ≠ significant effect; **n = 63** triplets; environmental task difficulty confound. |
| **Confidence** | Medium (for reporting the non-significant contrast, not for claiming benefit) |

---

### MS-05 — Mean git churn difference between cited and uncited paths is not significant

| Field | Value |
|-------|-------|
| **Claim ID** | MS-05 |
| **Exact wording** | Mean paired churn difference (cited − uncited) is **0.44** commits with 95% bootstrap CI **[−0.21, +1.15]** (includes zero). |
| **Supporting datasets** | `exports/truth_decay_pilot/cited_uncited_comparison.csv` |
| **Supporting figures** | `exports/truth_decay_pilot/figure_churn_difference_hist.pdf` |
| **Supporting tables** | `cited_uncited_summary.md` |
| **Statistical evidence** | See SS-05 for paired fraction vs mean divergence note in export interpretation. |
| **Limitations** | Mean and paired fraction can diverge under heavy-tail pairs; not evidence that cited paths are *less* stable on average. |
| **Confidence** | Medium |

---

### MS-06 — RQ3 maintenance-regime associations (observational)

| Field | Value |
|-------|-------|
| **Claim ID** | MS-06 |
| **Exact wording** | Agent-dominated instruction files show higher birth integrity index (**P(verified birth) = 0.343** on **5,182** verifiable refs) than human-only files (**0.105** on **8,958** refs) in the longitudinal panel. |
| **Supporting datasets** | `exports/truth_decay_pilot/rq3_dataset.csv`, `rq3_tables.csv` |
| **Supporting figures** | `exports/truth_decay_pilot/figure_rq3_birth_integrity.pdf`, `figure_rq3_repair_probability.pdf` |
| **Supporting tables** | Estimand table in `rq3_summary.md` |
| **Statistical evidence** | File counts: human_only **1188**, agent_assisted **215**, agent_dominated **595**. Post-verification decay P(decay\|verified): human_only **0.011**, agent_assisted **0.053**, agent_dominated **0.019**. |
| **Limitations** | **No causal claims** (explicit in export); ecological confounding; file-level regime aggregation; RQ3 export written when P4 was pending validation. |
| **Confidence** | Medium |

---

### MS-07 — Mediation audit: false claim often used but frequently non-load-bearing

| Field | Value |
|-------|-------|
| **Claim ID** | MS-07 |
| **Exact wording** | On B runs, **49/63** (**77.8%**) use the false claim in tool calls; **46/63** (**73.0%**) are classified non-load-bearing; **12/63** (**19.0%**) are classified `false_claim_caused_failure`. |
| **Supporting datasets** | `exports/rq5_agent_impact/rq5_mediation_dataset.csv`, `rq5_mediation_by_condition.csv` |
| **Supporting figures** | `exports/rq5_agent_impact/figure_failure_modes.pdf` |
| **Supporting tables** | Causal roles table in `rq5_mediation_summary.md` |
| **Statistical evidence** | `uptake_but_not_load_bearing`: **19/63** (**30.2%**), success rate **0.263**. `obstacle_recovered`: **5/63** (**7.9%**). |
| **Limitations** | Post-hoc trace heuristics; `task_failed_because_of_false_claim` is not independently validated; mediation summary interpretive text is not a statistical test. |
| **Confidence** | Medium |

---

### MS-08 — Environmental test failure dominates unsuccessful runs

| Field | Value |
|-------|-------|
| **Claim ID** | MS-08 |
| **Exact wording** | Among unsuccessful condition A runs, **57** are classified `tests_failed` (per uptake failure-reason block). |
| **Supporting datasets** | `exports/rq5_agent_impact/rq5_uptake_dataset.csv` |
| **Supporting figures** | `exports/rq5_agent_impact/figure_failure_modes.pdf` |
| **Supporting tables** | Failure reasons in `rq5_uptake_analysis.md` |
| **Statistical evidence** | Condition A unsuccessful with tests_failed **57**; Condition B **55**. Overall success A **12.3%** (8/65), B **12.7%** (8/63). |
| **Limitations** | Count is trace/outcome classification, not isolated causal attribution; denominator for rate not explicitly normalized in export. |
| **Confidence** | Medium |

---

### MS-09 — Condition C cohort execution complete (local export)

| Field | Value |
|-------|-------|
| **Claim ID** | MS-09 |
| **Exact wording** | Condition C executed **105** runs (**35** cases × **3** replicates) for Claude Code in `exports/rq5_agent_impact_c/`. |
| **Supporting datasets** | `exports/rq5_agent_impact_c/rq5_results.csv` (**workspace-local**, 105 data rows + header) |
| **Supporting figures** | `exports/rq5_agent_impact_c/figure_success.pdf` (**workspace-local**) |
| **Supporting tables** | Paired subset in `exports/rq5_agent_impact/rq5_abc_comparative_analysis.md` (uses C from local dir) |
| **Statistical evidence** | Row count in `rq5_results.csv`; ABC analysis confirms **63** paired triplets from overlap with partial A/B. |
| **Limitations** | Export directory not git-tracked at freeze; A/B on same cases incomplete (**128** runs, **22/35** cases in overlap narrative). |
| **Confidence** | Medium |

---

### MS-10 — Condition C aggregate success rate (local export)

| Field | Value |
|-------|-------|
| **Claim ID** | MS-10 |
| **Exact wording** | Across all **105** condition C runs, aggregate task success is **12/105** (**11.4%**). |
| **Supporting datasets** | `exports/rq5_agent_impact_c/rq5_results.csv` (**workspace-local**) |
| **Supporting figures** | — |
| **Supporting tables** | `exports/paper_synthesis/late_binding_evidence_table.csv` (row: Condition C aggregate success) |
| **Statistical evidence** | Descriptive proportion only; Wilson CI not reported in primary export. |
| **Limitations** | Workspace-local file; includes cases without A/B overlap; not paired-tested against A/B in this aggregate. |
| **Confidence** | Medium |

---

### MS-11 — P5 human documentation baseline feasibility

| Field | Value |
|-------|-------|
| **Claim ID** | MS-11 |
| **Exact wording** | Within-repo comparison of machine instruction files vs README/CONTRIBUTING is **feasible** (gate **PASS**) on **66** P1 repositories with **105** human doc files sampled. |
| **Supporting datasets** | `exports/truth_pilot/human_doc_reference_examples.csv` |
| **Supporting figures** | — |
| **Supporting tables** | `exports/truth_pilot/p5_human_doc_baseline.md` |
| **Statistical evidence** | **96/105** files (91.4%) have ≥1 verifiable reference; mean ambiguity ratio **36.8%**. |
| **Limitations** | Feasibility gate only; not an empirical equivalence or consumption study. |
| **Confidence** | Medium |

---

### MS-12 — Stratified uptake success deltas are small and unstable

| Field | Value |
|-------|-------|
| **Claim ID** | MS-12 |
| **Exact wording** | Among runs that followed the anchor, Δ success (A−B) = **−0.014** (A **0.149**, B **0.163**); among B runs that used the false claim, success rate = **0.163** (**n = 49**). |
| **Supporting datasets** | `exports/rq5_agent_impact/rq5_uptake_by_condition.csv` |
| **Supporting figures** | — |
| **Supporting tables** | Stratified table in `rq5_uptake_analysis.md` |
| **Statistical evidence** | Among B runs ignoring false claim (**n = 14**), success **0.000**. No hypothesis test reported for strata. |
| **Limitations** | Small stratum sizes; exploratory post-hoc; susceptible to multiple comparisons. |
| **Confidence** | Medium |

---

## Unsupported claims

Claims that are **not** supported by frozen outputs, are explicitly contradicted, or remain untested. Do not state these as findings.

---

### US-01 — Post-verification reference decay is common

| Field | Value |
|-------|-------|
| **Claim ID** | US-01 |
| **Exact wording** | Post-verification reference decay is a common failure mode in the cohort. |
| **Why unsupported** | SS-01: adjusted genuine decay **0/121**; Wilson upper bound **3.1%** among failures; cohort rate **0.00%** (CI upper **0.08%**). |
| **Contradicting / absent evidence** | `rq2_failure_audit_summary.md`, `rq2_summary.md` |
| **Confidence** | None (contradicted) |

---

### US-02 — False referential instructions reliably harm agent task success

| Field | Value |
|-------|-------|
| **Claim ID** | US-02 |
| **Exact wording** | Injecting confirmed-false referential content reliably reduces agent task success vs truthful content. |
| **Why unsupported** | SS-09: Δ(A−B) = **0.00 pp**, McNemar **p = 1.0**, CI includes zero. |
| **Contradicting / absent evidence** | `rq5_abc_comparative_analysis.md` |
| **Confidence** | None (contradicted on paired overlap) |

---

### US-03 — True referential instructions reliably improve agent task success

| Field | Value |
|-------|-------|
| **Claim ID** | US-03 |
| **Exact wording** | Truthful referential instructions reliably improve task success vs no instruction. |
| **Why unsupported** | MS-04: Δ(A−C) = **+4.76 pp** but cluster CI **[−12.70, +22.22]** includes zero; **p = 0.5811**. |
| **Contradicting / absent evidence** | `rq5_abc_comparative_analysis.md` |
| **Confidence** | None (not demonstrated) |

---

### US-04 — Instruction files are ignored when present

| Field | Value |
|-------|-------|
| **Claim ID** | US-04 |
| **Exact wording** | Agents ignore machine-consumed instruction files when they are present in the workspace. |
| **Why unsupported** | SS-08: **100%** `instruction_read` on **128/128** runs with injected files. |
| **Contradicting / absent evidence** | `rq5_uptake_analysis.md` |
| **Confidence** | None (contradicted) |

---

### US-05 — Agents consistently detect and reject false pointers

| Field | Value |
|-------|-------|
| **Claim ID** | US-05 |
| **Exact wording** | Agents consistently detect false referential pointers and reject them without acting. |
| **Why unsupported** | MS-03: **77.8%** `false_claim_used` on B; only **7.9%** `false_claim_corrected_by_agent` (5/63) in mediation audit. |
| **Contradicting / absent evidence** | `rq5_uptake_analysis.md`, `rq5_mediation_summary.md` |
| **Confidence** | None (contradicted) |

---

### US-06 — Observational truth decay implies measurable operational cost (Truth Debt promotion)

| Field | Value |
|-------|-------|
| **Claim ID** | US-06 |
| **Exact wording** | Static referential falsity causally imposes measurable task-failure cost on agents (Truth Debt as causal claim). |
| **Why unsupported** | SS-09 + MS-04: no significant paired success cost attributable to referential falsity; SS-10 shows behavioral amplification without outcome difference. |
| **Contradicting / absent evidence** | `rq5_abc_comparative_analysis.md`, `docs/LATE_BINDING_MODEL_v1.md` §8 |
| **Confidence** | None (not demonstrated) |

---

### US-07 — Cited paths are less stable than uncited controls on average

| Field | Value |
|-------|-------|
| **Claim ID** | US-07 |
| **Exact wording** | Paths cited in instruction files have higher mean git churn than matched uncited controls. |
| **Why unsupported** | MS-05: mean difference CI **[−0.21, +1.15]** includes zero; export states mean churn **not significantly different**. |
| **Contradicting / absent evidence** | `cited_uncited_summary.md` |
| **Confidence** | None (contradicted for mean-churn direction) |

---

### US-08 — RQ5 findings generalize across coding agents

| Field | Value |
|-------|-------|
| **Claim ID** | US-08 |
| **Exact wording** | RQ5 uptake and causal contrasts generalize to Copilot, Cursor, and other agents beyond Claude Code. |
| **Why unsupported** | All reported RQ5 runs use **`claude_code` only**; no multi-agent export exists. |
| **Contradicting / absent evidence** | `rq5_uptake_analysis.md`, `rq5_abc_comparative_analysis.md` |
| **Confidence** | None (untested) |

---

### US-09 — Human-facing docs behave like machine instruction files under agent consumption

| Field | Value |
|-------|-------|
| **Claim ID** | US-09 |
| **Exact wording** | README/CONTRIBUTING consumption by agents is equivalent to AGENTS.md/skills consumption (causal or behavioral). |
| **Why unsupported** | P5 is feasibility-only (**MS-11**); RQ5 manipulates machine instruction files only. |
| **Contradicting / absent evidence** | `p5_human_doc_baseline.md`, RQ5 protocol exports |
| **Confidence** | None (untested) |

---

### US-10 — Agent-dominated maintenance causes higher specification integrity

| Field | Value |
|-------|-------|
| **Claim ID** | US-10 |
| **Exact wording** | Agent-dominated maintenance **causes** higher specification integrity than human-only maintenance. |
| **Why unsupported** | RQ3 export explicitly forbids causal claims; associations only (**MS-06**). |
| **Contradicting / absent evidence** | `rq3_summary.md` §Interpretation guardrails |
| **Confidence** | None (untested causally) |

---

### US-11 — Complete 35-case A/B/C factorial is finished

| Field | Value |
|-------|-------|
| **Claim ID** | US-11 |
| **Exact wording** | All **35** cases have complete A, B, and C replicates in a single paired analysis. |
| **Why unsupported** | ABC analysis: **22** overlap cases, **63** triplets, **13** cases C-only without matching A/B; A/B partial **128** runs. |
| **Contradicting / absent evidence** | `rq5_abc_comparative_analysis.md`, `rq5_redesign_plan.md` |
| **Confidence** | None (contradicted) |

---

## Cross-reference index

| Claim ID | `late_binding_evidence_table.csv` row (paraphrase) | Paper section |
|----------|-----------------------------------------------------|---------------|
| SS-01 | Zero genuine post-verification decay | §5 Results RQ2 |
| SS-04 | Confirmed false at creation | §5 Results confirmatory |
| SS-05 | Cited paths disproportionately stable | §5 Results / §6 Discussion |
| SS-08 | Instruction read when present | §5 Results RQ5 uptake |
| SS-09 | No success difference A vs B paired | §5 Results / §6 Discussion |
| SS-10 | Files modified A/B vs C | §3 Conceptual model (directive channel) |
| MS-01 | Agent maintenance F1 | §5 Results P4 |
| US-02 – US-06 | Unsupported rows in model doc §8 | §6 Discussion / §7 Threats |

Full CSV: `exports/paper_synthesis/late_binding_evidence_table.csv`  
Conceptual framing: `docs/LATE_BINDING_MODEL_v1.md`  
LaTeX skeleton: `paper/main.tex`

---

## Freeze rules (binding)

1. **Do not** run agent experiments (`rq5-run`, causal pilots) during paper iteration.
2. **Do not** modify files under `exports/` except to commit previously generated workspace-local outputs unchanged.
3. **Do not** add paper claims without a new row in this document and the evidence CSV.
4. **Do** cite claim IDs (SS-/MS-/US-) in manuscript drafts for traceability.

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| v1 | 2026-07-03 | Initial scientific evidence freeze for paper-writing mode |
