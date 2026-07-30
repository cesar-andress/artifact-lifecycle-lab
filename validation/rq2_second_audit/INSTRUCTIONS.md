# Second-Auditor Instructions (RQ2, n=121)

## Role

You are an independent auditor. Classify each of the 121 blinded events using
`rq2_audit_codebook.md`. You should be independent of the original
classification. Prefer not to know the manuscript’s headline adjusted result
until after you finish.

## Materials

1. `rq2_audit_blinded.csv` — machine-readable evidence (no original labels).
2. `rq2_audit_form.xlsx` — same evidence plus empty annotation columns.
3. `rq2_audit_codebook.md` — category definitions and estimand.

## Procedure

1. Read the codebook once before labeling.
2. For each `event_id`, review evidence fields (reference, snippet, failure
   commit, verified-before-failure, returned-after-missing, basename collision,
   durations, repetition counts).
3. Fill `auditor_category`, `confidence`, `counts_as_genuine_decay`,
   `evidence_note`, and `category_ambiguity` if needed.
4. Do not leave rows blank; use `uncertain_insufficient_evidence` when stuck.
5. Save your completed sheet as:

   `rq2_second_auditor_labels.csv`

   with columns:

   `event_id,auditor_category,confidence,counts_as_genuine_decay,evidence_note,category_ambiguity,auditor_id,annotation_date`

6. Do not open `private/rq2_original_labels_private.csv` or the frozen
   `exports/truth_decay_pilot/rq2_failure_audit.csv` until labeling is done.

## After labeling

Return the completed CSV to the analysis maintainer. Agreement, kappa, and
adjudication scripts will then be run. Disagreements that change the binary
estimand will be adjudicated with an explicit rationale file; original labels
are never silently overwritten.
