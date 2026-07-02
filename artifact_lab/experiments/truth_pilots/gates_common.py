"""Shared helpers for pre-scaling validation gates (P3–P5)."""

from __future__ import annotations

import csv
from pathlib import Path

VERIFIABLE_REFERENCE_TYPES = frozenset({"path", "directory", "script_name", "dependency"})

DEFAULT_L1_PATHS = (
    Path("data/l1/file_event_log/v1/events.parquet"),
    Path("data/l1/e1_100/v1/events.parquet"),
)
DEFAULT_PILOT_EXPORT = Path("exports/truth_pilot")
DEFAULT_RQ1_LONGITUDINAL = Path("exports/truth_decay_pilot/reference_longitudinal.csv")


def load_p1_sample_keys(summary_csv: Path) -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    with summary_csv.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            keys.add((row["repo_id"], row["instruction_path"]))
    return keys


def load_repo_urls_from_l1(l1_paths: list[Path]) -> dict[str, str]:
    import pyarrow.parquet as pq

    repos: dict[str, str] = {}
    for l1_path in l1_paths:
        path = l1_path.resolve()
        if path.is_dir():
            parquet = path / "events.parquet"
            if not parquet.exists():
                continue
            table = pq.read_table(parquet)
        elif path.exists() and path.stat().st_size > 100:
            table = pq.read_table(path)
        else:
            continue
        for row in table.to_pylist():
            repos[row["repo_id"]] = row["repo_url"]
    return repos


def _csv_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).lower() in ("true", "1", "yes")


def load_longitudinal_rows(
    csv_path: Path,
    *,
    file_filter: set[tuple[str, str]] | None = None,
) -> list[dict]:
    rows: list[dict] = []
    with csv_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if file_filter is not None:
                key = (row["repo_id"], row["instruction_path"])
                if key not in file_filter:
                    continue
            row["reference_removed"] = _csv_bool(row.get("reference_removed"))
            row["reference_added"] = _csv_bool(row.get("reference_added"))
            row["first_failure"] = _csv_bool(row.get("first_failure"))
            row["repair_event"] = _csv_bool(row.get("repair_event"))
            rows.append(row)
    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    from artifact_lab.execution.atomic_io import atomic_write_text
    from io import StringIO

    if not rows:
        atomic_write_text(path, "")
        return
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    atomic_write_text(path, buffer.getvalue())
