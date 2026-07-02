# E1-1000 Scientific Cohort Protocol v1

**Status:** Frozen — pre-execution  
**Protocol version:** `E1_1000_protocol_v1`  
**Registry version:** `e1_1000_v1`  
**Companion manifest:** `protocol/experiment_manifest.yaml`

---

## Objective

Estimate the current adoption and distribution of AI-related repository artifacts using a deterministic stratified cohort of 1,000 public GitHub repositories.

This protocol defines **what will be measured**, **how**, and **under what scope limitations** — before any E1-1000 extraction is executed.

---

## Research Question

**RQ1:** How are AI-related repository artifacts currently adopted across the scientific E1-1000 cohort?

Primary estimands:

1. **Enriched-frame prevalence** — proportion of repositories with ≥1 matched convention path at HEAD, within the AI-instruction discovery stratum (and optionally mixed/control).
2. **General-OSS contrast** — same prevalence metric within the general-OSS stratum, enabling comparison against a repository-search frame without instruction-path discovery predicates.
3. **Artifact-family distribution** — frequency of matched paths and repositories by detector family (`table1`).

Secondary (descriptive, same protocol run): temporal accumulation of first appearances (`fig1`), stratum heterogeneity (RQ3 precursor), extraction feasibility (RQ5).

---

## Scope

| In scope | Out of scope |
|----------|--------------|
| Current artifact **presence** at HEAD | Lifecycle state transitions |
| Head-only path inspection | Survival / hazard models |
| Adoption census (E1) | Semantic drift |
| Repository-level aggregation | Ownership analysis (CODEOWNERS) |
| Deterministic stratified sample | Forecasting |
| Protocol family `ai_conventions_v1` | Full-history inspection (default) |

**Inspection mode:** `head-only`  
Matched paths are those visible in the HEAD tree at extraction time. Deleted or historical-only artifacts are not counted as currently present.

---

## Cohort

**Registry (frozen):** `data/registry/e1_1000_repos.csv`  
**Deterministic seed:** `42` (stratum-derived seeds: 42, 43, 44)  
**Target size:** 1,000 repositories  
**Registry hash (SHA-256):** see `protocol/experiment_manifest.yaml`

### Sampling strata

| Stratum | `cohort_stratum` | n | Description |
|---------|------------------|---|-------------|
| **AI discovery frame** | `ai_instruction_discovery` | 334 | Repositories entering the cohort via GitHub **code search** on instruction-artifact path predicates (VSDLC eligible pool). These repos are discoverable because convention-like paths were indexed. Supports **enriched-frame prevalence**. |
| **General OSS** | `general_oss` | 333 | Repositories entering via GitHub **repository search** on stars, language, and activity only. No instruction-path predicates. No AI-topic predicates. Supports **contrast against visible general OSS**. |
| **Mixed / control** | `mixed_control` | 333 | Repositories entering via GitHub **repository search** on AI-related **topic metadata** (e.g. `topic:llm`, `topic:ai-agent`). No guarantee of instruction-artifact paths at selection time. Supports **sensitivity / metadata-adjacent frame**. |

Full sampling procedure: `exports/e1_1000/cohort_design.md`

---

## Inclusion criteria

All strata:

- Public GitHub repository with valid `https://github.com/{owner}/{name}` URL
- Listed in the frozen registry CSV (`e1_1000_repos.csv`)
- Unique `repo_id` and `repo_url` within the registry
- Registry row sorted deterministically by `repo_url`

Stratum-specific pool eligibility (applied before sampling into registry):

- **Instruction frame:** Passes VSDLC Phase-2 eligibility on instruction-artifact discovery candidates
- **General OSS:** Returned by documented repository-search queries (`build_general_oss_pool.py`); `stars ≥ 100` in query predicates; `pushed_at ≥ 2024-06-01`
- **Mixed/control:** Present in VSDLC second-frame candidate pool; `stars ≥ 10`; `pushed_at ≥ 2024-06-01`; not overlapping prior strata URLs

Shared activity/quality floors where applicable:

- `pushed_at >= 2024-06-01`
- Not a fork, archived repo, GitHub template, or mirror

---

## Exclusion criteria

- Forks, archived repositories, templates, mirrors
- Duplicate `repo_id` or `repo_url` (within or across strata)
- Name patterns: `template`, `boilerplate`, `cookiecutter`, `starter-kit`, `awesome-*`, obvious mirror names
- Cross-stratum URL duplicates (deduplicated deterministically at registry build)
- Repositories outside the frozen 1,000-row registry

---

## Detector protocol

| Field | Value |
|-------|-------|
| Protocol family | `ai_conventions_v1` |
| Protocol / detector version | `1.0.0` |
| Pattern definition file | `artifact_lab/protocol/families/ai_conventions_v1.yaml` |
| Pattern version | `1.0.0` (embedded in family YAML `version` field) |
| Artifact families detected | `agents_md`, `claude_md`, `cursorrules`, `cursor_rules`, `copilot_instructions`, `github_instructions`, `windsurf_rules`, `agents_dir`, `skill_md`, `prompts` |
| Exclusion rules | Defined in `ai_conventions_v1.yaml` (`exclusion_patterns`) |

Detector behavior is **frozen** for this protocol version. Changes require a new protocol version and new extraction wave.

---

## Pipeline

```
L0  Registry          data/registry/e1_1000_repos.csv
         ↓
L1  Extraction        make e1-1000-extract  →  data/l1/e1_1000/v1/events.parquet
         ↓              wave: e1_1000_v1, inspection: head-only
L2  Panel             make e1-1000-derive   →  data/derived/file_state_panel/e1_1000/v1/panel_T180.parquet
         ↓              T = 180 days
E1  Adoption census    make e1-1000-exports  →  data/derived/adoption_census/e1_1000/v1/
         ↓
Exports               exports/e1_1000/
```

**Execution command (do not run until checklist complete):**

```bash
make e1-1000
```

Isolated sub-targets: `e1-1000-extract`, `e1-1000-derive`, `e1-1000-exports`, `e1-1000-performance`, `e1-1000-summary`, `e1-1000-qa`

---

## Outputs

### Durable datasets (artifact repository)

| Layer | Path |
|-------|------|
| L0 | `data/registry/e1_1000_repos.csv` |
| L1 events | `data/l1/e1_1000/v1/events.parquet` |
| L1 manifest | `data/l1/e1_1000/v1/manifest.yaml` |
| L2 panel | `data/derived/file_state_panel/e1_1000/v1/panel_T180.parquet` |
| L2 manifest | `data/derived/file_state_panel/e1_1000/v1/manifest_T180.yaml` |
| Census path | `data/derived/adoption_census/e1_1000/v1/path_census.parquet` |
| Census repo | `data/derived/adoption_census/e1_1000/v1/repo_census.parquet` |
| Census repo×family | `data/derived/adoption_census/e1_1000/v1/repo_family_census.parquet` |
| Profiling | `data/profiling/extraction_profile.parquet` (wave `e1_1000_v1` rows) |
| Blobs | `data/blobs/` (content-addressed, shared store) |
| Receipts | `data/receipts/` (per-repo audit trail) |

### Publication exports (`exports/e1_1000/`)

| Output | Path |
|--------|------|
| Cohort design | `exports/e1_1000/cohort_design.md` |
| E1 report | `exports/e1_1000/e1_census.md` |
| Figure 1 PDF | `exports/e1_1000/fig1.pdf` |
| Figure 1 data | `exports/e1_1000/fig1.csv` |
| Table 1 | `exports/e1_1000/table1.csv` |
| Performance report | `exports/e1_1000/pilot_performance.md` |
| Cohort summary | `exports/e1_1000/cohort_summary.md` |

### Optional paper export (one-way, sibling repo)

`../paper/figures/fig1.pdf`, `../paper/tables/table1.csv` — via `make paper` (not part of E1-1000 execution).

---

## Expected outputs

After successful execution:

- **fig1** — cumulative monthly first-appearance timeline of matched convention paths
- **table1** — artifact-family frequencies (`n_repos`, `n_files`, `share_repos_pct`) over registry-scoped repos
- **cohort_summary.md** — latest-per-repo accounting; stratum counts; extraction outcomes partition to 1,000
- **pilot_performance.md** — phase timings, failure modes, slowest repositories
- **e1_census.md** — scope summary with cohort interpretation note

---

## Threats to validity

| Threat | Mitigation / acknowledgment |
|--------|----------------------------|
| **Current presence only** | Head-only inspection; prevalence is a lower bound on ever-adopted; document explicitly |
| **Not GitHub-wide prevalence** | Three explicit frames; report stratum-specific estimands; never pool without labeling |
| **Deterministic stratified cohort** | Reproducible but not a simple random sample; confidence intervals are descriptive aids only |
| **Repository selection bias** | Instruction stratum enriched by discoverability; general OSS biased by star-ranked search |
| **Detection limitations** | Regex/path patterns miss non-standard conventions; protocol version frozen and documented |
| **False negatives** | Paths outside pattern catalog; non-markdown conventions; private repos excluded |
| **False positives** | Prompt-like content in non-convention paths matching broad patterns (e.g. `prompts/`) |
| **Temporal snapshot** | Extraction wave date fixes cross-section; GitHub index drift between freeze and run |
| **Mixed stratum ambiguity** | AI-topic metadata ≠ instruction artifacts; interpret as sensitivity frame |

---

## Success criteria

Execution is successful when **all** of the following hold:

1. **Pipeline completes** — `make e1-1000` exits 0 without manual intervention
2. **QA passes** — `make e1-1000-qa` reports no accounting warnings; `succeeded + failed + skipped + missing = 1000`
3. **Registry accounting** — latest-per-repo profile rows = 1,000; no duplicate repo_ids in summaries
4. **Outputs generated** — all paths listed in **Expected outputs** exist and are non-empty
5. **Manifests record** — L1 manifest includes `registry_version`, `extraction_wave`, `detector_version`, `code_git_sha`

---

## Re-run policy

| Situation | Action |
|-----------|--------|
| **First execution** | Run once after `pre_execution_checklist.md` complete; record `execution_date` and `wave_id` in manifest |
| **Transient clone/network failure** | Re-run `make e1-1000-extract` with queue resume (no registry change) |
| **Detector/protocol change** | **Forbidden** under v1 — create `E1_1000_protocol_v2`, new wave id, new registry if needed |
| **Registry change** | **Forbidden** under v1 — any registry edit requires new registry version and hash update |
| **Bugfix in extraction code** | Document commit SHA; if L1 outputs affected, full re-extract with `--force` and new manifest timestamp |
| **Census-only regeneration** | Allowed if L1 unchanged: `make e1-1000-derive e1-1000-exports e1-1000-performance e1-1000-summary` |
| **Exploratory re-analysis** | Allowed on frozen Parquet exports without re-extraction |

**Never** overwrite `exports/e1/` or `exports/e1_100/` when re-running E1-1000.
