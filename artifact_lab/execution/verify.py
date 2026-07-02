"""Verification of repository extraction artifacts (diagnostics only)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import pyarrow.parquet as pq

from artifact_lab.execution.paths import (
    global_events_path,
    global_manifest_path,
    receipt_path,
    repo_events_path,
    repo_manifest_path,
)
from artifact_lab.execution.states import COMPLETED, normalize_state
from artifact_lab.store.blobs import BlobStore
from artifact_lab.store.job_queue import JobQueue


@dataclass
class VerifyIssue:
    repo_id: str
    category: str
    message: str


@dataclass
class VerifyReport:
    ok: bool
    issues: list[VerifyIssue] = field(default_factory=list)

    def add(self, repo_id: str, category: str, message: str) -> None:
        self.issues.append(VerifyIssue(repo_id=repo_id, category=category, message=message))
        self.ok = False


def _tmp_files_for_repo(events_dir: Path, receipts_dir: Path, repo_id: str) -> list[Path]:
    candidates = [
        repo_events_path(events_dir, repo_id).with_name(f"{repo_id}.parquet.tmp"),
        repo_manifest_path(events_dir, repo_id).with_name(f"{repo_id}.manifest.yaml.tmp"),
        receipt_path(receipts_dir, repo_id).with_name(f"{repo_id}.json.tmp"),
    ]
    return [p for p in candidates if p.exists()]


def verify_blob_references(events: list[dict], blob_store: BlobStore) -> list[str]:
    missing: list[str] = []
    for event in events:
        blob_sha = (event.get("blob_sha") or "").strip()
        if blob_sha and not blob_store.has(blob_sha):
            missing.append(blob_sha)
    return missing


def verify_repo_completion(
    *,
    repo_id: str,
    events_dir: Path,
    receipts_dir: Path,
    blob_store: BlobStore,
) -> list[str]:
    """Return list of verification failures (empty means COMPLETED is valid)."""
    issues: list[str] = []

    tmp_files = _tmp_files_for_repo(events_dir, receipts_dir, repo_id)
    if tmp_files:
        issues.append(f"temporary files remain: {[str(p) for p in tmp_files]}")

    receipt = receipt_path(receipts_dir, repo_id)
    if not receipt.exists():
        issues.append("receipt missing")
        return issues

    try:
        receipt_data = json.loads(receipt.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        issues.append(f"receipt invalid json: {exc}")
        return issues

    manifest = repo_manifest_path(events_dir, repo_id)
    if not manifest.exists():
        issues.append("per-repo manifest missing")

    l1_path = repo_events_path(events_dir, repo_id)
    if not l1_path.exists():
        issues.append("per-repo L1 parquet missing")
        return issues

    try:
        table = pq.read_table(l1_path)
        events = table.to_pylist()
    except Exception as exc:  # noqa: BLE001 — diagnostic surface
        issues.append(f"L1 parquet unreadable: {exc}")
        return issues

    expected_n = int(receipt_data.get("n_events", -1))
    if expected_n >= 0 and len(events) != expected_n:
        issues.append(f"L1 row count {len(events)} != receipt n_events {expected_n}")

    missing_blobs = verify_blob_references(events, blob_store)
    if missing_blobs:
        issues.append(f"missing blob references: {missing_blobs[:5]}")

    return issues


def verify_registry(registry_path: Path) -> VerifyReport:
    report = VerifyReport(ok=True)
    if not registry_path.exists():
        report.add("", "registry", f"missing registry: {registry_path}")
        return report
    if registry_path.stat().st_size == 0:
        report.add("", "registry", "registry is empty")
    return report


def verify_queue(queue_path: Path, *, family: str, wave: str) -> VerifyReport:
    report = VerifyReport(ok=True)
    if not queue_path.exists():
        report.add("", "queue", f"missing queue db: {queue_path}")
        return report
    with JobQueue(queue_path) as queue:
        jobs = queue.list_jobs(family=family, wave=wave)
        if not jobs:
            report.add("", "queue", f"no jobs for family={family} wave={wave}")
    return report


def verify_completed_repos(
    *,
    events_dir: Path,
    receipts_dir: Path,
    blobs_dir: Path,
    queue_path: Path,
    family: str,
    wave: str,
) -> VerifyReport:
    report = VerifyReport(ok=True)
    blob_store = BlobStore(blobs_dir)

    with JobQueue(queue_path) as queue:
        for job in queue.list_jobs(family=family, wave=wave):
            if normalize_state(job.state) != COMPLETED:
                continue
            failures = verify_repo_completion(
                repo_id=job.repo_id,
                events_dir=events_dir,
                receipts_dir=receipts_dir,
                blob_store=blob_store,
            )
            for msg in failures:
                report.add(job.repo_id, "completed_repo", msg)

    return report


def verify_global_dataset(events_dir: Path) -> VerifyReport:
    report = VerifyReport(ok=True)
    events_path = global_events_path(events_dir)
    manifest_path = global_manifest_path(events_dir)

    repos_dir = events_dir / "repos"
    if repos_dir.exists():
        repo_files = sorted(repos_dir.glob("*.parquet"))
        if events_path.exists():
            try:
                global_table = pq.read_table(events_path)
                global_rows = global_table.to_pylist()
                per_repo_rows: list[dict] = []
                for path in repo_files:
                    if path.name.endswith(".tmp"):
                        continue
                    per_repo_rows.extend(pq.read_table(path).to_pylist())
                if len(global_rows) != len(per_repo_rows):
                    report.add(
                        "",
                        "global_events",
                        f"global row count {len(global_rows)} != sum(per-repo) {len(per_repo_rows)}",
                    )
            except Exception as exc:  # noqa: BLE001
                report.add("", "global_events", f"global events unreadable: {exc}")
        elif repo_files:
            report.add("", "global_events", "per-repo L1 exists but global events.parquet missing")

    if events_path.exists() and not manifest_path.exists():
        report.add("", "global_manifest", "events.parquet exists but manifest.yaml missing")

    return report


def run_verify(
    *,
    registry_path: Path,
    events_dir: Path,
    receipts_dir: Path,
    blobs_dir: Path,
    queue_path: Path,
    family: str,
    wave: str,
) -> VerifyReport:
    report = VerifyReport(ok=True)
    for partial in (
        verify_registry(registry_path),
        verify_queue(queue_path, family=family, wave=wave),
        verify_completed_repos(
            events_dir=events_dir,
            receipts_dir=receipts_dir,
            blobs_dir=blobs_dir,
            queue_path=queue_path,
            family=family,
            wave=wave,
        ),
        verify_global_dataset(events_dir),
    ):
        if not partial.ok:
            report.ok = False
            report.issues.extend(partial.issues)
    return report
