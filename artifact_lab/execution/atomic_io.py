"""Atomic filesystem writes: tmp → fsync → verify → rename."""

from __future__ import annotations

import os
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from artifact_lab.contracts.schemas import validate_columns


def _tmp_path(path: Path) -> Path:
    return path.with_name(path.name + ".tmp")


def _fsync_path(path: Path) -> None:
    with path.open("rb") as fh:
        os.fsync(fh.fileno())
    try:
        os.fsync(os.open(path.parent, os.O_RDONLY))
    except OSError:
        pass


def atomic_replace(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    _fsync_path(src)
    os.replace(src, dest)


def atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = _tmp_path(path)
    try:
        tmp.write_bytes(data)
        if len(data) != tmp.stat().st_size:
            raise OSError(f"size mismatch after write: {tmp}")
        atomic_replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)


def atomic_write_text(path: Path, text: str, *, encoding: str = "utf-8") -> None:
    atomic_write_bytes(path, text.encode(encoding))


def atomic_write_parquet(
    table: pa.Table,
    path: Path,
    *,
    expected_columns: tuple[str, ...] | None = None,
) -> int:
    if expected_columns:
        validate_columns(table, expected_columns)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = _tmp_path(path)
    try:
        pq.write_table(table, tmp)
        verified = pq.read_table(tmp)
        if verified.num_rows != table.num_rows:
            raise OSError(f"row count mismatch after parquet write: {tmp}")
        atomic_replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
    return table.num_rows


def remove_tmp_siblings(directory: Path) -> list[Path]:
    """Remove orphan *.tmp files under directory."""
    removed: list[Path] = []
    if not directory.exists():
        return removed
    for tmp in directory.rglob("*.tmp"):
        if tmp.is_file():
            tmp.unlink()
            removed.append(tmp)
    return removed
