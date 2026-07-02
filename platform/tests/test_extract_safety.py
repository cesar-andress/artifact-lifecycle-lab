"""Registry skip and receipt tests."""

from platform.ingest.extract import ExtractConfig, registry_skip_reason, run_extract


def test_registry_skip_archived():
    assert registry_skip_reason({"archived": "true"}) == "archived"
    assert registry_skip_reason({"skip_reason": "manual"}) == "skip:manual"


def test_skipped_repo_writes_receipt_and_marks_failed(tmp_path):
    registry = tmp_path / "registry.csv"
    registry.write_text(
        "repo_url,archived\nhttps://github.com/example/archived,true\n",
        encoding="utf-8",
    )
    cfg = ExtractConfig(
        registry_path=registry,
        family="ai_conventions_v1",
        scratch_dir=tmp_path / "scratch",
        events_dir=tmp_path / "l1" / "v1",
        blobs_dir=tmp_path / "blobs",
        receipts_dir=tmp_path / "receipts",
        queue_path=tmp_path / "jobs.db",
    )
    run_extract(cfg)
    receipts = list(cfg.receipts_dir.glob("*.json"))
    assert len(receipts) == 1
    from platform.store.job_queue import JobQueue

    with JobQueue(cfg.queue_path) as q:
        jobs = q.list_jobs()
        assert len(jobs) == 1
        assert jobs[0].status == "failed"
        assert jobs[0].failure_reason == "archived"
