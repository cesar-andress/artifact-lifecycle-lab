"""L2 monthly file-state panel derivation."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pyarrow as pa

from platform.contracts.datasets import L2_DATASET_VERSION
from platform.contracts.schemas import (
    FILE_STATE_PANEL_COLUMNS,
    PanelState,
    file_state_panel_schema,
)
from platform.store.manifest import write_manifest
from platform.store.parquet import read_parquet, read_parquet_dir, write_parquet


def _as_utc(ts: datetime) -> datetime:
    if ts.tzinfo is None:
        return ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc)


def _month_end(month_start: date) -> datetime:
    if month_start.month == 12:
        nxt = date(month_start.year + 1, 1, 1)
    else:
        nxt = date(month_start.year, month_start.month + 1, 1)
    return datetime(nxt.year, nxt.month, nxt.day, tzinfo=timezone.utc) - timedelta(seconds=1)


def _month_starts(min_ts: datetime, max_ts: datetime) -> list[date]:
    cur = date(min_ts.year, min_ts.month, 1)
    end = date(max_ts.year, max_ts.month, 1)
    months: list[date] = []
    while cur <= end:
        months.append(cur)
        if cur.month == 12:
            cur = date(cur.year + 1, 1, 1)
        else:
            cur = date(cur.year, cur.month + 1, 1)
    return months


def classify_state(
    *,
    exists: bool,
    ever_existed: bool,
    age_days: int | None,
    days_since_touch: int | None,
    T: int,
) -> PanelState:
    if not ever_existed:
        return "absent"
    if not exists:
        return "deleted"
    assert age_days is not None and days_since_touch is not None
    if age_days < T:
        return "young"
    if days_since_touch <= T:
        return "active"
    return "stale"


def _panel_row(
    repo_id: str,
    repo_url: str,
    family: str,
    path: str,
    panel_month: date,
    state: PanelState,
    T: int,
    introduced_at: datetime | None,
    last_touch_at: datetime | None,
    days_since_last_touch: int | None,
    detector_version: str,
) -> dict:
    return {
        "repo_id": repo_id,
        "repo_url": repo_url,
        "family": family,
        "path": path,
        "panel_month": panel_month,
        "state": state,
        "T_days": T,
        "introduced_at": introduced_at,
        "last_touch_at": last_touch_at,
        "days_since_last_touch": days_since_last_touch,
        "detector_version": detector_version,
    }


def build_panel_rows(events_table: pa.Table, *, T: int) -> list[dict]:
    events = events_table.to_pylist()
    if not events:
        return []

    events.sort(key=lambda e: (e["repo_id"], e["path"], e["commit_time"]))
    min_ts = _as_utc(events[0]["commit_time"])
    max_ts = _as_utc(events[-1]["commit_time"])
    for e in events:
        ts = _as_utc(e["commit_time"])
        min_ts = min(min_ts, ts)
        max_ts = max(max_ts, ts)
    months = _month_starts(min_ts, max_ts)

    groups: dict[tuple, list[dict]] = {}
    for e in events:
        key = (e["repo_id"], e["repo_url"], e["family"], e["path"], e["detector_version"])
        groups.setdefault(key, []).append(e)

    rows: list[dict] = []
    for (repo_id, repo_url, family, path, detector_version), grp in groups.items():
        grp.sort(key=lambda e: e["commit_time"])
        introduced_at = _as_utc(grp[0]["commit_time"])
        delete_times = [_as_utc(e["commit_time"]) for e in grp if e["change_type"] == "delete"]
        deleted_at = min(delete_times) if delete_times else None

        for month in months:
            as_of = _month_end(month)
            if as_of < introduced_at:
                rows.append(
                    _panel_row(repo_id, repo_url, family, path, month, "absent", T, None, None, None, detector_version)
                )
                continue

            touch_rows = [e for e in grp if _as_utc(e["commit_time"]) <= as_of]
            if not touch_rows:
                rows.append(
                    _panel_row(repo_id, repo_url, family, path, month, "absent", T, None, None, None, detector_version)
                )
                continue

            last = touch_rows[-1]
            last_touch = _as_utc(last["commit_time"])
            exists = last["change_type"] != "delete"
            if deleted_at and as_of >= deleted_at:
                exists = False
            age_days = (as_of - introduced_at).days
            days_since_touch = (as_of - last_touch).days
            state = classify_state(
                exists=exists,
                ever_existed=True,
                age_days=age_days,
                days_since_touch=days_since_touch,
                T=T,
            )
            rows.append(
                _panel_row(
                    repo_id,
                    repo_url,
                    family,
                    path,
                    month,
                    state,
                    T,
                    introduced_at,
                    last_touch,
                    days_since_touch,
                    detector_version,
                )
            )
    return rows


def run_panel(*, events_path: Path, output_dir: Path, T: int = 180, dataset_version: str = L2_DATASET_VERSION) -> Path:
    events_path = events_path.resolve()
    if events_path.is_dir():
        table = read_parquet_dir(events_path)
    else:
        table = read_parquet(events_path)
    input_label = str(events_path)

    rows = build_panel_rows(table, T=T)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"panel_T{T}.parquet"
    if rows:
        panel_table = pa.Table.from_pylist(rows, schema=file_state_panel_schema())
    else:
        panel_table = pa.table(
            {col: pa.array([], type=file_state_panel_schema().field(col).type) for col in FILE_STATE_PANEL_COLUMNS}
        )
    row_count = write_parquet(panel_table, out_path, expected_columns=FILE_STATE_PANEL_COLUMNS)

    protocol_versions = table.column("detector_version").unique().to_pylist() if table.num_rows else []
    write_manifest(
        output_dir / f"manifest_T{T}.yaml",
        dataset_name="file_state_panel",
        version=f"T{T}",
        input_datasets=[input_label],
        protocol_version=str(protocol_versions[0]) if protocol_versions else "unknown",
        row_count=row_count,
        columns=FILE_STATE_PANEL_COLUMNS,
        extra={
            "T_days": T,
            "dataset_version": dataset_version,
        },
    )
    return out_path
