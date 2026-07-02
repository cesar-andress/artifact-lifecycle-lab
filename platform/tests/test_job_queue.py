"""Job queue tests."""

from platform.store.job_queue import JobQueue


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
        assert job.status == "pending"


def test_failure_reason_recorded(tmp_path):
    db = tmp_path / "jobs.db"
    with JobQueue(db) as q:
        q.upsert_pending("abc", "https://github.com/o/r", "ai_conventions_v1", "pilot_v1")
        q.mark_running("abc", "ai_conventions_v1", "pilot_v1")
        q.mark_failed("abc", "ai_conventions_v1", "pilot_v1", reason="clone_timeout")
        job = q.get("abc", "ai_conventions_v1", "pilot_v1")
        assert job is not None
        assert job.status == "failed"
        assert job.failure_reason == "clone_timeout"
        assert job.attempt_count == 1
