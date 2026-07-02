"""Repository checkpoint states for crash-safe extraction."""

from __future__ import annotations

PENDING = "pending"
CLONING = "cloning"
EXTRACTING = "extracting"
WRITING = "writing"
VERIFYING = "verifying"
COMPLETED = "completed"
FAILED = "failed"

# Legacy aliases kept for migration and backward-compatible reads.
WRITING_L1 = WRITING
LEGACY_RUNNING = "running"
LEGACY_SUCCEEDED = "succeeded"
LEGACY_WRITING_L1 = "writing_l1"

IN_PROGRESS_STATES: frozenset[str] = frozenset(
    {CLONING, EXTRACTING, WRITING, VERIFYING, LEGACY_RUNNING, LEGACY_WRITING_L1}
)
TERMINAL_COMPLETED: frozenset[str] = frozenset({COMPLETED, LEGACY_SUCCEEDED})
TERMINAL_FAILED: frozenset[str] = frozenset({FAILED})

ALL_STATES: frozenset[str] = frozenset(
    {
        PENDING,
        CLONING,
        EXTRACTING,
        WRITING,
        VERIFYING,
        COMPLETED,
        FAILED,
        LEGACY_RUNNING,
        LEGACY_SUCCEEDED,
        LEGACY_WRITING_L1,
    }
)


def normalize_state(state: str) -> str:
    if state == LEGACY_SUCCEEDED:
        return COMPLETED
    if state == LEGACY_WRITING_L1:
        return WRITING
    return state


def is_in_progress(state: str) -> bool:
    return normalize_state(state) in {CLONING, EXTRACTING, WRITING, VERIFYING} or state in {
        LEGACY_RUNNING,
        LEGACY_WRITING_L1,
    }


def is_completed(state: str) -> bool:
    return normalize_state(state) == COMPLETED


def is_failed(state: str) -> bool:
    return state == FAILED
