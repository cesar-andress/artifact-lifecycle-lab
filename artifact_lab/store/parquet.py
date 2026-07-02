"""Parquet read/write helpers."""

from __future__ import annotations

from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from artifact_lab.contracts.schemas import validate_columns


def write_parquet(table: pa.Table, path: Path, *, expected_columns: tuple[str, ...] | None = None) -> int:
    if expected_columns:
        validate_columns(table, expected_columns)
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, path)
    return table.num_rows


def read_parquet(path: Path) -> pa.Table:
    return pq.read_table(path)


def read_parquet_dir(directory: Path) -> pa.Table:
    files = sorted(directory.glob("*.parquet"))
    if not files:
        raise FileNotFoundError(f"no parquet files in {directory}")
    tables = [pq.read_table(f) for f in files]
    return pa.concat_tables(tables, promote_options="default")
