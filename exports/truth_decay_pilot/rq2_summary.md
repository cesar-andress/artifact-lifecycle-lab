# RQ2 — Reference Half-Life (Survival Analysis)

## Research question

**RQ2:** What is the survival distribution (half-life) of verifiable references
in machine-consumed documentation?

## Methodological assumptions (explicit)

1. **Time origin:** first `VERIFIED` observation per reference (protocol RQ2).
2. **Event:** first `MISSING` after origin (single-failure, non-recurrent).
3. **Cohort:** verifiable types only (`path`, `directory`, `script_name`, `dependency`).
4. **Exclusion:** references never observed as VERIFIED (left-truncated / born stale).
5. **Censoring:** end of follow-up or reference removal without failure; `DELETED` coded separately.
6. **Independence:** references treated as independent; **repo clustering not adjusted** (naive Greenwood CI).
7. **Discrete snapshots:** inter-commit gaps; durations in calendar days between L1 events.
8. **Competing risks:** repair and deletion not modeled in primary KM; repair reported separately.

## Known limitations

- Repo-side fixes without instruction edits appear as continued VERIFIED (immortal time bias risk is low but non-zero).
- Engineering cohort (pilot + E1-100), not E1-1000 scientific frame.
- Zero-day failures common (commit-snapshot granularity).

## Cohort

- References entering at VERIFIED: **4521**
- Excluded (never VERIFIED in panel): **17747**
- Primary failure events (first missing): **121** (2.7%)
- Right-censored: **4263** (94.3%)
- Censored at instruction-file deletion: **137**

## Survival estimates

- **Median survival:** not reached (survival > 0.5 at end of follow-up)
- **Repairs after failure (count):** 17
- **Final cumulative repair incidence (post-failure):** 67.9%

## Survival function (selected horizons)

- **S(30 days):** 0.977
- **S(90 days):** 0.917
- **S(180 days):** 0.901
- **S(365 days):** 0.848

## Conditional failure time (non-KM)

- Among references with observed first missing (n=121), median time from first VERIFIED to first MISSING: **34.5 days**
- RQ1 reported ~16 days using a simpler exploratory median over all trajectories with both states present; RQ2 enforces post-origin failure ordering and censoring, yielding a higher conditional median among observed failures.
- This is **not** the Kaplan–Meier half-life because most references are right-censored without failure.

## Interpretation

- **Half-life (KM median):** not estimable in this cohort — survival remains > 0.5 through follow-up (S(365d) ≈ 0.848).
- **Primary decay signal:** 2.7% of verifiable references that reach VERIFIED subsequently fail; decay is rare but non-negligible.
- **Repair:** among post-failure follow-up, cumulative repair incidence reaches 67.9%.

## Outputs

- `rq2_survival.csv` — per-reference survival records
- `figure_survival.pdf` — Kaplan–Meier with 95% CI
- `figure_cumulative_hazard.pdf` — Nelson–Aalen cumulative hazard
- `figure_censoring.pdf` — event vs censoring distribution
