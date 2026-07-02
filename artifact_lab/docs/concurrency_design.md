# Concurrency design (not yet enabled for L1 extraction)

Measure-first policy: per-repository extraction remains **sequential** until
profiling shows where parallelism is safe and determinism tests pass.

## Two separate limits

| Pool | Default | Operations |
|------|---------|------------|
| **Network** | 2 (max 2) | `git clone`, `git fetch`, `git show` on filter=blob:none clones (lazy blob fetch) |
| **Local analysis** | `cpu_count - 2` (min 1) | Path matching, Parquet read/write, panel derivation, summaries |

Network and local pools are **independent semaphores**. Raising local concurrency
must not increase network concurrency.

## Profiling prerequisites

Before enabling any parallel git operations, each repository profile must record:

- `local_cpu_s` — Python CPU work (detector matching, blob store writes)
- `git_network_wait_s` — wall time in clone / lazy-fetch `git show`
- `git_local_wait_s` — wall time in log / ls-tree subprocesses (local pack reads)
- `n_git_subprocesses` — total git subprocess invocations
- `n_lazy_blob_fetches` — `git show` calls (proxy for blob materialization)
- `bytes_downloaded` — clone on-disk size + materialized blob bytes from `git show`

These fields live in `data/profiling/extraction_profile.parquet`.

## Determinism gate

Parallel per-repository extraction requires:

1. Identical L1 event rows (order-independent compare) on golden fixture
2. Bounded network concurrency never exceeding `MAX_NETWORK_CONCURRENCY`
3. No unbounded `ThreadPoolExecutor` over registry rows

Until those tests exist and pass, **do not parallelize extraction**.

## Constants

See `artifact_lab/contracts/concurrency.py`:

- `DEFAULT_NETWORK_CONCURRENCY = 2`
- `default_local_concurrency()` → `max(1, cpu_count - 2)`
- `MAX_NETWORK_CONCURRENCY = 2`
