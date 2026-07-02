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

E1_1000_REGISTRY_COLUMNS: tuple[str, ...] = (
    *E1_100_REGISTRY_COLUMNS[:9],
    "cohort_stratum",
    "notes",
)

E1_1000_REGISTRY_VERSION = "e1_1000_v1"
E1_1000_TARGET_SIZE = 1000
E1_1000_STRATUM_SIZES: dict[str, int] = {
    "ai_instruction_discovery": 334,
    "general_oss": 333,
    "mixed_control": 333,
}


def read_registry_rows(path: Path, *, columns: tuple[str, ...] = E1_100_REGISTRY_COLUMNS) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"registry missing header: {path}")
        missing = [col for col in columns if col not in reader.fieldnames]
        if missing:
            raise ValueError(f"registry {path} missing columns: {missing}")
        return [dict(row) for row in reader]


def _validate_unique_rows(path: Path, rows: list[dict[str, str]]) -> None:
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


def validate_e1_100_registry(path: Path, *, expected_rows: int | None = 100) -> list[dict[str, str]]:
    rows = read_registry_rows(path, columns=E1_100_REGISTRY_COLUMNS)
    if expected_rows is not None and len(rows) != expected_rows:
        raise ValueError(f"registry {path} expected {expected_rows} rows, got {len(rows)}")
    _validate_unique_rows(path, rows)
    return rows


def validate_e1_1000_registry(path: Path, *, expected_rows: int | None = E1_1000_TARGET_SIZE) -> list[dict[str, str]]:
    rows = read_registry_rows(path, columns=E1_1000_REGISTRY_COLUMNS)
    if expected_rows is not None and len(rows) != expected_rows:
        raise ValueError(f"registry {path} expected {expected_rows} rows, got {len(rows)}")
    _validate_unique_rows(path, rows)
    stratum_counts: dict[str, int] = {}
    for row in rows:
        stratum = row["cohort_stratum"].strip()
        if stratum not in E1_1000_STRATUM_SIZES:
            raise ValueError(f"registry {path} invalid cohort_stratum {stratum!r}")
        stratum_counts[stratum] = stratum_counts.get(stratum, 0) + 1
    for stratum, expected in E1_1000_STRATUM_SIZES.items():
        actual = stratum_counts.get(stratum, 0)
        if actual != expected:
            raise ValueError(
                f"registry {path} stratum {stratum} expected {expected} rows, got {actual}"
            )
    sorted_urls = [row["repo_url"].strip().lower() for row in rows]
    if sorted_urls != sorted(sorted_urls):
        raise ValueError(f"registry {path} rows must be sorted by repo_url")
    return rows
