"""Checkpoint transitions for per-repository extraction transactions."""

from __future__ import annotations

import time
from dataclasses import dataclass

from artifact_lab.execution.execution_log import ExecutionLog
from artifact_lab.execution.states import (
    CLONING,
    COMPLETED,
    EXTRACTING,
    FAILED,
    PENDING,
    VERIFYING,
    WRITING_L1,
)
from artifact_lab.store.job_queue import JobQueue


@dataclass
class RepoCheckpoint:
    queue: JobQueue
    log: ExecutionLog
    repo_id: str
    family: str
    wave: str
    _phase_start: float | None = None

    def transition(self, new_state: str, *, reason: str = "") -> None:
        job = self.queue.get(self.repo_id, self.family, self.wave)
        old_state = job.state if job else PENDING
        duration_s: float | None = None
        if self._phase_start is not None:
            duration_s = time.perf_counter() - self._phase_start
        increment = new_state == CLONING and old_state in {PENDING, FAILED}
        self.queue.mark_state(
            self.repo_id,
            self.family,
            self.wave,
            new_state,
            increment_attempt=increment,
        )
        self.log.append(
            repo_id=self.repo_id,
            old_state=old_state,
            new_state=new_state,
            reason=reason,
            duration_s=duration_s,
        )
        self._phase_start = time.perf_counter()

    def start_cloning(self) -> None:
        self.transition(CLONING, reason="begin repository transaction")

    def start_extracting(self) -> None:
        self.transition(EXTRACTING, reason="clone complete")

    def start_writing_l1(self) -> None:
        self.transition(WRITING_L1, reason="extraction complete")

    def start_verifying(self) -> None:
        self.transition(VERIFYING, reason="L1 artifacts written")

    def complete(self, *, n_events: int) -> None:
        self.queue.mark_completed(self.repo_id, self.family, self.wave, n_events=n_events)
        job = self.queue.get(self.repo_id, self.family, self.wave)
        old_state = VERIFYING
        self.log.append(
            repo_id=self.repo_id,
            old_state=old_state,
            new_state=COMPLETED,
            reason="verification passed",
            duration_s=(time.perf_counter() - self._phase_start) if self._phase_start else None,
        )

    def fail(self, *, reason: str) -> None:
        job = self.queue.get(self.repo_id, self.family, self.wave)
        old_state = job.state if job else PENDING
        self.queue.mark_failed(self.repo_id, self.family, self.wave, reason=reason, n_events=0)
        self.log.append(
            repo_id=self.repo_id,
            old_state=old_state,
            new_state=FAILED,
            reason=reason,
        )
