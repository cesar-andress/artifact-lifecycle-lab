"""SQLite WAL job queue for extraction pipeline state."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

JobState = Literal["pending", "running", "succeeded", "failed"]

DOCUMENTED_COLUMNS: tuple[str, ...] = (
    "repo_id",
    "repo_url",
    "state",
    "failure_reason",
    "attempt_count",
    "started_at",
    "finished_at",
)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS extraction_jobs (
    repo_id TEXT NOT NULL,
    repo_url TEXT NOT NULL,
    family TEXT NOT NULL,
    wave TEXT NOT NULL,
    state TEXT NOT NULL,
    failure_reason TEXT,
    attempt_count INTEGER NOT NULL DEFAULT 0,
    started_at TEXT,
    finished_at TEXT,
    n_events INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (repo_id, family, wave)
);
"""


@dataclass
class JobRecord:
    repo_id: str
    repo_url: str
    family: str
    wave: str
    state: JobState
    failure_reason: str | None
    attempt_count: int
    started_at: str | None
    finished_at: str | None
    n_events: int


class JobQueue:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.executescript(_SCHEMA)
        self._migrate_legacy_status_column()
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> JobQueue:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _migrate_legacy_status_column(self) -> None:
        rows = self._conn.execute("PRAGMA table_info(extraction_jobs)").fetchall()
        if not rows:
            return
        columns = {row["name"] for row in rows}
        if "status" in columns and "state" not in columns:
            self._conn.execute("ALTER TABLE extraction_jobs RENAME COLUMN status TO state")

    def reset_stale_running(self) -> int:
        cur = self._conn.execute(
            "UPDATE extraction_jobs SET state = 'pending' WHERE state = 'running'"
        )
        self._conn.commit()
        return cur.rowcount

    def upsert_pending(self, repo_id: str, repo_url: str, family: str, wave: str) -> None:
        self._conn.execute(
            """
            INSERT INTO extraction_jobs (repo_id, repo_url, family, wave, state)
            VALUES (?, ?, ?, ?, 'pending')
            ON CONFLICT(repo_id, family, wave) DO NOTHING
            """,
            (repo_id, repo_url, family, wave),
        )
        self._conn.commit()

    def get(self, repo_id: str, family: str, wave: str) -> JobRecord | None:
        row = self._conn.execute(
            "SELECT * FROM extraction_jobs WHERE repo_id = ? AND family = ? AND wave = ?",
            (repo_id, family, wave),
        ).fetchone()
        return self._row_to_record(row) if row else None

    def should_process(self, repo_id: str, family: str, wave: str, *, force: bool) -> bool:
        job = self.get(repo_id, family, wave)
        if job is None:
            return True
        if force:
            return True
        return job.state != "succeeded"

    def mark_running(self, repo_id: str, family: str, wave: str) -> None:
        now = _utc_now()
        self._conn.execute(
            """
            UPDATE extraction_jobs
            SET state = 'running',
                attempt_count = attempt_count + 1,
                started_at = ?,
                finished_at = NULL,
                failure_reason = NULL
            WHERE repo_id = ? AND family = ? AND wave = ?
            """,
            (now, repo_id, family, wave),
        )
        self._conn.commit()

    def mark_succeeded(self, repo_id: str, family: str, wave: str, *, n_events: int) -> None:
        now = _utc_now()
        self._conn.execute(
            """
            UPDATE extraction_jobs
            SET state = 'succeeded',
                finished_at = ?,
                failure_reason = NULL,
                n_events = ?
            WHERE repo_id = ? AND family = ? AND wave = ?
            """,
            (now, n_events, repo_id, family, wave),
        )
        self._conn.commit()

    def mark_failed(self, repo_id: str, family: str, wave: str, *, reason: str, n_events: int = 0) -> None:
        now = _utc_now()
        self._conn.execute(
            """
            UPDATE extraction_jobs
            SET state = 'failed',
                finished_at = ?,
                failure_reason = ?,
                n_events = ?
            WHERE repo_id = ? AND family = ? AND wave = ?
            """,
            (now, reason, n_events, repo_id, family, wave),
        )
        self._conn.commit()

    def counts_by_state(self) -> dict[str, int]:
        rows = self._conn.execute(
            "SELECT state, COUNT(*) AS n FROM extraction_jobs GROUP BY state"
        ).fetchall()
        return {row["state"]: row["n"] for row in rows}

    def list_jobs(self) -> list[JobRecord]:
        rows = self._conn.execute("SELECT * FROM extraction_jobs ORDER BY repo_id").fetchall()
        return [self._row_to_record(row) for row in rows]

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> JobRecord:
        return JobRecord(
            repo_id=row["repo_id"],
            repo_url=row["repo_url"],
            family=row["family"],
            wave=row["wave"],
            state=row["state"],
            failure_reason=row["failure_reason"],
            attempt_count=row["attempt_count"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
            n_events=row["n_events"],
        )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
