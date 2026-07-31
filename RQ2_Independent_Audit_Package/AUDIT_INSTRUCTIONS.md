# Audit Instructions — Independent RQ2 Reviewer

## Role

You are an independent human auditor. Classify all **121** blinded events.
Work alone from this package and repository evidence. Do not seek prior audit
labels, aggregate study results, or the study narrative.

## Materials to use

1. `rq2_audit_codebook.md` — read once before labeling.
2. `rq2_audit_form.xlsx` — preferred annotation surface.
3. `rq2_audit_blinded.csv` — identical evidence if you prefer CSV tooling.
4. Public repository URLs / commits listed in each row (inspect trees/history
   as needed).
5. `protocol/` — auditor-facing protocol excerpts only.

## What each row is

Each row is a **first post-verification Missing** candidate: the reference was
Verified at least once under the frozen detector, then later Missing.
Decide the taxonomy category and whether the event should count as
**genuine post-verification decay** for the study estimand.

## For every event, record

1. **category** — primary taxonomy label from the codebook  
   (`genuine_decay`, `rename_or_move`, `verification_anchor_issue`,
   `extractor_artifact`, `normative_or_prescriptive`,
   `external_or_environmental`, `ambiguous`, or
   `uncertain_insufficient_evidence`)
2. **genuine_decay** — `YES` / `NO` / `INSUFFICIENT_EVIDENCE`
3. **confidence** — `High` / `Medium` / `Low`
4. **notes** — evidence note, max 2–3 sentences
5. **ambiguity** — `true`/`false` or short note of competing categories

Also include `auditor_id` and `annotation_date` (ISO date) on every row.

## Rules

Use only:

- repository evidence (URL in the row)
- commits / file history / manifests / tree state
- extracted reference text and snippet in the row
- this package’s codebook and protocol excerpts

Do **not** consult:

- study write-ups or discussion text
- prior audit labels or withheld label files
- aggregate statistics or expected numerators

## Procedure

1. Open `rq2_audit_form.xlsx` (sheet `audit_form`).
2. For each `event_id`, review evidence columns, then fill the annotation
   columns (or export/complete the CSV schema below).
3. Leave no blank rows. Use `uncertain_insufficient_evidence` and
   `genuine_decay=INSUFFICIENT_EVIDENCE` when stuck.
4. Save your completed labels as `rq2_second_auditor_labels.csv` with header:

```text
event_id,category,genuine_decay,confidence,ambiguity,notes,auditor_id,annotation_date
```

5. Return that CSV to the package coordinator.

## Integrity

Do not reorder or drop `event_id` values. All 121 IDs from the blinded file
must appear exactly once in your deliverable.
