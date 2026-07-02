"""Parquet read/write helpers."""

from __future__ import annotations

from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from artifact_lab.contracts.schemas import validate_columns
from artifact_lab.execution.atomic_io import atomic_write_parquet


def write_parquet(table: pa.Table, path: Path, *, expected_columns: tuple[str, ...] | None = None) -> int:
    return atomic_write_parquet(table, path, expected_columns=expected_columns)


def read_parquet(path: Path) -> pa.Table:
    return pq.read_table(path)


def read_parquet_dir(directory: Path) -> pa.Table:
    files = sorted(directory.glob("*.parquet"))
    if not files:
        raise FileNotFoundError(f"no parquet files in {directory}")
    tables = [pq.read_table(f) for f in files]
    return pa.concat_tables(tables, promote_options="default")
