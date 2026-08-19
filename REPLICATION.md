# Replication guide

**Package version:** 1.2.0 (EMSE-facing packaging / documentation release)  
**Science freeze:** 2026-07-03 (primary observational evidence)  
**Validation extension:** 2026-07-31  
**Manuscript:** *Measuring Reference Integrity in Coding-Agent Instruction Files: An Audited Longitudinal Study* (Empirical Software Engineering)

This file is the entry point for reviewers and archivists. For a short overview, see [README.md](README.md).

## 1. What the study measures

Instruction-file references are tracked longitudinally. Never-verified (born-stale)
references and previously verified references that later become missing are reported
on disjoint bases. First post-verification missing candidates in the at-risk set are
audited under a frozen multi-estimator protocol, including independent human labels.

## 2. What this package contains

| Area | Location | Role |
|------|----------|------|
| Claim inventory | [`docs/SCIENTIFIC_EVIDENCE_FREEZE.md`](docs/SCIENTIFIC_EVIDENCE_FREEZE.md) | Supported / unsupported claims and canonical paths |
| Claim→evidence table | [`exports/paper_synthesis/late_binding_evidence_table.csv`](exports/paper_synthesis/late_binding_evidence_table.csv) | Frozen claim rows + validation rows |
| Human audit materials | [`validation/rq2_second_audit/`](validation/rq2_second_audit/) | Blinded package + independent human label streams |
| Validation protocol | [`docs/VALIDATION_EXTENSION_PROTOCOL.md`](docs/VALIDATION_EXTENSION_PROTOCOL.md) | Prespecified robustness analyses |
| Validation addendum | [`docs/VALIDATION_EXTENSION_ADDENDUM.md`](docs/VALIDATION_EXTENSION_ADDENDUM.md) | Relationship of validation layer to the primary freeze |
| Observational exports | `exports/truth_decay_pilot/`, `exports/truth_pilot/` | RQ1–RQ4, gates P1–P5, audits |
| Exploratory runtime probe | `exports/rq5_agent_impact/`, `exports/rq5_agent_impact_c/` | Frozen ledgers and analyses (package label RQ5) |
| Protocols | `protocol/` | Truth-decay and runtime-probe protocols |
| Code | `artifact_lab/` | Extraction, analysis, and report generators |
| Registries | `data/registry/` | Pilot / E1-100 / E1-1000 CSV frames |

The companion manuscript PDF and LaTeX sources are **not** stored here. Headline
metrics must be read from the frozen exports listed in the freeze inventory.

## 3. What is frozen evidence

| Class | Contents | Clean-clone expectation |
|-------|----------|-------------------------|
| **Frozen (authoritative)** | Audit CSVs/MD, human labels, RQ5 ledgers, uptake/ABC reports, evidence table | Present; cite these for manuscript numbers |
| **Observational regenerable** | Makefile targets that rewrite summaries from intermediate tables | Runnable after `pip install -e ".[dev,paper]"`; do not overwrite freeze without intent |
| **Non-regenerable here** | Runtime-probe agent runs (`make truth-decay-rq5-run`) | Require Claude Code CLI + credentials; **use frozen ledgers** |
| **Intentionally excluded** | `data/blobs/`, `scratch/`, job queues, private LB maps | Re-mine via extract if needed; not required to verify frozen tables |

Material-necessity / load-bearing annotation kits are **withdrawn**
(`exports/rq5_lb_blind_annotation/WITHDRAWN.md`).

## 4. Quick start (read-only verification)

```bash
git clone https://github.com/cesar-andress/artifact-lifecycle-lab.git
cd artifact-lifecycle-lab
git checkout v1.2.0

python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,paper]"

# Spot-check frozen headline paths
test -f exports/truth_decay_pilot/rq2_failure_audit_summary.md
test -f exports/truth_decay_pilot/gfc_confirmatory_summary.md
test -f exports/rq5_agent_impact/rq5_uptake_analysis.md
test -f exports/rq5_agent_impact/rq5_abc_comparative_analysis.md
test -f exports/rq5_agent_impact/rq5_results.csv
test -f exports/rq5_agent_impact_c/rq5_results.csv
test -f exports/paper_synthesis/late_binding_evidence_table.csv
test -f docs/SCIENTIFIC_EVIDENCE_FREEZE.md
test -d validation/rq2_second_audit

python -m pytest artifact_lab/tests -q
make validation-qc
```

## 5. Observational regeneration (optional)

These targets rewrite exports under `exports/truth_*` from committed intermediate
tables. They do **not** require Claude Code. Prefer frozen files for citation.

```bash
make truth-pilot-p1 truth-pilot-p2 truth-pilot-go-no-go
make truth-pilot-p3 truth-pilot-p4 truth-pilot-p5
make truth-decay-rq1 truth-decay-rq2 truth-decay-rq3 truth-decay-rq4
make truth-decay-born-stale-autopsy truth-decay-born-stale-audit
make truth-decay-rq2-failure-audit truth-decay-gfc-confirmatory-audit
make truth-decay-cited-uncited-audit
make truth-decay-rq5-uptake
make validation-all
```

Notes:

- `make truth-decay-rq5-mediation` regenerates an archived heuristic artifact only; not confirmatory evidence.
- `make truth-decay-rq5-run` / `truth-decay-rq5-report` are **frozen** for the manuscript; do not rerun for claim verification.
- LLM-assisted audit stages may be nondeterministic across model versions; frozen CSVs remain authoritative.
- Do **not** cite `exports/rq5_agent_impact/rq5_summary.md` (superseded 9-run summary). Use `rq5_uptake_analysis.md` (128 runs) and ABC reports.

## 6. External requirements / credentials boundary

| Need | Required for | Notes |
|------|--------------|-------|
| Python ≥ 3.11 (3.12 recommended) | Install + observational Make | See `pyproject.toml` |
| Network + git | Re-extracting registries into L1 | Not needed to read frozen exports |
| Claude Code CLI + credentials | Regenerating runtime-probe agent runs | Out of scope for archival verification |
| Local LLM weights (optional) | Re-running LLM audit residual stages | Frozen audit CSVs preferred |

## 7. Canonical manuscript paths

| Manuscript prose | Path |
|------------------|------|
| RQ2 / RQ3 failure audit | `exports/truth_decay_pilot/rq2_failure_audit_summary.md` |
| GFC confirmatory | `exports/truth_decay_pilot/gfc_confirmatory_summary.md` |
| Born-stale autopsy | `exports/truth_decay_pilot/born_stale_summary.md` |
| Runtime-probe uptake | `exports/rq5_agent_impact/rq5_uptake_analysis.md` |
| Runtime-probe A/B/C analysis | `exports/rq5_agent_impact/rq5_abc_comparative_analysis.md` |
| Runtime-probe A/B ledger | `exports/rq5_agent_impact/rq5_results.csv` |
| Runtime-probe C ledger | `exports/rq5_agent_impact_c/rq5_results.csv` |
| P4 validation | `exports/truth_pilot/p4_validation.md` |
| Freeze inventory | `docs/SCIENTIFIC_EVIDENCE_FREEZE.md` |
| Validation protocol | `docs/VALIDATION_EXTENSION_PROTOCOL.md` |
| RQ2 sensitivity | `validation/rq2_sensitivity/rq2_sensitivity_summary.md` |
| Concentration | `validation/concentration/concentration_summary.md` |
| Blinded human audit | `validation/rq2_second_audit/` |

## 8. Package versions and citation

| Version | Role |
|---------|------|
| **v1.2.0** (this release) | Recommended for EMSE manuscript readers; packaging/docs/metadata |
| **v1.1.0** | Prior archival package ([10.5281/zenodo.21716211](https://doi.org/10.5281/zenodo.21716211)) |
| **v1.0.0** | Prior primary freeze ([10.5281/zenodo.21711432](https://doi.org/10.5281/zenodo.21711432)) |

- License: [LICENSE](LICENSE) (MIT)
- Citation file: [CITATION.cff](CITATION.cff)
- Authors: César Andrés (corresponding); David Martín-Moncunill
- Zenodo **v1.2.0** version DOI: **pending mint** (update `CITATION.cff` after Zenodo archives this tag)
- Concept DOI: [10.5281/zenodo.21711431](https://doi.org/10.5281/zenodo.21711431)
- GitHub release: [v1.2.0](https://github.com/cesar-andress/artifact-lifecycle-lab/releases/tag/v1.2.0)

## Known limitations

1. L1b blob store (`data/blobs/`) is not shipped (size); full re-mine from registries requires re-extraction.
2. Prefer a fixed Git tag / Zenodo version over a moving `main` clone when citing.
3. Runtime-probe success/uptake numbers are ledger-frozen; agent products may drift if rerun.
4. Development notes under `docs/` (including historical venue readiness drafts) are not manuscript claims; use the freeze inventory.
