# Changelog

## [1.2.1] — 2026-08-19

### Documentation / metadata patch (frozen science unchanged)

- Align archived repository snapshot with package citation metadata after Zenodo v1.2.0
  captured an earlier commit than the DOI-recording docs.
- Bump package version to **1.2.1**; prefer Zenodo **concept DOI** `10.5281/zenodo.21711431` in-tree.
- Do not embed a not-yet-minted v1.2.1 version DOI; read it from the Zenodo landing after archive.
- Preserve v1.2.0 ([10.5281/zenodo.22009399](https://doi.org/10.5281/zenodo.22009399)) and earlier tags unchanged.
- Add `RELEASE_NOTES_v1.2.1.md`.

## [1.2.0] — 2026-08-19

### Packaging / documentation release (frozen science unchanged)

- Align public metadata and documentation with the Empirical Software Engineering (EMSE) manuscript
  *Measuring Reference Integrity in Coding-Agent Instruction Files: An Audited Longitudinal Study*.
- Bump package version to **1.2.0** (`.zenodo.json`, `CITATION.cff`, `pyproject.toml`, README / REPLICATION).
- Add `RELEASE_NOTES_v1.2.0.md` and `docs/historical/README.md` (navigation for pre-submission development notes).
- Preserve frozen observational exports, human labels, protocols, and scientific results.
- Prior archival versions remain available: v1.1.0 ([10.5281/zenodo.21716211](https://doi.org/10.5281/zenodo.21716211)),
  v1.0.0 ([10.5281/zenodo.21711432](https://doi.org/10.5281/zenodo.21711432)).
- Zenodo version DOI for v1.2.0: [10.5281/zenodo.22009399](https://doi.org/10.5281/zenodo.22009399).

## [1.1.0] — 2026-07-31

### Validation extension (does not alter frozen primary observations)

- Add `docs/VALIDATION_EXTENSION_PROTOCOL.md` and `docs/VALIDATION_EXTENSION_ADDENDUM.md`.
- Add blinded RQ2 second-auditor package under `validation/rq2_second_audit/` (private answer keys gitignored / regenerable).
- Add prespecified audit-rule sensitivity outputs (`validation/rq2_sensitivity/`; range 0–25/121).
- Add repository-concentration analyses (`validation/concentration/`).
- Add `make validation-*` targets, QC script, and pytest assertions for frozen counts / leakage.
- Update claim-to-evidence table with sensitivity and concentration rows.
- Independent human agreement metrics included under `validation/rq2_second_audit/` (Person 1, Person 2; Person 3 as sensitivity).
- Zenodo: published as **v1.1.0** ([10.5281/zenodo.21716211](https://doi.org/10.5281/zenodo.21716211)); do not silently replace archival **v1.0.0** ([10.5281/zenodo.21711432](https://doi.org/10.5281/zenodo.21711432)).

Science freeze for primary manuscript numbers remains **2026-07-03**.

## [1.0.0] — 2026-07-31

### Archival release (historical package identity preserved in RELEASE_NOTES.md)

- Add LICENSE (MIT), CITATION.cff, .zenodo.json, REPLICATION.md, RELEASE_NOTES.md.
- Document frozen versus regenerable outputs; mark RQ5 agent runs as non-regenerable for claim verification.
- Withdraw material-necessity annotation kit contents from the distribution tree.
- Mark superseded RQ5 nine-run summaries as obsolete in-file.
- Point P4 gold default at the committed worksheet path (no absolute local Downloads path).
- Align evidence-table Condition C source with the authoritative C ledger.
- Set package version to 1.0.0.

Science freeze for manuscript numbers remains **2026-07-03** (see `docs/SCIENTIFIC_EVIDENCE_FREEZE.md`).
