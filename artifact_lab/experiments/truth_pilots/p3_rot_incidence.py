"""Gate P3 — Rot incidence pilot (pre-scaling validation)."""

from __future__ import annotations

import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.truth_decay.longitudinal import (
    observations_to_rows,
    reconstruct_longitudinal_table,
)
from artifact_lab.experiments.truth_pilots.gates_common import (
    DEFAULT_L1_PATHS,
    DEFAULT_PILOT_EXPORT,
    DEFAULT_RQ1_LONGITUDINAL,
    VERIFIABLE_REFERENCE_TYPES,
    load_longitudinal_rows,
    load_p1_sample_keys,
    write_csv,
)

DAYS_PER_YEAR = 365.25
ROT_KILL_THRESHOLD = 0.025  # 2.5% references/year


@dataclass(frozen=True)
class RotTrajectory:
    repo_id: str
    instruction_path: str
    reference_type: str
    reference: str
    start_time: datetime
    end_time: datetime
    event_time: datetime | None
    censored: bool
    rot_event: bool


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _trajectory_key(row: dict) -> tuple[str, str, str, str]:
    return (row["repo_id"], row["instruction_path"], row["reference_type"], row["reference"])


def build_rot_trajectories(rows: list[dict]) -> list[RotTrajectory]:
    grouped: dict[tuple[str, str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        if row.get("reference_removed"):
            continue
        if row["reference_type"] not in VERIFIABLE_REFERENCE_TYPES:
            continue
        grouped[_trajectory_key(row)].append(row)

    trajectories: list[RotTrajectory] = []
    for key, events in grouped.items():
        events.sort(key=lambda r: r["commit_time"])
        start = _parse_time(events[0]["commit_time"])
        end = _parse_time(events[-1]["commit_time"])
        event_time: datetime | None = None
        for ev in events:
            if ev.get("first_failure") or (
                ev["state"] == "MISSING" and ev.get("transition", "").endswith("->MISSING")
            ):
                if event_time is None:
                    event_time = _parse_time(ev["commit_time"])
                break
        censored = event_time is None
        repo_id, instruction_path, ref_type, reference = key
        trajectories.append(
            RotTrajectory(
                repo_id=repo_id,
                instruction_path=instruction_path,
                reference_type=ref_type,
                reference=reference,
                start_time=start,
                end_time=end if censored else event_time,
                event_time=event_time,
                censored=censored,
                rot_event=not censored,
            )
        )
    return trajectories


def kaplan_meier_median_estimable(trajectories: list[RotTrajectory]) -> tuple[bool, float | None, str]:
    """Minimal KM gate check — not a full survival analysis module."""
    if not trajectories:
        return False, None, "no verifiable reference trajectories"

    points: list[tuple[float, int]] = []
    for traj in trajectories:
        days = float((traj.end_time - traj.start_time).days)
        if days < 0:
            continue
        points.append((days, 0 if traj.censored else 1))

    if not points:
        return False, None, "no valid follow-up durations"

    events = sum(event for _, event in points)
    if events < 5:
        return False, None, f"insufficient rot events for KM median (n={events})"

    censored_rate = sum(1 for _, event in points if event == 0) / len(points)
    if censored_rate > 0.85:
        return False, None, f"right-censoring too high ({censored_rate:.1%})"

    unique_times = sorted({time for time, _ in points})
    at_risk = len(points)
    survival = 1.0
    median: float | None = None
    for t in unique_times:
        d_i = sum(1 for time, event in points if event == 1 and time == t)
        c_i = sum(1 for time, event in points if event == 0 and time == t)
        if at_risk <= 0:
            break
        if d_i > 0:
            survival *= 1 - d_i / at_risk
        if survival <= 0.5 and median is None:
            median = t
        at_risk -= d_i + c_i

    if median is not None:
        return True, median, f"KM median ~{median:.0f} days ({median / DAYS_PER_YEAR:.2f} years)"
    return False, None, "survival curve did not fall to 0.5 — median not estimable"


def rot_events_csv_rows(trajectories: list[RotTrajectory]) -> list[dict]:
    return [
        {
            "repo_id": t.repo_id,
            "instruction_path": t.instruction_path,
            "reference_type": t.reference_type,
            "reference": t.reference,
            "start_time": t.start_time.isoformat(),
            "event_time": t.event_time.isoformat() if t.event_time else "",
            "end_time": t.end_time.isoformat(),
            "rot_event": "true" if t.rot_event else "false",
            "censored": "true" if t.censored else "false",
            "follow_up_days": (t.end_time - t.start_time).days,
        }
        for t in trajectories
    ]


def compute_rot_metrics(
    trajectories: list[RotTrajectory],
    p1_files: int,
    *,
    observation_span_years: float | None = None,
) -> dict:
    n_verifiable = len(trajectories)
    n_rot = sum(1 for t in trajectories if t.rot_event)
    n_censored = sum(1 for t in trajectories if t.censored)
    ref_years = sum((t.end_time - t.start_time).days / DAYS_PER_YEAR for t in trajectories)

    if observation_span_years is None or observation_span_years <= 0:
        observation_span_years = max(ref_years / n_verifiable, 1 / DAYS_PER_YEAR) if n_verifiable else 1.0

    ever_rot_rate = n_rot / n_verifiable if n_verifiable else 0.0
    rot_per_year = ever_rot_rate / observation_span_years

    files_with_rot: set[tuple[str, str]] = {
        (t.repo_id, t.instruction_path) for t in trajectories if t.rot_event
    }

    km_ok, km_median_days, km_note = kaplan_meier_median_estimable(trajectories)

    return {
        "p1_files_target": p1_files,
        "verifiable_references": n_verifiable,
        "references_ever_missing": n_rot,
        "ever_rot_proportion": ever_rot_rate,
        "observation_span_years": observation_span_years,
        "rot_incidence_per_year": rot_per_year,
        "rot_incidence_pct_per_year": rot_per_year * 100,
        "files_with_rot_event": len(files_with_rot),
        "right_censoring_rate": n_censored / n_verifiable if n_verifiable else 0.0,
        "reference_years": ref_years,
        "km_median_estimable": km_ok,
        "km_median_days": km_median_days,
        "km_note": km_note,
        "kill_rot_below_threshold": rot_per_year < ROT_KILL_THRESHOLD,
    }


def _p3_markdown(metrics: dict, *, source: str, p1_matched: int) -> str:
    gate = "PASS" if not metrics["kill_rot_below_threshold"] and metrics["km_median_estimable"] else "FAIL"
    if metrics["kill_rot_below_threshold"]:
        gate = "FAIL"
    elif not metrics["km_median_estimable"]:
        gate = "CONDITIONAL"

    lines = [
        "# Gate P3 — Rot Incidence Pilot",
        "",
        "## Scope",
        f"- P1 sample files (target): **{metrics['p1_files_target']}**",
        f"- P1 files with longitudinal data: **{p1_matched}**",
        f"- Longitudinal source: `{source}`",
        "",
        "## Rot metrics",
        f"- Verifiable references (trajectories): **{metrics['verifiable_references']}**",
        f"- References that ever become missing (rot): **{metrics['references_ever_missing']}** "
        f"({metrics['ever_rot_proportion']:.1%} of verifiable)",
        f"- Observation span: **{metrics['observation_span_years']:.2f} years**",
        f"- Rot incidence: **{metrics['rot_incidence_pct_per_year']:.2f}%** of verifiable references/year",
        f"- Files with ≥1 rot event: **{metrics['files_with_rot_event']}**",
        f"- Right-censoring rate: **{metrics['right_censoring_rate']:.1%}**",
        f"- Reference-years of follow-up: **{metrics['reference_years']:.1f}**",
        "",
        "## Kaplan-Meier median estimability",
        f"- Estimable: **{'Yes' if metrics['km_median_estimable'] else 'No'}**",
        f"- Note: {metrics['km_note']}",
    ]
    if metrics["km_median_days"] is not None:
        lines.append(f"- Approximate KM median: **{metrics['km_median_days']:.0f} days**")

    lines.extend(
        [
            "",
            "## Kill criteria (protocol)",
            f"- Rot incidence <2–3%/year: **{'TRIGGERED' if metrics['kill_rot_below_threshold'] else 'not triggered'}** "
            f"({metrics['rot_incidence_pct_per_year']:.2f}%)",
            f"- KM median not estimable (censoring): **{'TRIGGERED' if not metrics['km_median_estimable'] else 'not triggered'}**",
            "",
            f"## Gate verdict: **{gate}**",
            "",
        ]
    )
    return "\n".join(lines)


def run_p3_rot_incidence_gate(
    *,
    output_dir: Path,
    p1_summary_csv: Path,
    longitudinal_csv: Path | None = None,
    l1_paths: list[Path] | None = None,
    blobs_dir: Path | None = None,
    scratch_dir: Path | None = None,
    clone_timeout: int = 180,
    reconstruct_missing: bool = False,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    events_csv = output_dir / "p3_rot_events.csv"
    report_md = output_dir / "p3_rot_incidence.md"

    p1_keys = load_p1_sample_keys(p1_summary_csv)
    source = "existing longitudinal CSV"

    if longitudinal_csv and longitudinal_csv.exists():
        rows = load_longitudinal_rows(longitudinal_csv, file_filter=p1_keys)
        matched = len({(r["repo_id"], r["instruction_path"]) for r in rows})
        if reconstruct_missing and matched < len(p1_keys) and l1_paths and blobs_dir and scratch_dir:
            missing = p1_keys - {(r["repo_id"], r["instruction_path"]) for r in rows}
            extra = reconstruct_longitudinal_table(
                l1_paths=l1_paths,
                blobs_dir=blobs_dir,
                scratch_dir=scratch_dir,
                clone_timeout=clone_timeout,
                file_filter=missing,
            )
            rows.extend(observations_to_rows(extra))
            source = "longitudinal CSV + reconstruction for missing P1 files"
            matched = len({(r["repo_id"], r["instruction_path"]) for r in rows})
    elif l1_paths and blobs_dir and scratch_dir:
        observations = reconstruct_longitudinal_table(
            l1_paths=l1_paths,
            blobs_dir=blobs_dir,
            scratch_dir=scratch_dir,
            clone_timeout=clone_timeout,
            file_filter=p1_keys,
        )
        rows = observations_to_rows(observations)
        matched = len({(r["repo_id"], r["instruction_path"]) for r in rows})
        source = "reconstructed from L1"
    else:
        raise FileNotFoundError("longitudinal data required: provide CSV or L1+blobs+scratch")

    trajectories = build_rot_trajectories(rows)
    times = [_parse_time(r["commit_time"]) for r in rows if not r.get("reference_removed")]
    span_years = (max(times) - min(times)).days / DAYS_PER_YEAR if times else 1.0
    metrics = compute_rot_metrics(trajectories, p1_files=len(p1_keys), observation_span_years=span_years)
    write_csv(rot_events_csv_rows(trajectories), events_csv)
    atomic_write_text(report_md, _p3_markdown(metrics, source=source, p1_matched=matched))
    return report_md, events_csv
