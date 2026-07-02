"""Extraction pipeline profiling — measure before optimize."""

from __future__ import annotations

import statistics
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import pyarrow as pa

from artifact_lab.ingest.git_utils import parse_github_url

SLOW_REPO_THRESHOLD_S = 300.0

PHASE_NAMES = ("clone", "history", "detector", "blobs", "parquet_write", "cleanup")

PROFILE_COLUMNS: tuple[str, ...] = (
    "repo_id",
    "repo_slug",
    "repo_url",
    "extraction_wave",
    "status",
    "clone_s",
    "history_s",
    "detector_s",
    "blobs_s",
    "parquet_write_s",
    "cleanup_s",
    "total_s",
    "clone_bytes",
    "n_events",
    "n_matched_paths",
    "recorded_at",
)


def repo_slug(repo_url: str) -> str:
    parsed = parse_github_url(repo_url)
    if parsed:
        return f"{parsed[0]}/{parsed[1]}"
    return repo_url


def _fmt_seconds(seconds: float) -> str:
    return f"{seconds:.1f}s"


@dataclass
class PhaseTimings:
    clone_s: float = 0.0
    history_s: float = 0.0
    detector_s: float = 0.0
    blobs_s: float = 0.0
    parquet_write_s: float = 0.0
    cleanup_s: float = 0.0
    wall_s: float = 0.0

    def dominant_phase(self) -> tuple[str, float]:
        ranked = [
            ("clone", self.clone_s),
            ("history", self.history_s),
            ("detector", self.detector_s),
            ("blobs", self.blobs_s),
            ("parquet_write", self.parquet_write_s),
            ("cleanup", self.cleanup_s),
        ]
        phase, value = max(ranked, key=lambda item: item[1])
        if value <= 0 and self.wall_s > 0:
            return "unattributed", self.wall_s - sum(v for _, v in ranked)
        return phase, value

    @property
    def total_s(self) -> float:
        if self.wall_s > 0:
            return self.wall_s + self.parquet_write_s
        return (
            self.clone_s
            + self.history_s
            + self.detector_s
            + self.blobs_s
            + self.parquet_write_s
            + self.cleanup_s
        )


@dataclass
class ExtractionProfile:
    repo_id: str
    repo_url: str
    extraction_wave: str
    status: str
    timings: PhaseTimings = field(default_factory=PhaseTimings)
    clone_bytes: int = 0
    n_events: int = 0
    n_matched_paths: int = 0
    recorded_at: str = ""

    @property
    def repo_slug(self) -> str:
        return repo_slug(self.repo_url)

    def to_row(self) -> dict:
        return {
            "repo_id": self.repo_id,
            "repo_slug": self.repo_slug,
            "repo_url": self.repo_url,
            "extraction_wave": self.extraction_wave,
            "status": self.status,
            "clone_s": self.timings.clone_s,
            "history_s": self.timings.history_s,
            "detector_s": self.timings.detector_s,
            "blobs_s": self.timings.blobs_s,
            "parquet_write_s": self.timings.parquet_write_s,
            "cleanup_s": self.timings.cleanup_s,
            "total_s": self.timings.total_s,
            "clone_bytes": self.clone_bytes,
            "n_events": self.n_events,
            "n_matched_paths": self.n_matched_paths,
            "recorded_at": self.recorded_at,
        }


class PhaseTimer:
    def __init__(self) -> None:
        self._start: float | None = None

    def __enter__(self) -> PhaseTimer:
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args: object) -> None:
        self._start = None

    def elapsed(self) -> float:
        if self._start is None:
            return 0.0
        return time.perf_counter() - self._start


def format_progress_log(*, index: int, total: int, profile: ExtractionProfile) -> str:
    t = profile.timings
    lines = [
        f"[{index}/{total}]",
        profile.repo_slug,
        f"clone={_fmt_seconds(t.clone_s)}",
        f"history={_fmt_seconds(t.history_s)}",
        f"detector={_fmt_seconds(t.detector_s)}",
        f"blobs={_fmt_seconds(t.blobs_s)}",
        f"write={_fmt_seconds(t.parquet_write_s)}",
        f"cleanup={_fmt_seconds(t.cleanup_s)}",
        f"total={_fmt_seconds(t.total_s)}",
    ]
    return "\n".join(lines)


def slow_repo_warning(profile: ExtractionProfile, *, threshold_s: float = SLOW_REPO_THRESHOLD_S) -> str | None:
    total = profile.timings.total_s
    if total <= threshold_s:
        return None
    phase, value = profile.timings.dominant_phase()
    return (
        f"WARNING: {profile.repo_slug} exceeded {threshold_s / 60:.0f}m "
        f"(total={total:.1f}s); slowest phase: {phase} ({value:.1f}s)"
    )


def write_profiles(profiles: list[ExtractionProfile], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [p.to_row() for p in profiles]
    table = pa.Table.from_pylist(rows) if rows else pa.table({col: [] for col in PROFILE_COLUMNS})
    import pyarrow.parquet as pq

    pq.write_table(table, path)


def merge_profiles(existing: list[dict], fresh: list[ExtractionProfile]) -> list[ExtractionProfile]:
    by_key = {(row["repo_id"], row["extraction_wave"]): row for row in existing}
    for profile in fresh:
        by_key[(profile.repo_id, profile.extraction_wave)] = profile.to_row()
    return [_row_to_profile(by_key[key]) for key in sorted(by_key)]


def load_profiles(path: Path) -> list[ExtractionProfile]:
    if not path.exists():
        return []
    import pyarrow.parquet as pq

    return [_row_to_profile(row) for row in pq.read_table(path).to_pylist()]


def _row_to_profile(row: dict) -> ExtractionProfile:
    timings = PhaseTimings(
        clone_s=float(row["clone_s"]),
        history_s=float(row["history_s"]),
        detector_s=float(row["detector_s"]),
        blobs_s=float(row["blobs_s"]),
        parquet_write_s=float(row["parquet_write_s"]),
        cleanup_s=float(row["cleanup_s"]),
        wall_s=float(row["total_s"]) - float(row["parquet_write_s"]),
    )
    return ExtractionProfile(
        repo_id=row["repo_id"],
        repo_url=row["repo_url"],
        extraction_wave=row["extraction_wave"],
        status=row["status"],
        timings=timings,
        clone_bytes=int(row["clone_bytes"]),
        n_events=int(row["n_events"]),
        n_matched_paths=int(row["n_matched_paths"]),
        recorded_at=row["recorded_at"],
    )


def assign_parquet_write_share(profiles: list[ExtractionProfile], parquet_write_s: float) -> None:
    if not profiles or parquet_write_s <= 0:
        return
    share = parquet_write_s / len(profiles)
    for profile in profiles:
        profile.timings.parquet_write_s = share


def median_or_none(values: list[float]) -> float | None:
    if not values:
        return None
    return float(statistics.median(values))
