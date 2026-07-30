# Validation Extension Addendum (to Scientific Evidence Freeze)

**Date:** 2026-07-31  
**Does not overwrite:** `docs/SCIENTIFIC_EVIDENCE_FREEZE.md` (freeze 2026-07-03)  
**Protocol:** `docs/VALIDATION_EXTENSION_PROTOCOL.md`

## Relationship to v1.0.0

| Item | v1.0.0 (Zenodo DOI 10.5281/zenodo.21711432) | This extension (planned v1.1.0) |
|------|---------------------------------------------|-------------------------------|
| Primary observational exports | Frozen / authoritative | Unchanged |
| Adjusted genuine decay primary | 0/121 | Still primary; unchanged |
| Confirmed-false-at-birth | 1200/1405 | Unchanged |
| Blinded RQ2 second-auditor package | Absent | Added (`validation/rq2_second_audit/`) |
| Audit-rule sensitivity | Absent | Added (`validation/rq2_sensitivity/`) |
| Repository concentration | Absent | Added (`validation/concentration/`) |
| Human agreement metrics | N/A | **Not computed** (no second-auditor labels yet) |

## Exact changes

- Added validation protocol, scripts (`scripts/validation/`), Make targets (`validation-*`).
- Regenerable public artifacts under `validation/` (private answer keys under `validation/rq2_second_audit/private/`, gitignored).
- Automated QC assertions for frozen row counts and no label leakage.
- Manuscript updated to report primary 0/121 plus sensitivity range 0–25/121 and concentration results; RQ5 main-text compressed.

## Provenance snapshot (protocol declaration commit)

- Git commit at protocol declaration: `9dd13df9c642077d2994b2881e3f9eb3d992d948`
- Input SHA256 prefixes unchanged from protocol table (RQ2 audit `5efd790630e3de36`, born-stale `8d340848882a7f42`, GFC `b55eae8c4d6c22cb`).

## Remaining work

1. Independent human annotation of `validation/rq2_second_audit/rq2_audit_form.xlsx` / blinded CSV.
2. Run `make validation-agreement` and complete adjudication file.
3. Recompute second-auditor / adjudicated sensitivity scenarios.
4. Publish Zenodo **v1.1.0** (do not silently replace v1.0.0).
