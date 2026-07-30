# E1 — Repository Adoption Census

## Cohort interpretation
> This 100-repository cohort is an enriched engineering cohort, not a population sample. Adoption rates must not be interpreted as GitHub-wide prevalence.

## Scope
- Registry repositories: 100
- Repositories with matched convention files: 86
- Matched convention paths (ever): 3253

## Reproducible datasets
- Path-level census: `data/derived/adoption_census/e1_100/v1/path_census.csv`
- Repo × family census: `data/derived/adoption_census/e1_100/v1/repo_family_census.csv`
- Repo-level census: `data/derived/adoption_census/e1_100/v1/repo_census.csv`

## Publication exports (artifact)
- Figure 1 PDF: `exports/e1_100/fig1.pdf`
- Figure 1 data: `exports/e1_100/fig1.csv`
- Table 1: `exports/e1_100/table1.csv`

## Paper repository export
- `../paper/figures/fig1.pdf`
- `../paper/figures/fig1.csv`
- `../paper/tables/table1.csv`

## Regeneration
```bash
make e1-pilot   # bounded development pilot
make e1         # full pilot registry
make paper      # copy exports to ../paper/
```
