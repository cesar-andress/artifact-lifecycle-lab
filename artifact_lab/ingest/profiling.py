"""Extraction pipeline profiling — measure before optimize."""

from __future__ import annotations

import csv
import statistics
import threading
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

PHASE_TIMING_ATTR: dict[str, str] = {
    "clone": "clone_s",
    "inspection": "inspection_s",
    "history": "history_s",
    "detector": "detector_s",
    "blobs": "blobs_s",
    "parquet_write": "parquet_write_s",
    "manifest_write": "manifest_write_s",
    "cleanup": "cleanup_s",
}

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
    "local_cpu_s",
    "git_network_wait_s",
    "git_local_wait_s",
    "n_git_subprocesses",
    "n_lazy_blob_fetches",
    "bytes_downloaded",
    "clone_bytes",
    "n_events",
    "n_matched_paths",
    "recorded_at",
    "failure_reason",
    "timeout_phase",
)


def repo_slug(repo_url: str) -> str:
    parsed = parse_github_url(repo_url)
    if parsed:
        return f"{parsed[0]}/{parsed[1]}"
    return repo_url


@dataclass
class ResourceMetrics:
    local_cpu_s: float = 0.0
    git_network_wait_s: float = 0.0
    git_local_wait_s: float = 0.0
    n_git_subprocesses: int = 0
    n_lazy_blob_fetches: int = 0
    bytes_downloaded: int = 0


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

    def phase_elapsed(self, phase: str) -> float:
        attr = PHASE_TIMING_ATTR.get(phase)
        if not attr:
            return 0.0
        return float(getattr(self, attr, 0.0))

    def record_phase_partial(self, phase: str, elapsed_s: float) -> None:
        attr = PHASE_TIMING_ATTR.get(phase)
        if not attr:
            return
        current = float(getattr(self, attr, 0.0))
        if elapsed_s > current:
            setattr(self, attr, elapsed_s)

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
    resources: ResourceMetrics = field(default_factory=ResourceMetrics)
    clone_bytes: int = 0
    n_events: int = 0
    n_matched_paths: int = 0
    recorded_at: str = ""
    failure_reason: str | None = None
    timeout_phase: str | None = None

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
            "local_cpu_s": self.resources.local_cpu_s,
            "git_network_wait_s": self.resources.git_network_wait_s,
            "git_local_wait_s": self.resources.git_local_wait_s,
            "n_git_subprocesses": self.resources.n_git_subprocesses,
            "n_lazy_blob_fetches": self.resources.n_lazy_blob_fetches,
            "bytes_downloaded": self.resources.bytes_downloaded,
            "clone_bytes": self.clone_bytes,
            "n_events": self.n_events,
            "n_matched_paths": self.n_matched_paths,
            "recorded_at": self.recorded_at,
            "failure_reason": self.failure_reason,
            "timeout_phase": self.timeout_phase,
        }


@dataclass
class ExtractionLiveState:
    """Thread-safe extraction progress for timeout attribution."""

    profile: ExtractionProfile
    lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    current_phase: str = "clone"
    phase_started_at: float = field(default_factory=time.perf_counter)
    wall_started_at: float = field(default_factory=time.perf_counter)

    def enter_phase(self, phase: str) -> None:
        with self.lock:
            self.current_phase = phase
            self.phase_started_at = time.perf_counter()

    def build_timeout_profile(self) -> ExtractionProfile:
        with self.lock:
            phase = self.current_phase
            partial_elapsed = max(0.0, time.perf_counter() - self.phase_started_at)
            self.profile.timings.record_phase_partial(phase, partial_elapsed)
            self.profile.timings.wall_s = max(
                self.profile.timings.wall_s,
                time.perf_counter() - self.wall_started_at,
            )
            self.profile.timeout_phase = phase
            self.profile.failure_reason = f"timeout:{phase}"
            self.profile.status = "failed"
            return self.profile


def timeout_phase_from_reason(reason: str | None) -> str | None:
    if reason and reason.startswith("timeout:"):
        return reason.split(":", 1)[1]
    return None


def profile_dominant_phase_label(profile: ExtractionProfile) -> tuple[str, float]:
    phase = profile.timeout_phase or timeout_phase_from_reason(profile.failure_reason)
    if phase:
        return f"timeout:{phase}", profile.timings.phase_elapsed(phase)
    dominant, value = profile.timings.dominant_phase()
    return dominant, value


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
    if profile.status == "failed" and (profile.timeout_phase or timeout_phase_from_reason(profile.failure_reason)):
        label, elapsed = profile_dominant_phase_label(profile)
        lines.extend(["", _phase_line(label, elapsed)])
    return "\n".join(lines)


def slow_repo_warning(profile: ExtractionProfile, *, threshold_s: float = SLOW_REPO_THRESHOLD_S) -> str | None:
    total = profile.timings.total_s
    if profile.timeout_phase or timeout_phase_from_reason(profile.failure_reason):
        label, elapsed = profile_dominant_phase_label(profile)
        return (
            f"WARNING: Timed out repository ({profile.repo_slug}) — "
            f"slowest phase: {label} ({elapsed:.1f} s, total {total:.1f} s)"
        )
    if total <= threshold_s:
        return None
    phase, value = profile_dominant_phase_label(profile)
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
        resources=ResourceMetrics(
            local_cpu_s=float(row.get("local_cpu_s", 0.0)),
            git_network_wait_s=float(row.get("git_network_wait_s", 0.0)),
            git_local_wait_s=float(row.get("git_local_wait_s", 0.0)),
            n_git_subprocesses=int(row.get("n_git_subprocesses", 0)),
            n_lazy_blob_fetches=int(row.get("n_lazy_blob_fetches", 0)),
            bytes_downloaded=int(row.get("bytes_downloaded", 0)),
        ),
        clone_bytes=int(row.get("clone_bytes", 0)),
        n_events=int(row.get("n_events", 0)),
        n_matched_paths=int(row.get("n_matched_paths", 0)),
        recorded_at=row.get("recorded_at", ""),
        failure_reason=row.get("failure_reason"),
        timeout_phase=row.get("timeout_phase"),
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


def aggregate_slowest_phase(profiles: list[ExtractionProfile]) -> tuple[str, float]:
    totals = {phase: 0.0 for phase in PHASE_NAMES}
    for profile in profiles:
        t = profile.timings
        totals["clone"] += t.clone_s
        totals["inspection"] += t.inspection_s
        totals["history"] += t.history_s
        totals["detector"] += t.detector_s
        totals["blobs"] += t.blobs_s
        totals["parquet_write"] += t.parquet_write_s
        totals["manifest_write"] += t.manifest_write_s
        totals["cleanup"] += t.cleanup_s
    if not profiles:
        return "n/a", 0.0
    phase, value = max(totals.items(), key=lambda item: item[1])
    return phase, value


def format_extraction_summary(
    *,
    queue_counts: dict[str, int],
    run_profiles: list[ExtractionProfile],
    stale_recovered: int = 0,
    registry_limit: int | None = None,
) -> str:
    completed = queue_counts.get("succeeded", 0)
    failed = queue_counts.get("failed", 0)
    pending = queue_counts.get("pending", 0)
    totals = [p.timings.total_s for p in run_profiles]
    slowest_phase, slowest_value = aggregate_slowest_phase(run_profiles)
    lines = [
        "",
        "Extraction summary",
        f"  completed .......... {completed}",
        f"  failed ............. {failed}",
        f"  pending ............ {pending}",
        f"  median total time .. {median_or_none(totals):.1f} s" if totals else "  median total time .. n/a",
        f"  slowest phase ...... {slowest_phase} ({slowest_value:.1f} s aggregate)",
    ]
    if stale_recovered:
        lines.append(f"  stale recovered .... {stale_recovered} (running -> pending)")
    if registry_limit is not None:
        lines.append(f"  registry limit ..... {registry_limit}")
    if run_profiles:
        git_net = [p.resources.git_network_wait_s for p in run_profiles]
        local_cpu = [p.resources.local_cpu_s for p in run_profiles]
        lines.append(
            f"  median git network .. {median_or_none(git_net):.1f} s"
            if git_net
            else "  median git network .. n/a"
        )
        lines.append(
            f"  median local cpu ..... {median_or_none(local_cpu):.1f} s"
            if local_cpu
            else "  median local cpu ..... n/a"
        )
    return "\n".join(lines)
