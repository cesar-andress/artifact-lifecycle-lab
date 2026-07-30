# RQ5 Claim Audit

**Classification schema**

| Class | Meaning |
|-------|---------|
| **A** | Supported independently of RQ5 human load-bearing (LB) / material-necessity validation. May include exploratory A/B/C agent metrics (uptake, success deltas, edit scope) when reported as descriptive pilot facts with stated limits. |
| **B** | Depends on exploratory post-hoc analysis only (e.g., mediation 73% non-LB, uptake strata, causal-role labels from traces). Not confirmatory. |
| **C** | Depends on failed / infeasible human validation of LB or material necessity (blind annotation NOT FEASIBLE: 35/35 circular, 0 independent task oracles; v2 kit DO NOT DISTRIBUTE). |
| **D** | No longer supported. Prefer deletion over softening into a still-unsupported claim. |

**Binding negative results**

- Human blind LB/material-necessity annotation on RQ5 v1: **NOT FEASIBLE** (`RQ5_V1_V3_FEASIBILITY_REPORT.md`).
- Therefore: any claim that human experts validated load-bearing, or that material necessity was independently adjudicated for the 35 cases, is **D** (or **C** if the claim merely *requires* that validation to hold).
- RQ5 A/B/C may remain **exploratory descriptive pilot** only — not confirmatory causal proof of Truth Debt or of LB moderation.

---

## A — Supported without human LB validation

These claims stand on observational exports and/or frozen agent-run ledgers when framed within their limits. They do **not** require human LB coding.

### A1. Observational program (context for RQ5, not RQ5-causal)

| Claim | Support | Why A |
|-------|---------|-------|
| Genuine post-verification decay ~0/121 after RQ2 audit | RQ2 failure audit | Independent of RQ5 |
| Born-false / GFC 1200/1405 (85.4%) | GFC / born-stale autopsy | Independent of RQ5 |
| Cited paths often no-higher-churn than controls (stability fraction); mean churn CI crosses 0 | Cited-vs-uncited audit | Selection story does not need human LB labels |
| P4 agent-maintenance classifier metrics on gold sample | P4 validation | Observational attribution gate, not Truth Debt |

### A2. Exploratory RQ5 A/B/C descriptive pilot (retainable if demoted)

| Claim | Support | Why A (with framing constraint) |
|-------|---------|----------------------------------|
| Instruction read 128/128 on A/B under injection protocol | Uptake analysis | Trace/protocol fact; tautological under injection (threat), not LB-dependent |
| Instruction follow ~72.3% (A) / 77.8% (B); false-claim use 49/63 (77.8%) on B | Uptake analysis | Heuristic trace construct — Medium confidence; still independent of *human* LB validation |
| Triplet success 12.7% / 12.7% / 7.9% (A/B/C); Δ A−B = 0.00 pp; cluster bootstrap CI includes 0; McNemar *p* = 1.0 on 63 triplets | A/B/C analysis | Paired binary outcomes; **descriptive pilot statistic**, not confirmatory Truth Debt test |
| Mean files modified ~100 (A/B) vs ~1.7 (C) on triplets | A/B/C analysis | Behavioral presence contrast; exploratory |
| Coverage: 128 A/B on 22/35; 105 C on 35/35; 63 triplets; Claude Code only | Run ledger / reports | Design/execution fact |
| Compile success ~100% on triplets; failures dominated by tests | Uptake / ABC reports | Environmental difficulty description |
| Condition C required for interpreting A vs B (presence confound) | Protocol / redesign plan | Design logic, not LB validation |
| Truth Debt **must not be promoted** on this battery | Null pilot + threats | Conservative non-promotion is supported; positive “no harm” is not |

**Framing constraint for A2:** If the same numbers are used as *confirmatory causal proof* that referential falsity does not affect outcomes, or as proof of the late-binding LB mechanism, the claim leaves class A (see D / B).

### A3. Separability of estimands (vocabulary, not mechanism proof)

| Claim | Support | Why A |
|-------|---------|-------|
| Static panel integrity, runtime consumption, and task outcomes are distinct estimands | Program design + coexistence of panel falsity with high read/use in pilot | Conceptual hygiene supported by measurement architecture; does not require human LB |
| Observational “Truth Decay” (narrow mechanical misalignment) ≠ automatic operational harm | Audits + exploratory null A−B | Separation is justified; **not** a validated causal theory of LB |

---

## B — Depends on exploratory post-hoc analysis only

These claims may appear in exports or discussion as “hints.” They are **not** confirmatory and must not carry explanatory load for the manuscript’s central reframing.

| ID | Claim | Source | Why B | Disposition |
|----|-------|--------|-------|-------------|
| B1 | **46/63 (73.0%) of B runs are non-load-bearing** despite 49/63 false-claim use | `rq5_mediation_summary.md`; Results §5 | Post-hoc mediation; LB/causal-role labels from substring/heuristic trace rules; no human gold | **Remove** from manuscript as explanatory support (treat as D for *explanatory use*; export may remain archived) |
| B2 | Null A−B reflects “**primarily irrelevance / low load-bearingness**, not robustness” | Mediation summary Q5 | Same heuristic LB partition | **Delete** as interpretive conclusion |
| B3 | Causal-role frequencies on B (`false_claim_caused_failure` 19%, `uptake_but_not_load_bearing` 30.2%, etc.) | Mediation export | Post-hoc roles | Do not cite as validated mechanism |
| B4 | Stratified A−B by instruction follow (Δ ≈ −0.014 when followed; ignore *n*=14) | Uptake analysis; Discussion | Post-hoc strata; not in v1 primary protocol | Exploratory only; prefer omit from main prose |
| B5 | Mediation funnel stages (obstacle 27%, corrected 7.9%, task_failed_because_of_false_claim 19%) | Mediation summary | Heuristic obstacle/correction detection | Do not use to underwrite Truth Debt / LB theory |
| B6 | Manifest “load-bearing stratum” assignment 31/35 (4 unknown) without stratified inference | Threats / case manifest | Labeling without powered stratified analysis; not human material-necessity adjudication | Must not be presented as validated LB |

**Rule:** Class B material may remain in the replication package as *exploratory exports* if clearly marked, but manuscript Results/Discussion must not use B1–B2 as the explanation of the null.

---

## C — Depends on failed / infeasible human LB validation

Claims that are only tenable if humans (or an independent oracle) establish material necessity / load-bearing for the RQ5 v1 tasks.

| ID | Claim | Why C | Status |
|----|-------|-------|--------|
| C1 | Anchors in the RQ5 v1 battery are (or are not) **materially necessary** for independently defined SE tasks | Requires independent task oracle + blind LB coding | **Infeasible** on current data (35/35 circular) |
| C2 | Human experts validated load-bearing / non-load-bearing for RQ5 v1 cases | Same | **False / impossible** under current packets; never imply |
| C3 | Blind re-annotation with the v2 human kit will rescue LB construct validity | v2 briefs derive task from treated instruction | **DO NOT DISTRIBUTE**; recreates circularity |
| C4 | Trace-derived “load-bearing” in mediation equals human material-necessity judgments | Would need human validation of the construct | Validation path blocked for v1 |
| C5 | Pre-registered / confirmatory inference on human LB strata for these 35 cases | Requires feasible LB labels | Not available |
| C6 | Model prediction “null A−B **because** anchors are non-load-bearing” as an empirically established moderator on v1 | Needs validated LB moderator | Blocked; prediction may remain as *hypothesis for redesigned cases* only |

**Note:** Stating that blind LB annotation was **attempted and found not feasible** is itself an **A**-class process claim (supported by the feasibility report). Claiming the *scientific content* of LB labels is C/D.

---

## D — No longer supported (delete; do not soften)

| ID | Claim (as currently implied or written) | Why D | Preferred action |
|----|----------------------------------------|-------|------------------|
| D1 | RQ5 is a **confirmatory causal** demonstration that referential falsity does / does not impose Truth Debt | Incomplete factorial, single agent, low power, unvalidated mechanisms; LB path failed | Demote entire causal interpretation; delete confirmatory wording |
| D2 | The **73% non-load-bearing** figure **explains** the null A−B (Results) | Unvalidated post-hoc LB; circular if tied to human material necessity | **Delete sentence**; do not replace with softened “may suggest” |
| D3 | Null result is identified as **irrelevance of false claims** via mediation LB | Same as D2 | Delete |
| D4 | Construct table evidence for “Causal load-bearing reference” = “Null A−B; cited-path selection” | Null A−B does not measure LB; cited-path audit ≠ LB validation | Remove LB row or redefine as *hypothesized moderator with no validated measure in this paper* — prefer remove evidence link |
| D5 | C4/C5 prose treating **non-load-bearing anchors** as established reason for null coexistence | Depends on B1/C1 | Delete LB clause; keep power / test-friction clauses if desired |
| D6 | Any implication that stratified uptake / mediation **validates** the late-binding LB mechanism | Post-hoc + infeasible human LB | Delete mechanism-validation language |
| D7 | “Controlled A/B/C experiment” as completed confirmatory test of Gap G3 / Truth Debt | Pilot only | Replace with exploratory pilot language or delete “controlled experiment” as success claim |
| D8 | Future distribution of v2 annotation kit / “complete human LB coding on these cases” as near-term fix | NOT FEASIBLE + DO NOT DISTRIBUTE | Delete; replace with *redesign cases with independent task oracles* |
| D9 | STORYLINE central idea that success is gated by **load-bearingness** as an established empirical gate in this study | LB unvalidated | Rewrite: hypothesized moderator; not measured validly here |
| D10 | Positive claim that agents are **robust** to false referential content | Explicitly cautioned against in threats; CIs wide; success ~12% | Do not promote; “not supported” ≠ “robust” |

---

## Crosswalk: major manuscript sentences

| Location | Claim gist | Class | Notes |
|----------|------------|-------|-------|
| Abstract: controlled A/B/C experiment | Confirmatory design completed | **D** (as confirmatory) / redesign to **A** exploratory | |
| Abstract: 128/128, 77.8%, edit scope, Δ=0 | Pilot metrics | **A** | Keep with exploratory label |
| Abstract: separate from “causal operational cost” | Implies causal cost estimand identified | **D** / soften only by deleting “causal” identification | Prefer “operational cost (not established)” |
| Intro: “causal contrasts on task success” | Confirmatory | **D** → exploratory | |
| Intro: vocabulary “causal load-bearing references” | Construct as contribution | **C/D** as measured; **A** as named open construct | Prefer name without claiming measurement |
| Model C4–C5 non-LB moderator | Established | **D** (established); **A** if purely hypothetical | |
| `constructs.tex` LB evidence row | Null A−B evidences LB | **D** | |
| Design: “causal track” tests predictions | Confirmatory | **D** → exploratory pilot | |
| Design: LB contrasts “not fully realized” | Implies incomplete-but-possible | **C** mis-frame → state **NOT FEASIBLE** | |
| Results: bridge Truth Decay → Truth Debt | Tested bridge | **D** | |
| Results: 73% explains null | Explanatory mediation | **D** (was **B** as export) | |
| Results: Pred. 1–2 “satisfied” | Confirmatory model test | **D** if confirmatory; Pred. 2 edit-scope as **A** descriptive | |
| Discussion: variance “not attributable” to referential channel | Strong causal attribution of null | Borderline **D**; prefer “pilot does not detect / does not establish” | |
| Discussion: stratified uptake Δ | Post-hoc | **B** | Prefer delete |
| Threats: mediation labels heuristic | Accurate limit | **A** (threat statement) | Add NOT FEASIBLE |
| Threats: 31/35 LB stratum assigned | Label existence | **B**; not human validation | |
| Conclusion: null A−B + late-binding causal load | Mixed | Metrics **A**; “causal load” **D** | |
| STORYLINE LB gate | Established | **D** | |
| Mediation summary 73% / irrelevance | Post-hoc | **B**; explanatory use **D** | |
| Feasibility NOT FEASIBLE | Process fact | **A** | Cite in Design/Threats |

---

## Summary counts (manuscript-facing)

| Class | Role after audit |
|-------|------------------|
| **A** | Keep: observational audits; exploratory uptake / ABC success / edit-scope with explicit pilot limits; estimand separation; Truth Debt non-promotion; feasibility NOT FEASIBLE |
| **B** | Archive only / omit from main narrative: mediation 73%, causal roles, follow strata |
| **C** | Cannot be claimed for v1: human material necessity / LB validation; v2 kit rescue |
| **D** | Delete: confirmatory causal Truth Debt/LB mechanism; 73% as explanation; LB evidenced by null A−B; “controlled experiment” as completed causal proof; agent robustness |

**Editorial principle:** Prefer deleting D/B explanatory claims over rewriting them into hedges that still assert unsupported mechanisms.
