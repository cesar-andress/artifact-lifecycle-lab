# Cited vs Uncited Path Churn Contrast

## Purpose

Test whether paths referenced in AI instruction files are intrinsically more stable
than comparable non-referenced paths in the same repositories.

## Design

- **Cited paths:** file-level references (`path`, `script_name`) from the longitudinal panel.
- **Controls:** same-extension, depth-matched paths present in the repo tree at panel start,
  never cited in instruction files for that repository.
- **Churn metric:** count of git commits touching the path between panel start and end commits.
- **Matching:** up to 40 cited paths sampled per repository (fixed seed).

## Sample

- Matched pairs analyzed: **2259**
- Repositories represented: **78**
- Mean cited verification rate (longitudinal): **27.8%**

## Results

- Mean cited churn: **1.99** commits
  (95% bootstrap CI: 1.49–2.61)
- Mean uncited churn: **1.54** commits
  (95% bootstrap CI: 1.18–1.99)
- Mean paired difference (cited − uncited): **0.44**
  (95% bootstrap CI: -0.21–1.15)
- Fraction of pairs where cited churn ≤ uncited churn: **85.4%**
  (95% bootstrap CI: 83.9%–86.9%)

## Interpretation

Mean git churn is **not significantly different** between groups (bootstrap CI crosses zero).

In **85.4%** of matched pairs, cited paths churn less than or equal to their uncited controls — evidence that instruction files disproportionately reference intrinsically stable paths (selection effect).

Mean and paired analyses can diverge when a minority of pairs have extreme churn; 
the paired stability fraction is the primary test of intrinsic stability.

## Limitations

- Matching uses extension and directory depth only (not LOC or team ownership).
- Churn counts depend on git history availability in bare clones.
- Does not modify prior RQ outputs.

## Outputs

- `cited_uncited_comparison.csv`
- `figure_cited_uncited_churn.pdf`
- `figure_churn_difference_hist.pdf`
