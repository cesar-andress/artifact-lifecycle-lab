"""Table 1 — artifact family frequencies."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


def build_table1_rows(repo_family_rows: list[dict]) -> list[dict]:
    totals: dict[str, dict[str, int]] = defaultdict(lambda: {"n_repos": 0, "n_files": 0})
    for row in repo_family_rows:
        family = row["artifact_family"]
        totals[family]["n_repos"] += 1
        totals[family]["n_files"] += int(row["total_matched_files"])

    n_repos_total = len({r["repo_id"] for r in repo_family_rows})
    rows: list[dict] = []
    for family in sorted(totals):
        counts = totals[family]
        share = (counts["n_repos"] / n_repos_total * 100.0) if n_repos_total else 0.0
        rows.append(
            {
                "artifact_family": family,
                "n_repos": counts["n_repos"],
                "n_files": counts["n_files"],
                "share_repos_pct": round(share, 2),
            }
        )
    return rows


def write_table1(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["artifact_family", "n_repos", "n_files", "share_repos_pct"],
        )
        writer.writeheader()
        writer.writerows(rows)


def run_table1(*, repo_family_rows: list[dict], output_path: Path) -> list[dict]:
    rows = build_table1_rows(repo_family_rows)
    write_table1(rows, output_path)
    return rows
