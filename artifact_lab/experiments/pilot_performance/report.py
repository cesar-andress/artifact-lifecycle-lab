"""Generate pilot extraction performance notes for the paper repository."""

from __future__ import annotations

import statistics
from pathlib import Path

from artifact_lab.ingest.profiling import (
    PHASE_NAMES,
    SLOW_REPO_THRESHOLD_S,
    load_profiles,
    median_or_none,
    repo_slug,
)

DEFAULT_PROFILE_PATH = Path("data/profiling/extraction_profile.parquet")
DEFAULT_PAPER_NOTE = Path("../paper/notes/pilot_performance.md")


def _fmt_s(seconds: float | None) -> str:
    if seconds is None:
        return "n/a"
    return f"{seconds:.1f}s"


def _fmt_mb(n_bytes: int) -> str:
    return f"{n_bytes / 1_000_000:.1f} MB"


def build_report(profiles: list) -> str:
    if not profiles:
        return "# Pilot extraction performance\n\nNo profiling records found.\n"

    succeeded = [p for p in profiles if p.status in {"ok", "no_matches"}]
    phase_totals = {phase: 0.0 for phase in PHASE_NAMES}
    for profile in profiles:
        phase_totals["clone"] += profile.timings.clone_s
        phase_totals["history"] += profile.timings.history_s
        phase_totals["detector"] += profile.timings.detector_s
        phase_totals["blobs"] += profile.timings.blobs_s
        phase_totals["parquet_write"] += profile.timings.parquet_write_s
        phase_totals["cleanup"] += profile.timings.cleanup_s

    slowest_phase = max(phase_totals.items(), key=lambda item: item[1])
    slowest_repos = sorted(profiles, key=lambda p: p.timings.total_s, reverse=True)[:5]

    totals = [p.timings.total_s for p in profiles]
    clone_sizes = [p.clone_bytes for p in profiles if p.clone_bytes > 0]

    lines = [
        "# Pilot extraction performance",
        "",
        f"Profiled repositories: **{len(profiles)}**",
        f"Successful extractions: **{len(succeeded)}**",
        "",
        "## Summary",
        "",
        f"- Median extraction time: **{_fmt_s(median_or_none(totals))}**",
        f"- Median clone size: **{_fmt_mb(int(statistics.median(clone_sizes))) if clone_sizes else 'n/a'}**",
        f"- Slowest phase (aggregate): **{slowest_phase[0]}** ({slowest_phase[1]:.1f}s total)",
        f"- Slow-repo threshold: **{SLOW_REPO_THRESHOLD_S / 60:.0f} minutes**",
        "",
        "## Slowest repositories",
        "",
        "| Rank | Repository | Total | Clone | History | Detector | Blobs | Status |",
        "|------|------------|-------|-------|---------|----------|-------|--------|",
    ]
    for rank, profile in enumerate(slowest_repos, start=1):
        t = profile.timings
        lines.append(
            f"| {rank} | {profile.repo_slug} | {_fmt_s(t.total_s)} | {_fmt_s(t.clone_s)} | "
            f"{_fmt_s(t.history_s)} | {_fmt_s(t.detector_s)} | {_fmt_s(t.blobs_s)} | {profile.status} |"
        )

    lines.extend(
        [
            "",
            "## Phase totals",
            "",
            "| Phase | Total time | Share |",
            "|-------|------------|-------|",
        ]
    )
    grand = sum(phase_totals.values()) or 1.0
    for phase in PHASE_NAMES:
        value = phase_totals[phase]
        share = 100.0 * value / grand
        lines.append(f"| {phase} | {value:.1f}s | {share:.1f}% |")

    over_threshold = [p for p in profiles if p.timings.total_s > SLOW_REPO_THRESHOLD_S]
    lines.extend(["", "## Repositories over threshold", ""])
    if not over_threshold:
        lines.append("None.")
    else:
        for profile in sorted(over_threshold, key=lambda p: p.timings.total_s, reverse=True):
            phase, value = profile.timings.dominant_phase()
            lines.append(
                f"- **{profile.repo_slug}**: total={profile.timings.total_s:.1f}s; "
                f"slowest phase={phase} ({value:.1f}s)"
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
            "python3.12 -m artifact_lab.ingest extract \\",
            "  --registry data/registry/pilot_repos.csv \\",
            "  --family ai_conventions_v1 --force",
            "python3.12 -m artifact_lab.experiments.pilot_performance",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def _recommendations(slowest_phase: str, profiles: list, clone_sizes: list[int]) -> str:
    bullets: list[str] = []
    if slowest_phase == "history":
        bullets.append(
            "History traversal dominates: profile `git log --follow` call counts per matched path "
            "before changing algorithms."
        )
    elif slowest_phase == "detector":
        bullets.append(
            "Path discovery dominates: measure whether `git log --name-only` or HEAD tree walks "
            "are the bottleneck before caching path lists."
        )
    elif slowest_phase == "clone":
        bullets.append(
            "Clone time dominates: record network vs pack size variance; consider registry-level "
            "size hints before parallelizing clones."
        )
    elif slowest_phase == "blobs":
        bullets.append(
            "Blob materialization dominates: count blob fetches per repo before batching or skipping "
            "unchanged content hashes."
        )
    else:
        bullets.append(
            f"Aggregate time concentrates in `{slowest_phase}`; collect finer-grained timings before optimizing."
        )

    if clone_sizes:
        med = statistics.median(clone_sizes)
        if med > 0 and max(clone_sizes) > 2 * med:
            largest = max(clone_sizes)
            bullets.append(
                f"Clone size is heavy-tailed (max {_fmt_mb(largest)}): flag oversized repos in the registry "
                "before scaling the pilot."
            )

    failed = [p for p in profiles if p.status not in {"ok", "no_matches", "skipped"}]
    if failed:
        bullets.append(
            f"{len(failed)} repositories failed or timed out: inspect receipts and dominant phases before re-running."
        )

    bullets.append("Do not optimize until phase-level variance is understood across all pilot repositories.")
    return "\n".join(f"- {item}" for item in bullets)


def write_report(*, profile_path: Path, output_path: Path) -> None:
    profiles = load_profiles(profile_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_report(profiles), encoding="utf-8")
