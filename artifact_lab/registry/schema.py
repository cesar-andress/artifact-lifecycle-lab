"""E1 cohort registry CSV schema validation."""

from __future__ import annotations

import csv
from pathlib import Path

E1_100_REGISTRY_COLUMNS: tuple[str, ...] = (
    "repo_id",
    "repo_url",
    "owner",
    "name",
    "source",
    "stars",
    "language",
    "pushed_at",
    "selection_stratum",
    "notes",
)


def read_registry_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"registry missing header: {path}")
        missing = [col for col in E1_100_REGISTRY_COLUMNS if col not in reader.fieldnames]
        if missing:
            raise ValueError(f"registry {path} missing columns: {missing}")
        return [dict(row) for row in reader]


def validate_e1_100_registry(path: Path, *, expected_rows: int | None = 100) -> list[dict[str, str]]:
    rows = read_registry_rows(path)
    if expected_rows is not None and len(rows) != expected_rows:
        raise ValueError(f"registry {path} expected {expected_rows} rows, got {len(rows)}")
    seen_ids: set[str] = set()
    seen_urls: set[str] = set()
    for index, row in enumerate(rows, start=2):
        repo_id = row["repo_id"].strip()
        repo_url = row["repo_url"].strip().lower().rstrip("/")
        if not repo_id:
            raise ValueError(f"registry {path}:{index} missing repo_id")
        if repo_id in seen_ids:
            raise ValueError(f"registry {path}:{index} duplicate repo_id {repo_id}")
        if repo_url in seen_urls:
            raise ValueError(f"registry {path}:{index} duplicate repo_url {repo_url}")
        seen_ids.add(repo_id)
        seen_urls.add(repo_url)
    return rows
