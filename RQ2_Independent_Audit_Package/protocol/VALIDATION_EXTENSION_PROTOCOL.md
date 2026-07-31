# Independent RQ2 Human Audit — Auditor Protocol Excerpt

**Audience:** external independent auditor  
**Scope:** classification of 121 blinded post-verification Missing candidates  
**Blinding:** this excerpt deliberately omits prior labels and aggregate results

## Purpose

Provide an independent human classification of each candidate event for the
RQ2 estimand: whether a first post-verification Missing observation reflects
**genuine post-verification decay** (physical disappearance / irreversible loss
of the referenced artifact after prior verified existence), or an alternative
explanation under the study taxonomy.

## Units

One row = one candidate event, identified by opaque `event_id`.

## Required judgments (per event)

1. Primary taxonomy category (see codebook).
2. Binary estimand: genuine post-verification decay?
   `YES` / `NO` / `INSUFFICIENT_EVIDENCE`
3. Confidence: `High` / `Medium` / `Low`
4. Short evidence note (2–3 sentences).
5. Ambiguity flag / competing categories if needed.

## Evidence allowed

- Fields in the blinded CSV / XLSX form
- Public repository content at the listed URLs and commits
- Tree / history / manifest inspection you perform yourself

## Evidence forbidden during annotation

- Prior auditor labels or withheld label files
- Aggregate study numerators or study narrative
- Any file not shipped in this package except public repository contents

## Deliverable

`rq2_second_auditor_labels.csv` covering all 121 `event_id` values exactly once.

## After return

The study team will compare your labels to the frozen first-auditor labels
**after** your CSV is received. Those comparison steps are out of scope for
this package.
