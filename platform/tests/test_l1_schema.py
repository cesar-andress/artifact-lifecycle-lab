"""L1 schema validity."""

from datetime import datetime, timezone

import pyarrow as pa

from platform.contracts.schemas import FILE_EVENT_LOG_COLUMNS, file_event_log_schema, validate_columns


def test_l1_schema_columns():
    assert len(FILE_EVENT_LOG_COLUMNS) == 12
    row = {
        "repo_id": "r1",
        "repo_url": "https://github.com/o/r",
        "family": "ai_conventions_v1",
        "path": "AGENTS.md",
        "commit_sha": "abc",
        "commit_time": datetime(2024, 1, 1, tzinfo=timezone.utc),
        "author_name": "alice",
        "author_email_hash": "deadbeef",
        "change_type": "add",
        "blob_sha": "sha",
        "extraction_wave": "test",
        "detector_version": "1.0.0",
    }
    table = pa.Table.from_pylist([row], schema=file_event_log_schema())
    validate_columns(table, FILE_EVENT_LOG_COLUMNS)
