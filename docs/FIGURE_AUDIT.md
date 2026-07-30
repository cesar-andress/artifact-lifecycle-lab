# Figure Audit — Late Binding Paper

**Scope:** Every figure **used or planned** for the manuscript as of the current skeleton.  
**LaTeX status:** Only `Figure~\ref{fig:model-dag}` exists in `paper/sections/03-conceptual-model.tex` (placeholder box). `paper/figures/` contains no PDFs—only `README.md`. All other figures live in frozen `exports/` and are mapped via `paper/figures/README.md` and `docs/REVIEW_RESPONSE_PLAN.md`.  
**Constraint:** No new figures. “Clearer alternative” means an **existing** table or **existing** figure from this inventory.

**Central claims (reference):** C1 late-binding two-channel model · C2 negligible genuine post-verification decay · C3 born-false / GFC prevalence · C4 born-stale heterogeneity · C5 cited-path selection · C6 agent uptake (read/follow) · C7 behavioral amplification (files modified) · C8 null referential-truth effect on success · C9 environmental task difficulty · C10 RQ1 panel scale · C11 RQ2 survival context · C12 RQ3 regime associations · C13 RQ4 lifecycle occupancy · C14 load-bearing / mediation · C15 P4 attribution (no figure).

---

## Summary rank counts

| Rank | Count | Rule of thumb |
|------|------:|---------------|
| **Essential** | 5 | Paper loses a central claim without it |
| **Useful** | 8 | Strengthens one claim; table could suffice |
| **Redundant** | 14 | Duplicate sibling figure or claim already in table |
| **Remove** | 5 | Not cited, duplicate file, or wrong scope for this paper |

---

## A. Manuscript figure slot (LaTeX)

### `paper/figures/model-dag.pdf` (planned; `fig:model-dag`)

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Yes |
| **Which claim?** | **C1** — late-binding model: static layer, directive + referential channels, runtime binding, environmental gate |
| **Survive without?** | **No** — only visual home for the conceptual contribution; `tables/constructs.tex` is not enough |
| **Clearer alternative?** | `tables/constructs.tex` + prose for definitions; no other **existing** export figure replaces a DAG |
| **Rank** | **Essential** |

---

## B. RQ5 agent experiment figures (`exports/rq5_agent_impact/`)

### `figure_uptake_flow.pdf` → planned `uptake-flow.pdf`

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Yes |
| **Which claim?** | **C6** (128/128 read; 72–78% follow); supports **C1** runtime resolution path |
| **Survive without?** | **Yes** — `rq5_uptake_analysis.md` funnel + future `uptake-funnel.tex` |
| **Clearer alternative?** | **Table** (uptake funnel by condition) is clearer for exact percentages; figure better for narrative flow |
| **Rank** | **Useful** |

### `figure_trace_flow.pdf` → planned `trace-flow.pdf`

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Yes |
| **Which claim?** | **C6**, **C14** — read → follow → act; trace heuristic pipeline |
| **Survive without?** | **Yes** — overlaps `figure_uptake_flow.pdf` and mediation figure |
| **Clearer alternative?** | `figure_uptake_flow.pdf` for uptake; `figure_rq5_mediation_flow.pdf` for causal roles |
| **Rank** | **Redundant** |

### `figure_rq5_mediation_flow.pdf` → planned `mediation-flow.pdf`

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Yes |
| **Which claim?** | **C14** (load-bearing vs non-load-bearing); explains **C8** null alongside **C9** |
| **Survive without?** | **Yes** — `rq5_mediation_summary.md` tables |
| **Clearer alternative?** | **Table** (`mediation-roles.tex`) for counts; figure for B-condition funnel story |
| **Rank** | **Useful** |

### `figure_failure_modes.pdf`

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Yes |
| **Which claim?** | **C9** — tests_failed dominates unsuccessful runs |
| **Survive without?** | **Yes** — one row in uptake analysis |
| **Clearer alternative?** | **Table** (`failure-reasons.tex`) |
| **Rank** | **Redundant** |

### `figure_success_rate.pdf` → planned `abc-success.pdf`

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Yes |
| **Which claim?** | **C8** — A/B/C success (12.7% / 12.7% / 7.9%); primary causal contrast |
| **Survive without?** | **No** — flagship empirical result for Act III; abstract bullet (v) |
| **Clearer alternative?** | `tables/abc-contrasts.tex` for CIs and McNemar; **keep figure** for condition comparison at a glance |
| **Rank** | **Essential** |

### `figure_success.pdf` (local; not git-tracked; duplicate name)

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Same as `figure_success_rate.pdf` if identical content |
| **Which claim?** | **C8** |
| **Survive without?** | **Yes** — duplicate path |
| **Clearer alternative?** | Use **`figure_success_rate.pdf`** only |
| **Rank** | **Remove** |

### `figure_effect_sizes.pdf` (local only)

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Partial |
| **Which claim?** | **C8** — Cohen's h, bootstrap CIs (underpowered narrative) |
| **Survive without?** | **Yes** — not cited in paper body; stats in `rq5_abc_comparative_analysis.md` |
| **Clearer alternative?** | **Table** `abc-contrasts.tex` from same export |
| **Rank** | **Remove** |

### `exports/rq5_agent_impact_c/figure_*.pdf` (duplicates of A/B/C cohort)

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Partial (C-only cohort) |
| **Which claim?** | Condition C 105/105 — secondary to paired triplets |
| **Survive without?** | **Yes** — paper should not dual-publish same chart from two dirs |
| **Clearer alternative?** | Single **`figure_success_rate.pdf`** from paired analysis |
| **Rank** | **Remove** (for manuscript; keep in artifact index only) |

---

## C. Born-stale and confirmatory audits (`exports/truth_decay_pilot/`)

### `figure_born_stale_taxonomy.pdf` → planned `born-stale-taxonomy.pdf`

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Yes |
| **Which claim?** | **C3**, **C4** — 17,747 born-stale; heterogeneous categories; raw 7.9% `genuine_false_claim` |
| **Survive without?** | **No** — main visual for “staleness ≠ single decay process” |
| **Clearer alternative?** | Taxonomy **table** from `born_stale_summary.md` for paper; figure for composition |
| **Rank** | **Essential** |

### `figure_born_stale_by_reference_type.pdf`

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Yes |
| **Which claim?** | **C4** — stratum breakdown |
| **Survive without?** | **Yes** — slice of taxonomy figure |
| **Clearer alternative?** | **`figure_born_stale_taxonomy.pdf`** + table by type |
| **Rank** | **Redundant** |

### `figure_born_stale_by_repository.pdf`

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Yes |
| **Which claim?** | **C4**, selection / **M12** niche corpus |
| **Survive without?** | **Yes** — not in current §5 |
| **Clearer alternative?** | One sentence in **§7** + cohort table |
| **Rank** | **Redundant** |

### `figure_gfc_confirmatory.pdf` → planned `gfc-confirmatory.pdf`

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Yes |
| **Which claim?** | **C3** — 1200/1405 (85.4%) confirmed false at creation |
| **Survive without?** | **Yes** — overlaps taxonomy + GFC table |
| **Clearer alternative?** | **`tables/gfc-taxonomy.tex`** is clearer for TOSEM; figure optional |
| **Rank** | **Useful** |

---

## D. Cited vs uncited audit

### `figure_cited_uncited_churn.pdf` → planned `cited-churn.pdf`

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Yes |
| **Which claim?** | **C5** — 85.4% pairs cited churn ≤ uncited |
| **Survive without?** | **Yes** — `cited_uncited_summary.md` |
| **Clearer alternative?** | **Table** with paired fraction + mean diff CI |
| **Rank** | **Useful** |

### `figure_churn_difference_hist.pdf` → planned `churn-hist.pdf`

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Yes |
| **Which claim?** | **C5** — mean diff CI crosses zero |
| **Survive without?** | **Yes** |
| **Clearer alternative?** | **`figure_cited_uncited_churn.pdf`** OR table; not both needed |
| **Rank** | **Redundant** |

---

## E. RQ1 feasibility figures

### `figure_a_reference_density.pdf` → planned `reference-density.pdf`

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Yes |
| **Which claim?** | **C10** — corpus scale, reference density |
| **Survive without?** | **Yes** — numbers in `rq1_feasibility.md` |
| **Clearer alternative?** | **Table** `cohort-scale.tex` |
| **Rank** | **Redundant** |

### `figure_b_verified_vs_missing_by_age.pdf`

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Partial |
| **Which claim?** | **C10**, weak support for decay narrative |
| **Survive without?** | **Yes** — not cited in §5 |
| **Clearer alternative?** | **`figure_d_state_transitions.pdf`** for dynamics |
| **Rank** | **Remove** (for this paper’s storyline) |

### `figure_c_repair_latency.pdf`

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Partial |
| **Which claim?** | Repair construct (minor; m2 definition mismatch) |
| **Survive without?** | **Yes** — repair not central to late-binding thesis |
| **Clearer alternative?** | **Table** `repair-definitions.tex` |
| **Rank** | **Remove** |

### `figure_d_state_transitions.pdf` → planned `state-transitions.pdf`

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Yes |
| **Which claim?** | **C10**, **C13** — MISSING/UNVERIFIABLE mass vs VERIFIED rarity |
| **Survive without?** | **Yes** — one paragraph + RQ4 occupancy |
| **Clearer alternative?** | **`figure_rq4_state_occupancy.pdf`** if only one lifecycle visual allowed |
| **Rank** | **Useful** |

---

## F. RQ2 survival figures

### `figure_survival.pdf` → planned `survival.pdf`

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Yes |
| **Which claim?** | **C11**, **C2** context — 121 failures, S(365)≈0.848, decay rare among verified-at-origin |
| **Survive without?** | **Yes** — `rq2_summary.md` + audit table for **C2** headline |
| **Clearer alternative?** | **Table** rq2 cohort + **table** rq2 audit taxonomy for paper’s actual punchline (0/121 genuine) |
| **Rank** | **Useful** |

### `figure_cumulative_hazard.pdf`

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Partial |
| **Which claim?** | **C11** — complementary KM view |
| **Survive without?** | **Yes** |
| **Clearer alternative?** | **`figure_survival.pdf`** alone |
| **Rank** | **Redundant** |

### `figure_censoring.pdf`

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Partial |
| **Which claim?** | **C11** — 94.3% right-censored |
| **Survive without?** | **Yes** |
| **Clearer alternative?** | Cohort **table** one row |
| **Rank** | **Redundant** |

---

## G. RQ3 maintenance regime figures

### `figure_rq3_birth_integrity.pdf` → planned `rq3-birth.pdf`

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Yes |
| **Which claim?** | **C12** — association only; birth integrity by regime |
| **Survive without?** | **Yes** — RQ3 not in current §5 narrative; association peripheral to central idea |
| **Clearer alternative?** | **`tables/rq3-regime.tex`** |
| **Rank** | **Redundant** (for current six-act storyline; keep table if RQ3 subsection added) |

### `figure_rq3_repair_probability.pdf`

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Partial |
| **Which claim?** | **C12** |
| **Survive without?** | **Yes** |
| **Clearer alternative?** | RQ3 **table** |
| **Rank** | **Remove** |

### `figure_rq3_transition_matrix.pdf`

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Partial |
| **Which claim?** | **C12** |
| **Survive without?** | **Yes** |
| **Clearer alternative?** | RQ3 **table** |
| **Rank** | **Remove** |

---

## H. RQ4 lifecycle figures

### `figure_rq4_state_occupancy.pdf` → planned `rq4-occupancy.pdf`

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Yes |
| **Which claim?** | **C13** — integrity_loss 55.6% person-time; supports “panel mostly MISSING” |
| **Survive without?** | **Yes** — `rq4_summary.md` table |
| **Clearer alternative?** | **Table** `rq4-occupancy.tex` (m8) |
| **Rank** | **Useful** |

### `figure_rq4_lifecycle_diagram.pdf`

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Partial |
| **Which claim?** | **C13** — schematic |
| **Survive without?** | **Yes** — prose in §2/§4 |
| **Clearer alternative?** | **`model-dag.pdf`** already has lifecycle layer; avoid third diagram |
| **Rank** | **Redundant** |

### `figure_rq4_transition_matrix.pdf`

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Partial |
| **Which claim?** | **C13** — transition probabilities |
| **Survive without?** | **Yes** |
| **Clearer alternative?** | **Table** from `rq4_summary.md` |
| **Rank** | **Redundant** |

### `figure_rq4_repair_latency.pdf`

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Weak |
| **Which claim?** | Repair (peripheral) |
| **Survive without?** | **Yes** |
| **Clearer alternative?** | — |
| **Rank** | **Remove** |

### `figure_rq4_deletion_latency.pdf`

| Question | Answer |
|----------|--------|
| **Supports a claim?** | Weak |
| **Which claim?** | Deletion branch (peripheral) |
| **Survive without?** | **Yes** |
| **Clearer alternative?** | — |
| **Rank** | **Remove** |

---

## I. Missing visual for Essential claim C7

**Claim C7** (~100 vs ~1.7 files modified) is in abstract and §3 but **no dedicated figure exists** in exports—only numbers in `rq5_abc_comparative_analysis.md`.

| Question | Answer |
|----------|--------|
| **Supports a claim?** | N/A (no figure) |
| **Which claim?** | **C7** |
| **Survive without?** | **Yes** — **must** use `tables/abc-behavior.tex` + `tab:evidence-map` row |
| **Clearer alternative?** | **Table** only (no new figure per constraint) |
| **Rank** | — (not a figure) |

---

## Recommended paper figure set (no new figures)

Maximum **6 figures** aligned with `docs/STORYLINE.md` six acts and central idea:

| # | Figure | Act | Rank |
|---|--------|-----|------|
| 1 | `model-dag.pdf` | IV — model | Essential |
| 2 | `figure_born_stale_taxonomy.pdf` | III — static contradicts decay myth | Essential |
| 3 | `figure_success_rate.pdf` | III — null causal referential effect | Essential |
| 4 | `figure_uptake_flow.pdf` | III — agents consume | Useful → promote |
| 5 | `figure_rq5_mediation_flow.pdf` | IV/V — load-bearing / Truth Debt | Useful |
| 6 | `figure_cited_uncited_churn.pdf` OR `figure_rq4_state_occupancy.pdf` | IV — selection / panel occupancy | Useful (pick one) |

**Do not include** in main paper: RQ3 trio, RQ2 hazard/censoring, churn histogram, trace-flow duplicate, failure-modes, born-stale by repo/type, GFC if gfc-table present, RQ1 density/repair, effect_sizes, rq5_agent_impact_c duplicates.

---

## Full rank index (alphabetical by path)

| Figure | Rank |
|--------|------|
| `model-dag.pdf` (planned) | **Essential** |
| `exports/rq5_agent_impact/figure_success_rate.pdf` | **Essential** |
| `exports/truth_decay_pilot/figure_born_stale_taxonomy.pdf` | **Essential** |
| `exports/rq5_agent_impact/figure_uptake_flow.pdf` | **Useful** |
| `exports/rq5_agent_impact/figure_rq5_mediation_flow.pdf` | **Useful** |
| `exports/truth_decay_pilot/figure_gfc_confirmatory.pdf` | **Useful** |
| `exports/truth_decay_pilot/figure_cited_uncited_churn.pdf` | **Useful** |
| `exports/truth_decay_pilot/figure_survival.pdf` | **Useful** |
| `exports/truth_decay_pilot/figure_d_state_transitions.pdf` | **Useful** |
| `exports/truth_decay_pilot/figure_rq4_state_occupancy.pdf` | **Useful** |
| `exports/rq5_agent_impact/figure_trace_flow.pdf` | **Redundant** |
| `exports/rq5_agent_impact/figure_failure_modes.pdf` | **Redundant** |
| `exports/truth_decay_pilot/figure_born_stale_by_reference_type.pdf` | **Redundant** |
| `exports/truth_decay_pilot/figure_born_stale_by_repository.pdf` | **Redundant** |
| `exports/truth_decay_pilot/figure_churn_difference_hist.pdf` | **Redundant** |
| `exports/truth_decay_pilot/figure_a_reference_density.pdf` | **Redundant** |
| `exports/truth_decay_pilot/figure_cumulative_hazard.pdf` | **Redundant** |
| `exports/truth_decay_pilot/figure_censoring.pdf` | **Redundant** |
| `exports/truth_decay_pilot/figure_rq3_birth_integrity.pdf` | **Redundant** |
| `exports/truth_decay_pilot/figure_rq4_lifecycle_diagram.pdf` | **Redundant** |
| `exports/truth_decay_pilot/figure_rq4_transition_matrix.pdf` | **Redundant** |
| `exports/rq5_agent_impact/figure_success.pdf` | **Remove** |
| `exports/rq5_agent_impact/figure_effect_sizes.pdf` | **Remove** |
| `exports/rq5_agent_impact_c/figure_*.pdf` | **Remove** (from ms) |
| `exports/truth_decay_pilot/figure_b_verified_vs_missing_by_age.pdf` | **Remove** |
| `exports/truth_decay_pilot/figure_c_repair_latency.pdf` | **Remove** |
| `exports/truth_decay_pilot/figure_rq3_repair_probability.pdf` | **Remove** |
| `exports/truth_decay_pilot/figure_rq3_transition_matrix.pdf` | **Remove** |
| `exports/truth_decay_pilot/figure_rq4_repair_latency.pdf` | **Remove** |
| `exports/truth_decay_pilot/figure_rq4_deletion_latency.pdf` | **Remove** |

---

## Claim → figure coverage matrix

| Claim | Essential figure | Table fallback |
|-------|------------------|----------------|
| C1 Model | `model-dag.pdf` | `constructs.tex` |
| C2 0/121 decay | — | `rq2-audit-taxonomy.tex` |
| C3 GFC 1200/1405 | `born-stale-taxonomy.pdf` | `gfc-taxonomy.tex` |
| C4 Heterogeneity | `born-stale-taxonomy.pdf` | born_stale_summary |
| C5 Cited stability | `cited_uncited_churn.pdf` (optional) | `cited-uncited.tex` |
| C6 Uptake | `uptake_flow.pdf` (optional) | `uptake-funnel.tex` |
| C7 Files modified | — | `abc-behavior.tex` |
| C8 Δ A−B = 0 | `success_rate.pdf` | `abc-contrasts.tex` |
| C9 Task difficulty | — | `failure-reasons.tex` |
| C10 RQ1 scale | — | `cohort-scale.tex` |
| C11 RQ2 survival | `survival.pdf` (optional) | rq2_summary |
| C12 RQ3 regime | — | `rq3-regime.tex` |
| C13 RQ4 occupancy | `rq4_state_occupancy.pdf` (optional) | `rq4-occupancy.tex` |
| C14 Mediation | `rq5_mediation_flow.pdf` (optional) | `mediation-roles.tex` |
| C15 P4 F1 | — | `p4-validation.tex` |

**Gap:** C2 and C7 have **no** essential figure—by design, tables carry those claims.

---

## Document control

| Field | Value |
|-------|--------|
| Version | v1 |
| Date | 2026-07-03 |
| Figures in `paper/figures/` | 0 PDFs |
| Git-tracked export PDFs audited | 26 |
| Local-only duplicates noted | 6 |
