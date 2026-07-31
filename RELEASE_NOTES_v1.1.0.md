# Release notes — v1.1.0

**Title:** Artifact Lifecycle Lab — validation extension  
**Date:** 2026-07-31  
**Tag:** `v1.1.0`  
**Authors:** César Andrés (corresponding); David Martín-Moncunill  
**Zenodo version DOI:** [10.5281/zenodo.21716211](https://doi.org/10.5281/zenodo.21716211)  
**Prior freeze (v1.0.0):** [10.5281/zenodo.21711432](https://doi.org/10.5281/zenodo.21711432)  
**Concept DOI:** [10.5281/zenodo.21711431](https://doi.org/10.5281/zenodo.21711431)  
**GitHub release:** [TOSEM Replication Package v1.1.0](https://github.com/cesar-andress/artifact-lifecycle-lab/releases/tag/v1.1.0)  
**Relation to v1.0.0:** additive robustness layer; primary frozen exports unchanged.

## Summary

Pre-submission validation extension on the frozen observational exports used by the TOSEM manuscript.

## Highlights

- Blinded second-auditor package for all 121 RQ2 candidate events.
- Independent human labels (Person 1, Person 2; Person 3 as sensitivity) and recommended multi-estimator summaries.
- Prespecified audit-rule sensitivity alongside the frozen primary 0/121 estimator.
- Repository-concentration, leave-one-out, and template-cluster sensitivity analyses.
- Automated QC for frozen headline counts and blinded-package leakage.

## Archival status

1. Published **v1.0.0** (DOI `10.5281/zenodo.21711432`) remains intact.
2. Published **v1.1.0** (DOI `10.5281/zenodo.21716211`) on the same Zenodo concept DOI family.
3. Do not overwrite v1.0.0 files in place.

## Start here

1. [docs/VALIDATION_EXTENSION_PROTOCOL.md](docs/VALIDATION_EXTENSION_PROTOCOL.md)
2. [docs/VALIDATION_EXTENSION_ADDENDUM.md](docs/VALIDATION_EXTENSION_ADDENDUM.md)
3. `make validation-all`
