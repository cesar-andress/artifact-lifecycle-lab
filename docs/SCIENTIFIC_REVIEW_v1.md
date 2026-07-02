# Scientific Review v1 — Truth Decay TOSEM Program

**Reviewer stance:** ACM TOSEM Associate Editor (hostile but fair)  
**Date:** 2026-07-02  
**Evidence base:** Frozen protocol v1, RQ1/RQ2/born-stale exports, P1–P5 pilots, RQ5 design (not implemented)  
**Note:** No `rq1_summary.md` exists; this review uses `exports/truth_decay_pilot/rq1_feasibility.md` as the RQ1 summary artifact.

---

## Executive summary

The laboratory has produced **credible feasibility evidence** that machine-consumed instruction files contain mechanically checkable references and that many of those references are **missing at observation time**. That is a publishable *measurement* contribution if framed conservatively.

The program is **not yet** a coherent TOSEM flagship on **“The Half-Life of Truth.”** Current data show:

1. **Born-stale references dominate** the missing signal (17,747 never-VERIFIED verifiable references vs 121 post-verification decay events in RQ2).
2. **RQ2 half-life is not estimable** (KM median not reached; S(365d) ≈ 0.848).
3. **P3 and RQ2 contradict** on survival median and rot incidence framing.
4. **P4 remains unvalidated** — agent-attribution claims (RQ3) are blocked.
5. **RQ5 causal impact is design-only** — “Truth Debt” cannot be promoted.

**Recommendation:** Reframe the scientific program around a **decomposed reference lifecycle** (initial validity → conditional decay → repair/removal/death) before scaling or writing. Do not proceed to RQ3–RQ5 implementation until estimands are reconciled and P4 is closed.

---

## 1. Is the conceptual model complete?

### 1.1 Stated lifecycle

```
INIT
  ↓
Born-Stale  OR  Verified
                  ↓
              Truth Decay
                  ↓
               Repair
                  ↓
               Death
```

### 1.2 Verdict: **Incomplete — structurally promising but under-specified**

The decomposition introduced by the born-stale audit is **scientifically necessary** and should be **first-class in the protocol**, not a post-hoc footnote. Without it, the model collapses distinct phenomena into a single “missing” bucket.

### 1.3 Missing or under-modeled states

| Gap | Evidence | Why it matters |
|-----|----------|----------------|
| **BORN_STALE** (never VERIFIED) | 17,747 / 22,268 verifiable trajectories (~79.7%) never reach VERIFIED; 17,745 start `INIT→MISSING` | Not decay; measures extraction noise, template reuse, wrong verification anchor, or claims false from birth |
| **REMOVED** (reference dropped from text) | `reference_removed` flag exists; not a first-class lifecycle outcome in RQ2 | Competing exit from risk set; conflated with right-censoring |
| **SILENT_REPAIR** | Documented in threats: repo fixes without instruction edit → `VERIFIED` not `REPAIRED` | Decay hazard underestimated; repair hazard misattributed |
| **PERSISTENT_STALE** | 101,565 `MISSING→MISSING` observations in RQ1 | Absorbing state distinct from one-time decay event |
| **UNVERIFIABLE** (commands) | 51.9% of observations; 41,633 never-verified command trajectories | Parallel lifecycle for non-checkable claims; should not enter verifiable decay math |
| **EXTRACTION_AMBIGUOUS** | P1 precision proxy 24.7% at HEAD; born-stale audit: 10.1% prose false positives, 33.9% relative-path candidates | Measurement error state, not repository truth state |
| **FILE_DEATH vs REFERENCE_DEATH** | `DELETED` conflates instruction-file deletion with unobservability | Competing risk for RQ2/RQ4 |

### 1.4 Missing transitions

| Transition | Status | Consequence |
|------------|--------|-------------|
| `INIT→MISSING` (born-stale) | Observed (17,745) | Must not enter decay hazard denominator |
| `VERIFIED→REMOVED` (reference excised while repo still valid) | Partially captured | Misclassified as censoring vs intentional claim withdrawal |
| `MISSING→REMOVED` | Likely present | Persistent stale resolved by deletion, not repair |
| `VERIFIED→VERIFIED` (repo drift without snapshot change) | Invisible between commits | Interval censoring / immortal time |
| `UNVERIFIABLE→*` | Dominates panel | Competing process for command-heavy files |

### 1.5 Hidden assumptions

1. **Repo-root verification anchor:** All paths checked against commit tree root, not instruction-file-relative location → inflates born-stale (33.9% relative-path candidates).
2. **Regex extraction = claim identification:** A token in prose (e.g., `Node.js`) becomes a “reference.”
3. **First L1 snapshot = birth time:** References present before first instruction-file event are left-truncated without modeling.
4. **Reference independence:** 2,093 keys repeat across ≥2 trajectories; top 10 repos = 62.4% of born-stale mass.
5. **“Truth” = tree membership:** Semantic correctness explicitly out of scope but title/claims use “truth.”
6. **Repair requires instruction edit:** Repo-side satisfaction is invisible as repair.
7. **Commit snapshot spacing = time:** Zero-day failures dominate P3 median (~0 days).

### 1.6 Better abstraction (recommended)

Replace the linear lifecycle with a **competing-risks reference process**:

```
                    ┌── Born invalid (INIT→MISSING, never VERIFIED)
                    │
Entry (reference ───┼── Verified at origin ──► Decay (VERIFIED→MISSING)
  extracted)        │                              │
                    │                              ├──► Repair (edit or silent)
                    │                              ├──► Removal (text excised)
                    └── Unverifiable (commands)    └──► File death (DELETED)
```

**Primary estimands (revised):**

- **E1:** P(born valid) = P(first state VERIFIED | verifiable, extracted)
- **E2:** H_decay(t) = hazard of first MISSING | VERIFIED at origin
- **E3:** H_repair(t) | MISSING — competing with removal/death
- **E4:** P(stale at t) — descriptive prevalence, explicitly decomposed into born-stale + decayed

This matches the data better than a single “half-life” headline.

---

## 2. Are the research questions independent?

### 2.1 Current RQ map

| RQ | Focus | Independence |
|----|-------|--------------|
| **RQ1** | Truth lifecycle / evolution | **Overlaps RQ2, RQ4** — descriptive panel of same state machine |
| **RQ2** | Reference survival / half-life | **Conditional slice of RQ1** — not independent |
| **RQ3** | Agent vs human maintenance | **Depends on P4**; confounded with repo maturity |
| **RQ4** | Repair/death dynamics | **Overlaps RQ1 transitions**; repair definition overlaps RQ2 censoring |
| **RQ5** | (a) Machine vs human docs (P5); (b) Causal agent impact (RQ5 experiment) | **Two RQs sharing one number** — numbering collision |

### 2.2 Merge / split / reorder recommendations

| Action | Proposal | Rationale |
|--------|----------|-----------|
| **Merge** | RQ1 + RQ2 → **“Reference lifecycle panel”** with two estimands: prevalence dynamics (RQ1) + conditional survival (RQ2) | Same dataset, same state model, same unit of analysis |
| **Split** | RQ5 → **RQ5a** (descriptive: machine vs human doc density/staleness, P5) and **RQ5b** (causal: agent task impact) | Different estimands, different methods, different claims |
| **Elevate** | Born-stale → **RQ1a** or explicit sub-estimand | 79.7% of verifiable trajectories; dominates missing ratio |
| **Reorder** | **P4 → born-stale reconciliation → RQ2 reframing → RQ4 → RQ3 → RQ5b → scale** | Close measurement gates before causal/agent claims |
| **Defer/weaken** | RQ3 until P4 ≥0.80 **and** repo-cluster covariates specified | Attribution without validated labels is fatal at TOSEM |
| **Remove from title** | “Half-life” as primary claim | Data do not support KM median; S(365)≈0.85 |

### 2.3 Strengthened RQ set (minimal revision)

1. **RQ1:** What is the decomposed prevalence of reference states (born-stale, verified, decayed, repaired, removed) in machine-consumed instruction files over time?
2. **RQ2:** Conditional on first verification, what is the hazard of first mechanical failure and how much repair occurs post-failure?
3. **RQ3:** Do agent-attributed commits predict differential rates of born-stale introduction vs post-verification decay vs repair? (requires P4)
4. **RQ4:** When files accumulate stale references, do maintainers repair, delete references, delete files, or persist?
5. **RQ5a:** Do machine-consumed files differ from README/CONTRIBUTING in verifiable-claim burden and staleness decomposition?
6. **RQ5b:** Does observed rot causally degrade agent task success? (Truth Debt gate)

---

## 3. Construct contamination

Every pair below is a **reviewer confusion risk**:

| Construct A | Construct B | How contamination appears in our data |
|-------------|-------------|----------------------------------------|
| **Born-stale** | **Truth decay** | 36.4% missing ratio (RQ1) mixes both; 74.8% “ever missing” in P3 includes never-verified |
| **Truth** | **Mechanical satisfiability** | “Truth” in title; verification = `git ls-tree` membership |
| **Truth** | **Usefulness / task success** | RQ5 links them; not yet measured |
| **Reference validity** | **Semantic correctness** | Path exists but wrong file; command text uncheckable |
| **Decay** | **Extraction false positive** | `Node.js`, `//cursor.sh` counted as path references |
| **Decay** | **Wrong verification anchor** | Relative paths fail at repo root though “correct” relative to doc |
| **Repair** | **Silent repo fix** | VERIFIED without REPAIRED; 107 REPAIRED vs 17 post-failure repairs in RQ2 |
| **Repair** | **Reference removal** | Stale claim deleted from text ≠ repaired |
| **Agent maintenance** | **Dependabot/Renovate** | P4 explicitly excludes; still noisy in P2 (25.2% signal) |
| **Agent authorship** | **Co-authored human commit** | Co-Authored-By trailer ≠ agent-only maintenance |
| **Staleness rate** | **Missing-at-snapshot prevalence** | HEAD proxy 24.7% vs longitudinal conditioning |
| **Half-life** | **Conditional median among failures** | 16 days (RQ1) vs 34.5 days (RQ2 conditional) vs KM not reached |
| **Rot incidence** | **Event rate per reference-year** | P3: 23.2 events/ref-year vs RQ2: 2.7% ever fail post-verification |
| **Truth Decay** | **Documentation evolution** | Any edit changes references; not necessarily “decay” |
| **Truth Debt** | **Technical debt** | Debt metaphor implies cost; unproven without RQ5b |
| **Machine-consumed docs** | **All markdown conventions** | Family detector may miss or over-include |
| **Censoring** | **End of observation** | 94.3% right-censored in RQ2 — low power, not “stable truth” |
| **File deletion** | **Reference death** | DELETED state bundles file lifecycle |
| **Pilot cohort** | **OSS population** | Engineering frame (pilot + E1-100); Microsoft, Anthropic, Vercel overweight |

---

## 4. Could reviewers reinterpret the contribution differently?

**Yes — and likely will** if the paper leads with “Half-Life of Truth.”

| Reviewer-natural framing | Why it fits our data better than “Truth Decay” |
|--------------------------|-----------------------------------------------|
| **Documentation / ruleset evolution** | Longitudinal panel of instruction-file edits with extracted tokens |
| **Configuration drift detection** | Path references to repo artifacts; similar to IaC drift literature |
| **Knowledge synchronization failure** | Claims about repo structure not updated after refactors |
| **Specification maintenance for AI tools** | AGENTS.md / Cursor rules as machine-readable spec surfaces |
| **Regex-based claim auditing** | 51.9% UNVERIFIABLE; born-stale audit shows extraction artifacts |
| **Template propagation in agent rule packs** | 62.4% born-stale in top 10 repos; repeated keys across files |

**Defense:** Position as **“mechanical reference integrity in machine-consumed documentation”** — a measurable precondition for trustworthy agent context — not as philosophical “truth decay.”

The **novelty** is the longitudinal measurement instrument applied to a **new document class** (agent instruction files), not the survival math itself.

---

## 5. Does the protocol accidentally promise too much?

| Overstrong statement | Where | What data actually support | Safer wording |
|---------------------|-------|---------------------------|---------------|
| **“The Half-Life of Truth”** | Working title | KM median not estimable; S(365d)≈0.848 | “Mechanical reference integrity in machine-consumed documentation” |
| **“Truth decay” as primary phenomenon** | Central claim | Most missing is born-stale, not decay | “Decomposed reference invalidity: born-stale vs post-verification failure” |
| **Median survival / half-life estimand** | RQ2 protocol | Not reached (n=121 failures, 94% censored) | “Conditional failure hazard among verified references; report S(t) at fixed horizons” |
| **P3 PASS: survival median estimable** | `p3_rot_incidence.md` | Median ~0 days; contradicts RQ2 | “Event-rich panel on P1 subsample; median not stable across estimands” |
| **23.2 rot events/reference-year** | P3 | Mixes born-stale and decay; short follow-up per reference | “Crude incidence on P1 sample; decompose by origin state in analysis” |
| **74.8% references ever become missing** | P3 | Includes never-verified | “Share ever missing at least once (includes born-stale)” |
| **RQ1 supports TOSEM paper: YES** | `rq1_feasibility.md` | Feasibility yes; flagship claim no | “RQ1 demonstrates measurable signals warranting scaled study” |
| **Overall GO recommendation** | `go_no_go.md` | GO for feasibility, not for half-life claim | “GO for observational measurement program; NO-GO for half-life headline pending RQ2 reconciliation” |
| **24.7% precision proxy** | P1 | Mislabeled — it is verified/(verified+missing) at HEAD, not extractor precision | “HEAD mechanical satisfaction rate among checkable references” |
| **Agent attribution sufficient** | P2/P4 | P4 **PENDING** human review | “Attribution candidates exist; precision unvalidated” |
| **Truth Debt conditional on RQ5** | Phenomena hierarchy | RQ5 not implemented | Keep as hypothesis; do not mention in abstract |
| **Causal impact of rot** | RQ5 design | Zero runs completed | “Preregistered evaluation plan” |
| **Mechanical verification ≠ semantic** | Threats table | Stated but contradicted by “truth” branding | Remove “truth” from measurable claims entirely |

---

## 6. What would Reviewer #2 attack first?

*Simulated TOSEM review — pages 1–2 of rejection letter.*

---

**TOSEM-2026-XXXX: The Half-Life of Truth in Machine-Consumed Documentation**

**Recommendation: Reject (major conceptual and empirical gaps)**

---

### Summary

This paper proposes measuring “truth decay” in AI-oriented instruction files (AGENTS.md, Cursor rules, etc.) by extracting path-like references and checking them against git trees over time. While the topic is timely, the paper **overclaims**, **confounds distinct failure modes**, and presents **internally inconsistent survival results**. The headline half-life claim is **not supported** by the authors’ own RQ2 analysis.

### Major concerns

**M1 — The central estimand collapses under scrutiny.**

The abstract/framing promises half-life and truth decay. The full-cohort RQ2 analysis (`rq2_summary.md`) reports:

- KM **median not reached** (survival > 0.5 throughout follow-up)
- Only **121 post-verification failure events** among **4,521** verified references (2.7%)
- **S(365 days) ≈ 0.848**

Yet the gate pilot P3 (`p3_rot_incidence.md`) claims **PASS** with **23.2 events/reference-year** and **74.8%** of references ever missing, median ~**0 days**. The paper cannot report both “rapid rot” and “85% one-year survival” without reconciling estimands. As written, this reads as **p-hacking via metric selection** — or worse, a **fundamental construct error**.

**M2 — “Born-stale” dominates but arrives too late.**

The born-stale audit (post-review addition) shows **17,747** verifiable references **never** reach VERIFIED (~80% of verifiable trajectories). These are **`INIT→MISSING` from first observation**, not decay. The RQ1 headline **36.4% missing ratio** and **18,473 first-failure events** commingle born-stale with genuine `VERIFIED→MISSING` transitions. Without born-stale decomposition **in the main paper**, the prevalence results are **uninterpretable** as lifecycle decay.

**M3 — Measurement instrument unvalidated.**

Reference extraction is regex-based (`references.py`). The born-stale audit documents:

- **10.1%** prose false positives (e.g., product tokens parsed as paths)
- **33.9%** relative-path resolution candidates under repo-root verification
- P1 “precision proxy” of **24.7%** is not extractor precision — it is the fraction of checkable references that resolve at HEAD

There is **no gold-standard labeled sample** of extraction correctness. TOSEM will not accept decay rates built on an unvalidated auditor.

**M4 — Agent attribution (RQ3) is premature.**

P4 status: **PENDING HUMAN REVIEW**. The protocol requires ≥0.80 precision before agent-maintenance claims. Submitting RQ3 without closed P4 violates the authors’ own gate logic and invites **false attribution** (Co-Authored-By trailers, bot noise, missed signatures).

**M5 — Cohort invalid for population inference.**

Analysis uses pilot + E1-100 engineering repos. Born-stale mass concentrates: **top 10 repos = 62.4%** of exclusions, including large agent-ecosystem repos (Anthropic, Microsoft, Vercel). Results describe **a biased convenience sample of AI-heavy projects**, not “machine-consumed documentation” generally. No scientific stratum design (E1-1000 deferred) is offered.

**M6 — “Truth” is marketing, not measurement.**

States are `VERIFIED/MISSING/UNVERIFIABLE` against tree membership. **51.9%** of observations are UNVERIFIABLE commands. The paper explicitly excludes semantic correctness yet retains “truth” in the title. Reviewers will classify this as **construct invalidity** — the object of study is **mechanical reference satisfaction**, not truth.

### Minor concerns (truncated)

- Repair state barely used (107 REPAIRED observations; 0.03% ratio)
- Independence assumption across references within repo unjustified
- RQ5 causal design unexecuted — Truth Debt discussion is speculative

---

## 7. What would convince that reviewer?

| Criticism | Smallest additional experiment / analysis | Uses existing data? |
|-----------|------------------------------------------|---------------------|
| **M1 — Inconsistent survival** | Single reconciled incidence table: P3 metrics recomputed on **post-verification decay only**, same cohort definitions as RQ2; one row per estimand | **Yes** — `reference_longitudinal.csv`, `p3_rot_events.csv` |
| **M2 — Born-stale contamination** | Main-text decomposition: report prevalence of INIT→MISSING vs VERIFIED→MISSING; all RQ1 ratios **conditional on origin state** | **Yes** — born-stale audit + longitudinal |
| **M3 — Unvalidated extractor** | Manual labeling of **n≈100** references stratified from `reference_examples.csv` + born-stale examples: {correct extraction, false positive, wrong anchor} | **Partial** — sample from existing CSVs; ~4–8 hours human labeling |
| **M4 — P4 pending** | Complete **200-row** P4 worksheet; report precision/recall on agent-maintenance subset | **Yes** — worksheet exported |
| **M5 — Cohort bias** | Repo-cluster robust SEs; leave-one-repo-out sensitivity for top-10; report weighted vs unweighted | **Yes** — `born_stale_by_repo.csv`, RQ2 records |
| **M6 — “Truth” branding** | Rename claims throughout; one paragraph defining **Mechanical Reference Satisfaction (MRS)** | **Yes** — writing only |
| **Silent repair** | Count `MISSING→VERIFIED` without REPAIRED label; report as **repo-side reconciliation** | **Yes** — transition counts in RQ1 |
| **RQ5 causal gap** | Pilot **n=5 cases × 2 conditions × 2 agents × 3 replicates = 60 runs** (lower bound) before scaling design | **No** — requires agent runs (minimal) |
| **Half-life not estimable** | Report **S(30/90/180/365)** with cluster bootstrap; drop “median half-life” from abstract | **Yes** — RQ2 already has S(t) |
| **P3 zero-day median** | Sensitivity analysis excluding same-day failures; report calendar-time vs commit-index time | **Yes** — longitudinal timestamps |

**Priority order (analysis-only, before any scale):**

1. Reconcile P3/RQ2 estimands on one page  
2. Born-stale decomposition in all prevalence metrics  
3. Close P4 human review  
4. 100-reference extraction gold sample  

---

## 8. Is the current roadmap optimal?

### 8.1 Current sequence

```
P1 → P2 → P3 → P4 → P5 → RQ1 → RQ2 → born-stale audit → RQ3 → RQ4 → RQ5 → scale
```

### 8.2 Problems

| Issue | Detail |
|-------|--------|
| **P3 passed on wrong estimand** | Gate checked rot incidence before born-stale decomposition existed |
| **RQ2 implemented before estimand reconciliation** | Produced null half-life — should trigger gate review, not proceed |
| **P4 not closed before RQ1/RQ2** | Attribution join can proceed in parallel, but RQ3 must not |
| **Born-stale audit post-hoc** | Should be **Gate P6** before any survival claim |
| **RQ5 dual numbering** | Comparative (P5) and causal (impact) both “RQ5” |
| **Scale blocked but narrative isn’t** | Protocol says E1-1000 frozen; paper framing still sounds population-level |

### 8.3 Recommended roadmap

```
P1 ─ P2 ─ P5
         │
         ▼
    P4 (human close) ────────────────────────┐
         │                                    │
         ▼                                    │
  P6: Born-stale / estimand reconciliation   │  (NEW GATE — analysis only)
         │                                    │
         ├── RQ1 panel (decomposed prevalence)│
         ├── RQ2 conditional hazard (reframed)│
         └── RQ4 repair/removal/death         │
                 │                            │
                 ▼                            │
         RQ3 (attribution joins) ◄───────────┘
                 │
                 ▼
         RQ5a (machine vs human docs — descriptive)
                 │
                 ▼
         RQ5b pilot (causal impact — minimal runs)
                 │
                 ▼
         Gate: cost shown? → promote Truth Debt
                 │
                 ▼
         Large-scale execution (E1-1000 or targeted expansion)
```

### 8.4 Gates to add / remove

| Gate | Action |
|------|--------|
| **P6 — Construct reconciliation** | **Add:** born-stale share <80% of missing **or** explicitly framed as dual-estimand paper |
| **P3 PASS on median** | **Revise:** require alignment with full-cohort RQ2 S(t), not P1 subsample alone |
| **P4** | **Keep — block RQ3** until closed |
| **P5** | **Keep** — supports RQ5a only |
| **RQ5b before scale** | **Keep** — Truth Debt kill criterion |
| **E1-1000** | **Keep frozen** until P6 + P4 + RQ2 reframing published internally |

### 8.5 What to remove or defer

- **“Half-life” in title** until estimable or permanently dropped  
- **RQ3 implementation** until P4 ≥ 0.80  
- **Truth Debt language** in any abstract until RQ5b pilot completes  
- **Separate RQ2 as flagship** — merge into lifecycle section  

---

## 9. Weakest scientific component (choose one)

### **Weakest: The primary estimand — “reference half-life / truth decay rate”**

**Why this one (not extraction, not attribution, not scale):**

- Extraction weakness is serious but **born-stale audit already quantifies** its impact; mitigable with labeling and reframing.
- P4 attribution is **unvalidated but gated** — protocol acknowledges the risk.
- Scale/cohort bias is **disclosed** in threats.

The **fatal flaw** is that the program’s **namesake claim** (half-life of truth) is **empirically empty** after proper conditioning:

| Metric | Value | Implication |
|--------|-------|-------------|
| KM median | Not reached | No half-life |
| Post-verification failures | 121 / 4,521 (2.7%) | Rare event → low power |
| S(365d) | 0.848 | References **persist** mechanically |
| Born-stale share | ~80% of verifiable trajectories | “Decay” narrative describes **wrong construct** |
| P3 vs RQ2 | Contradictory medians/incidence | Estimands not stable |

A TOSEM AE will not accept a paper whose **title names an estimand the results nullify**, while **alternative estimands** (born-stale prevalence, decomposed invalidity) are stronger in the same dataset.

### How to fix (analysis-only, no new infrastructure)

1. **Retire half-life as primary claim**; lead with decomposed lifecycle (E1–E4 from §1.6).
2. **Recompute all incidence metrics** on three disjoint sets: born-stale, post-verification decay, persistent stale.
3. **Publish one reconciliation table** explaining P3 vs RQ2 (sample, origin state, time metric).
4. **Pre-register** RQ2 as conditional hazard with **S(t)** reporting, not median.
5. **Optional:** 100-reference gold label for extraction — strengthens but does not replace estimand fix.

**Estimated work:** 2–4 researcher-days analysis + 1 day P4 labeling + 1 day writing realignment. **No pipeline changes.**

---

## 10. Is this now a TOSEM program?

Scores reflect **today’s evidence**, not hypothetical completion. Scale: 0–10.

| Criterion | Score | Justification |
|-----------|------:|---------------|
| **Novelty** | **6** | New document class + longitudinal mechanical auditing is timely; survival framing and regex extraction are not novel |
| **Scientific rigor** | **4** | Gates exist but P3/RQ2 contradict; P4 open; gold labels absent |
| **Construct validity** | **3** | “Truth” vs mechanical satisfaction; born-stale/decay conflation in headline metrics |
| **Internal validity** | **5** | Commit-time verification is sound; extraction anchor and zero-day effects threaten causal interpretation even observationally |
| **External validity** | **3** | Pilot + E1-100 convenience sample; 62% born-stale in top-10 repos |
| **Feasibility** | **7** | Laboratory frozen; longitudinal panel exists; further RQs are analyzable without re-extraction |
| **Long-term impact** | **6** | If reframed, could influence agent-doc tooling standards; if “half-life” pursued, likely ignored |
| **Acceptance probability (flagship TOSEM, current framing)** | **15%** | Feasibility note: maybe; half-life truth paper: reject |
| **Acceptance probability (reframed observational measurement paper)** | **35–45%** | Conditional on P4 close, estimand reconciliation, extraction gold sample, conservative claims |

### Bottom line

| Question | Answer |
|----------|--------|
| Is this a research program? | **Yes** |
| Is this a TOSEM program **today**? | **Not yet — it is a strong feasibility study with a misaligned flagship claim** |
| Path to TOSEM | Reframe → reconcile → validate attribution → optional causal pilot → then scale |

---

## Appendix: Key numeric facts (frozen exports)

| Fact | Source |
|------|--------|
| 339,646 longitudinal observations | `rq1_feasibility.md` |
| 36.4% MISSING / 11.1% VERIFIED / 51.9% UNVERIFIABLE | `rq1_exploratory_stats.csv` |
| 18,335 `INIT→MISSING` vs decay transitions | `rq1_feasibility.md` |
| 4,521 RQ2 cohort; 121 failures; KM median NR; S(365)≈0.848 | `rq2_summary.md` |
| 17,747 born-stale (verifiable, never VERIFIED) | `born_stale_audit.md` |
| P3: 23.2 events/ref-year; 74.8% ever missing; median ~0d | `p3_rot_incidence.md` |
| P4: PENDING human review | `p4_attribution_precision.md` |
| P5: PASS — 91.4% human docs have verifiable refs | `p5_human_doc_baseline.md` |
| Top 10 repos: 62.4% born-stale | `born_stale_audit.md` |

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| v1 | 2026-07-02 | Initial hostile AE review pre-RQ3 implementation |
