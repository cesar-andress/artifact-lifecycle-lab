# Repository Concentration Summary

Frame: enriched E1–100 observational exports. These analyses do **not** claim external representativeness.

## Cohort concentration

| Cohort | Cases | Repos (zeros) | Top1 | Top5 | Top10 | HHI | Max repo |
|--------|------:|---------------|-----:|-----:|------:|----:|----------|
| `born_stale_all` | 17747 | 80 (0 zero) | 16.8% | 41.7% | 62.4% | 582 | `c65277d4b7b5f15d` |
| `prior_genuine_false_claim` | 1405 | 80 (23 zero) | 15.4% | 45.1% | 68.7% | 616 | `3f33ab9828ac52ad` |
| `confirmed_false_at_birth` | 1200 | 80 (27 zero) | 15.5% | 47.1% | 70.9% | 651 | `3f33ab9828ac52ad` |
| `born_stale_category__normative_prescriptive` | 5836 | 80 (8 zero) | 12.5% | 40.2% | 61.6% | 512 | `c65277d4b7b5f15d` |
| `born_stale_category__verification_anchor_mismatch` | 5301 | 80 (7 zero) | 25.7% | 59.5% | 73.3% | 1126 | `c65277d4b7b5f15d` |
| `born_stale_category__extraction_artifact` | 2235 | 80 (12 zero) | 37.1% | 59.3% | 73.2% | 1590 | `c65277d4b7b5f15d` |
| `born_stale_category__template_placeholder` | 1926 | 80 (14 zero) | 21.8% | 48.8% | 64.1% | 771 | `c6ac6f9616b35ee8` |
| `born_stale_category__genuine_false_claim` | 1405 | 80 (23 zero) | 15.4% | 45.1% | 68.7% | 616 | `3f33ab9828ac52ad` |

## Leave-one-repository-out

### `confirmed_false_among_prior_gfc`
- Full-sample proportion recomputed over LOO exclusions: min=0.8444, max=0.8577, range=0.0133
- Most influential exclusion: `79e5b3dcaadc644e` (Δ=-0.0097)

### `prior_gfc_among_born_stale`
- Full-sample proportion recomputed over LOO exclusions: min=0.0703, max=0.0951, range=0.0249
- Most influential exclusion: `c65277d4b7b5f15d` (Δ=+0.0160)

## Repository-balanced sensitivity

Unweighted mean/median of repository-level rates (sensitivity estimand, not a population estimate).

- `prior_gfc_among_born_stale`: pooled=0.0792, mean_repo=0.1429, median_repo=0.0866
- `confirmed_false_among_prior_gfc`: pooled=0.8541, mean_repo=0.7689, median_repo=0.8571

## Template-cluster sensitivity

Deterministic clusters: exact `(instruction_path, reference)` with `repeated_repo_count >= 5` and category in {template_placeholder, extraction_artifact, normative_prescriptive}.

- `none`: excluded 0 rows / 0 clusters; prior GFC remaining rate=0.0792
- `top_1_repeated_templateish_clusters`: excluded 17 rows / 1 clusters; prior GFC remaining rate=0.0792
- `top_3_repeated_templateish_clusters`: excluded 33 rows / 3 clusters; prior GFC remaining rate=0.0793
- `top_5_repeated_templateish_clusters`: excluded 43 rows / 5 clusters; prior GFC remaining rate=0.0794
- `top_10_repeated_templateish_clusters`: excluded 65 rows / 10 clusters; prior GFC remaining rate=0.0795
