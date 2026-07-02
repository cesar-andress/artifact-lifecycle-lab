"""E1 — repository adoption census from L1 file event log."""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pyarrow as pa

from artifact_lab.protocol.detector import match_pattern_id
from artifact_lab.store.parquet import read_parquet, write_parquet

CENSUS_COLUMNS: tuple[str, ...] = (
    "repo_id",
    "repo_url",
    "protocol_family",
    "artifact_family",
    "first_appearance",
    "last_appearance",
    "currently_present",
    "total_matched_files",
)

PATH_CENSUS_COLUMNS: tuple[str, ...] = (
    "repo_id",
    "repo_url",
    "protocol_family",
    "artifact_family",
    "path",
    "first_appearance",
    "last_appearance",
    "currently_present",
    "n_events",
)


def _as_utc(ts: datetime) -> datetime:
    if ts.tzinfo is None:
        return ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc)


def _path_currently_present(events: list[dict]) -> bool:
    ordered = sorted(events, key=lambda e: (_as_utc(e["commit_time"]), e["commit_sha"]))
    return ordered[-1]["change_type"] != "delete"


def build_path_census_rows(events: list[dict]) -> list[dict]:
    groups: dict[tuple[str, str, str, str, str], list[dict]] = defaultdict(list)
    for event in events:
        protocol_family = event["family"]
        artifact_family = match_pattern_id(event["path"], protocol_family)
        if artifact_family is None:
            continue
        key = (
            event["repo_id"],
            event["repo_url"],
            protocol_family,
            artifact_family,
            event["path"],
        )
        groups[key].append(event)

    rows: list[dict] = []
    for (repo_id, repo_url, protocol_family, artifact_family, path), grp in sorted(groups.items()):
        times = [_as_utc(e["commit_time"]) for e in grp]
        rows.append(
            {
                "repo_id": repo_id,
                "repo_url": repo_url,
                "protocol_family": protocol_family,
                "artifact_family": artifact_family,
                "path": path,
                "first_appearance": min(times),
                "last_appearance": max(times),
                "currently_present": _path_currently_present(grp),
                "n_events": len(grp),
            }
        )
    return rows


def build_repo_family_census_rows(path_rows: list[dict]) -> list[dict]:
    groups: dict[tuple[str, str, str, str], list[dict]] = defaultdict(list)
    for row in path_rows:
        key = (row["repo_id"], row["repo_url"], row["protocol_family"], row["artifact_family"])
        groups[key].append(row)

    rows: list[dict] = []
    for (repo_id, repo_url, protocol_family, artifact_family), grp in sorted(groups.items()):
        firsts = [_as_utc(r["first_appearance"]) for r in grp]
        lasts = [_as_utc(r["last_appearance"]) for r in grp]
        rows.append(
            {
                "repo_id": repo_id,
                "repo_url": repo_url,
                "protocol_family": protocol_family,
                "artifact_family": artifact_family,
                "first_appearance": min(firsts),
                "last_appearance": max(lasts),
                "currently_present": any(r["currently_present"] for r in grp),
                "total_matched_files": len(grp),
            }
        )
    return rows


def build_repo_census_rows(path_rows: list[dict]) -> list[dict]:
    groups: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in path_rows:
        key = (row["repo_id"], row["repo_url"], row["protocol_family"])
        groups[key].append(row)

    rows: list[dict] = []
    for (repo_id, repo_url, protocol_family), grp in sorted(groups.items()):
        families = sorted({r["artifact_family"] for r in grp})
        firsts = [_as_utc(r["first_appearance"]) for r in grp]
        lasts = [_as_utc(r["last_appearance"]) for r in grp]
        rows.append(
            {
                "repo_id": repo_id,
                "repo_url": repo_url,
                "protocol_family": protocol_family,
                "artifact_families": ",".join(families),
                "first_appearance": min(firsts),
                "last_appearance": max(lasts),
                "currently_present": any(r["currently_present"] for r in grp),
                "total_matched_files": len(grp),
            }
        )
    return rows


def build_census_from_events(events: list[dict]) -> dict[str, list[dict]]:
    path_rows = build_path_census_rows(events)
    return {
        "path": path_rows,
        "repo_family": build_repo_family_census_rows(path_rows),
        "repo": build_repo_census_rows(path_rows),
    }


def _write_csv(rows: list[dict], path: Path, columns: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns))
        writer.writeheader()
        for row in rows:
            out = dict(row)
            for key in ("first_appearance", "last_appearance"):
                if key in out and isinstance(out[key], datetime):
                    out[key] = out[key].isoformat()
            writer.writerow({col: out.get(col) for col in columns})


def _write_parquet(rows: list[dict], path: Path, columns: tuple[str, ...]) -> None:
    table = pa.Table.from_pylist(rows) if rows else pa.table({col: [] for col in columns})
    write_parquet(table, path, expected_columns=None)


def write_census_outputs(census: dict[str, list[dict]], output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "path_parquet": output_dir / "path_census.parquet",
        "path_csv": output_dir / "path_census.csv",
        "repo_family_parquet": output_dir / "repo_family_census.parquet",
        "repo_family_csv": output_dir / "repo_family_census.csv",
        "repo_parquet": output_dir / "repo_census.parquet",
        "repo_csv": output_dir / "repo_census.csv",
    }
    _write_parquet(census["path"], paths["path_parquet"], PATH_CENSUS_COLUMNS)
    _write_csv(census["path"], paths["path_csv"], PATH_CENSUS_COLUMNS)
    _write_parquet(census["repo_family"], paths["repo_family_parquet"], CENSUS_COLUMNS)
    _write_csv(census["repo_family"], paths["repo_family_csv"], CENSUS_COLUMNS)
    repo_columns = (
        "repo_id",
        "repo_url",
        "protocol_family",
        "artifact_families",
        "first_appearance",
        "last_appearance",
        "currently_present",
        "total_matched_files",
    )
    _write_parquet(census["repo"], paths["repo_parquet"], repo_columns)
    _write_csv(census["repo"], paths["repo_csv"], repo_columns)
    return paths


def run_census(*, l1_path: Path, output_dir: Path) -> dict[str, list[dict]]:
    events = read_parquet(l1_path).to_pylist()
    census = build_census_from_events(events)
    write_census_outputs(census, output_dir)
    return census
