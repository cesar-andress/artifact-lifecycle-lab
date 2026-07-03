# Reviewer #2 Simulation — ACM TOSEM Associate Editor

**Manuscript:** *Late Binding in Machine-Consumed Instruction Files*  
**Recommendation:** **REJECT** (not resubmit without fundamental redesign)  
**Reviewer stance:** Assume authors claim the Late Binding model is validated. Ignore author framing. Try to kill the paper.

---

## Executive verdict

This submission is a **post-hoc vocabulary** applied to a **fragmented internal benchmark report**. It does not validate a model; it **names** behaviors after the fact. The observational track (RQ1–RQ4) never tests two channels. The causal track (RQ5) is **incomplete**, **single-agent**, **underpowered**, and **confounded**. The central causal claim—referential static truth is weakly coupled to task success—is indistinguishable from **“the experiment failed to detect anything.”** The directive/referential decomposition is **not operationalized**, **not independently measured**, and **not falsifiable** as written.

I would not send this to reviewers in current form. Multiple sections are TODO stubs. Key artifacts cited in the paper are **not in the reproducibility bundle** (`p4_validation.md`, `rq5_results.csv`, entire `rq5_agent_impact_c/` per authors’ own freeze doc).

---

## Section-by-section dissection

### Abstract + Title (`paper/main.tex`)

| Claim | Simpler explanation? | Missing evidence | AE request before acceptance | Solvable with existing data? |
|-------|---------------------|------------------|------------------------------|------------------------------|
| “Late-binding model” explains agent consumption | **Yes:** agents read files when files exist; pointers are resolved at run time. That is tautology, not a model. | Formal model with **pre-registered predictions** distinct from “agents use files”; falsification criteria; held-out test of model predictions | Pre-register model **before** any RQ5 run; show at least one prediction that failed and forced model revision | **New evidence** (prospectively designed test) |
| Genuine post-verification decay rare (0/121) | **Yes:** your audit pipeline reclassifies 73.6% as extractor artifacts by construction; “0 genuine” may mean “heuristics don’t label genuine.” | Blind human adjudication sample; inter-rater κ; sensitivity analysis **without** deterministic override rules | n≥50 randomly sampled “genuine_decay” borderline cases with two independent human judges | Mostly **new evidence**; sensitivity re-run on `rq2_failure_audit.csv` possible but not sufficient |
| 1200/1405 confirmed false at creation | **Yes:** mechanical path-missing at first snapshot ≠ semantically “false instruction”; conflates template, anchor, glob, normative text | Semantic falsehood gold set; developer intent labels | Human validation on stratified 100 confirmed_false vs 100 normative/template cases | **New evidence**; partial re-label from `gfc_confirmatory_examples.csv` if humans available |
| Agents read 128/128 | **Yes:** you **inject** the file pre-run; 100% read is an **experimental artifact**, not uptake discovery | Condition where instruction is optional; naturalistic IDE discovery; read without injection | Remove forced injection; measure organic discovery; report read rate <100% or justify design | **New evidence** |
| ~100 vs ~2 files modified = directive channel | **Yes:** (a) agent told to edit broadly, (b) metric counts spurious touches, (c) test harness side effect, (d) C removes file so agent has different prompt surface—not channel separation | File-modification breakdown by intent; diff size; lines changed; human audit of 20 runs; D condition with **directive-only stub** without referential anchor | Add condition D: directive text only, no anchor path; add condition E: anchor only, no directive; decompose files_modified | **New evidence** (requires new conditions) |
| Static truth weakly coupled to success (Δ A−B = 0) | **Yes:** power ~0; tasks too hard; manipulation didn’t change binding; anchor not load-bearing; **all of the above** | Power analysis **before** experiment; pre-specified MDE; load-bearing stratum primary analysis | Complete 35×3×3 factorial; pre-registered load-bearing primary endpoint; report negative result with justified power | Partial: reanalyze **existing traces** for load-bearing subsample; completion of A/B on 13 missing cases uses **existing protocol** but **new runs** |

---

### §1 Introduction

| Claim | Simpler explanation? | Missing evidence | AE request | Existing data? |
|-------|---------------------|------------------|------------|----------------|
| Instruction files are “not ordinary documentation” | **Yes:** you never ran an experiment comparing consumption semantics to README; P5 is feasibility counts only | RQ5 arm with README/CONTRIBUTING at same pin; human reader study | Controlled comparison: machine instruction vs human doc vs none | **New evidence** |
| Two-channel semantics “split” | **Yes:** any doc has prose + links; relabeling markdown structure isn’t science | Automatic channel classifier with accuracy on gold corpus; inter-annotator agreement on channel labels | Publish classifier + 500-reference gold; report precision/recall per channel | Can **annotate existing** `born_stale_taxonomy.csv` / snippets—**existing data**, needs human labeling |
| Multi-stage program supports model | **Yes:** RQ1–4 measure git panel states; RQ5 measures agent traces; **nothing ties them into one estimand** | Joint model fit; same cases across observational + causal; preregistered bridge hypotheses | Single unified dataset linking panel references to RQ5 cases | **Existing data** partially (`rq5_candidate_dataset.csv`)—merge analysis possible, not done |
| Contributions include “reproducibility bundle” | **Yes:** CSV index ≠ reproducibility; half of RQ5 artifacts not git-tracked | Public artifact with checksums; all CSVs committed; Docker pin for Claude Code version | Commit all exports; pin agent version; Zenodo DOI | **Existing data** on disk—**editorial/process**, not science |

**Fatal on §1:** Central claim is presented as finding; it is a **definition** dressed as discovery.

---

### §2 Background

| Claim | Simpler explanation? | Missing evidence | AE request | Existing data? |
|-------|---------------------|------------------|------------|----------------|
| Born-stale vs post-decay distinction | **Yes:** standard left-truncation / survival framing; not novel | Prior art positioning (authors left TODO); proof distinction improves any downstream decision | Literature review + citation to survival bias / immortal time | **New evidence** for novelty; distinction itself is **descriptive** from existing RQ2 |
| P4 F1 0.9617 | **Yes:** N=200 stratified pilot; optimistically biased; file not in artifact | Independent holdout; second annotator; commit validation export | Second review pass on 100 fresh commits | **New evidence** for generalization; re-report from worksheet = **existing data** |
| RQ5 C separates presence from truth | **Yes:** C removes **both** channels (directive + referential), so A−C confounds presence with content | C_null_directive (empty file), C_straw_man (random paths), factorial separation | 2×2: {presence} × {truthful referential} | **New evidence** |

**Major on §2:** Background §2.1 is TODO. TOSEM does not publish outline drafts.

---

### §3 Conceptual Model

| Claim | Simpler explanation? | Missing evidence | AE request | Existing data? |
|-------|---------------------|------------------|------------|----------------|
| Late-binding model (Figure 1) | **Yes:** DAG is **not in the paper**—placeholder box; model is external markdown | Camera-ready DAG; structural equation or causal identification proof; testable implications listed **a priori** | Include figure; enumerate 5 falsifiable implications; show which RQ tests which edge | Figure from Mermaid = **existing**; **testing** needs new design |
| Directive channel “strongly shapes behavior” | **Yes:** agents edit more when a file exists—could be prompt injection, not “directive semantics” | Manipulation of directive text only (strict vs permissive) holding referential constant | Factorial directive manipulation | **New evidence** |
| Referential channel resolved at use time | **Yes:** trivial for any tool-using agent | Show case where static VERIFIED but runtime bind fails, **and** outcome changes | Trace-grounded counterexamples linked to outcomes | **Existing traces** may contain cases—needs **new analysis** |
| Causal load-bearing construct | **Yes:** post-hoc trace labels (`uptake_but_not_load_bearing`) | Pre-registration; external task graph; ground truth from task spec | Load-bearing labels frozen **before** runs; primary analysis on load-bearing subset only | Flags exist in redesign plan—**new runs** with pre-specified primary endpoint |
| 85.4% cited ≤ uncited ⇒ peripheral false claims | **Yes:** selection on stable paths does **not** imply false claims are peripheral to **tasks**—only to git churn | Task-level load-bearing correlated with churn; within-repo case studies | Per-case analysis: is manipulated anchor high-churn or low-churn? | **Existing data** in case manifest + cited_uncited |

**Fatal on §3:** The “model” is **not a model**—it is a diagram and a glossary. TOSEM publishes **evaluated** engineering theories, not naming conventions.

---

### §4 Study Design

| Claim | Simpler explanation? | Missing evidence | AE request | Existing data? |
|-------|---------------------|------------------|------------|----------------|
| “Frozen laboratory corpus” | **Yes:** pilot + E1-100 engineering frame; authors admit not scientific strata | Registry inclusion criteria; representativeness vs GitHub population | Cohort table with selection flow; bias discussion quantified | **Existing** `rq1_feasibility.md` threats—needs writing, not new runs |
| RQ1–RQ4 observational track | **Yes:** four related descriptives; not one study | Unified pre-analysis plan; multiplicity control across RQs | Single SAP with family-wise error control | **Existing data**; **new** analysis discipline |
| GFC / RQ2 audits | **Yes:** deterministic rules dominate; LLM used on 1/121 post-verification cases, 0/1405 GFC | LLM/human adjudication rates; failure mode of rules | Audit protocol with human escalation threshold | Re-audit = **new evidence** |
| RQ5: 128 A/B on 22/35 cases; 105 C on 35/35 | **Yes:** **stopped early** on A/B; complete C; paired analysis on overlap **only** | Why stopped; preregistered stopping rules; complete A/B on all 35 | Finish A/B for remaining 13 cases minimum | **New runs** (same protocol) |
| Single agent (Claude Code CLI) | **Yes:** vendor-specific prompt/tooling behavior | ≥2 agents (IDE + CLI) on identical pinned workspaces | Cross-agent replication table as **primary** result | **New evidence** |
| Design TODOs (prompt, registry, cohort sizes) | N/A | Complete protocol in paper body | Full task prompt, test command policy, case selection algorithm in appendix | **Existing** in `protocol/RQ5_AGENT_IMPACT_EXPERIMENT_v1.md`—**editorial extraction** |

**Fatal on §4:** Causal study is **not completed**. Publishing incomplete factorial + post-hoc ABC merge is unacceptable for TOSEM causal claims.

---

### §5 Results

| Claim | Simpler explanation? | Missing evidence | AE request | Existing data? |
|-------|---------------------|------------------|------------|----------------|
| RQ1 panel scale (339k obs) | **Yes:** large N from regex extraction over many UNVERIFIABLE commands | Validated sample of references; precision/recall of extractor | P3-style extraction audit on random 500 refs | **Existing** `p3_rot_incidence.md`—cite and bound claims |
| 0/121 genuine decay | **Yes:** see audit circularity above | Human replication | Blind audit sample | **New evidence** |
| 1200 confirmed false | **Yes:** path missing at birth in mechanical checker | Semantic falsehood | Human semantic audit subset | **New evidence** |
| 85.4% paired stability | **Yes:** extension/depth matching weak; mean diff CI crosses 0 | Stronger matching (LOC, ownership, team); within-repo diff-in-diff | Re-match analysis | **Existing** `cited_uncited_comparison.csv`—**new analysis** possible |
| RQ3 regime differences | **Yes:** ecological confounding; file-level regime; P4 was “pending” when RQ3 written | Regression with repo fixed effects; propensity scoring | Reanalyze RQ3 with validated P4 only + controls | **Existing** `rq3_dataset.csv`—**new analysis** |
| 100% instruction_read | **Yes:** injection + trace definition equates file mention with read | Independent read verification (file access logs) | Redefine read; report sensitivity | **Existing traces**—**new coding** |
| 77.8% instruction_followed | **Yes:** string match on anchor in tool args | Precision vs human coding of “followed” on 30 traces | Human trace audit | **Existing traces**—**new human labels** |
| Δ A−B = 0.00 pp | **Yes:** null because true effect zero **or** n too small **or** manipulation ineffective | Equivalence test with pre-specified margin; Bayes factor | TOST or Bayes analysis with priors | **Existing** `rq5_effect_sizes.csv`—**new analysis** |
| ~100 files modified | **Yes:** metric insanity—100 files median smells like counter bug or repo-wide scan | Validate metric against `git diff --stat`; manual review | Metric validation appendix | **Existing** run workspaces if preserved—else **new evidence** |
| 12.7% vs 7.9% A vs C | **Yes:** underpowered; 3 discordant pairs drive narrative | Full n=105 paired; CI still wide | Complete pairing | **New runs** for A/B on 13 cases |

**Major on §5:** Results read like a **lab wiki export**, not a curated empirical study. No effect sizes linked to pre-registered hypotheses.

---

### §6 Discussion

| Claim | Simpler explanation? | Missing evidence | AE request | Existing data? |
|-------|---------------------|------------------|------------|----------------|
| Model “reconciles” observational + causal | **Yes:** reconciliation is **storytelling** when causal arm is null and observational arm uses different construct | Formal joint likelihood or Bayesian model combining both layers | Fit unified model or drop “reconciles” language | **New evidence** / **rewrite** |
| Environmental task difficulty dominates (~88% failure) | **Yes:** you picked hard repos/tests; agents fail for many reasons | Task difficulty calibration; success rate floor/ceiling analysis | Report task difficulty distribution; show manipulation works on easy subset | **Existing** `rq5_failure_modes.csv`, traces—**new analysis** |
| Truth Debt not supported | Agree—but then **why is this a TOSEM paper?** | Positive contribution beyond “null result + glossary” | Clarify contribution: measurement instruments? cohort? protocol? | N/A |
| Alternatives “weakened” | **Yes:** you **fail to reject** alternatives; that is not weakening | Pre-specified alternative tests with pass/fail | Register alternatives as competing hypotheses | **New design** |
| Tool builder implications (§6.5) | **Yes:** generic SE advice not validated by intervention | User study or tool prototype showing lint/split helps | At least one implemented lint rule evaluated on corpus | **New evidence** |

**Fatal on §6:** Discussion admits Truth Debt unsupported, experiment incomplete, single agent—then asserts model anyway. That is **internal contradiction**.

---

### §7 Threats to Validity

| Claim | Simpler explanation? | Missing evidence | AE request | Existing data? |
|-------|---------------------|------------------|------------|----------------|
| Authors list threats | Listing threats ≠ mitigating | Mitigations attempted (even failed) | For each fatal threat: what was done? | Mostly **writing** |
| Underpowered McNemar | **Yes:** threat acknowledged, paper proceeds | Power retrospective; justify n | Post-hoc power or justify as pilot-only paper | **Existing data** for power calc |
| instruction_followed heuristic | **Yes:** core construct invalid | Human-validated trace coding | κ on 50 runs | **Existing traces** + **new labels** |

**Major on §7:** Threats section is honest enough to **justify rejection** on its own.

---

### §8 Reproducibility

| Claim | Simpler explanation? | Missing evidence | AE request | Existing data? |
|-------|---------------------|------------------|------------|----------------|
| “All reported numbers from frozen exports” | **False:** key paths workspace-local per `SCIENTIFIC_EVIDENCE_FREEZE.md` | Git commit containing **all** cited files | Single artifact tarball matching paper SHA | **Process fix**—commit existing files |
| Makefile targets TODO | N/A | Exact commands that regenerate every table | Runnable CI job reproducing numbers | **Existing** Makefile—**editorial** |
| “No further agent experiments” | N/A for reproducibility | Then causal claims must be **downgraded** to pilot | Label RQ5 as exploratory in title/abstract | **Writing** |

**Fatal on §8:** Reproducibility failure for TOSEM artifact evaluation standard.

---

### §9 Conclusion

| Claim | Simpler explanation? | Missing evidence | AE request | Existing data? |
|-------|---------------------|------------------|------------|----------------|
| “Behave as late-binding artifacts” | **Yes:** restates thesis without proof | Any non-vacuous falsification attempt | One failed test of model | **New evidence** |
| Future work list (complete ABC, load-bearing, cross-agent) | **Yes:** that list is what **this paper should have done** | N/A | Do the future work; submit v2 | **New evidence** |

---

## Ranked criticisms

### FATAL (paper cannot be accepted; reject)

| ID | Criticism | Simpler alternative | Missing evidence | AE requirement | Existing data? |
|----|-----------|---------------------|------------------|----------------|----------------|
| F1 | **Late Binding model is not tested—only illustrated.** No pre-registered predictions; no falsification; DAG is placeholder. | Rename behaviors after seeing RQ5 nulls | Pre-specified model tests; held-out prediction | Model registered before experiments; ≥3 tested implications | **New evidence** |
| F2 | **RQ5 causal study incomplete:** 22/35 A/B cases, 63/105 paired triplets, A/B and C in separate export trees. | Analyze only complete overlap because that's all you have | Full 35-case factorial with unified ledger | Complete A/B; single `rq5_results.csv` | **New runs** (+ merge **existing**) |
| F3 | **Single agent (Claude Code CLI).** All causal claims are vendor-specific. | Claude-specific prompt compliance | Replication on Cursor + Copilot minimum | Multi-agent as **primary**, not future work | **New evidence** |
| F4 | **100% instruction_read is tautological** under forced injection. | Experimental setup guarantees read | Naturalistic consumption design | Redesign read metric or downgrade claim to “file present in context” | **New evidence** |
| F5 | **Directive vs referential channels not operationalized or measured independently.** ~100 files modified attributed to “directive channel” without isolation. | File presence changes prompt | Factorial D/E conditions; validated channel parser | 2×2 manipulation study | **New evidence** |
| F6 | **0/121 genuine decay depends on audit that classifies 73.6% as artifacts using same pipeline that created labels.** | Zero by definitional closure | Blind human audit; rule ablation study | Independent adjudication sample n≥50 | Mostly **new evidence** |
| F7 | **Reproducibility bundle incomplete:** `p4_validation.md`, `rq5_results.csv`, `rq5_agent_impact_c/` not git-tracked at freeze. | N/A | Artifact DOI matching paper commit | Commit/publish all cited paths | **Existing on disk**—process |
| F8 | **Central causal claim (weak coupling of static truth to success) is indistinguishable from low power + bad tasks.** | Type II error | Pre-specified MDE; equivalence test; easy-task stratum where manipulation binds | Power analysis + load-bearing primary analysis | Partial **existing** reanalysis; stratum needs **new runs** |
| F9 | **Not a TOSEM contribution as structured:** amalgam of internal RQs, TODO sections, external model doc, no related work. | Technical report | Related work; single coherent research question | Rewrite as one RQ or split into 2 papers | **Writing** + scope cut |

---

### MAJOR (would block acceptance until fixed)

| ID | Criticism | Simpler alternative | Missing evidence | AE requirement | Existing data? |
|----|-----------|---------------------|------------------|----------------|----------------|
| M1 | **Confirmed false at creation (1200/1405) equates mechanical MISSING with semantic false claim.** | Extractor says path absent | Human semantic gold on 200 cases | Validation subset with κ | **New evidence** |
| M2 | **instruction_followed / false_claim_used are trace heuristics without validated accuracy.** | Substring match in logs | Human coding of 50 traces; precision/recall | Trace validation study | **Existing traces** + **new labels** |
| M3 | **files_modified ≈ 100 median is implausible without metric validation.** | Counter bug or “list dir” behavior | Manual diff audit on 10 runs | Metric definition + sanity checks | **Existing** if workspaces kept |
| M4 | **Condition C confounds removal of referential + directive content.** | Any file removal changes behavior | Empty file / whitespace / README substitution arms | Expanded baseline conditions | **New evidence** |
| M5 | **Cited vs uncited stability does not support load-bearing peripherality**—different estimand. | Authors cite stable paths | Link anchor churn to task outcome per case | Case-level merge table | **Existing** case manifest + audits |
| M6 | **RQ3 causal language in discussion despite observational design.** | Confounding | Fixed-effects models; explicit “association only” | Reanalyze or delete causal phrasing | **Existing** `rq3_dataset.csv` |
| M7 | **P4 validation N=200 single reviewer; not committed.** | Overfit to heuristic | Second reviewer; holdout | Publish validation artifact | **Existing** worksheet; **new** review |
| M8 | **Mediation roles (19% caused failure vs null A−B) internally inconsistent.** | Heuristic labels incompatible | Align mediation taxonomy with outcome regression | Sensitivity analysis | **Existing** mediation CSV |
| M9 | **No comparison to human documentation (P5 feasibility only).** | Machine ≠ human untested | RQ5 with README control | Human-doc arm | **New evidence** |
| M10 | **Multiplicity:** dozens of tests across RQ1–5 without correction. | p-hacking by RQ shopping | Pre-registered primary endpoints | SAP document | **Writing** + **existing** reanalysis |
| M11 | **Born-stale heterogeneity (7 categories) ignored in causal design.** | One anchor type may dominate | Stratum-specific A−B effects | Report by reference type | **Existing** taxonomy + case manifest |
| M12 | **Generalizability:** AI-convention repos are a biased niche (projects that adopt AGENTS.md). | Selection bias | Comparison to random OSS sample | Selection diagram | **Existing** registry metadata |

---

### MINOR (must fix for publication quality)

| ID | Criticism | Simpler alternative | Missing evidence | AE requirement | Existing data? |
|----|-----------|---------------------|------------------|----------------|----------------|
| m1 | Abstract lists five findings but none establish “late binding” vs obvious runtime file use | Wording | Sharpen claims | Rewrite abstract claims | **Writing** |
| m2 | RQ1 “repair ratio 0.0%” vs RQ2 “67.9% repair incidence”—not reconciled in paper | Definition mismatch | Cross-RQ definition table | One paragraph reconciling repair constructs | **Existing** summaries |
| m3 | Wilson CIs on 0/121 and 8/63 success are wide; paper treats point estimates too confidently | Small n | Always pair with CI in text | Add CI to every proportion claim | **Existing** stats |
| m4 | Cohen's h reported as 0.1575 for A−C but labeled unsupported—pick narrative | — | Consistent interpretation | Clarify effect size threshold | **Existing** |
| m5 | Execution time differences not discussed despite being collected | Noise | Report or drop | Include or cut variable | **Existing** ABC analysis |
| m6 | `rq5_summary.md` stale (9 runs) exists in repo—confusing artifact | — | Remove or archive stale exports | Clean artifact tree | **Editorial** |
| m7 | Evidence table row P4 cites `p4_validation.md` not in artifact | — | Path alignment | Fix citation to committed file | **Editorial** |
| m8 | RQ4 person-time occupancy dominates integrity_loss—paper underplays that most life is “missing” | — | Interpretive balance | Expand RQ4 integration | **Existing** |
| m9 | No quantitative cost ($114 agent spend mentioned in lab notes?) in paper | — | Cost transparency | Report total experiment cost | **Existing** logs if saved |

---

### EDITORIAL (reject from desk if submitted today)

| ID | Issue | AE requirement | Existing data? |
|----|-------|----------------|----------------|
| E1 | §2.1, §4.1, §4.2, §8.2 contain `\todo{}` placeholders | Complete all TODOs | **Writing** |
| E2 | Figure 1 is a literal “TODO” box | Replace with figure | **Existing** Mermaid export |
| E3 | `\bibliography{references}` with empty/stub bib | Related work for TOSEM | **New writing** (literature review) |
| E4 | Authors, affiliations, DOI all TODO | Anonymization ok for review, not for decision | **Writing** |
| E5 | Paper organization paragraph TODO | Finish | **Writing** |
| E6 | `paper/figures/` empty—figures only in exports | Copy figures or submission incomplete | **Existing** PDFs |
| E7 | Internal paths (`docs/LATE_BINDING_MODEL_v1.md`) cited in prose | Self-contained paper | **Writing** |
| E8 | CCS concepts generic; keywords don't mention empirical methods limitations | Tune metadata | **Writing** |

---

## What simpler story explains **everything** without Late Binding?

**The Occam narrative:**

1. Regex panel over instruction files produces noisy VERIFIED/MISSING labels.
2. Most “staleness” is born-at-birth missing paths, templates, and extractor error—not time decay.
3. You ran a small Claude Code benchmark on hard test tasks.
4. Swapping one anchor string true→false did not change pass rate because tasks fail on tests, anchors are often irrelevant, and n is tiny.
5. Agents edit more when an instruction file is in the prompt context.
6. You packaged (1)–(5) as “two channels” and “late binding.”

That story fits **all** reported numbers. The paper does not show it is **wrong**.

---

## Minimum bar for **reconsideration** (not acceptance)

I would not accept without:

1. **Complete RQ5 ABC** on all 35 cases, unified dataset, pre-registered analysis plan.
2. **≥2 agent platforms** on identical cases.
3. **Human-validated trace coding** for `instruction_followed` (κ reported).
4. **Factorial separation** of directive vs referential manipulation (not just A/B/C).
5. **Independent audit sample** for post-verification decay claims (or stop claiming 0).
6. **Committed reproducibility artifact** matching every cited path.
7. **Related work** positioning against documentation drift, context for LLMs, software traceability—authors currently cite nothing.
8. **Downgrade or delete** “model validated” language unless a pre-registered test survives falsification.

Estimated work: **new experiments required**; observational reanalysis alone is insufficient.

---

## Existing data that authors **could** mine (does not salvage acceptance)

| Analysis | Data source | Would fix |
|----------|-------------|-----------|
| Load-bearing primary stratum A−B | `rq5_mediation_dataset.csv`, case flags | F8 partially |
| Post-hoc power / equivalence on A−B | `rq5_effect_sizes.csv` | F8 narrative |
| Case-level anchor churn vs outcome | case manifest + `cited_uncited_comparison.csv` | M5 |
| RQ3 with repo fixed effects | `rq3_dataset.csv` | M6 |
| Human trace audit sample | `exports/rq5_agent_impact/traces/*.jsonl` | M2 |
| Channel annotation pilot | born-stale snippets | §3 operationalization pilot |
| Commit workspace-local exports | disk | F7 |

None of these replace F2, F3, F5, F9.

---

## Simulated AE letter (final paragraph)

> I recommend **reject**. The submission proposes terminology for known facts (agents read files at run time; static analysis labels disagree with outcomes) and attaches it to an **incomplete, single-vendor, underpowered** experiment whose null results are interpreted as support for a **post-hoc conceptual diagram**. The observational corpus is useful; the causal evidence is not ready; the model is not tested. The manuscript is **not submission-complete** (TODO figures, sections, bibliography). Reorganize as a rigorous measurement paper **or** complete the factorial agent study **then** resubmit. In current form this is an internal lab report, not TOSEM.

---

## Document control

| Field | Value |
|-------|-------|
| Version | v1 |
| Date | 2026-07-03 |
| Role | Simulated AE / Reviewer #2 (reject bias) |
| Sources read | `paper/main.tex`, `paper/sections/01–09`, `paper/tables/*`, `docs/LATE_BINDING_MODEL_v1.md`, `docs/SCIENTIFIC_EVIDENCE_FREEZE.md`, `exports/paper_synthesis/late_binding_evidence_table.csv`, key RQ5/truth_decay summaries |

**Note:** This document is adversarial by assignment. It does not assert authors are wrong—only that **TOSEM acceptance bar** is not met.
