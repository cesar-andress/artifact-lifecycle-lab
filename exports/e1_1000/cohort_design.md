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
