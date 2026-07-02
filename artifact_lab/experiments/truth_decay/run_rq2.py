"""RQ2 survival analysis — reference half-life."""

from __future__ import annotations

import csv
import statistics
from io import StringIO
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.truth_pilots.gates_common import (
    DEFAULT_RQ1_LONGITUDINAL,
    load_longitudinal_rows,
)
from artifact_lab.experiments.truth_decay.rq2_figures import (
    render_figure_censoring,
    render_figure_cumulative_hazard,
    render_figure_survival,
)
from artifact_lab.experiments.truth_decay.survival_dataset import (
    OUTCOME_FIRST_MISSING,
    build_survival_dataset,
    records_to_rows,
)
from artifact_lab.experiments.truth_decay.survival_estimators import (
    censoring_summary,
    kaplan_meier_with_na,
    median_survival,
    median_survival_ci,
    repair_cumulative_incidence,
)

DEFAULT_RQ2_EXPORT = Path("exports/truth_decay_pilot")


def _write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        atomic_write_text(path, "")
        return
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    atomic_write_text(path, buffer.getvalue())


def _survival_at(points: list, day: float) -> float | None:
    if not points:
        return None
    for pt in points:
        if pt.time_days >= day:
            return pt.survival
    return points[-1].survival


def _conditional_median_failure(records) -> float | None:
    failed = [r.duration_days for r in records if r.outcome == OUTCOME_FIRST_MISSING]
    if not failed:
        return None
    return float(statistics.median(failed))


def _summary_markdown(
    *,
    meta: dict,
    censoring: dict[str, int],
    median: float | None,
    median_lo: float | None,
    median_hi: float | None,
    n_events: int,
    cohort: int,
    repair_incidence_final: float,
    survival_30: float | None,
    survival_90: float | None,
    survival_180: float | None,
    survival_365: float | None,
    conditional_median_failure: float | None,
) -> str:
    event_rate = n_events / cohort if cohort else 0.0
    censor_rate = censoring.get("right_censored", 0) / cohort if cohort else 0.0

    lines = [
        "# RQ2 — Reference Half-Life (Survival Analysis)",
        "",
        "## Research question",
        "",
        "**RQ2:** What is the survival distribution (half-life) of verifiable references",
        "in machine-consumed documentation?",
        "",
        "## Methodological assumptions (explicit)",
        "",
        "1. **Time origin:** first `VERIFIED` observation per reference (protocol RQ2).",
        "2. **Event:** first `MISSING` after origin (single-failure, non-recurrent).",
        "3. **Cohort:** verifiable types only (`path`, `directory`, `script_name`, `dependency`).",
        "4. **Exclusion:** references never observed as VERIFIED (left-truncated / born stale).",
        "5. **Censoring:** end of follow-up or reference removal without failure; `DELETED` coded separately.",
        "6. **Independence:** references treated as independent; **repo clustering not adjusted** (naive Greenwood CI).",
        "7. **Discrete snapshots:** inter-commit gaps; durations in calendar days between L1 events.",
        "8. **Competing risks:** repair and deletion not modeled in primary KM; repair reported separately.",
        "",
        "## Known limitations",
        "",
        "- Repo-side fixes without instruction edits appear as continued VERIFIED (immortal time bias risk is low but non-zero).",
        "- Engineering cohort (pilot + E1-100), not E1-1000 scientific frame.",
        "- Zero-day failures common (commit-snapshot granularity).",
        "",
        "## Cohort",
        "",
        f"- References entering at VERIFIED: **{cohort}**",
        f"- Excluded (never VERIFIED in panel): **{meta.get('excluded_never_verified', 0)}**",
        f"- Primary failure events (first missing): **{n_events}** ({event_rate:.1%})",
        f"- Right-censored: **{censoring.get('right_censored', 0)}** ({censor_rate:.1%})",
        f"- Censored at instruction-file deletion: **{censoring.get('deleted', 0)}**",
        "",
        "## Survival estimates",
        "",
    ]
    if median is not None:
        lines.append(f"- **Median survival (half-life):** **{median:.1f} days**")
        if median_lo is not None and median_hi is not None:
            lines.append(f"- **95% CI for median:** [{median_lo:.1f}, {median_hi:.1f}] days")
    else:
        lines.append("- **Median survival:** not reached (survival > 0.5 at end of follow-up)")

    lines.append(f"- **Repairs after failure (count):** {censoring.get('repaired_after_failure', 0)}")
    lines.append(f"- **Final cumulative repair incidence (post-failure):** {repair_incidence_final:.1%}")

    lines.extend(["", "## Survival function (selected horizons)", ""])
    for label, val in (
        ("30 days", survival_30),
        ("90 days", survival_90),
        ("180 days", survival_180),
        ("365 days", survival_365),
    ):
        if val is not None:
            lines.append(f"- **S({label}):** {val:.3f}")

    if conditional_median_failure is not None:
        lines.extend(
            [
                "",
                "## Conditional failure time (non-KM)",
                "",
                f"- Among references with observed first missing (n={n_events}), "
                f"median time from first VERIFIED to first MISSING: **{conditional_median_failure:.1f} days**",
                "- RQ1 reported ~16 days using a simpler exploratory median over all trajectories with both "
                "states present; RQ2 enforces post-origin failure ordering and censoring, yielding a higher "
                "conditional median among observed failures.",
                "- This is **not** the Kaplan–Meier half-life because most references are right-censored without failure.",
            ]
        )

    if median is not None:
        half_life_line = f"- **Half-life (KM median):** **{median:.1f} days**"
        if median_lo is not None and median_hi is not None:
            half_life_line += f" (95% CI: [{median_lo:.1f}, {median_hi:.1f}])"
    else:
        half_life_note = (
            f"(S(365d) ≈ {survival_365:.3f})."
            if survival_365 is not None
            else "(long follow-up not reached)."
        )
        half_life_line = (
            "- **Half-life (KM median):** not estimable in this cohort — survival remains > 0.5 through follow-up "
            + half_life_note
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            half_life_line,
            f"- **Primary decay signal:** {event_rate:.1%} of verifiable references that reach VERIFIED subsequently fail; "
            "decay is rare but non-negligible.",
            "- **Repair:** among post-failure follow-up, cumulative repair incidence reaches "
            f"{repair_incidence_final:.1%}.",
            "",
        ]
    )

    lines.extend(
        [
            "## Outputs",
            "",
            "- `rq2_survival.csv` — per-reference survival records",
            "- `figure_survival.pdf` — Kaplan–Meier with 95% CI",
            "- `figure_cumulative_hazard.pdf` — Nelson–Aalen cumulative hazard",
            "- `figure_censoring.pdf` — event vs censoring distribution",
            "",
        ]
    )
    return "\n".join(lines)


def run_rq2_survival_analysis(
    *,
    longitudinal_csv: Path = DEFAULT_RQ1_LONGITUDINAL,
    output_dir: Path = DEFAULT_RQ2_EXPORT,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    survival_csv = output_dir / "rq2_survival.csv"
    summary_md = output_dir / "rq2_summary.md"
    fig_survival = output_dir / "figure_survival.pdf"
    fig_hazard = output_dir / "figure_cumulative_hazard.pdf"
    fig_censor = output_dir / "figure_censoring.pdf"

    rows = load_longitudinal_rows(longitudinal_csv)
    records, meta = build_survival_dataset(rows)
    record_rows = records_to_rows(records)

    km_points = kaplan_meier_with_na(records)
    censoring = censoring_summary(records)
    repair_points = repair_cumulative_incidence(records)
    repair_final = repair_points[-1].cumulative_incidence if repair_points else 0.0

    median = median_survival(km_points)
    median_lo, median_hi = median_survival_ci(km_points)
    n_events = censoring.get(OUTCOME_FIRST_MISSING, 0)
    s30 = _survival_at(km_points, 30)
    s90 = _survival_at(km_points, 90)
    s180 = _survival_at(km_points, 180)
    s365 = _survival_at(km_points, 365)
    cond_median = _conditional_median_failure(records)

    # Per-reference survival dataset only (curve estimates in summary + figures).
    _write_csv(record_rows, survival_csv)

    atomic_write_text(
        summary_md,
        _summary_markdown(
            meta=meta,
            censoring=censoring,
            median=median,
            median_lo=median_lo,
            median_hi=median_hi,
            n_events=n_events,
            cohort=len(records),
            repair_incidence_final=repair_final,
            survival_30=s30,
            survival_90=s90,
            survival_180=s180,
            survival_365=s365,
            conditional_median_failure=cond_median,
        ),
    )

    render_figure_survival(km_points, fig_survival)
    render_figure_cumulative_hazard(km_points, fig_hazard)
    render_figure_censoring(censoring, fig_censor)

    return {
        "survival_csv": survival_csv,
        "summary": summary_md,
        "figure_survival": fig_survival,
        "figure_hazard": fig_hazard,
        "figure_censoring": fig_censor,
    }
