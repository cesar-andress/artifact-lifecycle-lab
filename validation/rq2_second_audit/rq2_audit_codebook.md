# RQ2 Second-Auditor Codebook

Use this taxonomy exactly. Do not invent new primary categories unless a case
cannot be represented; then use `uncertain_insufficient_evidence` and note why.

## Estimand reminder

You are classifying **first post-verification Missing** events: the reference was
Verified at least once, then later Missing under the frozen detector. Decide
whether the event is **genuine post-verification decay** for the RQ2 adjusted
estimand (physical disappearance / loss of the referenced artifact after prior
verified existence), or an alternative explanation.

You must **not** be told the original audit labels or the aggregate 0/121 result
while annotating.

## Categories

### A — `genuine_decay`

- **Definition:** After at least one verified observation, the referenced
  artifact genuinely disappears (or becomes unavailable) such that the
  instruction claim is now false for the same intended target.
- **Inclusion:** Clear before/after tree evidence of deletion or irreversible
  loss of the target; not explained by rename/move, extractor error, or
  normative/template text.
- **Exclusion:** Renames/moves with continuity; false detector triggers;
  anchors/templates; external URLs.
- **Minimum evidence:** Verified-before-failure plus failure commit evidence that
  the same target is gone without a rename/move account.
- **Counts as genuine decay for RQ2:** yes.

### B — `rename_or_move`

- **Definition:** Target identity continues under a new path/name (return after
  missing, basename collision with a verified peer, or clear move).
- **Inclusion:** `returned_after_missing` and/or rename/move evidence in history.
- **Exclusion:** True deletion with no continuity.
- **Minimum evidence:** Continuity signal (return or rename/move) tied to the
  same logical artifact.
- **Counts as genuine decay for RQ2:** no (under primary protocol).

### C — `verification_anchor_issue`

- **Definition:** Missing status driven by verification-anchor / path-resolution
  mismatch rather than physical disappearance of the intended artifact.
- **Inclusion:** Anchor or resolution mismatch explains the Missing transition.
- **Exclusion:** Unequivocal deletion of the intended target.
- **Minimum evidence:** Anchor/path evidence inconsistent with a simple delete.
- **Counts as genuine decay for RQ2:** no (under primary protocol).

### D — `extractor_artifact`

- **Definition:** The “reference” is an extraction/template/placeholder artifact
  (not a durable repository claim about a real path/URL).
- **Inclusion:** Placeholder patterns, extraction debris, non-claims.
- **Exclusion:** Real path/URL claims that later fail.
- **Minimum evidence:** Snippet or reference form showing non-claim / template.
- **Counts as genuine decay for RQ2:** no.

### E — `normative_or_prescriptive`

- **Definition:** Prescriptive/instructional language (“should”, “ensure”,
  examples) rather than an existential claim that a path currently exists.
- **Inclusion:** Normative framing in snippet.
- **Exclusion:** Factual existence claims.
- **Minimum evidence:** Snippet supporting normative reading.
- **Counts as genuine decay for RQ2:** no.

### F — `external_or_environmental`

- **Definition:** External resource / environment dependency outside repo tree
  verification scope.
- **Inclusion:** Clearly external target.
- **Exclusion:** In-repo paths.
- **Minimum evidence:** External URL/host or env marker.
- **Counts as genuine decay for RQ2:** no.

### G — `ambiguous`

- **Definition:** Competing explanations remain after reviewing available
  evidence; a category can be named but confidence is insufficient.
- **Inclusion:** Two plausible categories remain.
- **Exclusion:** Clear single category.
- **Minimum evidence:** Explicit competing accounts in the note.
- **Counts as genuine decay for RQ2:** no under primary protocol (sensitivity
  scenarios may reclassify).

### U — `uncertain_insufficient_evidence`

- **Definition:** Evidence package is insufficient to classify.
- **Inclusion:** Missing snippet/tree/history needed for a decision.
- **Exclusion:** Merely hard cases that still have enough evidence.
- **Counts as genuine decay for RQ2:** no (record separately).

## Required annotation fields

| Field | Values |
|-------|--------|
| `auditor_category` | A–G labels above, or `uncertain_insufficient_evidence` |
| `confidence` | `high` / `medium` / `low` |
| `counts_as_genuine_decay` | `true` / `false` — whether this event should count in the RQ2 adjusted numerator |
| `evidence_note` | concise note citing which evidence fields you used |
| `category_ambiguity` | optional: names of competing categories |

## Examples outside the 121 set

Use born-stale taxonomy documentation and non-RQ2 examples in
`exports/truth_decay_pilot/born_stale_examples.csv` and
`exports/truth_decay_pilot/gfc_confirmatory_examples.csv` for calibration.
Do **not** open `rq2_failure_audit.csv` or any private answer key while labeling.

## Blindedness

The blinded CSV/XLSX omit original `final_category`, `is_genuine_decay`,
heuristic conclusions, and LLM judge fields. Do not seek those files until
annotation is complete.
