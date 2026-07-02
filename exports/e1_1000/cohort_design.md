# E1-1000 cohort design

> **Scope warning:** This cohort supports two interpretable estimands: (1) prevalence within
> the AI-instruction discovery frame, and (2) contrast against general OSS repositories.
> It is **not** a GitHub-wide population sample. Adoption is measured under **head-only**
> inspection (current-presence at HEAD), not full lifecycle history.

## Purpose

E1-1000 is the default **scientific cohort** for the TOSEM paper (RQ1–RQ3, RQ5).
It replaces E1-100 as the primary inference population while preserving E1-100 as the
engineering regression cohort.

## Three explicit strata

| Stratum | `cohort_stratum` | Size | Interpretation |
|---------|------------------|------|----------------|
| AI-instruction discovery frame | `ai_instruction_discovery` | 334 | Repositories discovered via GitHub **code search** on instruction-artifact path predicates (VSDLC frame). Supports enriched-frame prevalence. |
| General OSS | `general_oss` | 333 | Repositories discovered via **repository search** on stars/language/activity only — no instruction-path predicates, no AI-topic predicates. Contrast arm. |
| Mixed / control | `mixed_control` | 333 | Repositories discovered via **repository search** on AI-related **topics** (metadata frame) without guaranteed instruction-artifact signals. |

## Inclusion criteria (all strata)

- Public GitHub repository with parseable `owner/name` URL
- `stars >= 10` (instruction and mixed frames; general OSS queries start at 100 stars)
- `pushed_at >= 2024-06-01` (activity floor)
- Not a fork, archived repository, template, mirror, or duplicate URL
- Name/topic exclusion filters: templates, boilerplates, awesome-* collections, obvious mirrors

## Exclusion criteria

- Forks, archived repositories, GitHub templates, mirrors
- Duplicate `repo_id` or `repo_url` across the registry
- Obvious collection repos (`awesome-*`, `/awesome` suffix)
- Template/starter/boilerplate name patterns
- Cross-stratum duplicates (deterministic deduplication by URL when building strata)

## Sampling algorithm

1. **Seed:** `42` (deterministic; stratum-specific derived seeds `42`, `43`, `44`)
2. Load candidate pools:
   - Instruction frame: `/home/cesar/papers/vsdlc/vsdlc/data/interim/eligible_repos_enriched.jsonl`
   - General OSS: `data/registry/sources/general_oss_candidates.jsonl`
   - Mixed/control: `/home/cesar/papers/vsdlc/vsdlc/data/raw/second_frame_candidates.jsonl`
3. Group candidates within each stratum by `(family_or_language_or_topic, star_bucket)`
4. Sort within groups by `repository_url` (case-insensitive)
5. Shuffle group keys with stratum seed; round-robin draw one repo per group per pass
6. Merge strata, sort final registry by `repo_url`

## Star buckets (`selection_stratum` suffix)

- `stars_small`: stars < 500
- `stars_medium`: 500 ≤ stars < 5000
- `stars_large`: stars ≥ 5000

## Registry metadata

- Registry path: `data/registry/e1_1000_repos.csv`
- Registry version: `e1_1000_v1`
- Target size: **1000**
- Extraction wave (planned): `e1_1000_v1`
- Protocol family: `ai_conventions_v1`
- Inspection mode: `head-only`

## Expected limitations

- **Not GitHub-wide prevalence:** All three strata are visibility-biased frames on public GitHub.
- **Head-only adoption:** Counts reflect files present at HEAD, not deleted or historical-only artifacts.
- **Discovery-frame inflation:** Instruction stratum repos were selected because convention paths were discoverable.
- **General OSS is not random:** Repository search ranks by stars; language quotas are query-defined, not proportional to GitHub language share.
- **Mixed/control stratum is AI-topic adjacent:** Topic predicates enrich for AI-adjacent metadata; this is a sensitivity frame, not a pure control.
- **Temporal snapshot:** Registry freeze and extraction wave timestamp bound all prevalence estimates.

## Dual interpretability (RQ1)

Report separately:

1. **Enriched frame prevalence** — strata `ai_instruction_discovery` (+ optionally `mixed_control`)
2. **General OSS contrast** — stratum `general_oss`

Do not pool strata without explicit labeling. Combined cohort statistics are descriptive only.

## Why deterministic sampling?

E1-1000 uses **seed 42** and deterministic sort keys so that any researcher with the same candidate pools and builder script reproduces the **exact same 1,000 URLs**.

Determinism serves three purposes:

1. **Pre-registration integrity** — the registry can be committed and cited before extraction; results cannot be tuned by post-hoc repo substitution.
2. **Auditability** — stratum round-robin selection is replayable from documented inputs.
3. **Regression isolation** — pipeline changes are separated from cohort changes; E1-100 remains the engineering regression cohort.

Deterministic sampling is **not** claim of simple random sampling from GitHub. It is a reproducible stratified draw from documented frames.

## Why three strata?

A single discovery frame cannot support both enriched prevalence and OSS contrast. Three strata separate interpretable estimands:

| Stratum | Answers |
|---------|---------|
| **AI discovery frame** | “Among repos discoverable via instruction-artifact code search, how prevalent are convention files at HEAD?” |
| **General OSS** | “Among star-ranked visible OSS repos (no AI discovery predicate), what is the contrast prevalence?” |
| **Mixed/control** | “Among AI-topic metadata repos without guaranteed instruction paths, where does metadata discovery land?” |

Pooling would confound discoverability with adoption. RQ1 requires **separate reporting** per stratum or explicitly labeled contrasts.

## Why this is NOT GitHub-wide prevalence

None of the three strata is a probability sample of all GitHub repositories:

- **Visibility bias** — only public repos; search-indexed; star/activity floors.
- **Frame bias** — instruction stratum requires path discoverability; general OSS requires star-ranked search hits.
- **Head-only** — measures current presence, not historical adoption.
- **English / platform bias** — GitHub API and search semantics favor certain ecosystems.

All prevalence figures are **conditional on frame ℱ**, documented in `cohort_stratum`. The paper must never extrapolate to “all of GitHub.”

## Why head-only is appropriate for E1

E1 is an **adoption census**, not a lifecycle study. RQ1 asks whether convention artifacts are **currently present** at HEAD in each cohort repository.

Head-only inspection (`list_head_paths`):

- Matches the estimand (current-presence prevalence).
- Avoids full-history traversal cost at n=1,000 scale.
- Was validated as feasible in E1-100 engineering cohort (RQ4 pilot evidence).

Head-only **undercounts** repos that adopted then deleted conventions. That is a documented lower bound, not a bug — correcting it requires a different protocol (full-history or panel-based lifecycle).

## Why lifecycle analyses require another protocol

The following questions are **explicitly out of scope** for `E1_1000_protocol_v1`:

| Question | Required capability | Protocol |
|----------|---------------------|----------|
| When were artifacts deleted? | Full history or L2 panel delete events | E2 / lifecycle protocol (future) |
| Survival / hazard of conventions | Longitudinal state machine | E2+ |
| Semantic drift of content | Blob diffs + LLM coding | L5 / E5 (future) |
| Ownership concentration | CODEOWNERS + blame | L3 (future) |
| Co-change with code | Commit coupling graph | L4 (future) |

E1-1000 produces the **cross-sectional baseline** that later longitudinal protocols extend. Running lifecycle analysis on the same wave without a separate protocol would conflate estimands and invalidate claims.

## Protocol cross-references

- Scientific protocol: `protocol/E1_1000_protocol_v1.md`
- Experiment manifest: `protocol/experiment_manifest.yaml`
- Pre-execution checklist: `protocol/pre_execution_checklist.md`
- Dataset lineage: `docs/dataset_lineage.md`
