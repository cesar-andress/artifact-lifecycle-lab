"""Repository checkpoint states for crash-safe extraction."""

from __future__ import annotations

PENDING = "pending"
CLONING = "cloning"
EXTRACTING = "extracting"
WRITING_L1 = "writing_l1"
VERIFYING = "verifying"
COMPLETED = "completed"
FAILED = "failed"

# Legacy aliases kept for migration and backward-compatible reads.
LEGACY_RUNNING = "running"
LEGACY_SUCCEEDED = "succeeded"

IN_PROGRESS_STATES: frozenset[str] = frozenset(
    {CLONING, EXTRACTING, WRITING_L1, VERIFYING, LEGACY_RUNNING}
)
TERMINAL_COMPLETED: frozenset[str] = frozenset({COMPLETED, LEGACY_SUCCEEDED})
TERMINAL_FAILED: frozenset[str] = frozenset({FAILED})

ALL_STATES: frozenset[str] = frozenset(
    {PENDING, CLONING, EXTRACTING, WRITING_L1, VERIFYING, COMPLETED, FAILED, LEGACY_RUNNING, LEGACY_SUCCEEDED}
)


def normalize_state(state: str) -> str:
    if state == LEGACY_SUCCEEDED:
        return COMPLETED
    return state


def is_in_progress(state: str) -> bool:
    return state in IN_PROGRESS_STATES


def is_completed(state: str) -> bool:
    return normalize_state(state) == COMPLETED


def is_failed(state: str) -> bool:
    return state == FAILED
