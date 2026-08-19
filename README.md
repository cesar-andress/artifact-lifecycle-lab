# Artifact Lifecycle Lab

Replication package **v1.2.0** for the Empirical Software Engineering (EMSE) manuscript  
*Measuring Reference Integrity in Coding-Agent Instruction Files: An Audited Longitudinal Study*.

**Authors:** César Andrés (corresponding); David Martín-Moncunill

| | |
|--|--|
| **Recommended package tag** | [`v1.2.0`](https://github.com/cesar-andress/artifact-lifecycle-lab/releases/tag/v1.2.0) |
| **Zenodo v1.2.0 DOI** | [10.5281/zenodo.22009399](https://doi.org/10.5281/zenodo.22009399) |
| **Prior package v1.1.0** | [10.5281/zenodo.21716211](https://doi.org/10.5281/zenodo.21716211) (historical) |
| **Prior freeze v1.0.0** | [10.5281/zenodo.21711432](https://doi.org/10.5281/zenodo.21711432) (historical) |
| **Concept DOI** | [10.5281/zenodo.21711431](https://doi.org/10.5281/zenodo.21711431) |

**Start here:** **[REPLICATION.md](REPLICATION.md)** · release notes: **[RELEASE_NOTES_v1.2.0.md](RELEASE_NOTES_v1.2.0.md)**

## What the study measures

Repository instruction files name paths, scripts, and dependencies. Detector-level
`Missing` labels mix never-resolved references, extraction artefacts, renames, and
breakage of previously verified paths. This package supports an audited longitudinal
measurement that keeps those denominators separate.

## What this package contains

| Need | Location |
|------|----------|
| How to reproduce / what is frozen | [REPLICATION.md](REPLICATION.md) |
| Claim inventory (authoritative) | [docs/SCIENTIFIC_EVIDENCE_FREEZE.md](docs/SCIENTIFIC_EVIDENCE_FREEZE.md) |
| Claim→evidence mapping | [exports/paper_synthesis/late_binding_evidence_table.csv](exports/paper_synthesis/late_binding_evidence_table.csv) |
| Human audit materials | [validation/rq2_second_audit/](validation/rq2_second_audit/) |
| Validation protocol | [docs/VALIDATION_EXTENSION_PROTOCOL.md](docs/VALIDATION_EXTENSION_PROTOCOL.md) |
| Observational exports | `exports/truth_decay_pilot/`, `exports/truth_pilot/` |
| Runtime-probe ledgers (exploratory) | `exports/rq5_agent_impact/`, `exports/rq5_agent_impact_c/` |
| Citation metadata | [CITATION.cff](CITATION.cff) |
| Version history | [CHANGELOG.md](CHANGELOG.md) |
| Historical release notes | [RELEASE_NOTES.md](RELEASE_NOTES.md) (v1.0.0), [RELEASE_NOTES_v1.1.0.md](RELEASE_NOTES_v1.1.0.md) |
| Development notes (not claims) | [docs/historical/README.md](docs/historical/README.md) |

Package version **1.2.0** aligns public metadata and documentation with the EMSE
manuscript. Frozen scientific evidence is unchanged relative to the archival freeze.

## Install

```bash
git clone https://github.com/cesar-andress/artifact-lifecycle-lab.git
cd artifact-lifecycle-lab
git checkout v1.2.0

python3.12 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev,paper]"
python -m pytest artifact_lab/tests -q
make validation-qc
```

Requires **Python ≥ 3.11** (3.12 recommended).

## Repository structure

```
artifact_lab/     Installable package (ingest, derive, experiments)
protocol/         Frozen measurement protocols
data/registry/    Cohort registry CSVs (pilot, E1-100, E1-1000)
exports/          Frozen scientific exports (authoritative for the manuscript)
validation/       Validation-extension artifacts (public; private keys gitignored)
docs/             Freeze inventory, validation protocol, historical notes
```

Working directories created locally and **not** required to verify frozen tables:

- `scratch/` — ephemeral clones  
- `data/blobs/` — L1b blob store (re-extract if needed)  
- `data/state/`, `data/receipts/`, `data/profiling/` — job queue / audit trail  

## Observational Make targets (optional regeneration)

See [REPLICATION.md](REPLICATION.md). Headline targets:

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

**Do not** use `exports/rq5_agent_impact/rq5_summary.md` for run counts (obsolete; 9 runs).  
**Do not** rerun `make truth-decay-rq5-run` to verify manuscript numbers (requires Claude Code; use frozen ledgers).

## License

MIT — see [LICENSE](LICENSE).
