# RQ5 Dependency Map

**Scope:** Live working copy under `paper/` (`main.tex`, `sections/*.tex`, `tables/*.tex`), plus key lab docs that shape interpretation.  
**Archive note:** `paper/archive/tex/sections/` and `paper/archive/tables/` are synced snapshots of the same claims; treat live `paper/sections/` as authoritative for edit work.  
**Fixed scientific facts (binding for this map):**

1. Blinded human load-bearing / material-necessity annotation for RQ5 v1 is **NOT FEASIBLE** (35/35 cases lack an independent task oracle; circular with the treated instruction). Source: `exports/rq5_lb_blind_annotation/v3_feasibility/RQ5_V1_V3_FEASIBILITY_REPORT.md`.
2. The v2 human annotation kit is **DO NOT DISTRIBUTE** (`exports/rq5_lb_blind_annotation/DO_NOT_DISTRIBUTE_V2.md`).
3. RQ5 A/B/C agent metrics may remain only as an **exploratory descriptive pilot**, not confirmatory causal proof of Truth Debt or material necessity.
4. The 73% “non-load-bearing” mediation figure must **not** be treated as confirmed/validated explanatory support.
5. Prefer **deletion** of unsupported claims over softening into still-unsupported wording.
6. Never imply that human experts validated load-bearing.

**Columns:** Importance = High / Med / Low for manuscript integrity if left as-is.  
**Interp. change?** = whether removing or demoting the claim would change the paper’s scientific interpretation (Yes / No).

---

## 1. Manuscript — title and abstract

| ID | File | Section / locus | Claim (paraphrase) | Imp. | Interp. change? |
|----|------|-----------------|--------------------|------|-----------------|
| M-T1 | `paper/main.tex` | `\title` | Title frames the work as “Late Binding…” (runtime resolution distinct from authoring-time integrity). | High | No — title is compatible with observational + exploratory pilot (see change plan). |
| M-A1 | `paper/main.tex` | Abstract | Late-binding model “motivates a frozen empirical program” including “a controlled A/B/C experiment” (RQ5). | High | Yes — “controlled experiment” reads as confirmatory causal design. |
| M-A2 | `paper/main.tex` | Abstract | Agents read injected instructions (128/128), follow anchors in 77.8% of B runs, expand edit scope (~100 vs ~2), with null paired A−B success (Δ = 0.00 pp; McNemar *p* = 1.0). | High | No if retained as exploratory descriptive metrics; Yes if presented as confirmatory causal proof. |
| M-A3 | `paper/main.tex` | Abstract | Contribution keeps “observational truth decay separate from **causal** operational cost.” | High | Yes — “causal operational cost” overstates what the pilot can identify. |

---

## 2. Introduction

| ID | File | Section / locus | Claim | Imp. | Interp. change? |
|----|------|-----------------|-------|------|-----------------|
| M-I1 | `sections/01-introduction.tex` | Opening framing | Null causal contrast ≠ proof agents ignore instructions; prevalence ≠ operational harm. | Med | No — separation of estimands remains valid. |
| M-I2 | `sections/01-introduction.tex` | Program overview | Results include “**causal contrasts** on task success”; discussion separates Truth Decay from Truth Debt. | High | Yes — “causal contrasts” as confirmatory is unsupported after LB validation failure. |
| M-I3 | `sections/01-introduction.tex` | Three findings | Reports uptake (128/128; 72.3–77.8% follow), edit scope, null Δ A−B as a core reframing finding. | High | Partial — metrics OK as exploratory; bundling them as equal to observational audits overweights RQ5. |
| M-I4 | `sections/01-introduction.tex` | Contributions | Vocabulary includes “**causal load-bearing** references.” | High | Yes — construct cannot be human-validated on v1 cases; must not imply validated LB. |

---

## 3. Background

| ID | File | Section / locus | Claim | Imp. | Interp. change? |
|----|------|-----------------|-------|------|-----------------|
| M-B1 | `sections/02-background.tex` | Gap G1 | No framework jointly measures static integrity, read/follow, and outcomes under controlled referential truth; RQ5 adds condition C for identifiability. | Med | No if RQ5 is redesignated exploratory pilot testing the *design*, not proving the gap closed. |
| M-B2 | `sections/02-background.tex` | Gap G3 | Protocol withholds Truth Debt promotion unless controlled experimentation demonstrates downstream cost. | High | No — withholding remains correct; strengthen: current pilot still does not demonstrate cost. |

---

## 4. Conceptual model

| ID | File | Section / locus | Claim | Imp. | Interp. change? |
|----|------|-----------------|-------|------|-----------------|
| M-C1 | `sections/03-conceptual-model.tex` | C4 | Environmental difficulty and **causal load-bearing status** are explicit moderators; followed anchors may lie off the task-critical path (cites RQ5 protocol / case manifest). | High | Yes — LB status is hypothesized, not validated (human LB infeasible; mediation LB is post-hoc heuristic). |
| M-C2 | `sections/03-conceptual-model.tex` | C5 | Static falsity may coexist with null paired success when power is limited, anchors are **non-load-bearing**, or test friction dominates. | High | Yes — “non-load-bearing” as explanatory support is the 73% pathway; must delete or strip as confirmed mechanism. |
| M-C3 | `sections/03-conceptual-model.tex` + `tables/constructs.tex` | Construct table | Directive channel evidenced by RQ5 A/B vs C edit scope; late binding by RQ5 uptake on B; runtime resolution by RQ5 uptake; **causal load-bearing** evidenced by “Null A−B; cited-path selection.” | High | Yes — LB row falsely ties null A−B to validated load-bearing; uptake/edit-scope rows OK if labeled exploratory. |
| M-C4 | `sections/03-conceptual-model.tex` | Predictions | Prediction 1: A−B null when difficulty dominates and anchors are **non-load-bearing**. Prediction 2: A/B vs C collapses edit scope. | High | Yes for Pred. 1 LB clause; No for Pred. 2 if demoted to exploratory behavioral observation. |

---

## 5. Study design

| ID | File | Section / locus | Claim | Imp. | Interp. change? |
|----|------|-----------------|-------|------|-----------------|
| M-D1 | `sections/04-study-design.tex` | Track split | “**Causal track** (RQ5) addresses runtime consumption and task outcomes under manipulated referential truth.” | High | Yes — rename/demote to exploratory agent pilot. |
| M-D2 | `sections/04-study-design.tex` | Design purpose | Causal track “**tests** the first two model predictions” on uptake, edit scope, success. | High | Yes — “tests” implies confirmatory hypothesis testing of Truth Debt / LB mechanism. |
| M-D3 | `sections/04-study-design.tex` | RQ5 protocol | Describes A/B/C, 35 cases, Claude Code only, partial A/B coverage, 63 triplets, primary estimand paired success difference, McNemar / cluster bootstrap. | Med | No — design facts remain accurate if labeled exploratory / incomplete. |
| M-D4 | `sections/04-study-design.tex` | Unrealized elements | “Blind human outcome adjudication … and **stratified load-bearing contrasts** were specified but not fully realized.” | High | Yes — must update: blind **material-necessity / LB** annotation is not merely unrealized—it is **not feasible** on v1 data (circular; 0/35 independent oracles). Do not imply future v2 kit distribution. |
| M-D5 | `sections/04-study-design.tex` | Freeze gaps | Lists “load-bearing stratified contrasts” among unavailable elements. | Med | Yes — align wording with NOT FEASIBLE + DO NOT DISTRIBUTE (not “pending annotation”). |

---

## 6. Results

| ID | File | Section / locus | Claim | Imp. | Interp. change? |
|----|------|-----------------|-------|------|-----------------|
| M-R1 | `sections/05-results.tex` | Framing | RQ5 is “**operational harm** at pinned commits” / bridge from Truth Decay to Truth Debt. | High | Yes — bridge-as-tested overclaims; demote to exploratory pilot. |
| M-R2 | `sections/05-results.tex` | Coverage & rates | Partial A/B, full C, 63 triplets; read 128/128; follow 72.3%/77.8%; false-claim use 77.8%; triplet success 12.7/12.7/7.9%; Δ A−B 0.00 pp CIs; McNemar *p*-values. | High | No as descriptive pilot facts. |
| M-R3 | `sections/05-results.tex` | Interpretation | Null A−B “cannot be dismissed as non-consumption” because of read/use. | Med | No if kept as descriptive consistency check (exploratory). |
| M-R4 | `sections/05-results.tex` | **Mediation 73%** | “Post-hoc mediation audit … classifies 46/63 runs (73.0%) as **non-load-bearing** … which **explains** how follow and use can coexist with null success effects without invoking universal agent robustness.” | High | **Yes — DELETE.** Unsupported explanatory support; depends on unvalidated post-hoc LB labels. |
| M-R5 | `sections/05-results.tex` | Caveats | Non-significant ≠ robustness; low power; Claude Code / pytest / born-stale cases; uptake stratification post-hoc; mechanisms not inferred from follow/ignore. | Med | No — keep/strengthen; remove any residual LB mediation as explanation. |
| M-R6 | `sections/05-results.tex` | Model predictions | Within uncertainty, referential-truth manipulation does not move paired success (Pred. 1); presence collapses edit scope (Pred. 2). | High | Yes if phrased as confirmatory support for late-binding / LB account; No if limited to exploratory description of pilot outcomes. |
| M-R7 | `tables/evidence-summary.tex` | Evidence map rows | Instruction read/follow; Δ A−B; files modified A vs C; C complete — sourced to RQ5 analyses. | Med | No if limitations column marks exploratory / heuristic / incomplete. |
| M-R8 | Figures | `fig:uptake-flow`, `fig:rq5-panels` | Visualize uptake and ABC success. | Med | No if captions say exploratory pilot. |

---

## 7. Discussion

| ID | File | Section / locus | Claim | Imp. | Interp. change? |
|----|------|-----------------|-------|------|-----------------|
| M-Di1 | `sections/06-discussion.tex` | Truth Debt | Truth Debt “is **not supported** … because outcome variance is not attributable to the manipulated referential channel.” | High | Partial — “not supported” is correct directionally; “not attributable” can read as positive identification of null causal effect. Prefer: pilot does not establish Truth Debt; do not claim channel attribution proven. |
| M-Di2 | `sections/06-discussion.tex` | Runtime coexistence | Panel falsity coexists with readership and false-claim use; presence expands edit scope. | Med | No as exploratory descriptive synthesis. |
| M-Di3 | `sections/06-discussion.tex` | Peripheral refs | Cited-path stability + difficulty may explain weak success differentiation (selection / environment). | Med | No — observational selection argument does not require human LB validation. |
| M-Di4 | `sections/06-discussion.tex` | Agent robustness | Robustness “weakened but not falsified”; stratified uptake Δ ≈ −0.014 when followed. | Med | Yes — stratified uptake is post-hoc exploratory (class B); delete or demote heavily. |
| M-Di5 | `sections/06-discussion.tex` | Practice advice | “**load-bearing strata** and powered binding tasks should be pre-specified before scaling.” | Med | No as future-work recommendation; must not imply LB was measured in v1. |
| M-Di6 | `sections/06-discussion.tex` | Future work | “Test falsifiable model predictions under **load-bearing task designs**.” | Low | No — forward-looking; must not imply current human LB validation exists. |

---

## 8. Threats to validity

| ID | File | Section / locus | Claim | Imp. | Interp. change? |
|----|------|-----------------|-------|------|-----------------|
| M-Th1 | `sections/threats_revised.tex` | Trace heuristics (T-C*) | Read/follow/false-claim use and **mediation causal-role labels** from traces/heuristics, not human coding of binding. | High | No — keep; extend: human LB/material-necessity coding is **infeasible** on v1 (circular). |
| M-Th2 | Same | Follow rates | Follow rates are Medium-confidence inputs to late-binding model. | Med | No. |
| M-Th3 | Same | Injection (I-*) | 100% read under injection protocol. | Med | No. |
| M-Th4 | Same | Channel factorial | No referential-only factorial; channel-specific causal claims unsupported. | High | No — already correctly unsupported. |
| M-Th5 | Same | I-1 Incomplete factorial | Partial A/B; primary claims on 21-case overlap. | High | No if primary is demoted from confirmatory. |
| M-Th6 | Same | Task battery / LB stratum | “Referential falsity might harm … where cited paths are **load-bearing**”; “31/35 cases assigned load-bearing stratum (4 unknown) **without stratified inference**.” | High | Yes — “assigned load-bearing stratum” must not be read as human-validated LB; update with NOT FEASIBLE for blind material-necessity. |
| M-Th7 | Same | S-1 Power | Low success, wide CIs; Truth Debt not supported; stronger robustness claim would not be. | Med | No. |
| M-Th8 | Same | S-6 Post-hoc stratification | Stratified A−B by follow and **mediation causal-role** after runs; labeled exploratory. | High | Yes — strengthen: mediation LB (incl. 73%) must not be used as explanatory support at all. |
| M-Th9 | Same | Closing | Conservative RQ5 null + observational audits survive; unsupported promotions rejected. | Med | Partial — “conservative null” as confirmatory causal finding should be softened to exploratory pilot bounds. |

---

## 9. Reproducibility and conclusion

| ID | File | Section / locus | Claim | Imp. | Interp. change? |
|----|------|-----------------|-------|------|-----------------|
| M-Rp1 | `sections/08-reproducibility.tex` | Package map | Lists RQ5 run ledgers, uptake analyses; `make truth-decay-rq5-uptake truth-decay-rq5-mediation`. | Med | Yes for mediation target if 73% narrative is removed from manuscript (keep Makefile target as archive-only if needed). |
| M-Rp2 | Same | Freeze | Partial A/B fixed; no further agent runs; use 128-run uptake report. | Low | No. |
| M-Co1 | `sections/09-conclusion.tex` | Empirical wrap | Repeats null A−B, read 128/128, edit scope as established findings alongside observational audits. | High | Yes — demote RQ5 sentences to exploratory pilot. |
| M-Co2 | Same | Model wrap | Late-binding separates prevalence from “**causal load** on task outcomes.” | High | Yes — “causal load” implies LB/Truth Debt identification. |
| M-Co3 | Same | Open questions | “Referential harm under **load-bearing tasks**”; complete A/B/C factorial. | Med | No as open questions; must not imply LB already validated. |

---

## 10. Key lab documents (not every packet)

| ID | File | Section / locus | Claim | Imp. | Interp. change? |
|----|------|-----------------|-------|------|-----------------|
| D-S1 | `docs/STORYLINE.md` | Central idea | Success “gated by environment and **load-bearingness**,” not commit-time truth. | High | Yes — LB presented as established gate; revise to hypothesized / unvalidated on v1. |
| D-S2 | Same | Act III–IV | Null A−B as causal impact axis; late-binding model with **causally load-bearing** references explaining weak differentiation. | High | Yes — same LB explanatory overclaim. |
| D-S3 | Same | Act V–VI | Truth Debt not promoted from null A−B; future validate LB against human-coded trajectories; complete factorial on LB strata. | Med | Partial — future human validation must note v1 blind LB is NOT FEASIBLE (needs new case design with independent oracles). |
| D-T1 | `docs/TOSEM_READINESS.md` | Scores / blockers | RQ5 incomplete/underpowered; cannot support central coupling; reframe as measurement paper; RQ5 as exploratory pilot appendix. | High | No — already aligned with demotion; update with LB annotation NOT FEASIBLE fact. |
| D-T2 | Same | Strong assets | “RQ5 uptake + null A−B = Exploratory pilot; not headline.” | Med | No. |
| D-M1 | `exports/rq5_agent_impact/rq5_mediation_summary.md` | Q2 / Q5 | 46/63 (73%) not load-bearing; null “**Primarily irrelevance / low load-bearingness**, not robustness.” | High | **Yes — do not cite as confirmed.** Retain only as superseded post-hoc heuristic export if archived. |
| D-F1 | `exports/rq5_lb_blind_annotation/v3_feasibility/RQ5_V1_V3_FEASIBILITY_REPORT.md` | Verdict | `NOT_FEASIBLE_WITH_CURRENT_RQ5_V1_DATA`; 0/35 independent; 35/35 circular. | High | N/A (authoritative negative result). |
| D-F2 | `exports/rq5_lb_blind_annotation/DO_NOT_DISTRIBUTE_V2.md` | Kit status | v2 kit must not be distributed or used to claim blind LB re-annotation. | High | N/A (process constraint). |
| D-A1 | `paper/archive/current_claims.md` | RQ5 row | RQ5 labeled “**Causal** (A/B/C)”; contributions list null A−B with observational audits. | High | Yes — archive baseline must be superseded by exploratory labeling. |

**Explicitly out of scope for this map:** individual `packets/*/packet.md` and `human_annotation_kit/PACKETS/**` (circular/non-distributable; do not inventory per packet).

---

## 11. Dependency clusters (for edit sequencing)

1. **Confirmatory-causal language cluster** (High): M-A1, M-A3, M-I2, M-D1–D2, M-R1, M-Di1 (attribution wording), M-Co1–Co2, D-A1.  
2. **Load-bearing / material-necessity explanatory cluster** (High — delete or strip): M-C1–C2, M-C3 LB row, M-C4 Pred.1 LB clause, M-R4, M-Di4 (stratified uptake as mechanism), M-Th6/Th8, D-S1–S2, D-M1.  
3. **Exploratory A/B/C metrics cluster** (retain with demotion): M-A2, M-I3 (partial), M-D3, M-R2–R3, M-R5–R8, M-Di2–Di3, evidence-map RQ5 rows.  
4. **Process / feasibility cluster** (must add): M-D4–D5, M-Th1/Th6, D-F1–F2, updates to STORYLINE future work and TOSEM_READINESS.

---

## 12. Archive pointer

`paper/archive/tex/sections/{01–09,threats_revised}.tex` and `paper/archive/tables/{constructs,evidence-summary}.tex` mirror the live claim surface. After live edits, re-sync or mark archive stale; do not treat archive as a second scientific source of truth.
