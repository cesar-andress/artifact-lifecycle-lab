"""Golden fixture: value-stable L1 and L2 outputs from synthetic repo."""

from __future__ import annotations

import json
from pathlib import Path

import pyarrow as pa

from artifact_lab.contracts.schemas import FILE_EVENT_LOG_COLUMNS, file_event_log_schema
from artifact_lab.derive.panel import build_panel_rows
from artifact_lab.ingest.extract import extract_repo_events
from artifact_lab.store.blobs import BlobStore
from artifact_lab.tests.golden_repo import build_golden_bare_repo


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _event_signature(event: dict) -> dict:
    return {
        "path": event["path"],
        "change_type": event["change_type"],
        "commit_time": event["commit_time"].isoformat(),
        "author_name": event["author_name"],
        "blob_sha_nonempty": bool(event["blob_sha"]),
    }


def test_golden_l1_and_l2_outputs(tmp_path):
    bare = build_golden_bare_repo(tmp_path)
    repo_url = "https://github.com/golden/fixture"
    repo_id = "golden_fixture_id"
    events = extract_repo_events(
        bare,
        repo_id=repo_id,
        repo_url=repo_url,
        family="ai_conventions_v1",
        extraction_wave="golden",
        detector_version="1.0.0",
        blob_store=BlobStore(tmp_path / "blobs"),
        git_timeout=60,
    )
    signatures = sorted([_event_signature(e) for e in events], key=lambda r: (r["path"], r["commit_time"]))
    expected_l1 = json.loads((FIXTURES / "golden_l1_expected.json").read_text(encoding="utf-8"))
    assert signatures == sorted(expected_l1, key=lambda r: (r["path"], r["commit_time"]))

    table = pa.Table.from_pylist(events, schema=file_event_log_schema())
    panel_rows = build_panel_rows(table, T=180)
    panel_sig = sorted(
        [
            {
                "path": row["path"],
                "panel_month": row["panel_month"].isoformat(),
                "state": row["state"],
            }
            for row in panel_rows
            if row["panel_month"].isoformat() <= "2024-03-01"
        ],
        key=lambda r: (r["path"], r["panel_month"]),
    )
    expected_l2 = json.loads((FIXTURES / "golden_l2_expected.json").read_text(encoding="utf-8"))
    assert panel_sig == sorted(expected_l2, key=lambda r: (r["path"], r["panel_month"]))
