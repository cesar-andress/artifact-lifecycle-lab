"""Dataset contracts and schema definitions."""

from __future__ import annotations

import hashlib
from typing import Literal

import pyarrow as pa

ChangeType = Literal["add", "modify", "delete"]
PanelState = Literal["absent", "young", "active", "stale", "deleted"]

FILE_EVENT_LOG_COLUMNS: tuple[str, ...] = (
    "repo_id",
    "repo_url",
    "family",
    "path",
    "commit_sha",
    "commit_time",
    "author_name",
    "author_email_hash",
    "change_type",
    "blob_sha",
    "extraction_wave",
    "detector_version",
)

FILE_STATE_PANEL_COLUMNS: tuple[str, ...] = (
    "repo_id",
    "repo_url",
    "family",
    "path",
    "panel_month",
    "state",
    "T_days",
    "introduced_at",
    "last_touch_at",
    "days_since_last_touch",
    "detector_version",
)


def file_event_log_schema() -> pa.Schema:
    return pa.schema(
        [
            ("repo_id", pa.string()),
            ("repo_url", pa.string()),
            ("family", pa.string()),
            ("path", pa.string()),
            ("commit_sha", pa.string()),
            ("commit_time", pa.timestamp("us", tz="UTC")),
            ("author_name", pa.string()),
            ("author_email_hash", pa.string()),
            ("change_type", pa.string()),
            ("blob_sha", pa.string()),
            ("extraction_wave", pa.string()),
            ("detector_version", pa.string()),
        ]
    )


def file_state_panel_schema() -> pa.Schema:
    return pa.schema(
        [
            ("repo_id", pa.string()),
            ("repo_url", pa.string()),
            ("family", pa.string()),
            ("path", pa.string()),
            ("panel_month", pa.date32()),
            ("state", pa.string()),
            ("T_days", pa.int32()),
            ("introduced_at", pa.timestamp("us", tz="UTC")),
            ("last_touch_at", pa.timestamp("us", tz="UTC")),
            ("days_since_last_touch", pa.int32()),
            ("detector_version", pa.string()),
        ]
    )


def schema_hash(columns: tuple[str, ...]) -> str:
    digest = hashlib.sha256("|".join(columns).encode("utf-8")).hexdigest()
    return digest[:16]


def validate_columns(table: pa.Table, expected: tuple[str, ...]) -> None:
    actual = tuple(table.schema.names)
    if actual != expected:
        raise ValueError(f"schema mismatch: expected {expected}, got {actual}")


def hash_email(email: str) -> str:
    normalized = email.strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]
