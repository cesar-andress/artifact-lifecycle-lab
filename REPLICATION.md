# Replication guide

**Package version:** 1.1.0 (validation extension; Zenodo archival v1.0.0 unchanged)
**Science freeze:** 2026-07-03 (primary)
**Validation extension:** 2026-07-31
**Manuscript:** *Measuring Reference Integrity in Coding-Agent Instruction Files: An Audited Longitudinal Study* (Empirical Software Engineering)

Historical TOSEM-era titles in freeze notes and `RELEASE_NOTES.md` record how v1.0.0 / v1.1.0 were created. They are not the current manuscript identity.

This file is the entry point for reviewers and archivists. For platform internals, see [README.md](README.md).

## What this archive contains

| Area | Location | Role |
|------|----------|------|
| Claim inventory | [`docs/SCIENTIFIC_EVIDENCE_FREEZE.md`](docs/SCIENTIFIC_EVIDENCE_FREEZE.md) | Supported / unsupported claims and canonical paths |
| Validation protocol | [`docs/VALIDATION_EXTENSION_PROTOCOL.md`](docs/VALIDATION_EXTENSION_PROTOCOL.md) | Prespecified robustness analyses |
| Validation addendum | [`docs/VALIDATION_EXTENSION_ADDENDUM.md`](docs/VALIDATION_EXTENSION_ADDENDUM.md) | v1.0.0 ↔ v1.1.0 relationship |
| Claim→evidence table | [`exports/paper_synthesis/late_binding_evidence_table.csv`](exports/paper_synthesis/late_binding_evidence_table.csv) | Frozen claim rows + validation rows |
| Observational exports | `exports/truth_decay_pilot/`, `exports/truth_pilot/` | RQ1–RQ4, gates P1–P5, audits |
| Validation artifacts | `validation/` | Blinded RQ2 package, sensitivity, concentration |
| Exploratory RQ5 | `exports/rq5_agent_impact/`, `exports/rq5_agent_impact_c/` | Frozen ledgers and analyses |
| Protocols | `protocol/` | Truth-decay and RQ5 experiment protocols |
| Code | `artifact_lab/` | Extraction, analysis, and report generators |
| Registries | `data/registry/` | Pilot / E1-100 / E1-1000 CSV frames |

The companion manuscript PDF and LaTeX sources are **not** stored in this repository (submission workspace is separate). Headline metrics must be read from the frozen exports listed in the freeze inventory.

## Frozen versus regenerable

| Class | Contents | Clean-clone expectation |
|-------|----------|-------------------------|
| **Frozen (authoritative)** | Audit CSVs/MD, RQ5 ledgers, uptake/ABC reports, evidence table | Present; cite these for manuscript numbers |
| **Observational regenerable** | Makefile targets that rewrite summaries from `reference_longitudinal.csv` and sibling exports | Runnable after `pip install -e ".[dev,paper]"`; do not overwrite freeze without intent |
| **Non-regenerable here** | RQ5 agent runs (`make truth-decay-rq5-run`) | Require Claude Code CLI + credentials; **use frozen ledgers** |
| **Intentionally excluded** | `data/blobs/` (L1b content-addressed text), `scratch/`, job queues, private LB maps | Re-mine via extract if needed; not required to verify frozen tables |

Material-necessity / load-bearing annotation kits are **withdrawn** and are not distribution targets (see `exports/rq5_lb_blind_annotation/WITHDRAWN.md`).

## Quick start (read-only verification)

```bash
git clone https://github.com/cesar-andress/artifact-lifecycle-lab.git
cd artifact-lifecycle-lab
git checkout v1.0.0

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

python -m pytest artifact_lab/tests -q
```

## Observational regeneration (optional)

These targets rewrite exports under `exports/truth_*` from committed intermediate tables. They do **not** require Claude Code. Prefer frozen files for citation.

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

## External requirements

| Need | Required for | Notes |
|------|--------------|-------|
| Python ≥ 3.11 (3.12 recommended) | Install + observational Make | See `pyproject.toml` |
| Network + git | Re-extracting registries into L1 | Not needed to read frozen exports |
| Claude Code CLI + credentials | Regenerating RQ5 agent runs | Out of scope for archival verification |
| Local LLM weights (optional) | Re-running LLM audit residual stages | Frozen audit CSVs preferred |

## Canonical manuscript paths

| Manuscript prose | Path |
|------------------|------|
| RQ2 failure audit | `exports/truth_decay_pilot/rq2_failure_audit_summary.md` |
| GFC confirmatory | `exports/truth_decay_pilot/gfc_confirmatory_summary.md` |
| Born-stale autopsy | `exports/truth_decay_pilot/born_stale_summary.md` |
| RQ5 uptake | `exports/rq5_agent_impact/rq5_uptake_analysis.md` |
| RQ5 A/B/C analysis | `exports/rq5_agent_impact/rq5_abc_comparative_analysis.md` |
| RQ5 A/B ledger | `exports/rq5_agent_impact/rq5_results.csv` |
| RQ5 C ledger | `exports/rq5_agent_impact_c/rq5_results.csv` |
| P4 validation | `exports/truth_pilot/p4_validation.md` |
| P4 gold worksheet | `exports/truth_pilot/agent_attribution_gold_worksheet.csv` |
| Freeze inventory | `docs/SCIENTIFIC_EVIDENCE_FREEZE.md` |
| Validation protocol | `docs/VALIDATION_EXTENSION_PROTOCOL.md` |
| RQ2 sensitivity | `validation/rq2_sensitivity/rq2_sensitivity_summary.md` |
| Concentration | `validation/concentration/concentration_summary.md` |
| Blinded RQ2 audit | `validation/rq2_second_audit/` (no public answer key) |

## License and citation

- License: [LICENSE](LICENSE) (MIT)
- Citation: [CITATION.cff](CITATION.cff)
- Authors: César Andrés (corresponding); David Martín-Moncunill
- Current archival DOI: [https://doi.org/10.5281/zenodo.21716211](https://doi.org/10.5281/zenodo.21716211) (version **1.1.0**)
- Prior freeze DOI: [https://doi.org/10.5281/zenodo.21711432](https://doi.org/10.5281/zenodo.21711432) (version **1.0.0**; keep intact)
- Concept DOI: [https://doi.org/10.5281/zenodo.21711431](https://doi.org/10.5281/zenodo.21711431)
- GitHub release: [v1.1.0](https://github.com/cesar-andress/artifact-lifecycle-lab/releases/tag/v1.1.0)
- Development repository: [https://github.com/cesar-andress/artifact-lifecycle-lab](https://github.com/cesar-andress/artifact-lifecycle-lab)

## Known limitations

1. L1b blob store (`data/blobs/`) is not shipped (size); full re-mine from registries requires re-extraction.
2. Prefer the Zenodo v1.1.0 deposit ([10.5281/zenodo.21716211](https://doi.org/10.5281/zenodo.21716211)) over a moving `main` clone when citing the full package; use v1.0.0 ([10.5281/zenodo.21711432](https://doi.org/10.5281/zenodo.21711432)) when citing the original primary freeze alone.
3. RQ5 success/uptake numbers are ledger-frozen; agent products and model versions may drift if rerun.
4. Development notes under `docs/` (gap analyses, storyline drafts) are not manuscript claims; use the freeze inventory.
5. Independent RQ2 human agreement is undefined until `rq2_second_auditor_labels.csv` exists; do not simulate labels.
