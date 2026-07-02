"""Pilot dataset summary from L1, L2, queue, and receipts."""

from __future__ import annotations

import json
from pathlib import Path

import pyarrow.parquet as pq

from artifact_lab.store.job_queue import JobQueue
from artifact_lab.store.parquet import read_parquet, read_parquet_dir


def _read_l1(events_path: Path) -> object | None:
    path = events_path.resolve()
    if path.is_dir():
        parquet = path / "events.parquet"
        if not parquet.exists():
            files = sorted(path.glob("*.parquet"))
            if not files:
                return None
            parquet = files[0]
        return pq.read_table(parquet)
    if path.exists():
        return pq.read_table(path)
    return None


def _read_l2(panel_path: Path) -> object | None:
    path = panel_path.resolve()
    if path.is_dir():
        files = sorted(path.glob("panel_T*.parquet"))
        if not files:
            return None
        return pq.read_table(files[0])
    if path.exists():
        return pq.read_table(path)
    return None


def build_summary(
    *,
    l1_path: Path,
    l2_path: Path | None = None,
    queue_path: Path | None = None,
    receipts_dir: Path | None = None,
    blobs_dir: Path | None = None,
) -> dict:
    summary: dict = {
        "repos_attempted": 0,
        "repos_succeeded": 0,
        "repos_failed": 0,
        "repos_pending": 0,
        "repos_running": 0,
        "l1_rows": 0,
        "unique_blobs": 0,
        "unique_paths": 0,
        "l2_states": {},
        "top_repos_by_events": [],
    }

    if queue_path and queue_path.exists():
        with JobQueue(queue_path) as queue:
            counts = queue.counts_by_state()
            summary["repos_succeeded"] = counts.get("completed", 0) + counts.get("succeeded", 0)
            summary["repos_failed"] = counts.get("failed", 0)
            summary["repos_pending"] = counts.get("pending", 0)
            in_progress = sum(
                counts.get(state, 0)
                for state in ("running", "cloning", "extracting", "writing", "writing_l1", "verifying")
            )
            summary["repos_running"] = in_progress
            summary["repos_attempted"] = sum(counts.values())
    elif receipts_dir and receipts_dir.exists():
        receipts = list(receipts_dir.glob("*.json"))
        summary["repos_attempted"] = len(receipts)
        for path in receipts:
            data = json.loads(path.read_text(encoding="utf-8"))
            status = data.get("status")
            if status in {"ok", "no_matches"}:
                summary["repos_succeeded"] += 1
            else:
                summary["repos_failed"] += 1

    l1 = _read_l1(l1_path)
    if l1 is not None and l1.num_rows:
        summary["l1_rows"] = l1.num_rows
        paths = set(l1.column("path").to_pylist())
        summary["unique_paths"] = len(paths)
        blob_vals = [b for b in l1.column("blob_sha").to_pylist() if b]
        summary["unique_blobs"] = len(set(blob_vals))

        repo_counts: dict[str, int] = {}
        for repo_id, _path in zip(l1.column("repo_id").to_pylist(), l1.column("path").to_pylist()):
            repo_counts[repo_id] = repo_counts.get(repo_id, 0) + 1
        summary["top_repos_by_events"] = sorted(
            repo_counts.items(), key=lambda item: item[1], reverse=True
        )[:10]

    if blobs_dir and blobs_dir.exists():
        blob_files = [p for p in blobs_dir.rglob("*.txt") if p.is_file()]
        if blob_files:
            summary["unique_blobs"] = max(summary["unique_blobs"], len(blob_files))

    if l2_path is not None:
        l2 = _read_l2(l2_path)
        if l2 is not None and l2.num_rows:
            states: dict[str, int] = {}
            for state in l2.column("state").to_pylist():
                states[state] = states.get(state, 0) + 1
            summary["l2_states"] = states

    return summary


def format_summary(summary: dict) -> str:
    lines = [
        "Pilot summary",
        f"  repos attempted:  {summary['repos_attempted']}",
        f"  repos succeeded:  {summary['repos_succeeded']}",
        f"  repos failed:     {summary['repos_failed']}",
        f"  repos pending:    {summary['repos_pending']}",
        f"  repos running:    {summary['repos_running']}",
        f"  L1 rows:          {summary['l1_rows']}",
        f"  unique paths:     {summary['unique_paths']}",
        f"  unique blobs:     {summary['unique_blobs']}",
    ]
    if summary["l2_states"]:
        lines.append("  L2 states:")
        for state, count in sorted(summary["l2_states"].items()):
            lines.append(f"    {state}: {count}")
    if summary["top_repos_by_events"]:
        lines.append("  top repos by matched events:")
        for repo_id, count in summary["top_repos_by_events"]:
            lines.append(f"    {repo_id}: {count}")
    return "\n".join(lines) + "\n"
