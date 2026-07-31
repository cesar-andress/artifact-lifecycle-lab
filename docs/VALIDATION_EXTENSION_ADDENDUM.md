# Validation Extension Addendum (to Scientific Evidence Freeze)

**Date:** 2026-07-31  
**Does not overwrite:** `docs/SCIENTIFIC_EVIDENCE_FREEZE.md` (freeze 2026-07-03)  
**Protocol:** `docs/VALIDATION_EXTENSION_PROTOCOL.md`

## Relationship to v1.0.0

| Item | v1.0.0 | This extension (v1.1.0) |
|------|--------|-------------------------|
| Primary observational exports | Frozen | Unchanged |
| Adjusted genuine decay primary | 0/121 | Still primary |
| Independent human audits | Absent | Person 1 17/121; Person 2 18/121; Person 3 sensitivity 27/121 |
| Paired both-YES consensus | N/A | 13/121 (conservative proxy) |
| Juan stream | N/A | Excluded (provisional) |
| Audit-rule sensitivity | Absent | 0–25/121 |
| Repository concentration | Absent | Added |

## Recommended human-validation study (2026-07-31)

- Retained streams: Person 1 + Person 2 (primary pair); Person 3 (upper sensitivity).
- Excluded: Juan.
- Outputs: `validation/rq2_second_audit/agreement/recommended_study_summary.md`.
- Formal third-party adjudication of the 9–10 Person 1–Person 2 disagreements remains optional.


## Exact changes

- Added validation protocol, scripts (`scripts/validation/`), Make targets (`validation-*`).
- Regenerable public artifacts under `validation/` (private answer keys under `validation/rq2_second_audit/private/`, gitignored).
- Automated QC assertions for frozen row counts and no label leakage.
- Manuscript updated to report primary 0/121 plus sensitivity range 0–25/121 and concentration results; RQ5 main-text compressed.

## Provenance snapshot (protocol declaration commit)

- Git commit at protocol declaration: `9dd13df9c642077d2994b2881e3f9eb3d992d948`
- Input SHA256 prefixes unchanged from protocol table (RQ2 audit `5efd790630e3de36`, born-stale `8d340848882a7f42`, GFC `b55eae8c4d6c22cb`).

## Remaining work

1. ~~Independent human annotation~~ — Person 1, Person 2, and Person 3 labels ingested; Juan excluded.
2. ~~Agreement summaries~~ — `make validation-recommended` / recommended study outputs under `validation/rq2_second_audit/agreement/`.
3. Formal third-party adjudication of the remaining Person 1–Person 2 binary disagreements remains optional.
4. ~~Publish Zenodo **v1.1.0**~~ — published as [10.5281/zenodo.21716211](https://doi.org/10.5281/zenodo.21716211); do not silently replace v1.0.0 ([10.5281/zenodo.21711432](https://doi.org/10.5281/zenodo.21711432)).
