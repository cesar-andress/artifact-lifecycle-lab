"""Figure 1 — cumulative adoption timeline of AI convention files."""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from artifact_lab.experiments.e1_adoption_census.census import build_path_census_rows


def _month_start(ts: datetime) -> date:
    ts = ts.astimezone(timezone.utc)
    return date(ts.year, ts.month, 1)


def build_adoption_timeline(path_rows: list[dict]) -> list[dict]:
    """Monthly new and cumulative first appearances of matched convention paths."""
    by_month: dict[date, int] = defaultdict(int)
    for row in path_rows:
        month = _month_start(row["first_appearance"])
        by_month[month] += 1

    if not by_month:
        return []

    months = sorted(by_month)
    cumulative = 0
    rows: list[dict] = []
    for month in months:
        new_files = by_month[month]
        cumulative += new_files
        rows.append(
            {
                "month": month.isoformat(),
                "new_convention_files": new_files,
                "cumulative_convention_files": cumulative,
            }
        )
    return rows


def write_fig1_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["month", "new_convention_files", "cumulative_convention_files"],
        )
        writer.writeheader()
        writer.writerows(rows)


def render_fig1_pdf(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        fig, ax = plt.subplots(figsize=(6.5, 3.75))
        ax.text(0.5, 0.5, "No matched convention files", ha="center", va="center")
        ax.set_axis_off()
        fig.savefig(path, format="pdf", bbox_inches="tight")
        plt.close(fig)
        return

    months = [datetime.fromisoformat(r["month"]).date() for r in rows]
    cumulative = [r["cumulative_convention_files"] for r in rows]

    fig, ax = plt.subplots(figsize=(6.5, 3.75))
    ax.plot(months, cumulative, color="#1f4e79", linewidth=2.0, marker="o", markersize=3.5)
    ax.set_xlabel("Month of first appearance")
    ax.set_ylabel("Cumulative convention files")
    ax.set_title("Adoption timeline of AI convention files")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_minor_locator(mdates.MonthLocator((1, 4, 7, 10)))
    ax.grid(True, axis="y", linestyle="--", linewidth=0.5, alpha=0.6)
    ax.set_xlim(months[0], months[-1])
    ax.set_ylim(0, max(cumulative) * 1.08 if cumulative else 1)
    fig.tight_layout()
    fig.savefig(path, format="pdf", bbox_inches="tight")
    plt.close(fig)


def run_fig1(*, events: list[dict], csv_path: Path, pdf_path: Path) -> list[dict]:
    path_rows = build_path_census_rows(events)
    timeline = build_adoption_timeline(path_rows)
    write_fig1_csv(timeline, csv_path)
    render_fig1_pdf(timeline, pdf_path)
    return timeline
