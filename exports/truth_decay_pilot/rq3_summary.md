# RQ3 — Specification Integrity by Maintenance Regime

## Research question (observational)

**RQ3:** How does specification integrity differ between human-maintained and
agent-maintained machine-consumable specifications?

> **No causal claims.** This analysis reports **associations** between git-derived
> maintenance regimes and mechanical reference integrity in the longitudinal panel.
> Regime labels describe **observed commit attribution patterns**, not interventions.

## Join specification

- Longitudinal panel: `reference_longitudinal.csv`
- Attribution: `agent_commit_candidates.csv`
- Join key: `(repo_id, instruction_path, commit_sha)`
- Commit–attribution match rate (unique file commits): **100.0%**

## Maintenance regime definitions

File-level regime from commits touching each instruction file (P4 agent-maintenance rules;
Dependabot/Renovate/security bots excluded from agent tally):

- **human_only:** 0% agent-maintenance commits among labeled commits
- **agent_assisted:** 0% < agent share < 50%
- **agent_dominated:** agent share ≥ 50%
- **unknown:** no attribution label for any commit in the file panel

## File counts by regime

- **human_only:** 1188 instruction files
- **agent_assisted:** 215 instruction files
- **agent_dominated:** 595 instruction files
- **unknown:** 11 instruction files

- Reference trajectories analyzed: **64048**

## Estimands (observational proportions)

| Regime | N (verifiable) | P(verified birth) | P(born-stale) | P(decay\|verified) | P(repair\|decay) |
|--------|---------------:|------------------:|--------------:|-------------------:|------------------:|
| human_only | 8958 | 0.105 | 0.895 | 0.011 | 0.000 |
| agent_assisted | 5182 | 0.343 | 0.657 | 0.053 | 0.179 |
| agent_dominated | 8024 | 0.224 | 0.776 | 0.019 | 0.200 |
| unknown | 104 | 0.106 | 0.894 | 0.000 | 0.000 |

### Construct definitions

- **Birth integrity index:** P(reference ever reaches VERIFIED | verifiable type)
- **Born-stale:** verifiable reference never VERIFIED in panel (see born-stale autopsy)
- **Decay:** VERIFIED observed, then later MISSING (post-verification)
- **Repair:** decay trajectory with ≥1 repair event or REPAIRED state

## Threats to validity

1. **Attribution precision unvalidated (P4 pending):** regime labels inherit heuristic
   git-metadata errors (missing Co-Authored-By, false signatures).
2. **Ecological confounding:** agent-dominated files may differ in project type,
   template reuse, and team maturity — not controlled observationaly.
3. **File-level regime aggregation:** birth and decay events may occur under different
   commits than the dominant regime label.
4. **Mechanical integrity ≠ semantic correctness:** VERIFIED is tree membership only.
5. **Born-stale heterogeneity:** stale-at-birth mixes extraction artifacts, templates,
   and genuine false claims (see born-stale autopsy).
6. **Selection bias:** pilot + E1-100 engineering cohort; not population representative.
7. **Repo clustering:** multiple references within repos are not independent;
   proportions are unadjusted for clustering.
8. **Unknown regime mass:** commits without attribution candidates inflate unknown stratum.
9. **No temporal ordering claim:** higher born-stale in agent-dominated files does not
   imply agents *cause* stale references without experimental design (RQ5).

## Interpretation guardrails

- Report **differences in observed integrity**, not agent *effects*.
- Stratify future work by born-stale taxonomy before comparing maintenance regimes.
- Do not merge born-stale prevalence with post-verification decay rates.

## Outputs

- `rq3_dataset.csv` — per-reference trajectory with regime and integrity flags
- `rq3_tables.csv` — regime metrics + transition counts
- `figure_rq3_birth_integrity.pdf`
- `figure_rq3_repair_probability.pdf`
- `figure_rq3_transition_matrix.pdf`
