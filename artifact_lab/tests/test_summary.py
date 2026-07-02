"""Summary command tests."""

import json

from artifact_lab.derive.summary import build_summary, format_summary
from artifact_lab.store.job_queue import JobQueue


def test_summary_counts(tmp_path):
    l1_dir = tmp_path / "l1" / "v1"
    l1_dir.mkdir(parents=True)
    # minimal parquet via pyarrow
    import pyarrow as pa
    import pyarrow.parquet as pq
    from datetime import datetime, timezone

    table = pa.table(
        {
            "repo_id": ["a", "a", "b"],
            "repo_url": ["u1", "u1", "u2"],
            "family": ["f", "f", "f"],
            "path": ["p1", "p2", "p1"],
            "commit_sha": ["c1", "c2", "c3"],
            "commit_time": [datetime(2024, 1, 1, tzinfo=timezone.utc)] * 3,
            "author_name": ["x"] * 3,
            "author_email_hash": ["h"] * 3,
            "change_type": ["add", "modify", "add"],
            "blob_sha": ["b1", "b2", ""],
            "extraction_wave": ["w"] * 3,
            "detector_version": ["1"] * 3,
        }
    )
    pq.write_table(table, l1_dir / "events.parquet")

    db = tmp_path / "jobs.db"
    with JobQueue(db) as q:
        q.upsert_pending("a", "u1", "f", "w")
        q.mark_running("a", "f", "w")
        q.mark_succeeded("a", "f", "w", n_events=2)
        q.upsert_pending("b", "u2", "f", "w")
        q.mark_running("b", "f", "w")
        q.mark_failed("b", "f", "w", reason="clone_fail")

    summary = build_summary(l1_path=l1_dir, queue_path=db)
    assert summary["l1_rows"] == 3
    assert summary["unique_paths"] == 2
    assert summary["unique_blobs"] == 2
    assert summary["repos_succeeded"] == 1
    assert summary["repos_failed"] == 1
    text = format_summary(summary)
    assert "repos succeeded" in text
