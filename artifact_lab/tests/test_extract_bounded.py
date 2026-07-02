"""Bounded extraction and timeout tests."""

from __future__ import annotations

from unittest.mock import patch

from artifact_lab.ingest.extract import (
    ExtractConfig,
    normalize_failure_reason,
    run_extract,
)
from artifact_lab.ingest.profiling import ExtractionProfile, PhaseTimings, format_extraction_summary
from artifact_lab.store.job_queue import JobQueue


def test_normalize_failure_reason_timeout():
    assert normalize_failure_reason("RepoTimeoutError: exceeded 600s") == "timeout"
    assert normalize_failure_reason("timeout") == "timeout"
    assert normalize_failure_reason("clone failed") == "clone failed"


def test_limit_processes_only_first_n_registry_rows(tmp_path):
    registry = tmp_path / "registry.csv"
    registry.write_text(
        "repo_url\n"
        "https://github.com/example/a\n"
        "https://github.com/example/b\n"
        "https://github.com/example/c\n",
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
        limit=2,
        force=True,
    )

    def fake_extract(cfg, row, blob_store):
        return {
            "repo_id": row["repo_id"],
            "repo_url": row["normalized_repo_url"],
            "family": cfg.family,
            "extraction_wave": cfg.extraction_wave,
            "status": "no_matches",
            "events": [],
            "profile": ExtractionProfile(
                repo_id=row["repo_id"],
                repo_url=row["normalized_repo_url"],
                extraction_wave=cfg.extraction_wave,
                status="no_matches",
            ),
        }

    with patch("artifact_lab.ingest.extract.extract_one_repo", side_effect=fake_extract):
        run_extract(cfg)

    with JobQueue(cfg.queue_path) as q:
        jobs = q.list_jobs()
    assert len(jobs) == 2


def test_timeout_marks_failed_and_continues(tmp_path):
    registry = tmp_path / "registry.csv"
    registry.write_text(
        "repo_url\n"
        "https://github.com/example/slow\n"
        "https://github.com/example/fast\n",
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
        force=True,
        repo_timeout=1,
    )
    calls: list[str] = []

    def fake_extract(cfg, row, blob_store):
        calls.append(row["repo_url"])
        if len(calls) == 1:
            return {
                "repo_id": row["repo_id"],
                "repo_url": row["normalized_repo_url"],
                "family": cfg.family,
                "extraction_wave": cfg.extraction_wave,
                "status": "failed",
                "events": [],
                "error": "timeout",
                "profile": ExtractionProfile(
                    repo_id=row["repo_id"],
                    repo_url=row["normalized_repo_url"],
                    extraction_wave=cfg.extraction_wave,
                    status="failed",
                    timings=PhaseTimings(wall_s=120.0),
                ),
            }
        return {
            "repo_id": row["repo_id"],
            "repo_url": row["normalized_repo_url"],
            "family": cfg.family,
            "extraction_wave": cfg.extraction_wave,
            "status": "ok",
            "events": [],
            "profile": ExtractionProfile(
                repo_id=row["repo_id"],
                repo_url=row["normalized_repo_url"],
                extraction_wave=cfg.extraction_wave,
                status="ok",
            ),
        }

    with patch("artifact_lab.ingest.extract.extract_one_repo", side_effect=fake_extract):
        run_extract(cfg)

    assert len(calls) == 2
    with JobQueue(cfg.queue_path) as q:
        jobs = q.list_jobs()
    assert len(jobs) == 2
    assert sum(1 for j in jobs if j.failure_reason == "timeout") == 1
    assert sum(1 for j in jobs if j.state == "succeeded") == 1


def test_stale_running_becomes_pending(tmp_path):
    db = tmp_path / "jobs.db"
    with JobQueue(db) as q:
        q.upsert_pending("abc", "https://github.com/o/r", "ai_conventions_v1", "pilot_v1")
        q.mark_running("abc", "ai_conventions_v1", "pilot_v1")
        n = q.reset_stale_running()
        assert n == 1
        job = q.get("abc", "ai_conventions_v1", "pilot_v1")
        assert job is not None
        assert job.state == "pending"


def test_format_extraction_summary():
    profiles = [
        ExtractionProfile(
            repo_id="a",
            repo_url="https://github.com/o/a",
            extraction_wave="w",
            status="ok",
            timings=PhaseTimings(clone_s=1.0, inspection_s=5.0, wall_s=6.0),
        ),
        ExtractionProfile(
            repo_id="b",
            repo_url="https://github.com/o/b",
            extraction_wave="w",
            status="failed",
            timings=PhaseTimings(clone_s=2.0, history_s=3.0, wall_s=5.0),
        ),
    ]
    text = format_extraction_summary(
        queue_counts={"succeeded": 1, "failed": 1, "pending": 3},
        run_profiles=profiles,
        stale_recovered=1,
        registry_limit=3,
    )
    assert "completed .......... 1" in text
    assert "failed ............. 1" in text
    assert "pending ............ 3" in text
    assert "median total time" in text
    assert "slowest phase" in text
    assert "stale recovered" in text
