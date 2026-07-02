"""Git subprocess activity accounting for extraction profiling."""

from __future__ import annotations

import time
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Iterator, Literal

GitOpKind = Literal["network", "lazy_blob", "local"]


@dataclass
class GitActivityStats:
    git_network_wait_s: float = 0.0
    git_local_wait_s: float = 0.0
    n_git_subprocesses: int = 0
    n_lazy_blob_fetches: int = 0
    bytes_from_git: int = 0


_git_activity: ContextVar[GitActivityStats | None] = ContextVar("git_activity", default=None)


def active_git_activity() -> GitActivityStats | None:
    return _git_activity.get()


@contextmanager
def track_git_activity() -> Iterator[GitActivityStats]:
    stats = GitActivityStats()
    token = _git_activity.set(stats)
    try:
        yield stats
    finally:
        _git_activity.reset(token)


def classify_git_command(args: list[str]) -> GitOpKind:
    if not args or args[0] != "git":
        return "local"
    sub = args[1] if len(args) > 1 else ""
    if sub == "clone":
        return "network"
    if sub in {"fetch", "pull"}:
        return "network"
    if sub == "show":
        return "lazy_blob"
    return "local"


def record_git_subprocess(
    args: list[str],
    *,
    elapsed_s: float,
    stdout_bytes: int = 0,
    stats: GitActivityStats | None = None,
) -> None:
    target = stats or active_git_activity()
    if target is None:
        return
    target.n_git_subprocesses += 1
    kind = classify_git_command(args)
    if kind == "network":
        target.git_network_wait_s += elapsed_s
        target.bytes_from_git += stdout_bytes
    elif kind == "lazy_blob":
        target.n_lazy_blob_fetches += 1
        target.git_network_wait_s += elapsed_s
        target.bytes_from_git += stdout_bytes
    else:
        target.git_local_wait_s += elapsed_s
