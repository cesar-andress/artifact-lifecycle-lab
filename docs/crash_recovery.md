# Crash recovery for E1-1000 extraction

This document describes how the artifact-lifecycle-lab pipeline survives interruptions without recomputing successful repositories.

## Transaction model

Each repository is an **independent transaction** with explicit checkpoint states stored in SQLite (`data/state/extraction_jobs.db`):

```
PENDING → CLONING → EXTRACTING → WRITING → VERIFYING → COMPLETED
                                                   ↘ FAILED
```

Properties:

- State transitions are **atomic** (single SQLite UPDATE per transition).
- Intermediate states are **never skipped** in the happy path.
- A repository enters **COMPLETED** only after verification passes (see below).

## Atomic writes

Final files are never written in place. The pattern is:

```
artifact.tmp → fsync → verify → atomic rename → artifact
```

Applied to:

| Artifact | Location |
|----------|----------|
| Per-repo L1 | `data/l1/e1_1000/v1/repos/{repo_id}.parquet` |
| Global L1 | `data/l1/e1_1000/v1/events.parquet` |
| L2 panel | `data/derived/file_state_panel/e1_1000/v1/panel_T180.parquet` |
| Manifests | `*.manifest.yaml`, `manifest.yaml` |
| Receipts | `data/receipts/{repo_id}.json` |
| Blobs | `data/blobs/{prefix}/{sha}.txt` |
| Exports | `exports/e1_1000/fig1.csv`, `fig1.pdf`, `table1.csv`, reports |

Partially-written outputs must not appear as final paths (only `.tmp` siblings may exist transiently).

## Resume semantics

After any interruption, running:

```bash
make e1-1000
```

behaves as follows:

| Queue state | Action |
|-------------|--------|
| `completed` | **Skip** — never recompute |
| `pending` | **Process** |
| In-progress (`cloning`, `extracting`, `writing`, `verifying`, legacy `running`) | **Reset to `pending`** on startup |
| `failed` | **Skip** unless `--retry-failed` is passed to extract |

Completed repositories are **immutable** unless `--force` is used.

## Verification before COMPLETED

A repository is marked `completed` only when all checks pass:

- Receipt exists (no `.tmp` sibling)
- Per-repo manifest exists
- Per-repo L1 parquet exists and row count matches receipt
- All blob references resolve in the blob store
- No temporary files remain for that repository

Otherwise the job is marked **FAILED** and may be retried with `--retry-failed`.

## Scratch recovery

Directories under `scratch/{repo_id}/` are **disposable**. At extraction startup and during `make recover`:

1. Abandoned scratch directories are detected
2. All scratch content is removed
3. Scratch is never used to resume partial git state

## Write-ahead execution log

Append-only log at **`data/state/execution.log`**.

Each line is a JSON record:

```json
{
  "timestamp": "2026-07-02T12:00:00+00:00",
  "repo_id": "...",
  "old_state": "extracting",
  "new_state": "writing",
  "reason": "extraction complete",
  "duration_s": 12.345
}
```

The log is append-only: no edits, no rewrites.

## Recovery and integrity commands

```bash
make recover   # repair stale jobs, clean scratch/tmp, verify receipts, list incomplete repos, rebuild global L1
make verify    # read-only consistency report (no repairs)
```

`make recover` **never recomputes** extraction for valid `completed` repositories — it only repairs metadata and rebuilds the global merge from per-repo L1 artifacts.

## Dataset manifest fields

Every L1 dataset manifest includes:

| Field | Description |
|-------|-------------|
| `registry_version` | Registry version label |
| `registry_hash` | SHA-256 of registry CSV |
| `wave_id` | Extraction wave (e.g. `e1_1000_v1`) |
| `protocol_version` | Protocol family version |
| `detector_version` | Detector pattern version |
| `git_commit` | Git SHA at manifest write |
| `python_version` | Python interpreter version |
| `execution_start` | First activity timestamp for wave |
| `execution_finish` | Last manifest write timestamp |
| `completed_repositories` | Count of completed jobs |
| `failed_repositories` | Count of failed jobs |

Session timestamps persist in `data/state/extraction_session.json` across interrupted runs.

## Scientific guarantee

1. **Repeated executions after interruption produce identical datasets** — global L1 is rebuilt deterministically from verified per-repo artifacts sorted by `repo_id`.
2. **Successful repositories are immutable** — `completed` jobs are skipped on resume.
3. **Recovery never recomputes valid completed work** — `make recover` only reconciles queue/receipt/manifest consistency and rebuilds the merge.

## Known limitations

| Limitation | Mitigation |
|------------|------------|
| `kill -9` / OOM cannot run cleanup handlers | Stale in-progress jobs reset to `pending` on next startup |
| Derive/exports stages are not per-repo transactional | Re-run `make e1-1000-derive` / exports after L1 completes; L1 crash-safety is the critical path |
| Git subprocess may survive parent kill | Scratch wiped on restart; job retried from clone |
| Global L1 rebuilt after each repo completion | Correctness over speed (no performance optimization in this milestone) |
| `--force` reprocesses completed repos | Intentional escape hatch; not used in normal E1-1000 runs |

## Related documentation

- Protocol freeze: `protocol/E1_1000_protocol_v1.md`
- Implementation notes: `docs/crash_safe_execution.md` (earlier milestone draft; superseded by this document for operational guidance)
