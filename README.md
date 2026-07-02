# Artifact Lifecycle Lab

Research platform for mining **artifact lifecycles** in Git repositories. Git clones are **temporary transport**; the permanent dataset is **Parquet + content-addressed blobs + manifests**.

## Architecture spine

| Layer | Name | Output |
|-------|------|--------|
| L0 | Repository registry | `data/registry/*.csv` |
| L1 | File event log | `data/l1/file_event_log/v1/` |
| L1b | Blob store | `data/blobs/` |
| L2 | Monthly file-state panel | `data/derived/file_state_panel/v1/` |
| L3 | Ownership layer | (future) |
| L4 | Co-change coupling | (future) |
| L5 | Semantic drift / LLM | (future) |
| — | Experiments | isolated leaves under `artifact_lab/experiments/` |

Pipeline state (job queue) lives in `data/state/extraction_jobs.db` (SQLite WAL).

```
artifact_lab/
  protocol/     YAML detector families
  ingest/       ephemeral clone → L1 + blobs
  contracts/    schema definitions, repo_id, dataset versions
  store/        Parquet, blobs, manifests, job queue
  derive/       L2+ derivations, pilot summary
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
- **No shallow clones.** Each repo is cloned to `scratch/<repo_id>/`, extracted, then **deleted** (including on failure).
- Matched text blobs and event rows are the durable artifacts.

## Permanent vs regenerable

| Permanent | Regenerable |
|-----------|-------------|
| L1 Parquet (`data/l1/file_event_log/v1/`) | `scratch/` clones |
| L1b blobs (`data/blobs/`) | extraction receipts (audit trail) |
| L2+ derived Parquet (`data/derived/.../v1/`) | any layer re-built from upstream + code |
| manifests (`manifest.yaml`) | — |
| job queue (`data/state/extraction_jobs.db`) | reset/rebuild from registry + `--force` |
| protocol YAML | — |
| registry CSV | — |

## Pilot workflow

```bash
cd ~/papers/artifact-lifecycle-lab/artifact-lifecycle-lab
/usr/bin/python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# L1: clone-extract-delete over pilot registry
python3.12 -m artifact_lab.ingest extract \
  --registry data/registry/pilot_repos.csv \
  --family ai_conventions_v1

# L2: monthly file-state panel (T=180 days)
python3.12 -m artifact_lab.derive panel --T 180

# Pilot summary
python3.12 -m artifact_lab.derive summary

# Tests
python3.12 -m pytest artifact_lab/tests
```

## Resume workflow

Extraction uses a SQLite WAL job queue at `data/state/extraction_jobs.db`.

- Each repo is tracked as `pending`, `running`, `succeeded`, or `failed`.
- Re-run the same `extract` command after interruption: stale `running` jobs reset to `pending`.
- **Succeeded repos are skipped**; their L1 rows are preserved in `events.parquet`.
- Failed repos are retried on the next run.

```bash
python3.12 -m artifact_lab.ingest extract \
  --registry data/registry/pilot_repos.csv \
  --family ai_conventions_v1
```

## Force re-run workflow

Re-extract all repos (ignore succeeded queue state):

```bash
python3.12 -m artifact_lab.ingest extract \
  --registry data/registry/pilot_repos.csv \
  --family ai_conventions_v1 \
  --force
```

## Cleanup behavior

- `scratch/<repo_id>/` is **always** removed in a `finally` block after each repo.
- On per-repo timeout, the clone is removed before recording failure.
- Failure and skip **receipts** are always written to `data/receipts/<repo_id>.json`.
- Regenerable paths: `scratch/`, receipts (audit only).

## Extraction limits

| Flag | Default | Purpose |
|------|---------|---------|
| `--clone-timeout` | 300s | `git clone` wall-clock limit |
| `--repo-timeout` | 600s | total per-repo extraction limit |
| `--max-clone-mb` | 500 | skip extraction when bare clone exceeds size |

Registry CSV columns for pre-filtering (no clone attempted):

- `archived=true` — skip archived repos
- `skip_reason=<text>` — manual skip with reason
- `too_large=true` — skip repos known to be oversized

## Repository identifiers

`repo_id` is a deterministic 16-char SHA-256 prefix of the normalized URL. The registry stores only `repo_url`. See [`artifact_lab/docs/repo_id.md`](artifact_lab/docs/repo_id.md).

## Dataset versioning

Core datasets are versioned by directory:

- L1: `data/l1/file_event_log/v1/events.parquet`
- L2: `data/derived/file_state_panel/v1/panel_T180.parquet`

Manifests include `dataset_version`, `code_git_sha`, `protocol_version`, and `schema_hash`.

Query with DuckDB:

```bash
python3.12 -c "
import duckdb
print(duckdb.sql(\"\"\"
  SELECT repo_id, path, change_type, count(*) AS n
  FROM read_parquet('data/l1/file_event_log/v1/events.parquet')
  GROUP BY 1,2,3 ORDER BY n DESC LIMIT 10
\"\"\").df())
"
```

## Known limitations

- GitHub-centric URL normalization; other hosts use generic rules.
- No live GitHub API metadata fetch (archived/too-large via registry columns only).
- Per-repo timeout uses in-process threading (no subprocess kill of hung git).
- Blob store uses plain `.txt` files (no compression yet).
- Job queue is single-machine SQLite, not a distributed scheduler.
- L1 merge on resume replaces rows only for repos processed in the current run.

## Legacy reference

The old project at `~/papers/legacy/ai-artifact-cochange/` is **reference only**. See [`artifact_lab/docs/legacy_map.md`](artifact_lab/docs/legacy_map.md).

## Constraints

- No permanent git clones
- No shallow clones
- Experiments never write into core datasets
- All outputs reproducible from protocol + registry + code

Use **Python ≥ 3.11** (3.12 recommended). The installable package is `artifact_lab` (no conflict with the stdlib `platform` module).
