"""Fault injection tests for crash-safe extraction."""

from __future__ import annotations

import json
from pathlib import Path

from artifact_lab.contracts.repo_id import repo_id_from_url

from unittest.mock import patch
import pyarrow.parquet as pq
import pytest

from artifact_lab.execution.recover import run_recover
from artifact_lab.execution.states import COMPLETED, FAILED, PENDING, WRITING_L1
from artifact_lab.execution.verify import verify_repo_completion
from artifact_lab.ingest import extract as extract_module
from artifact_lab.ingest.extract import ExtractConfig, run_extract
from artifact_lab.ingest.profiling import ExtractionProfile
from artifact_lab.store.blobs import BlobStore
from artifact_lab.store.job_queue import JobQueue


def _registry(tmp_path, n: int = 1) -> Path:
    lines = ["repo_url"] + [f"https://github.com/example/repo{i}" for i in range(n)]
    path = tmp_path / "registry.csv"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _cfg(tmp_path, registry_path: Path, **kwargs) -> ExtractConfig:
    defaults = dict(
        registry_path=registry_path,
        family="ai_conventions_v1",
        scratch_dir=tmp_path / "scratch",
        events_dir=tmp_path / "l1" / "v1",
        blobs_dir=tmp_path / "blobs",
        receipts_dir=tmp_path / "receipts",
        queue_path=tmp_path / "jobs.db",
        extraction_wave="test_wave",
        force=True,
    )
    defaults.update(kwargs)
    return ExtractConfig(**defaults)


def _repo_id(n: int = 0) -> str:
    return repo_id_from_url(f"https://github.com/example/repo{n}")


def _ok_receipt(row, events=None):
    events = events or []
    return {
        "repo_id": row["repo_id"],
        "repo_url": row["normalized_repo_url"],
        "family": "ai_conventions_v1",
        "extraction_wave": "test_wave",
        "status": "ok" if events else "no_matches",
        "n_events": len(events),
        "matched_paths": sorted({e["path"] for e in events}),
        "events": events,
        "profile": ExtractionProfile(
            repo_id=row["repo_id"],
            repo_url=row["normalized_repo_url"],
            extraction_wave="test_wave",
            status="ok" if events else "no_matches",
            n_events=len(events),
        ),
    }


def test_completed_skipped_on_resume(tmp_path):
    registry = _registry(tmp_path, 2)
    cfg = _cfg(tmp_path, registry)
    calls: list[str] = []

    def fake_extract(cfg, row, blob_store, checkpoint=None):
        calls.append(row["repo_id"])
        return _ok_receipt(row)

    with patch.object(extract_module, "extract_one_repo", side_effect=fake_extract):
        run_extract(cfg)

    assert len(calls) == 2
    calls.clear()

    cfg2 = ExtractConfig(**{**cfg.__dict__, "force": False})
    with patch.object(extract_module, "extract_one_repo", side_effect=fake_extract):
        run_extract(cfg2)

    assert calls == []


def test_failed_skipped_without_retry_failed(tmp_path):
    repo0 = _repo_id(0)
    registry = _registry(tmp_path, 1)
    cfg = _cfg(tmp_path, registry)

    def fake_fail(cfg, row, blob_store, checkpoint=None):
        return {
            "repo_id": row["repo_id"],
            "repo_url": row["normalized_repo_url"],
            "family": cfg.family,
            "extraction_wave": cfg.extraction_wave,
            "status": "failed",
            "n_events": 0,
            "events": [],
            "error": "simulated",
            "profile": ExtractionProfile(
                repo_id=row["repo_id"],
                repo_url=row["normalized_repo_url"],
                extraction_wave=cfg.extraction_wave,
                status="failed",
                failure_reason="simulated",
            ),
        }

    with patch.object(extract_module, "extract_one_repo", side_effect=fake_fail):
        run_extract(cfg)

    with JobQueue(cfg.queue_path) as q:
        assert q.get(repo0, cfg.family, cfg.extraction_wave).state == FAILED

    calls: list[str] = []

    def track(cfg, row, blob_store, checkpoint=None):
        calls.append(row["repo_id"])
        return fake_fail(cfg, row, blob_store, checkpoint)

    cfg2 = ExtractConfig(**{**cfg.__dict__, "force": False})
    with patch.object(extract_module, "extract_one_repo", side_effect=track):
        run_extract(cfg2)
    assert calls == []

    cfg3 = ExtractConfig(**{**cfg.__dict__, "force": False, "retry_failed": True})
    with patch.object(extract_module, "extract_one_repo", side_effect=track):
        run_extract(cfg3)
    assert len(calls) == 1


def test_stale_in_progress_reset_to_pending(tmp_path):
    db = tmp_path / "jobs.db"
    with JobQueue(db) as q:
        q.upsert_pending("abc", "https://github.com/o/r", "ai_conventions_v1", "pilot_v1")
        q.mark_state("abc", "ai_conventions_v1", "pilot_v1", "extracting", increment_attempt=True)
        n = q.reset_stale_in_progress()
        assert n == 1
        job = q.get("abc", "ai_conventions_v1", "pilot_v1")
        assert job.state == PENDING


def test_fault_injection_crash_during_parquet_write(tmp_path):
    repo0 = _repo_id(0)
    registry = _registry(tmp_path, 1)
    cfg = _cfg(tmp_path, registry)

    def fake_extract(cfg, row, blob_store, checkpoint=None):
        return _ok_receipt(row)

    def crash_on_parquet(phase: str) -> None:
        if phase == "parquet":
            raise KeyboardInterrupt("simulated Ctrl+C during parquet write")

    extract_module.FAULT_INJECTION_HOOK = crash_on_parquet
    try:
        with patch.object(extract_module, "extract_one_repo", side_effect=fake_extract):
            with pytest.raises(KeyboardInterrupt):
                run_extract(cfg)
    finally:
        extract_module.FAULT_INJECTION_HOOK = None

    with JobQueue(cfg.queue_path) as q:
        job = q.get(repo0, cfg.family, cfg.extraction_wave)
        assert job.state in {WRITING_L1, "extracting", "cloning", PENDING, FAILED}

    report = run_recover(
        registry_path=cfg.registry_path,
        events_dir=cfg.events_dir,
        receipts_dir=cfg.receipts_dir,
        blobs_dir=cfg.blobs_dir,
        queue_path=cfg.queue_path,
        scratch_dir=cfg.scratch_dir,
        family=cfg.family,
        wave=cfg.extraction_wave,
        protocol_version="1.0.0",
        extraction_wave=cfg.extraction_wave,
    )
    assert report.global_events_rebuilt is True

    with patch.object(extract_module, "extract_one_repo", side_effect=fake_extract):
        run_extract(ExtractConfig(**{**cfg.__dict__, "force": False}))

    with JobQueue(cfg.queue_path) as q:
        job = q.get(repo0, cfg.family, cfg.extraction_wave)
        assert job.state == COMPLETED


def test_fault_injection_crash_before_receipt(tmp_path):
    repo0 = _repo_id(0)
    registry = _registry(tmp_path, 1)
    cfg = _cfg(tmp_path, registry)

    def fake_extract(cfg, row, blob_store, checkpoint=None):
        return _ok_receipt(row)

    def crash_before_receipt(phase: str) -> None:
        if phase == "receipt":
            raise RuntimeError("simulated crash before receipt")

    extract_module.FAULT_INJECTION_HOOK = crash_before_receipt
    try:
        with patch.object(extract_module, "extract_one_repo", side_effect=fake_extract):
            with pytest.raises(RuntimeError):
                run_extract(cfg)
    finally:
        extract_module.FAULT_INJECTION_HOOK = None

    with JobQueue(cfg.queue_path) as q:
        job = q.get(repo0, cfg.family, cfg.extraction_wave)
        assert job.state != COMPLETED

    blob_store = BlobStore(cfg.blobs_dir)
    failures = verify_repo_completion(
        repo_id=repo0,
        events_dir=cfg.events_dir,
        receipts_dir=cfg.receipts_dir,
        blob_store=blob_store,
    )
    assert any("receipt" in f for f in failures)


def test_fault_injection_crash_during_clone(tmp_path):
    repo0 = _repo_id(0)
    registry = _registry(tmp_path, 1)
    cfg = _cfg(tmp_path, registry)

    def crash_clone(phase: str) -> None:
        if phase == "clone":
            raise KeyboardInterrupt("simulated Ctrl+C during clone")

    extract_module.FAULT_INJECTION_HOOK = crash_clone
    try:
        with pytest.raises(KeyboardInterrupt):
            run_extract(cfg)
    finally:
        extract_module.FAULT_INJECTION_HOOK = None

    with JobQueue(cfg.queue_path) as q:
        job = q.get(repo0, cfg.family, cfg.extraction_wave)
        assert job.state in {"cloning", "extracting", PENDING}

    run_recover(
        registry_path=cfg.registry_path,
        events_dir=cfg.events_dir,
        receipts_dir=cfg.receipts_dir,
        blobs_dir=cfg.blobs_dir,
        queue_path=cfg.queue_path,
        scratch_dir=cfg.scratch_dir,
        family=cfg.family,
        wave=cfg.extraction_wave,
        protocol_version="1.0.0",
        extraction_wave=cfg.extraction_wave,
    )
    with JobQueue(cfg.queue_path) as q:
        job = q.get(repo0, cfg.family, cfg.extraction_wave)
        assert job.state == PENDING


def test_atomic_parquet_no_tmp_after_success(tmp_path):
    repo0 = _repo_id(0)
    registry = _registry(tmp_path, 1)
    cfg = _cfg(tmp_path, registry)

    with patch.object(extract_module, "extract_one_repo", side_effect=lambda c, r, b, cp=None: _ok_receipt(r)):
        run_extract(cfg)

    repo_parquet = cfg.events_dir / "repos" / f"{repo0}.parquet"
    assert repo_parquet.exists()
    assert not repo_parquet.with_name(f"{repo0}.parquet.tmp").exists()
    global_parquet = cfg.events_dir / "events.parquet"
    assert global_parquet.exists()
    pq.read_table(global_parquet)


def test_execution_log_records_transitions(tmp_path):
    registry = _registry(tmp_path, 1)
    cfg = _cfg(tmp_path, registry)

    with patch.object(extract_module, "extract_one_repo", side_effect=lambda c, r, b, cp=None: _ok_receipt(r)):
        run_extract(cfg)

    log_path = cfg.events_dir / "execution.log"
    assert log_path.exists()
    lines = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    states = [entry["new_state"] for entry in lines]
    assert "cloning" in states
    assert COMPLETED in states


def test_recover_reverts_inconsistent_completed(tmp_path):
    repo0 = _repo_id(0)
    registry = _registry(tmp_path, 1)
    cfg = _cfg(tmp_path, registry)

    with JobQueue(cfg.queue_path) as q:
        q.upsert_pending(repo0, "https://github.com/example/repo0", cfg.family, cfg.extraction_wave)
        q.mark_completed(repo0, cfg.family, cfg.extraction_wave, n_events=0)

    report = run_recover(
        registry_path=cfg.registry_path,
        events_dir=cfg.events_dir,
        receipts_dir=cfg.receipts_dir,
        blobs_dir=cfg.blobs_dir,
        queue_path=cfg.queue_path,
        scratch_dir=cfg.scratch_dir,
        family=cfg.family,
        wave=cfg.extraction_wave,
        protocol_version="1.0.0",
        extraction_wave=cfg.extraction_wave,
    )
    assert repo0 in report.reverted_to_failed

    with JobQueue(cfg.queue_path) as q:
        job = q.get(repo0, cfg.family, cfg.extraction_wave)
        assert job.state == FAILED
