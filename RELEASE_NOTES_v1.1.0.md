# Release notes — v1.1.0 (planned / in-repo)

**Title:** Artifact Lifecycle Lab — validation extension  
**Date:** 2026-07-31  
**Tag:** `v1.1.0`  
**Relation to v1.0.0:** additive robustness layer; primary frozen exports unchanged.

## Summary

Pre-submission validation extension on the frozen observational exports used by the TOSEM manuscript.

## Highlights

- Blinded second-auditor package for all 121 RQ2 candidate events.
- Prespecified audit-rule sensitivity (primary 0/121; decay-favoring 25/121; high-specificity 0/121).
- Repository-concentration, leave-one-out, and template-cluster sensitivity analyses.
- Automated QC for frozen headline counts and blinded-package leakage.
- **Not included:** agreement/kappa/adjudicated estimates (await real human annotator).

## Zenodo plan

1. Keep published **v1.0.0** (DOI `10.5281/zenodo.21711432`) intact.
2. Upload a new version **v1.1.0** on the same Zenodo concept DOI after annotation status is documented.
3. Do not overwrite v1.0.0 files in place.

## Start here

1. [docs/VALIDATION_EXTENSION_PROTOCOL.md](docs/VALIDATION_EXTENSION_PROTOCOL.md)
2. [docs/VALIDATION_EXTENSION_ADDENDUM.md](docs/VALIDATION_EXTENSION_ADDENDUM.md)
3. `make validation-all`
