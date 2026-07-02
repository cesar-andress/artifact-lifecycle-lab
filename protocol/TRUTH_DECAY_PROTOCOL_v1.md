# Truth Decay Protocol v1

**Status:** Frozen — RQ1 feasibility + pre-scaling gates (P3–P5) implemented; scaling blocked until gates pass  
**Protocol version:** `TRUTH_DECAY_PROTOCOL_v1`  
**Working title:** *The Half-Life of Truth in Machine-Consumed Documentation*  
**Companion pilot exports:** `exports/truth_pilot/`  
**RQ1 feasibility exports:** `exports/truth_decay_pilot/`  
**Pilot implementation:** `artifact_lab/experiments/truth_pilots/`  
**RQ1 implementation:** `artifact_lab/experiments/truth_decay/`

---

## Central claim

Machine-consumed documentation (AGENTS.md, Cursor rules, Copilot instructions, skills, prompts) encodes **mechanically verifiable claims** about repository structure—file paths, directories, scripts, dependencies, commands—that **decay over time** as the codebase evolves. When instruction files are maintained by AI agents rather than humans, decay and repair dynamics may differ systematically. This protocol defines how to measure **truth decay**, **reference half-life**, and **self-maintenance attribution** using the existing artifact lifecycle laboratory (L0–L2) without scaling E1-1000 until longitudinal design is validated.

---

## Research questions

### RQ1 — Truth decay

Do machine-consumed instruction files contain verifiable references, and what fraction of those references are **stale** (missing or incorrect) at a given repository snapshot?

**Primary estimand:** Proportion of verifiable references in state `missing` at time *t*, conditional on instruction-file family and repository frame.

**Unit of analysis:** Individual extracted reference within an instruction file at snapshot *t*.

---

### RQ2 — Reference half-life

How long do verified references remain true before transitioning to `missing`, `repaired`, or `deleted`?

**Primary estimand:** Median survival time (half-life) from first observation in state `verified` to first transition to `missing`, censored at file deletion or end of observation window.

**Unit of analysis:** Reference trajectory keyed by `(repo_id, instruction_path, reference_type, reference_text)`.

---

### RQ3 — Agent vs human self-maintenance

Are changes to instruction files disproportionately **agent-authored** or **agent-co-authored**, and does attribution class predict reference staleness or repair rate?

**Primary estimand:** Difference in reference staleness rate and repair probability between commits classified as agent-attributed vs human-only, conditional on instruction-file family.

**Unit of analysis:** Commit or commit-window touching an instruction file, joined to reference-state panel.

---

### RQ4 — Repair / death dynamics

When references go stale, do maintainers **repair** instruction text, **delete** instruction files, or leave them in a persistently false state?

**Primary estimand:**

1. Hazard of transition from `missing` → `repaired` vs `missing` → persistent stale vs instruction-file deletion.
2. Time-to-deletion for instruction files with high stale-reference burden.

**Unit of analysis:** Instruction file lifecycle and reference-state transitions over the observation window.

---

### RQ5 — Machine-consumed vs human-facing documentation (comparative)

Do machine-consumed instruction files differ from human-facing documentation (README.md, CONTRIBUTING.md) in **reference density**, **verifiable-claim burden**, and **staleness rate**?

**Primary estimand:** Difference in verifiable-reference density and missing-reference ratio between instruction files and human-facing docs within the same repository.

**Unit of analysis:** Matched repository, comparing instruction-file snapshots vs README/CONTRIBUTING at the same commit window.

**Gate:** P5 human-doc baseline must pass before comparative analysis is scaled.

---

## Pre-scaling validation gates (mandatory)

**Do not run E1-1000 or scale cohorts until P3, P4, and P5 pass.** Command: `make pre-scaling-gates`

| Gate | Purpose | Outputs | Pass condition |
|------|---------|---------|----------------|
| **P3 — Rot incidence** | Confirm decay rate supports half-life study | `p3_rot_incidence.md`, `p3_rot_events.csv` | Rot ≥2–3%/reference-year; KM median estimable |
| **P4 — Attribution precision** | Audit agent-signal accuracy before RQ3 | `agent_attribution_gold_worksheet.csv`, `agent_attribution_precision.md` | Human-review precision ≥0.80 on agent-maintenance subset |
| **P5 — Human doc baseline** | Feasibility of comparative RQ5 | `human_doc_baseline.md`, `human_doc_reference_examples.csv` | Sufficient human docs with verifiable references |

### P3 — Rot incidence (mandatory go/no-go)

Uses P1 sample (400 instruction files) with longitudinal reference states. Reports verifiable references, rot events, incidence per year, censoring rate, and Kaplan-Meier median estimability (gate check only — not full RQ2 survival module).

### P4 — Attribution precision (mandatory gate)

Samples ~200 flagged commits into a human-review worksheet. Auto-summary **separates**:

- Claude / Cursor / Copilot message signatures
- Co-Authored-By trailers
- Generic bot authors
- **Dependabot / Renovate / security bots (excluded from agent maintenance)**

Dependabot and Renovate must **not** count as agent maintenance unless explicitly justified in review notes.

### P5 — Human documentation baseline (mandatory gate)

For P1 repositories, samples README.md and CONTRIBUTING.md where available; runs identical reference extraction. Determines whether machine-vs-human comparative RQ is technically viable.

---

## Kill criteria (pre-scaling)

The program **stops scaling** (including E1-1000) if any mandatory gate fails:

| Criterion | Threshold | Gate |
|-----------|-----------|------|
| Rot incidence | **<2–3%** references per year | P3 |
| Attribution precision | **<0.80** on agent-maintenance commits (human-reviewed) | P4 |
| Survival median | **Not estimable** due to excessive right-censoring | P3 |

---

## Go/no-go pilot evidence

Pilot executed on existing L1/L1b (pilot + E1-100 cohorts). **Recommendation: GO.** Full report: `exports/truth_pilot/go_no_go.md`.

| Signal | Pilot result | Implication |
|--------|-------------|-------------|
| Reference density | **72%** of sampled instruction files (400/400 stratified sample) contain ≥1 mechanically verifiable reference | RQ1/RQ2 feasible — sufficient claim density |
| Median verifiable refs/file | **3.0** | Supports per-file and per-reference survival analysis |
| Agent commit signal | **25.2%** of commits touching instruction files carry agent attribution | RQ3 feasible — attribution not rare |
| Agent file signal | **30.4%** of instruction files (989/3253) have ≥1 agent-attributed commit | RQ3/RQ4 join coverage adequate for stratified analysis |
| Precision proxy (verified / verified+missing) | **24.7%** at HEAD in pilot | Staleness signal exists; decay study has material failure rate |

Pilot commands: `make truth-pilots` (see `docs/truth_decay_pilots.md`).

**Explicitly deferred from E1 census framing:**

- Ecosystem-scale adoption prevalence as primary TOSEM claim
- LLM-judged semantic correctness (L5)
- E1-1000 execution until longitudinal protocol is implemented and reviewed

---

## Required datasets

| Layer | Path | Role |
|-------|------|------|
| L0 | `data/registry/pilot_repos.csv`, `data/registry/e1_100_repos.csv` | Repository frame and URLs |
| L1 | `data/l1/file_event_log/v1/events.parquet`, `data/l1/e1_100/v1/events.parquet` | File events, commit SHAs, paths |
| L1b | `data/blobs/{prefix}/{sha}.txt` | Instruction file text at each blob_sha |
| L2 | `data/derived/file_state_panel/v1/` (extend for truth panel) | Monthly file presence / change flags |
| Truth pilot | `exports/truth_pilot/reference_summary.csv` | Per-file reference density baseline |
| Truth pilot | `exports/truth_pilot/agent_commit_candidates.csv` | Commit-level attribution candidates |
| Ephemeral | `scratch/` bare clones | HEAD verification and commit message fetch only |

**Protocol family (frozen for v1):** `ai_conventions_v1` (`artifact_lab/protocol/families/ai_conventions_v1.yaml`)

**Instruction-file families in scope:**

- AGENTS.md / `.agents/`
- CLAUDE.md
- Cursor rules (`.cursor/rules/`, `.cursorrules`)
- Copilot instructions (`.github/copilot-instructions.md`)
- GitHub instructions (`.github/instructions/`)
- Skills (`SKILL.md`)
- Prompt files (`prompts/`)

---

## Join key

All truth-decay and attribution analyses join on:

```
(repo_id, instruction_path, commit_sha | commit_time)
```

Extended reference trajectories add:

```
(repo_id, instruction_path, reference_type, reference_text, observation_time)
```

**Join graph:**

```
L1 events ──► L1b blob text ──► reference extraction
     │
     ├──► ephemeral clone @ commit ──► reference verification state
     │
     └──► commit metadata ──► attribution state
              │
              └──► merged truth panel (reference × attribution × time)
```

---

## Reference state model

Each mechanically extracted reference is assigned one state per observation snapshot:

| State | Definition |
|-------|------------|
| `verified` | Reference resolves against repository tree or dependency manifest at the observation commit |
| `missing` | Reference is mechanically checkable but not satisfied at the observation commit (path, directory, script, or dependency absent) |
| `unverifiable` | Reference cannot be resolved mechanically in v1 (e.g. generic shell command, make target without script mapping) |
| `repaired` | Reference was `missing` at *t−1* and is `verified` at *t*, with intervening instruction-file edit |
| `deleted` | Instruction file or referenced artifact removed; reference no longer observable |

**Transitions of interest for RQ2/RQ4:**

```
verified ──► missing          (decay)
missing  ──► verified         (repair, via instruction or repo change)
missing  ──► missing          (persistent stale)
*        ──► deleted          (file or repo artifact death)
```

**Verifiable reference types (v1):** `path`, `directory`, `script_name`, `dependency`  
**Extracted but typically unverifiable:** `command`

---

## Attribution state model

Each commit touching an instruction file receives one attribution class via deterministic heuristics (no LLM):

| State | Definition |
|-------|------------|
| `human-only` | No Co-Authored-By agent trailer, no bot author, no tool signature in message |
| `agent-authored` | Bot author account, or commit message contains tool/agent signature (Claude, Cursor, Copilot, etc.) without Co-Authored-By |
| `agent-coauthored` | `Co-Authored-By` trailer matching agent/bot patterns |
| `bot` | Author name/email matches known automation accounts (dependabot, github-actions, renovate, etc.) |

**Signature sources (v1):**

- `Co-Authored-By` trailers
- Bot account patterns (`[bot]`, dependabot, renovate, cursoragent)
- Message signatures (claude, anthropic, cursor, copilot, openai, aider, devin, codeium)
- Tool phrases (`Generated by`, `Written by`, `Created with`, `Assisted by`)

Pilot mapping: `agent-authored` ← `agent_signature_in_message`; `agent-coauthored` ← `agent_coauthored`; `bot` ← `bot_author`; `human-only` ← `human`.

---

## Threats to validity

| Threat | Description | Mitigation (protocol v1) |
|--------|-------------|--------------------------|
| **Construct validity** | Mechanical verification ≠ semantic truth; instructions may be correct but unverifiable | Report `unverifiable` rate separately; do not claim semantic correctness |
| **Selection bias** | Pilot cohort is engineering frame (pilot + E1-100), not E1-1000 scientific strata | Frame-conditional inference; defer population claims until longitudinal panel design |
| **Attribution false positives/negatives** | Developers omit Co-Authored-By; bots misclassified as human | Deterministic rules only; report signature-type breakdown; sensitivity with stricter patterns |
| **HEAD-only verification** | Pilot verifies at clone HEAD, not necessarily at L1 commit_sha | RQ1 feasibility verifies at L1 `commit_sha` (see `exports/truth_decay_pilot/`) |
| **Reference extraction recall** | Regex extraction misses non-standard path formats | Pilot density audit; versioned extractor; manual spot-check sample |
| **Survivorship** | Deleted instruction files drop out of L1 | Explicit `deleted` state; use full commit history before deletion |
| **Confounding** | Agent-adoption repos may differ in engineering maturity | Include repo covariates (stars, activity, family) from registry |
| **Multiple comparisons** | Many reference types and families tested | Pre-register primary estimands per RQ; family-level FDR in analysis plan |

---

## Scope boundaries (v1)

| In scope | Out of scope |
|----------|--------------|
| Mechanical reference extraction and verification | LLM-based truth scoring (L5) |
| Deterministic agent attribution from git metadata | Author intent survey or interview |
| Longitudinal panel on existing cohorts | E1-1000 scaling |
| Instruction-file lifecycle (repair/death) | General markdown / README analysis |
| Join with L1/L1b/L2 spine | Paper writing |

**Do not run:** `make e1-1000` until pre-scaling gates P3–P5 pass and P4 human review confirms precision ≥0.80.

---

## Next implementation steps

**Completed (RQ1 feasibility milestone):**

1. Commit-time verification at L1 `commit_sha` — `artifact_lab/experiments/truth_decay/verify_at_commit.py`
2. Reference trajectory table — `exports/truth_decay_pilot/reference_longitudinal.csv`
3. Reference state model documentation — `docs/reference_state_model.md`
4. Exploratory RQ1 statistics and figures — `exports/truth_decay_pilot/rq1_feasibility.md`

**Completed (pre-scaling gates):**

5. P3 rot incidence pilot — `exports/truth_pilot/p3_rot_incidence.md`
6. P4 attribution precision worksheet — `exports/truth_pilot/agent_attribution_gold_worksheet.csv`
7. P5 human doc baseline — `exports/truth_pilot/human_doc_baseline.md`

**Remaining (post-gate, later milestones):**

1. **Human review P4 worksheet** — compute attribution precision; confirm ≥0.80 or kill.
2. **Attribution join** — Merge `agent_commit_candidates` onto L1 events (RQ3).
3. **L2 extension** — Stale-reference counts per month on instruction files.
4. **Survival analysis module** — RQ2 half-life estimators (post-P3 gate pass).
5. **Repair/death module** — RQ4 transition accounting.
6. **Comparative RQ5 analysis** — Machine vs human doc staleness (requires P5 pass).
7. **Analysis-ready export** — `exports/truth_decay/` for external review.
8. **Protocol v1.1 trigger** — if detector, attribution rules, or cohort frame changes.

---

## Pilot outputs (frozen evidence)

| File | Content |
|------|---------|
| `exports/truth_pilot/reference_density.md` | P1 density report |
| `exports/truth_pilot/reference_summary.csv` | Per-file reference counts |
| `exports/truth_pilot/reference_examples.csv` | True/false/ambiguous examples |
| `exports/truth_pilot/agent_attribution.md` | P2 attribution report |
| `exports/truth_pilot/agent_commit_candidates.csv` | Commit-level candidates |
| `exports/truth_pilot/agent_attribution_summary.csv` | Summary metrics |
| `exports/truth_pilot/go_no_go.md` | GO recommendation and RQ mapping |

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| v1 | 2026-07-02 | Initial protocol post go/no-go pilot (400-file P1, full L1 P2 on pilot + E1-100) |
| v1.0-rq1 | 2026-07-02 | RQ1 longitudinal feasibility study implemented (`exports/truth_decay_pilot/`) |
| v1.0-gates | 2026-07-02 | Pre-scaling gates P3–P5 implemented (`make pre-scaling-gates`) |
