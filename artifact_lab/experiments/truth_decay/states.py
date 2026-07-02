"""Deterministic reference state model for RQ1 longitudinal study."""

from __future__ import annotations

REFERENCE_STATES = (
    "VERIFIED",
    "MISSING",
    "UNVERIFIABLE",
    "REPAIRED",
    "DELETED",
)

BASE_VERIFY_TO_STATE = {
    "verified": "VERIFIED",
    "missing": "MISSING",
    "unverifiable": "UNVERIFIABLE",
}


def reference_key(reference_type: str, reference_text: str) -> tuple[str, str]:
    return (reference_type, reference_text)


def resolve_observation_state(
    *,
    verify_status: str,
    previous_state: str | None,
    file_deleted: bool,
) -> str:
    """Map verification outcome + history to observation state."""
    if file_deleted:
        return "DELETED"

    base = BASE_VERIFY_TO_STATE.get(verify_status, "UNVERIFIABLE")
    if previous_state == "MISSING" and base == "VERIFIED":
        return "REPAIRED"
    return base


def transition_label(previous_state: str | None, current_state: str) -> str:
    if not previous_state:
        return f"INIT->{current_state}"
    if previous_state == current_state:
        return f"{previous_state}->{current_state}"
    return f"{previous_state}->{current_state}"
