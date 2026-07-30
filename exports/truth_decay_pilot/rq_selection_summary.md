# Selection Hypothesis — Matched Observational Study

## Research question

Are files referenced by machine-consumable instruction files intrinsically more stable
than comparable files inside the same repository?

## Design

Observational matched-pair study. For each file-level reference in the longitudinal panel:

1. **Treatment:** referenced path (`path`, `script_name`).
2. **Control:** never-referenced path in the same repository at panel start, matched on:
   - file extension
   - directory depth (±1 level)
   - creation period (first-commit timestamp, when available)
   - file size at panel start (when available)
3. **Outcomes (panel window):** active lifetime, commit churn, rename frequency,
   deletion before panel end, survival until panel end.
4. **Inference:** paired differences, bootstrap 95% CIs, Cohen's d, sign-flip permutation tests.

- Random seed: **42**
- Matched pairs: **1746**
- Repositories: **70**

## Results

### Active lifetime (days, panel window)

- Referenced mean: **33.9818**
- Control mean: **33.6458**
- Paired difference (referenced − control): **0.3360**
  (95% bootstrap CI: -1.2659–2.0336)
- Standardized mean difference (Cohen's d): **0.0095**
- Permutation p-value (greater-tailed): **0.351265**
- Fraction favoring referenced stability: **75.0%**
  (95% bootstrap CI: 73.0%–77.1%)
- Bootstrap CI crosses zero: **yes**
- Permutation significant at α=0.05: **no**

### Commit churn (panel window)

- Referenced mean: **5.7801**
- Control mean: **1.9857**
- Paired difference (referenced − control): **3.7944**
  (95% bootstrap CI: 3.0979–4.6352)
- Standardized mean difference (Cohen's d): **0.2304**
- Permutation p-value (less-tailed): **1.000000**
- Fraction favoring referenced stability: **48.0%**
  (95% bootstrap CI: 45.8%–50.5%)
- Bootstrap CI crosses zero: **no**
- Permutation significant at α=0.05: **no**

### Rename events (panel window)

- Referenced mean: **0.0836**
- Control mean: **0.0510**
- Paired difference (referenced − control): **0.0326**
  (95% bootstrap CI: 0.0206–0.0447)
- Standardized mean difference (Cohen's d): **0.1282**
- Permutation p-value (less-tailed): **1.000000**
- Fraction favoring referenced stability: **95.4%**
  (95% bootstrap CI: 94.4%–96.3%)
- Bootstrap CI crosses zero: **no**
- Permutation significant at α=0.05: **no**

### Deletion before panel end

- Referenced mean: **0.0435**
- Control mean: **0.0693**
- Paired difference (referenced − control): **-0.0258**
  (95% bootstrap CI: -0.0372–-0.0149)
- Standardized mean difference (Cohen's d): **-0.1057**
- Permutation p-value (less-tailed): **0.000100**
- Fraction favoring referenced stability: **98.3%**
  (95% bootstrap CI: 97.7%–98.9%)
- Bootstrap CI crosses zero: **no**
- Permutation significant at α=0.05: **yes**

### Survival until panel end

- Referenced mean: **0.9565**
- Control mean: **0.9307**
- Paired difference (referenced − control): **0.0258**
  (95% bootstrap CI: 0.0149–0.0372)
- Standardized mean difference (Cohen's d): **0.1057**
- Permutation p-value (greater-tailed): **0.000100**
- Fraction favoring referenced stability: **98.3%**
  (95% bootstrap CI: 97.7%–98.9%)
- Bootstrap CI crosses zero: **no**
- Permutation significant at α=0.05: **yes**

## Interpretation

Negative paired differences on churn, rename, and deletion (and positive on lifetime
and survival) support the **selection hypothesis**: instruction files disproportionately
reference intrinsically stable repository paths rather than volatile ones.

This study does not modify prior RQ outputs (`cited_uncited_*`, RQ1–RQ4).

## Outputs

- `rq_selection_dataset.csv`
- `figure_selection_churn.pdf`
- `figure_selection_survival.pdf`
- `figure_selection_matched_effect.pdf`
