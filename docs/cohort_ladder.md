# E1 cohort ladder

Artifact Lifecycle Lab uses a **progression of cohorts** with distinct scientific roles. Each cohort has isolated exports under `exports/` and must not overwrite sibling cohort outputs.

## Pilot (17 repositories)

| Property | Value |
|----------|-------|
| Registry | `data/registry/pilot_repos.csv` |
| Exports | `exports/e1/` |
| Purpose | Development, profiling, inspection-mode experiments, bounded smoke tests |
| Inference | **None** — qualitative pipeline evidence only |

The pilot registry mixes AI-adopter seeds and general-OSS anchors. It validates extraction economics (RQ5 pilot evidence) and detector behavior before scaling.

## Engineering cohort (100 repositories)

| Property | Value |
|----------|-------|
| Registry | `data/registry/e1_100_repos.csv` |
| Exports | `exports/e1_100/` |
| Wave | `e1_100_v1` |
| Purpose | End-to-end pipeline regression, first quantitative census, QA accounting |
| Inference | **Limited** — enriched engineering frame; not the TOSEM default |

E1-100 combines 17 pilot seeds with 83 VSDLC instruction-frame repos (seed 42). It proved latest-per-repo accounting and cohort_summary QA but is **not** positioned as a population sample.

## Scientific cohort (1,000 repositories)

| Property | Value |
|----------|-------|
| Registry | `data/registry/e1_1000_repos.csv` |
| Design doc | `exports/e1_1000/cohort_design.md` |
| Exports | `exports/e1_1000/` |
| Wave | `e1_1000_v1` |
| Purpose | **Default E1 scientific cohort** for TOSEM (RQ1–RQ3, RQ5) |
| Inference | Frame-conditional prevalence + general-OSS contrast |

E1-1000 is explicitly stratified into three interpretable arms:

1. **`ai_instruction_discovery`** (334) — VSDLC instruction-artifact code-search frame
2. **`general_oss`** (333) — GitHub repository search on stars/language/activity only
3. **`mixed_control`** (333) — AI-topic metadata discovery without guaranteed instruction paths

**Limitations (always explicit):**

- Not GitHub-wide prevalence
- Head-only current-presence adoption at HEAD
- Deterministic stratified sample (seed 42), not a random draw from all GitHub

Build: `make e1-1000-registry` (registry + design doc) or full pipeline `make e1-1000`.

QA: `make e1-1000-qa`

## Future population-scale cohorts

Not implemented in this milestone. Population-scale work would require:

- Independent L0 sampling frame definition (beyond discovery-visible repos)
- Documented API snapshot dates and quota accounting
- Extraction infrastructure changes (parallelism, caching) **after** scientific validity of E1-1000 is established

E1-1000 is the gate: fix measurement and reporting before scaling to 10k+ repositories.

## Export isolation

| Cohort | Must not overwrite |
|--------|-------------------|
| `exports/e1/` | — (pilot) |
| `exports/e1_100/` | `exports/e1/` |
| `exports/e1_1000/` | `exports/e1/`, `exports/e1_100/` |

Each cohort writes to its own L1 path (`data/l1/<cohort>/v1/`), census directory, and profiling wave label.
