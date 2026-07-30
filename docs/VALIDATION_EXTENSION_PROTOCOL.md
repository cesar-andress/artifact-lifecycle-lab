# Validation Extension Protocol (pre-submission robustness)

**Status:** active extension on frozen exports  
**Date declared:** 2026-07-31  
**Does not overwrite:** `docs/SCIENTIFIC_EVIDENCE_FREEZE.md`  
**Relation to freeze:** original observational analyses remain the preregistered / main analyses; all work here is validation or sensitivity.

## Purpose

Add three pre-submission robustness layers without altering frozen primary observations:

1. Independent human validation of all **121** RQ2 post-verification Missing audit events.
2. Prespecified audit-rule sensitivity for the adjusted **0/121** estimand.
3. Repository-concentration analysis for born-stale and confirmed-false-at-birth results.

## Frozen inputs (authoritative)

Recorded at protocol declaration against commit `9dd13df9c642077d2994b2881e3f9eb3d992d948`.

| Role | Path | Rows (expected) | SHA256 (first 16 hex) |
|------|------|----------------:|------------------------|
| RQ2 failure audit labels | `exports/truth_decay_pilot/rq2_failure_audit.csv` | 121 | `5efd790630e3de36` |
| RQ2 audit summary | `exports/truth_decay_pilot/rq2_failure_audit_summary.md` | — | `83cc8293eef3a060` |
| Born-stale taxonomy | `exports/truth_decay_pilot/born_stale_taxonomy.csv` | 17747 | `8d340848882a7f42` |
| Born-stale by repo | `exports/truth_decay_pilot/born_stale_by_repo.csv` | — | (derived) |
| GFC confirmatory audit | `exports/truth_decay_pilot/gfc_confirmatory_audit.csv` | 1405 | `b55eae8c4d6c22cb` |
| Longitudinal trajectories | `exports/truth_decay_pilot/reference_longitudinal.csv` | — | `f1c6ca05879e285e` |
| Scientific freeze inventory | `docs/SCIENTIFIC_EVIDENCE_FREEZE.md` | — | — |

### Existing aggregate values (must remain reproducible)

| Claim | Value |
|-------|------:|
| RQ2 candidate events | 121 |
| Adjusted genuine post-verification decay (primary) | 0/121 |
| Born-stale references | 17747 |
| Prior genuine-false-claim labels | 1405 |
| Confirmed-false-at-birth | 1200 |

## Planned analyses

### A. Independent second-auditor package (human)

- Blind all fields that reveal first-auditor conclusions.
- Retain raw evidence needed for independent classification.
- Private answer key held out of public release until annotation completes.
- **Do not** compute agreement, kappa, or adjudicated estimates until a real human second auditor supplies labels.
- **Do not** use an LLM as a substitute second human auditor.

### B. Audit-rule sensitivity (deterministic; scenarios locked before computing aggregates)

Scenarios are fixed here. Scripts must implement these rules only.

1. **primary_frozen**  
   Binary estimand = frozen `is_genuine_decay` (True iff `final_category == genuine_decay`).

2. **decay_favoring**  
   Count as genuine decay if **any** of:
   - frozen `final_category` ∈ {`genuine_decay`, `ambiguous`, `verification_anchor_issue`};
   - `returned_after_missing` is True (treat return-after-missing as decay rather than rename);
   - `basename_collision_verified` is True (treat basename collision as decay rather than rename).  
   Rationale: a reasonable reviewer could interpret these as physical disappearance / identity loss after verified existence.

3. **high_specificity**  
   Count as genuine decay **only** if frozen `final_category == genuine_decay`.  
   (Identical to primary under the current freeze; retained as the conservative bound of the protocol.)

4. **second_auditor**  
   Binary estimand from independent human labels (`counts_as_genuine_decay`).  
   **Computed only when** `validation/rq2_second_audit/rq2_second_auditor_labels.csv` exists with all 121 event IDs.

5. **adjudicated**  
   Binary estimand from `validation/rq2_second_audit/rq2_disagreement_adjudication.csv`.  
   **Computed only when** adjudication is complete.

For each available scenario report: numerator/121, %, Wilson 95% CI, category composition (where defined), case IDs that differ from primary, and rule rationale.

### C. Repository concentration

Separately for:

- all born-stale references (17747);
- prior `genuine_false_claim` labels (1405);
- confirmed-false-at-birth (`is_confirmed_false == True`, 1200);
- major born-stale categories with repository IDs.

Report repo-level counts/rates, distribution summaries, top-1/5/10 shares, HHI, leave-one-repository-out pooled proportions, deterministic template-cluster exclusion if identifiable from existing fields, and repository-balanced (unweighted mean/median repo-level rate) as a sensitivity estimand only.

**Template-cluster procedure (deterministic):** group rows by exact `(instruction_path, reference)` when `repeated_repo_count >= 5` and `final_category`/`heuristic` indicates template or placeholder; exclude the largest such clusters in a sensitivity table. No manual family inference.

## Decisions required before observing new aggregates

Locked before script execution of sensitivity numerators:

- Decay-favoring inclusion rules as listed above (no post-hoc expansion).
- High-specificity = literal `genuine_decay` only.
- Concentration metrics = shares, HHI on repo shares of case counts, LOO pooled proportions.
- Second-auditor / adjudicated scenarios remain missing until human work completes.
- Original 0/121 remains the primary frozen estimate in the manuscript regardless of sensitivity range.

## Outputs

| Path | Public before human annotation? |
|------|----------------------------------|
| `validation/rq2_second_audit/rq2_audit_blinded.csv` | Yes |
| `validation/rq2_second_audit/rq2_audit_form.xlsx` | Yes |
| `validation/rq2_second_audit/rq2_audit_codebook.md` | Yes |
| `validation/rq2_second_audit/INSTRUCTIONS.md` | Yes |
| `validation/rq2_second_audit/rq2_original_labels_private.csv` | **No** |
| `validation/rq2_sensitivity/*` | Yes |
| `validation/concentration/*` | Yes |
| `docs/VALIDATION_EXTENSION_PROTOCOL.md` | Yes |

## Limitations

- Does not add repositories, rerun agents, or change extractors.
- Sensitivity scenarios are interpretive bounds, not new ground truth.
- Concentration analyses do not imply external representativeness beyond the enriched E1–100 frame.
- Human agreement metrics are undefined until independent annotation exists.
- Private answer keys must not appear in Zenodo/public tarballs before annotation completes.

## Make targets

```text
make validation-package   # blinded audit + private key (local)
make validation-sensitivity
make validation-concentration
make validation-qc
make validation-all       # package + sensitivity + concentration + qc
```
