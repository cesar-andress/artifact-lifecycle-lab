# ACM TOSEM Paper Skeleton

**Working title:** Late Binding in Machine-Consumed Instruction Files

**Status:** Paper-writing mode — experiments frozen.

## Build

Requires ACM `acmart` class (TeX Live / ACM template).

```bash
cd paper
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

## Structure

| Path | Role |
|------|------|
| `main.tex` | ACM scaffold, abstract, includes |
| `sections/01-introduction.tex` … `09-conclusion.tex` | Section bodies |
| `tables/` | LaTeX table fragments |
| `figures/` | Figure PDFs (copy from `exports/`) |
| `references.bib` | Bibliography stub |

## Evidence discipline

- All numeric claims must appear in `exports/paper_synthesis/late_binding_evidence_table.csv`.
- Mark `\textbf{TODO:}` in prose where cohort sizes or citations are pending.
- Do **not** rerun agents during paper iteration.

## Related docs

- `docs/LATE_BINDING_MODEL_v1.md` — conceptual model
- `exports/paper_synthesis/` — evidence table and README
