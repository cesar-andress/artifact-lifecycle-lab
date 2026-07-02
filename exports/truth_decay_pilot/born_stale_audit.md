# Born-Stale Audit — Never-Verified References

## Construct distinction

**Born-stale:** a reference is observed as checkable (`path`, `directory`, `script_name`,
`dependency`) but **never** reaches `VERIFIED` in the longitudinal panel — typically
`INIT→MISSING` from the first snapshot.

**Post-verification decay (RQ2):** a reference that was `VERIFIED` at least once and
subsequently fails. RQ2 survival conditions on the latter; born-stale references are
excluded by design.

## Cohort

- RQ2 exclusion cohort (verifiable, never VERIFIED): **17747**
- Broader never-verified trajectories (all types): **59380**
- Repos contributing born-stale references: **80**

## 1. Never-verified counts by reference type

### RQ2 exclusion cohort (verifiable only)

- **path:** 13349
- **directory:** 3216
- **script_name:** 1149
- **dependency:** 33

### Broader born-stale population (includes commands)

- **command:** 41633 (never VERIFIED; mechanically UNVERIFIABLE by protocol)
- **path:** 13349
- **directory:** 3216
- **script_name:** 1149
- **dependency:** 33

> Commands are excluded from RQ2 because they are not mechanically verifiable; they
> represent a separate surface (shell blocks) from verifiable path-like claims.

## 2. Extraction surface (proxy classification)

Longitudinal CSV does not store extraction `context`. Counts use deterministic heuristics
aligned with the extraction grammar in `references.py` (bash blocks, install lines, bare
paths, example paths, comment-adjacent filenames).

- **Code blocks / script invocations:** 1149 (6.5%)
- **Comments (comment-adjacent paths):** 27 (0.2%)
- **Examples (example directories or filenames):** 980 (5.5%)
- **Prose / false-positive bare tokens:** 1786 (10.1%)
- **Structured repo paths (backtick/bare path shape):** 13805 (77.8%)
- **Unclear:** 0 (0.0%)

## 3. Relative-path resolution candidates

- **Count:** 6015 (33.9% of RQ2 exclusion cohort)
- Heuristic: `./`/`../` prefixes, or single-segment filenames verified from repo root
  (instruction-file-relative anchors are not modeled in v1 verification).

## 4. Likely external references

- **Count:** 2060 (11.6%)
- Heuristic: dependencies, URL-like tokens, scoped package names (`@scope/pkg`),
  or prose product tokens without repo path structure (e.g. `Node.js`).

## 5. Cross-file / cross-repo repetition

- Unique `(type, reference)` keys: **12248**
- Keys appearing in ≥2 trajectories: **2093**
- Trajectories whose key appears in ≥5 instruction files: **3346**
- Trajectories whose key appears in ≥5 repos: **1338**

## 6. Repo concentration

- Top 5 repos account for **41.7%** of born-stale references
- Top 10 repos account for **62.4%**

See `born_stale_by_repo.csv` for full distribution.

## Implications for the paper

1. **Born-stale is not longitudinal decay.** These references fail from the first
   observable snapshot (`INIT→MISSING`). They measure *initial validity* of extracted
   claims, not half-life after a reference was once true.
2. **RQ2 estimates a conditional hazard.** Kaplan–Meier survival applies only to
   references that cross the `VERIFIED` threshold at least once (n=4,521 in this cohort).
   The 17,747 exclusions are a different construct and must not be merged into decay rates.
3. **Future models should separate components:** (a) probability a new reference is
   born valid vs born stale; (b) hazard of failure given prior verification. Mixing
   them inflates apparent decay and confounds extraction noise with lifecycle drift.
4. **Extraction surface matters.** A large share of born-stale references are prose
   false positives, example paths, or relative-path candidates — not post-hoc repo drift.
5. **Cohort concentration:** born-stale mass is concentrated in a small number of repos;
   repo-level covariates (template reuse, agent rule packs) likely explain much of the
   signal before file-age effects.

## Outputs

- `born_stale_examples.csv` — ranked illustrative trajectories
- `born_stale_by_repo.csv` — per-repo counts
- `born_stale_by_type.csv` — type-level summary
