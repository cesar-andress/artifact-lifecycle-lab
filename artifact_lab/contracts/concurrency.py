"""Concurrency limit design — not enabled for extraction until profiling proves safety."""

from __future__ import annotations

import os

# Network-bound git operations: clone, fetch, git show (lazy blob fetch on filter=blob:none).
DEFAULT_NETWORK_CONCURRENCY = 2

# Local analysis: path matching, Parquet I/O, panel derivation, summaries.
def default_local_concurrency() -> int:
    cores = os.cpu_count() or 4
    return max(1, cores - 2)


MAX_NETWORK_CONCURRENCY = 2
"""Hard ceiling — never allow unlimited parallel git network operations."""
