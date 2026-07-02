# Crash-safe execution for E1-1000

This document describes the reliability guarantees for long-running cohort extraction.

## Scientific guarantee

**E1-1000 execution is crash-safe.**

- Each repository is an independent transaction with explicit checkpoint states.
- **Completed repositories are immutable** — a repo in `completed` state is never reprocessed unless `--force` is passed.
- **Recovered executions produce identical datasets** — global `events.parquet` is rebuilt deterministically from per-repo L1 artifacts for all `completed` jobs.

## Checkpoint states

Each repository progresses through:

```
PENDING → CLONING → EXTRACTING → WRITING_L1 → VERIFYING → COMPLETED
                                                      ↘ FAILED
```

Transitions are recorded in the append-only `execution.log` under the L1 events directory.

## Atomic writes

All durable artifacts use **tmp → verify → atomic rename**:

| Artifact | Path |
|----------|------|
| Per-repo L1 | `data/l1/e1_1000/v1/repos/{repo_id}.parquet` |
| Per-repo manifest | `data/l1/e1_1000/v1/repos/{repo_id}.manifest.yaml` |
| Global L1 | `data/l1/e1_1000/v1/events.parquet` |
| Global manifest | `data/l1/e1_1000/v1/manifest.yaml` |
| Receipt | `data/receipts/{repo_id}.json` |
| Blob store | `data/blobs/{prefix}/{sha}.txt` |

## Resume semantics

Running `make e1-1000` after interruption:

| State | Behavior |
|-------|----------|
| `completed` | **Skipped** — never repeat successful work |
| `failed` | **Skipped** unless `--retry-failed` |
| `pending` | **Resumed** automatically |
| In-progress (`cloning`, `extracting`, `writing_l1`, `verifying`, legacy `running`) | **Reset to `pending`** on startup |

## Verification before COMPLETED

A repository is marked `completed` only when:

1. Receipt exists (no `.tmp` sibling)
2. Per-repo manifest exists
3. Per-repo L1 parquet exists and is readable
4. Row count matches receipt `n_events`
5. All blob references resolve in the blob store
6. No temporary files remain for that repo

Otherwise the job reverts to `failed`.

## Scratch workspace

Clone directories under `scratch/{repo_id}/` are **disposable**. On every extraction run and during `make recover`, all scratch directories are removed. Never trust scratch contents after restart.

## Write-ahead execution log

Append-only log at `data/l1/e1_1000/v1/execution.log`:

```json
{"timestamp": "...", "repo_id": "...", "old_state": "...", "new_state": "...", "reason": "...", "duration_s": 1.23}
```

## Recovery and integrity commands

```bash
make recover   # repair stale jobs, remove orphan scratch/tmp, verify receipts, rebuild global L1
make verify    # diagnostics only — registry, queue, receipts, manifests, parquet, blobs
```

`recover` never recomputes completed per-repo extraction — it only repairs metadata and rebuilds the global merge.

## Recoverable crash scenarios

| Scenario | Recovery |
|----------|----------|
| Ctrl+C during clone | In-progress → pending; scratch cleaned; resume skips completed |
| Ctrl+C during blob extraction | Same |
| Crash during Parquet write | Incomplete `.tmp` removed by recover; repo stays failed/pending |
| Crash before manifest | Verification fails; repo reverted to failed |
| Crash before receipt | Verification fails; repo reverted to failed |
| Power loss before cleanup | Scratch removed on restart; in-progress → pending |
| SIGTERM mid-run | Same as Ctrl+C |
| OOM kill | Same as power loss |
| Machine reboot | Stale in-progress reset; `make e1-1000` continues |

## Idempotency

Re-running extraction on an already-completed cohort produces **no change** to completed per-repo artifacts or global L1 (unless `--force`).
