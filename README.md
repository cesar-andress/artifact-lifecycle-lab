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

Pipeline state (job queue) lives at `data/state/extraction_jobs.db` (SQLite WAL).
The canonical path is defined in `artifact_lab/contracts/paths.py` as `EXTRACTION_QUEUE_PATH`.
Do not use alternate filenames such as `extraction_jobs.sqlite`.

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

## Scientific workflow

Research proceeds through **staged cohorts**, each with a distinct epistemic role. Do not skip stages or merge export directories.

```
Pilot (17 repos)
       ↓  pipeline development, profiling, inspection-mode validation
Engineering cohort (100 repos)
       ↓  end-to-end regression, accounting QA, first census
Scientific cohort (1,000 repos)     ← E1-1000 (frozen, not yet executed)
       ↓  TOSEM default; stratified prevalence + OSS contrast
Future longitudinal studies         ← separate protocols (E2+); not implemented
```

| Stage | Registry | Role | Inference |
|-------|----------|------|-----------|
| **Pilot** | `pilot_repos.csv` (17) | Detector smoke tests, timeout profiling, bounded `make e1-pilot` | None — qualitative evidence only |
| **Engineering** | `e1_100_repos.csv` (100) | Pipeline regression, latest-per-repo QA, E1-100 census | Limited — enriched engineering frame |
| **Scientific** | `e1_1000_repos.csv` (1000) | TOSEM primary cohort; three-stratum design | Frame-conditional RQ1 + OSS contrast |
| **Longitudinal** | (future) | Lifecycle, drift, ownership, coupling | Requires new protocol per estimand |

**E1-1000 status:** Protocol frozen. See `protocol/E1_1000_protocol_v1.md`, `protocol/pre_execution_checklist.md`, and `protocol/experiment_manifest.yaml`. Do **not** run `make e1-1000` until the checklist is complete.

## Cohort ladder

E1 experiments use a staged cohort progression. See [docs/cohort_ladder.md](docs/cohort_ladder.md) for Makefile targets and export paths:

- **Pilot (17)** — development and profiling
- **Engineering (100)** — pipeline regression (`make e1-100`)
- **Scientific (1000)** — TOSEM default cohort (`make e1-1000`, frozen pre-execution)
- **Future population-scale** — not implemented

See also [docs/dataset_lineage.md](docs/dataset_lineage.md) for the full L0→paper dependency chain.

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

## Scientific pilot (E1)

```bash
pip install -e ".[dev,paper]"

# Bounded development run (3 repos, 120s timeouts, partial exports)
make e1-pilot

# Full pilot registry (resume-friendly; do not use --force casually)
make e1

# Copy exports to paper repo and compile LaTeX (no mining)
make paper
```

| Target | Scope |
|--------|-------|
| `make e1-pilot` | First 3 registry repos, `--skip-slow`; all artifact outputs under `exports/e1/` only |
| `make e1` | Full registry extract (resume) → panel → census → `exports/e1/` (including `pilot_performance.md`) |
| `make paper` | Create `../paper/figures`, `../paper/tables`, `../paper/notes`; copy E1 exports from `exports/e1/`; attempt LaTeX compile (skips gracefully if `main.tex` is missing or compile fails) |

Artifact targets never write directly into `../paper/`. The paper repo is updated only via `make paper`.

Use **`make e1-pilot` for development**. Use **`make e1` only for the full pilot**. Avoid `--force` unless you intentionally want to re-extract succeeded repositories.

### E1 100-repository cohort

```bash
make e1-100
```

| Target | Scope |
|--------|-------|
| `make e1-100` | Full 100-repo registry (`data/registry/e1_100_repos.csv`), head-only inspection, exports under `exports/e1_100/` |

Rebuild the registry CSV (requires VSDLC eligible JSONL):

```bash
python -m artifact_lab.registry.build_e1_100
```

Pilot outputs in `exports/e1/` are never overwritten by `make e1-100`.

The pilot performance report (`exports/e1/pilot_performance.md`) includes only repositories listed in `data/registry/pilot_repos.csv`. Synthetic fixture repos from tests (e.g. `example/slow`) are excluded unless `--test-mode` is passed explicitly to the report CLI.

### Bounded extraction flags

```bash
python3.12 -m artifact_lab.ingest extract \
  --registry data/registry/pilot_repos.csv \
  --family ai_conventions_v1 \
  --limit 3 \
  --skip-slow
```

- `--limit N` — process only the first *N* rows of the registry CSV.
- `--skip-slow` — cap clone and repo timeouts at 120 s; repos exceeding `--repo-timeout` are marked `failed` with reason `timeout:<phase>` and the run continues.
- `--repo-timeout SECS` — per-repo wall-clock limit (default 600; use with `--skip-slow` for bounded runs).
- `--inspection-mode head-only|full-history` — how candidate paths are discovered (default: `head-only`).

### Inspection modes

| Mode | Git command | Use case |
|------|-------------|----------|
| `head-only` (default) | `git ls-tree -r HEAD` | E1 adoption census — current file presence |
| `full-history` | `git log --all --name-only` + HEAD | Exact lifecycle studies — paths ever touched |

`head-only` is suitable for current-presence / adoption census questions. Use `full-history` when you need deleted or historical paths that are no longer at HEAD. `make e1` and `make e1-pilot` pass `--inspection-mode head-only` by default.

After each extract run, a summary is printed: completed / failed / pending counts, median total time, and slowest aggregate phase.

### Stale-running recovery

At the start of every extract run, jobs left as `running` from an interrupted process are reset to **`pending`** (not failed). They are retried on the next run unless already `succeeded` and `--force` is not set. The number recovered is printed when non-zero.

### Concurrency (design only)

Per-repository extraction remains **sequential**. Planned limits (not yet enabled):

- **Network concurrency:** default 2 (clone, fetch, lazy `git show`)
- **Local analysis concurrency:** `cpu_count - 2` (matching, Parquet, panel)

See [`artifact_lab/docs/concurrency_design.md`](artifact_lab/docs/concurrency_design.md).

Profiling now records `local_cpu_s`, `git_network_wait_s`, `git_local_wait_s`, `n_git_subprocesses`, `n_lazy_blob_fetches`, and `bytes_downloaded` per repository.

## Extraction profiling

Each processed repository records phase timings:

`clone`, `inspection`, `history`, `detector`, `blobs`, `parquet_write`, `manifest_write`, `cleanup`, `total`, `inspection_mode`

Profiles: `data/profiling/extraction_profile.parquet` and `.csv`.

Progress log example:

```text
[3/16]

Repository:
astral-sh/ruff

clone ............ 8.3 s
history .......... 4.8 s
detectors ........ 0.2 s
blobs ............ 1.1 s
write ............ 0.3 s
cleanup .......... 0.1 s

TOTAL ............ 14.8 s
```

Repositories exceeding **300 s** emit `WARNING: Slow repository` with the slowest phase.

## Resume workflow

Extraction uses a SQLite WAL job queue at `data/state/extraction_jobs.db`.

Documented columns on `extraction_jobs`:

| Column | Description |
|--------|-------------|
| `repo_id` | Deterministic repository identifier |
| `repo_url` | Normalized clone URL |
| `state` | `pending`, `running`, `succeeded`, or `failed` |
| `failure_reason` | Last failure/skip reason (nullable) |
| `attempt_count` | Extraction attempts in this wave |
| `started_at` | ISO-8601 UTC start of current/last attempt |
| `finished_at` | ISO-8601 UTC completion of last attempt |

Inspect queue state:

```bash
sqlite3 data/state/extraction_jobs.db "
  SELECT repo_id, repo_url, state, failure_reason, attempt_count, started_at, finished_at
  FROM extraction_jobs
  ORDER BY started_at;
"
```

- Each repo is tracked as `pending`, `running`, `succeeded`, or `failed`.
- The extract CLI prints one profiling block per processed repository and warns when total time exceeds 5 minutes.
- Profile rows are written to `data/profiling/extraction_profile.parquet`.
- Re-run the same `extract` command after interruption: stale `running` jobs reset to `pending` (see **Stale-running recovery** above).
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
