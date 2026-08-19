# Replication Package v1.2.1

**Title:** Artifact Lifecycle Lab: Replication Package for Measuring Reference Integrity in Coding-Agent Instruction Files  
**Date:** 2026-08-19  
**Tag:** `v1.2.1`  
**Authors:** César Andrés (corresponding); David Martín-Moncunill  
**Manuscript:** *Measuring Reference Integrity in Coding-Agent Instruction Files: An Audited Longitudinal Study* (Empirical Software Engineering)

**Concept DOI (all versions):** [10.5281/zenodo.21711431](https://doi.org/10.5281/zenodo.21711431)  
**Prior version DOI (v1.2.0):** [10.5281/zenodo.22009399](https://doi.org/10.5281/zenodo.22009399)  
**GitHub release:** [v1.2.1](https://github.com/cesar-andress/artifact-lifecycle-lab/releases/tag/v1.2.1)

The version-specific Zenodo DOI for **v1.2.1** is assigned when Zenodo archives this tag. Read it from the public Zenodo landing after mint; do not invent it in-tree.

## Summary

Patch release aligning the replication-package documentation and archival metadata with the EMSE manuscript. The frozen observational data, human labels, protocols, analysis outputs, and scientific results are unchanged from v1.2.0. This release corrects documentation/package-version consistency so that the archived repository state and its public metadata are aligned.

## Why this patch

Zenodo v1.2.0 (`10.5281/zenodo.22009399`) archived Git state `7f037e0`, while documentation that recorded the minted version DOI landed in a later commit (`0bf31da`). Those documentation-only fixes are packaged here as **v1.2.1** without moving or rewriting v1.2.0.

## Changes in this release (documentation / metadata only)

- Bump package version to **1.2.1** (`.zenodo.json`, `CITATION.cff`, `pyproject.toml`, README / REPLICATION).
- Prefer the stable **concept DOI** in package citation metadata; do not embed a not-yet-minted version DOI.
- Record v1.2.0 as a preserved prior version DOI.
- Clarify the mint → landing → cite workflow so the archived ZIP does not claim a version DOI that did not exist at archive time.

## What did not change

- Frozen observational exports under `exports/`
- Independent human audit labels and audit decisions
- Frozen protocols and claim-to-evidence mappings
- Scientific numerators and denominators
- Science freeze date for primary manuscript numbers: **2026-07-03**

## Start here

1. [REPLICATION.md](REPLICATION.md)
2. [docs/SCIENTIFIC_EVIDENCE_FREEZE.md](docs/SCIENTIFIC_EVIDENCE_FREEZE.md)
3. [CITATION.cff](CITATION.cff)
4. After Zenodo mints v1.2.1, use the landing version DOI for manuscript citation updates
