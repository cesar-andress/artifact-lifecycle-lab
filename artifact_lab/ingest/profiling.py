"""Extraction pipeline profiling — measure before optimize."""

from __future__ import annotations

import csv
import statistics
import time
from dataclasses import dataclass, field
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from artifact_lab.ingest.git_utils import parse_github_url

SLOW_REPO_THRESHOLD_S = 300.0

PHASE_NAMES: tuple[str, ...] = (
    "clone",
    "inspection",
    "history",
    "detector",
    "blobs",
    "parquet_write",
    "manifest_write",
    "cleanup",
)

PROFILE_COLUMNS: tuple[str, ...] = (
    "repo_id",
    "repo_slug",
    "repo_url",
    "extraction_wave",
    "status",
    "clone_s",
    "inspection_s",
    "history_s",
    "detector_s",
    "blobs_s",
    "parquet_write_s",
    "manifest_write_s",
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


@dataclass
class PhaseTimings:
    clone_s: float = 0.0
    inspection_s: float = 0.0
    history_s: float = 0.0
    detector_s: float = 0.0
    blobs_s: float = 0.0
    parquet_write_s: float = 0.0
    manifest_write_s: float = 0.0
    cleanup_s: float = 0.0
    wall_s: float = 0.0

    def phase_values(self) -> list[tuple[str, float]]:
        return [
            ("clone", self.clone_s),
            ("inspection", self.inspection_s),
            ("history", self.history_s),
            ("detector", self.detector_s),
            ("blobs", self.blobs_s),
            ("parquet_write", self.parquet_write_s),
            ("manifest_write", self.manifest_write_s),
            ("cleanup", self.cleanup_s),
        ]

    def dominant_phase(self) -> tuple[str, float]:
        phase, value = max(self.phase_values(), key=lambda item: item[1])
        if value <= 0 and self.wall_s > 0:
            attributed = sum(v for _, v in self.phase_values())
            return "unattributed", max(0.0, self.wall_s - attributed + self.parquet_write_s + self.manifest_write_s)
        return phase, value

    @property
    def total_s(self) -> float:
        if self.wall_s > 0:
            return self.wall_s + self.parquet_write_s + self.manifest_write_s
        return sum(value for _, value in self.phase_values())


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
            "inspection_s": self.timings.inspection_s,
            "history_s": self.timings.history_s,
            "detector_s": self.timings.detector_s,
            "blobs_s": self.timings.blobs_s,
            "parquet_write_s": self.timings.parquet_write_s,
            "manifest_write_s": self.timings.manifest_write_s,
            "cleanup_s": self.timings.cleanup_s,
            "total_s": self.timings.total_s,
            "clone_bytes": self.clone_bytes,
            "n_events": self.n_events,
            "n_matched_paths": self.n_matched_paths,
            "recorded_at": self.recorded_at,
        }


def _phase_line(label: str, seconds: float) -> str:
    dots = max(3, 16 - len(label))
    return f"{label}{'.' * dots} {seconds:.1f} s"


def format_progress_log(*, index: int, total: int, profile: ExtractionProfile) -> str:
    t = profile.timings
    write_s = t.parquet_write_s + t.manifest_write_s
    lines = [
        f"[{index}/{total}]",
        "",
        "Repository:",
        profile.repo_slug,
        "",
        _phase_line("clone", t.clone_s),
        _phase_line("history", t.history_s),
        _phase_line("detectors", t.detector_s),
        _phase_line("blobs", t.blobs_s),
        _phase_line("write", write_s),
        _phase_line("cleanup", t.cleanup_s),
        "",
        _phase_line("TOTAL", t.total_s).replace(" s", " s", 1),
    ]
    return "\n".join(lines)


def slow_repo_warning(profile: ExtractionProfile, *, threshold_s: float = SLOW_REPO_THRESHOLD_S) -> str | None:
    total = profile.timings.total_s
    if total <= threshold_s:
        return None
    phase, value = profile.timings.dominant_phase()
    return f"WARNING: Slow repository ({profile.repo_slug}) — slowest phase: {phase} ({value:.1f} s, total {total:.1f} s)"


def write_profiles(profiles: list[ExtractionProfile], parquet_path: Path, *, csv_path: Path | None = None) -> None:
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    rows = [p.to_row() for p in profiles]
    table = pa.Table.from_pylist(rows) if rows else pa.table({col: [] for col in PROFILE_COLUMNS})
    pq.write_table(table, parquet_path)
    csv_target = csv_path or parquet_path.with_suffix(".csv")
    with csv_target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(PROFILE_COLUMNS))
        writer.writeheader()
        writer.writerows(rows)


def merge_profiles(existing: list[dict], fresh: list[ExtractionProfile]) -> list[ExtractionProfile]:
    by_key = {(row["repo_id"], row["extraction_wave"]): row for row in existing}
    for profile in fresh:
        by_key[(profile.repo_id, profile.extraction_wave)] = profile.to_row()
    return [_row_to_profile(by_key[key]) for key in sorted(by_key)]


def load_profiles(path: Path) -> list[ExtractionProfile]:
    if not path.exists():
        return []
    return [_row_to_profile(row) for row in pq.read_table(path).to_pylist()]


def _row_to_profile(row: dict) -> ExtractionProfile:
    parquet_write = float(row.get("parquet_write_s", 0.0))
    manifest_write = float(row.get("manifest_write_s", 0.0))
    inspection = float(row.get("inspection_s", row.get("repository_inspection_s", 0.0)))
    detector = float(row.get("detector_s", 0.0))
    if "inspection_s" not in row and "repository_inspection_s" not in row and detector > 0:
        inspection = detector
        detector = 0.0
    timings = PhaseTimings(
        clone_s=float(row.get("clone_s", 0.0)),
        inspection_s=inspection,
        history_s=float(row.get("history_s", 0.0)),
        detector_s=detector,
        blobs_s=float(row.get("blobs_s", 0.0)),
        parquet_write_s=parquet_write,
        manifest_write_s=manifest_write,
        cleanup_s=float(row.get("cleanup_s", 0.0)),
        wall_s=float(row.get("total_s", 0.0)) - parquet_write - manifest_write,
    )
    return ExtractionProfile(
        repo_id=row["repo_id"],
        repo_url=row["repo_url"],
        extraction_wave=row["extraction_wave"],
        status=row["status"],
        timings=timings,
        clone_bytes=int(row.get("clone_bytes", 0)),
        n_events=int(row.get("n_events", 0)),
        n_matched_paths=int(row.get("n_matched_paths", 0)),
        recorded_at=row.get("recorded_at", ""),
    )


def assign_batch_write_shares(
    profiles: list[ExtractionProfile],
    *,
    parquet_write_s: float,
    manifest_write_s: float,
) -> None:
    if not profiles:
        return
    n = len(profiles)
    parquet_share = parquet_write_s / n if parquet_write_s > 0 else 0.0
    manifest_share = manifest_write_s / n if manifest_write_s > 0 else 0.0
    for profile in profiles:
        profile.timings.parquet_write_s = parquet_share
        profile.timings.manifest_write_s = manifest_share


def median_or_none(values: list[float]) -> float | None:
    if not values:
        return None
    return float(statistics.median(values))


def mean_or_none(values: list[float]) -> float | None:
    if not values:
        return None
    return float(statistics.mean(values))
