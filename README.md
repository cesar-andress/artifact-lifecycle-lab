# Artifact Lifecycle Lab

**Archival replication package (v1.0.0 on Zenodo; in-repo validation extension → v1.1.0)** for the ACM TOSEM manuscript  
*Measuring Mechanical Reference Integrity in Machine-Consumed Instruction Files*.

**Start here for reviewers and Zenodo users:** **[REPLICATION.md](REPLICATION.md)**

| Document | Purpose |
|----------|---------|
| [REPLICATION.md](REPLICATION.md) | Frozen vs regenerable outputs, Make targets, limitations |
| [docs/SCIENTIFIC_EVIDENCE_FREEZE.md](docs/SCIENTIFIC_EVIDENCE_FREEZE.md) | Authoritative claim inventory (freeze 2026-07-03) |
| [docs/VALIDATION_EXTENSION_PROTOCOL.md](docs/VALIDATION_EXTENSION_PROTOCOL.md) | Pre-submission robustness protocol |
| [docs/VALIDATION_EXTENSION_ADDENDUM.md](docs/VALIDATION_EXTENSION_ADDENDUM.md) | Relationship of validation layer to the freeze / v1.0.0 |
| [RELEASE_NOTES.md](RELEASE_NOTES.md) | v1.0.0 release notes |
| [RELEASE_NOTES_v1.1.0.md](RELEASE_NOTES_v1.1.0.md) | v1.1.0 validation-extension notes |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [CITATION.cff](CITATION.cff) | Citation metadata |
| [LICENSE](LICENSE) | MIT |

## Install

```bash
git clone https://github.com/cesar-andress/artifact-lifecycle-lab.git
cd artifact-lifecycle-lab
git checkout v1.1.0   # or v1.0.0 for the original archival snapshot

python3.12 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev,paper]"
python -m pytest artifact_lab/tests -q
make validation-qc
```

Requires **Python ≥ 3.11** (3.12 recommended).

## Repository structure

```
artifact_lab/     Installable package (ingest, derive, truth-decay experiments)
protocol/         Frozen measurement protocols
data/registry/    Cohort registry CSVs (pilot, E1-100, E1-1000)
exports/          Frozen scientific exports (authoritative for the manuscript)
validation/       Validation-extension artifacts (public; private keys gitignored)
docs/             Freeze inventory + validation protocol/addendum
```

Working directories created locally and **not** shipped in the archive:

- `scratch/` — ephemeral clones  
- `data/blobs/` — L1b blob store (re-extract if needed)  
- `data/state/`, `data/receipts/`, `data/profiling/` — job queue / audit trail  

## Scientific workflow (cohorts)

```
Pilot (17 repos) → Engineering E1-100 (98 extracted) → E1-1000 (specified, not executed)
```

| Stage | Registry | Role |
|-------|----------|------|
| Pilot | `data/registry/pilot_repos.csv` | Pipeline development |
| Engineering | `data/registry/e1_100_repos.csv` | Manuscript observational frame |
| Scientific | `data/registry/e1_1000_repos.csv` | Frozen design; **do not** run `make e1-1000` for this release |

## Observational Make targets (optional regeneration)

See [REPLICATION.md](REPLICATION.md) for the full list. Headline targets used in the manuscript:

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
**Do not** invent second-auditor labels; agreement scripts no-op until a real human CSV exists.

## Architecture spine (platform)

| Layer | Name | Output |
|-------|------|--------|
| L0 | Repository registry | `data/registry/*.csv` |
| L1 | File event log | `data/l1/...` (local / re-extractable) |
| L1b | Blob store | `data/blobs/` (not shipped) |
| L2+ | Derived panels | `data/derived/` (local) |
| Exports | Paper-facing tables | `exports/` (**shipped, frozen**) |

Git clones are temporary transport under `scratch/<repo_id>/` and are deleted after extraction.

```bash
python3.12 -m artifact_lab.ingest extract \
  --registry data/registry/pilot_repos.csv \
  --family ai_conventions_v1
```

## Development notes vs manuscript claims

Files such as `docs/LATE_BINDING_MODEL_*.md`, `docs/STORYLINE.md`, and review simulations are **development notes**.  
They are not manuscript contributions. Cite only paths listed in `docs/SCIENTIFIC_EVIDENCE_FREEZE.md`.

## License

MIT — see [LICENSE](LICENSE).
