# RQ4 — Lifecycle Dynamics After Birth

## Research question

**RQ4:** What are the lifecycle dynamics of machine-consumable specifications after birth?

> This analysis models the reference panel as a **multi-state process**, not a survival
> half-life. Primary estimands are **transition probabilities**, **state occupancy**,
> and **latencies** between lifecycle phases.

## Lifecycle model

```
Birth → Operational → Integrity loss → Repair → Deletion
          ↘ Unverifiable (parallel branch at birth)
```

Mechanical observation states map to lifecycle phases:

| Mechanical | Lifecycle phase |
|------------|-----------------|
| VERIFIED | operational |
| MISSING | integrity_loss |
| REPAIRED | repair |
| DELETED | deletion |
| UNVERIFIABLE | unverifiable |

- Reference trajectories: **64,048**

## First transition probabilities (at birth)

| To phase | Count | P(to \| birth) |
|----------|------:|---------------:|
| operational | 4,603 | 0.072 |
| integrity_loss | 18,335 | 0.286 |
| unverifiable | 41,110 | 0.642 |
| repair | 0 | 0.000 |
| deletion | 0 | 0.000 |

## Key transition probabilities (post-birth)

| From | To | P(to \| from) |
|------|-----|--------------:|
| operational | integrity_loss | 0.492 |
| integrity_loss | repair | 0.170 |
| repair | operational | 0.842 |
| integrity_loss | deletion | 0.830 |
| operational | deletion | 0.505 |

## State occupancy (person-time)

| Phase | Person-days | Proportion |
|-------|------------:|-----------:|
| operational | 174,944 | 0.092 |
| integrity_loss | 1,054,485 | 0.556 |
| repair | 475 | 0.000 |
| deletion | 12,137 | 0.006 |
| unverifiable | 653,949 | 0.345 |

## Latencies (days)

| Latency | n | Median | Mean | p90 |
|---------|--:|-------:|-----:|----:|
| Integrity loss → repair | 99.0 | 13.17 | 33.91 | 70.67 |
| Birth → deletion | 2088.0 | 0.21 | 30.1 | 96.06 |
| Operational → deletion | 154.0 | 48.39 | 74.14 | 200.05 |

## Method notes

- **No survival model as primary result** — RQ2 KM curves are complementary, not RQ4 headline.
- Transition probabilities are **empirical row proportions** conditional on departing a phase.
- State occupancy weights commit intervals; last observation contributes zero tail dwell.
- Repair latency: first integrity_loss commit → first repair commit (REPAIRED phase).
- Born-stale references enter at **integrity_loss** at birth; post-verification decay is a separate path.

## Threats to validity

1. **Irregular panel spacing:** commit-sampled observations under-estimate brief phases.
2. **Mechanical states ≠ semantic lifecycle:** VERIFIED is tree membership only.
3. **DELETED conflates file death and reference removal** from instruction text.
4. **Repair detection:** MISSING→VERIFIED is labeled REPAIRED; silent fixes may be missed.
5. **Born-stale mass:** ~80% of verifiable refs never reach operational; occupancy skews to integrity_loss.
6. **No competing-risks adjustment:** transitions treated as nominal phase changes.
7. **Pilot cohort selection** limits generalization.

## Outputs

- `rq4_multistate.csv` — trajectories + aggregate multi-state table
- `figure_rq4_lifecycle_diagram.pdf`
- `figure_rq4_transition_matrix.pdf`
- `figure_rq4_state_occupancy.pdf`
- `figure_rq4_repair_latency.pdf`
- `figure_rq4_deletion_latency.pdf`
