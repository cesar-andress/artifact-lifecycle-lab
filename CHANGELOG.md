# Changelog

## [1.1.0] — 2026-07-31

### Validation extension (does not alter frozen primary observations)

- Add `docs/VALIDATION_EXTENSION_PROTOCOL.md` and `docs/VALIDATION_EXTENSION_ADDENDUM.md`.
- Add blinded RQ2 second-auditor package under `validation/rq2_second_audit/` (private answer keys gitignored / regenerable).
- Add prespecified audit-rule sensitivity outputs (`validation/rq2_sensitivity/`; range 0–25/121).
- Add repository-concentration analyses (`validation/concentration/`).
- Add `make validation-*` targets, QC script, and pytest assertions for frozen counts / leakage.
- Update claim-to-evidence table with sensitivity and concentration rows.
- **Human agreement metrics not included** (no real second-auditor labels yet).
- Zenodo: publish as **v1.1.0**; do not silently replace archival **v1.0.0**.

Science freeze for primary manuscript numbers remains **2026-07-03**.

## [1.0.0] — 2026-07-31

### Archival release (TOSEM replication package)

- Add LICENSE (MIT), CITATION.cff, .zenodo.json, REPLICATION.md, RELEASE_NOTES.md.
- Document frozen versus regenerable outputs; mark RQ5 agent runs as non-regenerable for claim verification.
- Withdraw material-necessity annotation kit contents from the distribution tree.
- Mark superseded RQ5 nine-run summaries as obsolete in-file.
- Point P4 gold default at the committed worksheet path (no absolute local Downloads path).
- Align evidence-table Condition C source with the authoritative C ledger.
- Set package version to 1.0.0.

Science freeze for manuscript numbers remains **2026-07-03** (see `docs/SCIENTIFIC_EVIDENCE_FREEZE.md`).
