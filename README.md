# Artifact Lifecycle Lab

Research platform for mining **artifact lifecycles** in Git repositories. Git clones are **temporary transport**; the permanent dataset is **Parquet + content-addressed blobs + manifests**.

## Architecture spine

| Layer | Name | Output |
|-------|------|--------|
| L0 | Repository registry | `data/registry/*.csv` |
| L1 | File event log | `data/l1/file_event_log/` |
| L1b | Blob store | `data/blobs/` |
| L2 | Monthly file-state panel | `data/derived/file_state_panel/` |
| L3 | Ownership layer | (future) |
| L4 | Co-change coupling | (future) |
| L5 | Semantic drift / LLM | (future) |
| — | Experiments | isolated leaves under `platform/experiments/` |

```
platform/
  protocol/     YAML detector families
  ingest/       ephemeral clone → L1 + blobs
  contracts/    schema definitions
  store/        Parquet, blobs, manifests
  derive/       L2+ derivations
  label/        L3 annotations (stub)
  experiments/  research leaves (stub)
  paper/        paper exports (stub)
  dag/          pipeline graph (stub)
  tests/
  docs/
```

## Why clones are ephemeral

- Reproducibility comes from **registry + protocol + code**, not from keeping mirrors.
- Bare partial clones (`--bare --filter=blob:none`) minimize fetch size while preserving full history metadata.
- **No shallow clones.** Each repo is cloned to `scratch/`, extracted, then **deleted** (including on failure).
- Matched text blobs and event rows are the durable artifacts.

## Permanent vs regenerable

| Permanent | Regenerable |
|-----------|-------------|
| L1 Parquet (`data/l1/`) | `scratch/` clones |
| L1b blobs (`data/blobs/`) | extraction receipts (audit trail, optional) |
| L2+ derived Parquet | any layer re-built from upstream + code |
| manifests (`manifest.yaml`) | — |
| protocol YAML | — |
| registry CSV | — |

## Pilot workflow

```bash
cd ~/papers/artifact-lifecycle-lab/artifact-lifecycle-lab
/usr/bin/python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# L1: clone-extract-delete over pilot registry (16 public repos; ~30–60 min depending on network)
python3.12 -m platform.ingest extract \
  --registry data/registry/pilot_repos.csv \
  --family ai_conventions_v1

# L2: monthly file-state panel (T=180 days)
python3.12 -m platform.derive panel \
  --events data/l1/file_event_log \
  --T 180

# Tests
python3.12 -m pytest platform/tests
```

Query with DuckDB:

```bash
python -c "
import duckdb
print(duckdb.sql(\"SELECT repo_id, path, change_type, count(*) n
  FROM read_parquet('data/l1/file_event_log/events.parquet')
  GROUP BY 1,2,3 ORDER BY n DESC LIMIT 10\"))
"
```

## Legacy reference

The old project at `~/papers/legacy/ai-artifact-cochange/` is **reference only**. See [`platform/docs/legacy_map.md`](platform/docs/legacy_map.md) for what to reuse vs leave behind.

Do **not** copy its permanent clone layout, paper-oriented Makefile workflow, or PostgreSQL assumptions.

## Constraints

- No permanent git clones
- No shallow clones
- Experiments never write into core datasets
- All outputs reproducible from protocol + registry + code

## Note on the `platform` package name

The top-level package is intentionally named `platform` (per project layout). `platform/__init__.py` re-exports the **stdlib** `platform` API so dependencies like pytest and pyarrow keep working. Use **Python ≥ 3.11** (3.12 recommended).
