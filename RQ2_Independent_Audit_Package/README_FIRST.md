# README FIRST — RQ2 Independent Human Audit

## Purpose

This package supports an **independent, blinded** human audit of **121**
candidate post-verification Missing events from a frozen empirical software
engineering study.

Your task is to classify each event using only the materials in this package
and publicly inspectable repository evidence (commits, trees, histories).

This package is intentionally **blinded**: it does **not** disclose any prior
audit labels, aggregate study results, or expected outcomes. Do not seek those
materials while annotating.

## Files included

| Path | Role |
|------|------|
| `README_FIRST.md` | This file |
| `AUDIT_INSTRUCTIONS.md` | Step-by-step audit procedure |
| `rq2_audit_codebook.md` | Category taxonomy and estimand |
| `rq2_audit_form.xlsx` | Workbook to fill (preferred) |
| `rq2_audit_blinded.csv` | Same evidence in CSV form |
| `blinding_report.md` | Attestation that distribution materials are blinded |
| `evidence/README.md` | Where case evidence lives |
| `protocol/` | Auditor-facing protocol excerpts (PDF) |
| `checksums/SHA256SUMS.txt` | SHA-256 hashes of packaged files |

## Expected deliverable

Return a single CSV named:

`rq2_second_auditor_labels.csv`

with columns:

```text
event_id,category,genuine_decay,confidence,ambiguity,notes,auditor_id,annotation_date
```

Field guidance is in `AUDIT_INSTRUCTIONS.md` and `rq2_audit_codebook.md`.

## Estimated effort

About **8–12 hours** for a careful pass over all 121 events
(roughly 4–6 minutes per event, plus setup).

## Contact

Package coordinator: **[NAME / EMAIL / ORCID — fill before distribution]**

## Blinding statement

This distribution package was assembled and machine-checked so that it does
**not** contain prior classifications, withheld label files, private mappings,
or aggregate numerator results. Please do not seek external study summaries or
prior audit files while annotating.
