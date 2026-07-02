"""Generate pilot extraction performance notes."""

from __future__ import annotations

import statistics
from pathlib import Path

from artifact_lab.experiments.pilot_performance.registry_filter import (
    DEFAULT_REGISTRY_PATH,
    filter_pilot_profiles,
)
from artifact_lab.ingest.profiling import (
    PHASE_NAMES,
    SLOW_REPO_THRESHOLD_S,
    ExtractionProfile,
    load_profiles,
    mean_or_none,
    median_or_none,
    timeout_phase_from_reason,
)

DEFAULT_PROFILE_PATH = Path("data/profiling/extraction_profile.parquet")
DEFAULT_E1_EXPORT = Path("exports/e1/pilot_performance.md")
DEFAULT_PAPER_NOTE = Path("../paper/notes/pilot_performance.md")

_BATCH_PHASES = frozenset({"parquet_write", "manifest_write"})


def _fmt_s(seconds: float | None) -> str:
    if seconds is None:
        return "n/a"
    return f"{seconds:.1f} s"


def _fmt_mb(n_bytes: int) -> str:
    return f"{n_bytes / 1_000_000:.1f} MB"


def report_failure_phase(profile: ExtractionProfile) -> str:
    """Human-readable slowest phase for failed repositories."""
    phase = profile.timeout_phase or timeout_phase_from_reason(profile.failure_reason)
    if phase:
        elapsed = profile.timings.phase_elapsed(phase)
        return f"timeout:{phase} ({elapsed:.1f} s)"
    dominant, value = profile.timings.dominant_phase()
    if profile.status == "failed" and (
        value <= 0 or dominant in _BATCH_PHASES or dominant == "unattributed"
    ):
        return "timeout/unknown"
    if value <= 0:
        return "unknown"
    return f"{dominant} ({value:.1f} s)"


def _display_failure_reason(profile: ExtractionProfile) -> str:
    if profile.failure_reason:
        return profile.failure_reason
    phase = profile.timeout_phase or timeout_phase_from_reason(profile.failure_reason)
    if phase:
        return f"timeout:{phase}"
    if profile.status == "failed" and report_failure_phase(profile) == "timeout/unknown":
        return "timeout"
    return "unknown"


def build_report(profiles: list[ExtractionProfile], *, test_mode: bool = False) -> str:
    if not profiles:
        header = "# Pilot extraction performance\n\nNo pilot registry profiling records found.\n"
        if test_mode:
            header = "# Pilot extraction performance (test mode)\n\nNo profiling records found.\n"
        return header

    succeeded = [p for p in profiles if p.status in {"ok", "no_matches"}]
    skipped = [p for p in profiles if p.status == "skipped"]
    failed = [p for p in profiles if p.status not in {"ok", "no_matches", "skipped"}]

    phase_totals = {phase: 0.0 for phase in PHASE_NAMES}
    for profile in profiles:
        t = profile.timings
        phase_totals["clone"] += t.clone_s
        phase_totals["inspection"] += t.inspection_s
        phase_totals["history"] += t.history_s
        phase_totals["detector"] += t.detector_s
        phase_totals["blobs"] += t.blobs_s
        phase_totals["parquet_write"] += t.parquet_write_s
        phase_totals["manifest_write"] += t.manifest_write_s
        phase_totals["cleanup"] += t.cleanup_s

    slowest_phase = max(phase_totals.items(), key=lambda item: item[1])
    slowest_repos = sorted(profiles, key=lambda p: p.timings.total_s, reverse=True)[:10]

    totals = [p.timings.total_s for p in profiles]
    clone_sizes = [p.clone_bytes for p in profiles if p.clone_bytes > 0]
    total_execution = sum(totals)

    title = "# Pilot extraction performance"
    if test_mode:
        title = "# Pilot extraction performance (test mode)"

    lines = [
        title,
        "",
        "Documentation-only summary of pilot registry extraction profiling.",
        "",
        "## Summary",
        "",
        f"- Profiled repositories: **{len(profiles)}**",
        f"- Total execution time (sum of per-repo totals): **{_fmt_s(total_execution)}**",
        f"- Median extraction time: **{_fmt_s(median_or_none(totals))}**",
        f"- Mean extraction time: **{_fmt_s(mean_or_none(totals))}**",
        f"- Successful extractions: **{len(succeeded)}**",
        f"- Skipped repositories: **{len(skipped)}**",
        f"- Failed repositories: **{len(failed)}**",
        f"- Slow-repo threshold: **{SLOW_REPO_THRESHOLD_S:.0f} s**",
        "",
        "## Slowest repositories",
        "",
        "| Rank | Repository | Total | Clone | Inspection | History | Detector | Blobs | Status |",
        "|------|------------|-------|-------|------------|---------|----------|-------|--------|",
    ]
    for rank, profile in enumerate(slowest_repos, start=1):
        t = profile.timings
        lines.append(
            f"| {rank} | {profile.repo_slug} | {_fmt_s(t.total_s)} | {_fmt_s(t.clone_s)} | "
            f"{_fmt_s(t.inspection_s)} | {_fmt_s(t.history_s)} | {_fmt_s(t.detector_s)} | "
            f"{_fmt_s(t.blobs_s)} | {profile.status} |"
        )

    lines.extend(["", "## Slowest phases (aggregate)", ""])
    grand = sum(phase_totals.values()) or 1.0
    for phase in sorted(phase_totals, key=lambda p: phase_totals[p], reverse=True):
        value = phase_totals[phase]
        share = 100.0 * value / grand
        lines.append(f"- **{phase}**: {value:.1f} s ({share:.1f}% of attributed phase time)")

    lines.extend(["", "## Clone sizes", ""])
    if not clone_sizes:
        lines.append("No clone size measurements recorded.")
    else:
        lines.extend(
            [
                f"- Median clone size: **{_fmt_mb(int(statistics.median(clone_sizes)))}**",
                f"- Mean clone size: **{_fmt_mb(int(statistics.mean(clone_sizes)))}**",
                f"- Largest clone: **{_fmt_mb(max(clone_sizes))}**",
                "",
                "| Repository | Clone size |",
                "|------------|------------|",
            ]
        )
        for profile in sorted(profiles, key=lambda p: p.clone_bytes, reverse=True):
            if profile.clone_bytes > 0:
                lines.append(f"| {profile.repo_slug} | {_fmt_mb(profile.clone_bytes)} |")

    lines.extend(["", "## Repositories skipped", ""])
    if not skipped:
        lines.append("None.")
    else:
        for profile in skipped:
            reason = profile.failure_reason or "skipped"
            lines.append(f"- {profile.repo_slug} ({reason})")

    lines.extend(["", "## Repositories failed", ""])
    if not failed:
        lines.append("None.")
    else:
        for profile in failed:
            reason = _display_failure_reason(profile)
            phase_label = report_failure_phase(profile)
            timeout_phase = profile.timeout_phase or timeout_phase_from_reason(profile.failure_reason) or "n/a"
            lines.append(
                f"- **{profile.repo_slug}**: total={profile.timings.total_s:.1f} s; "
                f"timeout_phase={timeout_phase}; slowest phase={phase_label}; failure_reason={reason}"
            )

    lines.extend(
        [
            "",
            "## Recommendations",
            "",
            _recommendations(slowest_phase[0], profiles, clone_sizes),
            "",
            "## Regeneration",
            "",
            "```bash",
            "make e1-pilot   # development",
            "make e1         # full pilot",
            "make paper      # copy exports to ../paper/",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def _recommendations(slowest_phase: str, profiles: list[ExtractionProfile], clone_sizes: list[int]) -> str:
    bullets: list[str] = []
    if slowest_phase == "history":
        bullets.append(
            "History traversal dominates aggregate time: quantify `git log --follow` calls per matched path "
            "before changing traversal strategy."
        )
    elif slowest_phase == "inspection":
        bullets.append(
            "Repository inspection dominates: compare cost of full-history path listing vs HEAD-only tree walks "
            "before caching or indexing paths."
        )
    elif slowest_phase == "detector":
        bullets.append(
            "Detector matching dominates unexpectedly: verify whether regex evaluation or path normalization "
            "scales with candidate path count."
        )
    elif slowest_phase == "clone":
        bullets.append(
            "Clone time dominates: separate network latency from on-disk pack size before parallelizing clones."
        )
    elif slowest_phase == "blobs":
        bullets.append(
            "Blob retrieval dominates: count `git show` calls and unchanged blob hashes before batching fetches."
        )
    else:
        bullets.append(
            f"Aggregate time concentrates in `{slowest_phase}`; keep collecting per-repo variance before optimizing."
        )

    if clone_sizes:
        med = statistics.median(clone_sizes)
        if med > 0 and max(clone_sizes) > 2 * med:
            bullets.append(
                f"Clone size is heavy-tailed (max {_fmt_mb(max(clone_sizes))}): mark oversized repos in the registry "
                "before scaling beyond the pilot."
            )

    failed = [p for p in profiles if p.status not in {"ok", "no_matches", "skipped"}]
    if failed:
        bullets.append(
            f"{len(failed)} repositories failed or timed out: inspect receipts and phase timings before re-running."
        )

    bullets.append("Measure first, optimize second — do not change detectors or infrastructure until variance is understood.")
    return "\n".join(f"- {item}" for item in bullets)


def write_report(
    *,
    profile_path: Path,
    output_path: Path,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    test_mode: bool = False,
) -> None:
    profiles = load_profiles(profile_path)
    profiles = filter_pilot_profiles(profiles, registry_path, test_mode=test_mode)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_report(profiles, test_mode=test_mode), encoding="utf-8")
