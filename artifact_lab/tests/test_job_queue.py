"""Job queue tests."""

import sqlite3

from artifact_lab.store.job_queue import DOCUMENTED_COLUMNS, JobQueue


def test_resume_skips_completed_unless_force(tmp_path):
    db = tmp_path / "jobs.db"
    with JobQueue(db) as q:
        q.upsert_pending("abc", "https://github.com/o/r", "ai_conventions_v1", "pilot_v1")
        q.mark_running("abc", "ai_conventions_v1", "pilot_v1")
        q.mark_completed("abc", "ai_conventions_v1", "pilot_v1", n_events=3)

        assert q.should_process("abc", "ai_conventions_v1", "pilot_v1", force=False) is False
        assert q.should_process("abc", "ai_conventions_v1", "pilot_v1", force=True) is True


def test_retry_failed_only_when_requested(tmp_path):
    db = tmp_path / "jobs.db"
    with JobQueue(db) as q:
        q.upsert_pending("abc", "https://github.com/o/r", "ai_conventions_v1", "pilot_v1")
        q.mark_running("abc", "ai_conventions_v1", "pilot_v1")
        q.mark_failed("abc", "ai_conventions_v1", "pilot_v1", reason="timeout")

        assert q.should_process("abc", "ai_conventions_v1", "pilot_v1", force=False, retry_failed=False) is False
        assert q.should_process("abc", "ai_conventions_v1", "pilot_v1", force=False, retry_failed=True) is True


def test_resume_skips_succeeded_unless_force(tmp_path):
    db = tmp_path / "jobs.db"
    with JobQueue(db) as q:
        q.upsert_pending("abc", "https://github.com/o/r", "ai_conventions_v1", "pilot_v1")
        q.mark_running("abc", "ai_conventions_v1", "pilot_v1")
        q.mark_succeeded("abc", "ai_conventions_v1", "pilot_v1", n_events=3)

        assert q.should_process("abc", "ai_conventions_v1", "pilot_v1", force=False) is False
        assert q.should_process("abc", "ai_conventions_v1", "pilot_v1", force=True) is True


def test_reset_stale_running(tmp_path):
    db = tmp_path / "jobs.db"
    with JobQueue(db) as q:
        q.upsert_pending("abc", "https://github.com/o/r", "ai_conventions_v1", "pilot_v1")
        q.mark_running("abc", "ai_conventions_v1", "pilot_v1")
        n = q.reset_stale_running()
        assert n == 1
        job = q.get("abc", "ai_conventions_v1", "pilot_v1")
        assert job is not None
        assert job.state == "pending"


def test_failure_reason_recorded(tmp_path):
    db = tmp_path / "jobs.db"
    with JobQueue(db) as q:
        q.upsert_pending("abc", "https://github.com/o/r", "ai_conventions_v1", "pilot_v1")
        q.mark_running("abc", "ai_conventions_v1", "pilot_v1")
        q.mark_failed("abc", "ai_conventions_v1", "pilot_v1", reason="clone_timeout")
        job = q.get("abc", "ai_conventions_v1", "pilot_v1")
        assert job is not None
        assert job.state == "failed"
        assert job.failure_reason == "clone_timeout"
        assert job.attempt_count == 1


def test_documented_columns_exist_and_are_queryable(tmp_path):
    db = tmp_path / "jobs.db"
    with JobQueue(db) as q:
        q.upsert_pending("abc", "https://github.com/o/r", "ai_conventions_v1", "pilot_v1")
        q.mark_running("abc", "ai_conventions_v1", "pilot_v1")
        q.mark_failed("abc", "ai_conventions_v1", "pilot_v1", reason="clone_timeout")

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    columns = {row[1] for row in conn.execute("PRAGMA table_info(extraction_jobs)").fetchall()}
    for name in DOCUMENTED_COLUMNS:
        assert name in columns

    row = conn.execute(
        """
        SELECT repo_id, repo_url, state, failure_reason, attempt_count, started_at, finished_at
        FROM extraction_jobs
        WHERE repo_id = ?
        """,
        ("abc",),
    ).fetchone()
    assert row["repo_id"] == "abc"
    assert row["repo_url"] == "https://github.com/o/r"
    assert row["state"] == "failed"
    assert row["failure_reason"] == "clone_timeout"
    assert row["attempt_count"] == 1
    assert row["started_at"] is not None
    assert row["finished_at"] is not None
    conn.close()


def test_migrates_legacy_status_column(tmp_path):
    db = tmp_path / "jobs.db"
    conn = sqlite3.connect(db)
    conn.executescript(
        """
        CREATE TABLE extraction_jobs (
            repo_id TEXT NOT NULL,
            repo_url TEXT NOT NULL,
            family TEXT NOT NULL,
            wave TEXT NOT NULL,
            status TEXT NOT NULL,
            failure_reason TEXT,
            attempt_count INTEGER NOT NULL DEFAULT 0,
            started_at TEXT,
            finished_at TEXT,
            n_events INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (repo_id, family, wave)
        );
        INSERT INTO extraction_jobs (
            repo_id, repo_url, family, wave, status, failure_reason,
            attempt_count, started_at, finished_at, n_events
        ) VALUES (
            'abc', 'https://github.com/o/r', 'ai_conventions_v1', 'pilot_v1',
            'pending', NULL, 0, NULL, NULL, 0
        );
        """
    )
    conn.commit()
    conn.close()

    with JobQueue(db) as q:
        job = q.get("abc", "ai_conventions_v1", "pilot_v1")
        assert job is not None
        assert job.state == "pending"

    conn = sqlite3.connect(db)
    columns = {row[1] for row in conn.execute("PRAGMA table_info(extraction_jobs)").fetchall()}
    assert "state" in columns
    assert "status" not in columns
    conn.close()
