# Born-Stale Autopsy — Taxonomy Summary

## Purpose

Descriptive decomposition of **17,747** verifiable references that **never** reach
`VERIFIED` in the longitudinal panel. Categories explain **why** each reference
failed mechanical verification from first observation — not engineering fault codes.

## Cohort

- Born-stale references classified: **17747**
- LLM dual-judge adjudication enabled: **yes**
- References sent to LLM judges: **150**
- Judge disagreements (unresolved): **6**

## Inferred taxonomy (not hardcoded)

Categories emerge from deterministic heuristics first, then dual local LLM judges
when heuristic confidence is insufficient. Letter codes are illustrative only.

| Letter | Category | Count | % |
|--------|----------|------:|--:|
| A | `extraction_artifact` | 2235 | 12.6% |
| B | `template_placeholder` | 1926 | 10.9% |
| C | `normative_prescriptive` | 5836 | 32.9% |
| D | `pre_observation_evolution` | 876 | 4.9% |
| E | `external_reference` | 33 | 0.2% |
| G | `verification_anchor_mismatch` | 5301 | 29.9% |
| F | `genuine_false_claim` | 1532 | 8.6% |
| U | `unresolved_disagreement` | 8 | 0.0% |

## Adjudication status

- **deterministic_high:** 8579 (48.3%)
- **deterministic_medium:** 7628 (43.0%)
- **llm_quota_exceeded:** 1390 (7.8%)
- **llm_agreement:** 144 (0.8%)
- **llm_disagreement:** 6 (0.0%)

## Heuristic confidence distribution

- **high:** 8579 (48.3%)
- **low:** 1540 (8.7%)
- **medium:** 7628 (43.0%)

## Documented heuristics (deterministic pass)

### extraction_artifact (A)
- Prose product tokens (`Node.js`), invalid path chars, URL-like paths, directory `/`
- Reference fails `VALID_FILENAME` grammar without repo path structure

### template_placeholder (B)
- `examples/` paths, placeholder syntax (`<>`, `{}`, `path_to_`, `TODO`)
- Cross-repo generic tokens (`SKILL.md`, `package.json`) with ≥3 repo repetitions

### normative_prescriptive (C)
- Rule/skill/cursor instruction surfaces
- References to convention docs (`AGENTS.md`, `SKILL.md`) with prescriptive snippet language

### pre_observation_evolution (D)
- Structured path, file `change_type=modify` at first snapshot, ≥2 observations, always MISSING

### external_reference (E)
- Dependencies, scoped packages, URL tokens, prose external product names

### verification_anchor_mismatch (G)
- `./`/`../` prefixes or single-segment filenames verified from repo root only

### genuine_false_claim (F)
- Structured repo-like path, always MISSING, no higher-priority rule fired (low confidence)

## LLM adjudication protocol

- **Judge A:** `deepseek-coder-v2:lite` (Ollama, JSON output)
- **Judge B:** `devstral:latest` (skeptical framing, same taxonomy)
- Trigger: heuristic confidence `low`, or medium `genuine_false_claim`, or no category
- **Agreement:** `final_category` = shared label; status `llm_agreement`
- **Disagreement:** `final_category` = `unresolved_disagreement`; row copied to
  `born_stale_disagreements.csv`; **never silently merged**

## Uncertainty and limitations

1. **Snippets optional:** when L1b blob missing, heuristics use path shape only.
2. **Normative vs false claim** is ambiguous without semantic interpretation.
3. **Pre-observation evolution** cannot confirm path existed before panel without git archaeology.
4. **LLM judges** are local, non-blinded to heuristics, and not validated against human gold.
5. **Descriptive only:** no causal claims; does not modify RQ1/RQ2 datasets.
6. **Repo concentration** persists — taxonomy mass may reflect template repos.

## Implications

- Born-stale is **heterogeneous**; a single "staleness rate" blends measurement error,
  templates, and genuine false claims.
- RQ3 (agent vs human) should stratify by taxonomy category, not aggregate born-stale.
- Primary scientific construct shifts from **Truth Decay** to **initial reference validity**.

## Outputs

- `born_stale_taxonomy.csv` — full per-reference classification
- `born_stale_statistics.csv` — aggregate counts
- `born_stale_disagreements.csv` — unresolved LLM disagreements only
- `born_stale_examples.csv` — stratified examples per category
- `figure_born_stale_taxonomy.pdf`
- `figure_born_stale_by_reference_type.pdf`
- `figure_born_stale_by_repository.pdf`
