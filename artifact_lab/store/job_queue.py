"""SQLite WAL job queue for extraction pipeline state."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from artifact_lab.execution.states import (
    CLONING,
    COMPLETED,
    FAILED,
    IN_PROGRESS_STATES,
    LEGACY_SUCCEEDED,
    PENDING,
    normalize_state,
)

JobState = Literal[
    "pending",
    "cloning",
    "extracting",
    "writing_l1",
    "verifying",
    "completed",
    "failed",
    "running",
    "succeeded",
]

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
        self._migrate_legacy_states()
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

    def _migrate_legacy_states(self) -> None:
        self._conn.execute(
            "UPDATE extraction_jobs SET state = ? WHERE state = ?",
            (COMPLETED, LEGACY_SUCCEEDED),
        )

    def reset_stale_in_progress(self, *, max_age_seconds: int | None = None) -> int:
        """Reset interrupted in-progress jobs to pending for resumable extraction."""
        placeholders = ",".join("?" for _ in IN_PROGRESS_STATES)
        params: list[object] = list(IN_PROGRESS_STATES)
        if max_age_seconds is None:
            cur = self._conn.execute(
                f"UPDATE extraction_jobs SET state = ? WHERE state IN ({placeholders})",
                [PENDING, *params],
            )
            self._conn.commit()
            return cur.rowcount

        cutoff = datetime.now(timezone.utc).timestamp() - max_age_seconds
        rows = self._conn.execute(
            f"SELECT repo_id, family, wave, started_at FROM extraction_jobs WHERE state IN ({placeholders})",
            params,
        ).fetchall()
        reset = 0
        for row in rows:
            started_at = row["started_at"]
            stale = False
            if not started_at:
                stale = True
            else:
                try:
                    stale = datetime.fromisoformat(started_at).timestamp() < cutoff
                except ValueError:
                    stale = True
            if stale:
                self._conn.execute(
                    """
                    UPDATE extraction_jobs SET state = ?
                    WHERE repo_id = ? AND family = ? AND wave = ?
                    """,
                    (PENDING, row["repo_id"], row["family"], row["wave"]),
                )
                reset += 1
        self._conn.commit()
        return reset

    def reset_stale_running(self) -> int:
        """Backward-compatible alias for reset_stale_in_progress()."""
        return self.reset_stale_in_progress()

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

    def should_process(
        self,
        repo_id: str,
        family: str,
        wave: str,
        *,
        force: bool,
        retry_failed: bool = False,
    ) -> bool:
        job = self.get(repo_id, family, wave)
        if job is None:
            return True
        if force:
            return True
        state = normalize_state(job.state)
        if state == COMPLETED:
            return False
        if state == FAILED:
            return retry_failed
        return True

    def mark_state(
        self,
        repo_id: str,
        family: str,
        wave: str,
        state: str,
        *,
        increment_attempt: bool = False,
    ) -> None:
        now = _utc_now()
        if increment_attempt:
            self._conn.execute(
                """
                UPDATE extraction_jobs
                SET state = ?,
                    attempt_count = attempt_count + 1,
                    started_at = ?,
                    finished_at = NULL,
                    failure_reason = NULL
                WHERE repo_id = ? AND family = ? AND wave = ?
                """,
                (state, now, repo_id, family, wave),
            )
        else:
            self._conn.execute(
                """
                UPDATE extraction_jobs
                SET state = ?
                WHERE repo_id = ? AND family = ? AND wave = ?
                """,
                (state, repo_id, family, wave),
            )
        self._conn.commit()

    def mark_running(self, repo_id: str, family: str, wave: str) -> None:
        self.mark_state(repo_id, family, wave, CLONING, increment_attempt=True)

    def mark_completed(self, repo_id: str, family: str, wave: str, *, n_events: int) -> None:
        now = _utc_now()
        self._conn.execute(
            """
            UPDATE extraction_jobs
            SET state = ?,
                finished_at = ?,
                failure_reason = NULL,
                n_events = ?
            WHERE repo_id = ? AND family = ? AND wave = ?
            """,
            (COMPLETED, now, n_events, repo_id, family, wave),
        )
        self._conn.commit()

    def mark_succeeded(self, repo_id: str, family: str, wave: str, *, n_events: int) -> None:
        self.mark_completed(repo_id, family, wave, n_events=n_events)

    def mark_failed(self, repo_id: str, family: str, wave: str, *, reason: str, n_events: int = 0) -> None:
        now = _utc_now()
        self._conn.execute(
            """
            UPDATE extraction_jobs
            SET state = ?,
                finished_at = ?,
                failure_reason = ?,
                n_events = ?
            WHERE repo_id = ? AND family = ? AND wave = ?
            """,
            (FAILED, now, reason, n_events, repo_id, family, wave),
        )
        self._conn.commit()

    def counts_by_state(self) -> dict[str, int]:
        rows = self._conn.execute(
            "SELECT state, COUNT(*) AS n FROM extraction_jobs GROUP BY state"
        ).fetchall()
        counts: dict[str, int] = {}
        for row in rows:
            state = normalize_state(row["state"])
            counts[state] = counts.get(state, 0) + row["n"]
        return counts

    def list_jobs(self, *, family: str | None = None, wave: str | None = None) -> list[JobRecord]:
        query = "SELECT * FROM extraction_jobs"
        params: list[str] = []
        clauses: list[str] = []
        if family is not None:
            clauses.append("family = ?")
            params.append(family)
        if wave is not None:
            clauses.append("wave = ?")
            params.append(wave)
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY repo_id"
        rows = self._conn.execute(query, params).fetchall()
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
