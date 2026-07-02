"""Dataset manifest writer."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from artifact_lab.contracts.schemas import schema_hash
from artifact_lab.execution.atomic_io import atomic_write_text


def git_sha() -> str | None:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def write_manifest(
    path: Path,
    *,
    dataset_name: str,
    version: str,
    input_datasets: list[str],
    protocol_version: str,
    row_count: int,
    columns: tuple[str, ...],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "dataset": dataset_name,
        "version": version,
        "input_datasets": input_datasets,
        "protocol_version": protocol_version,
        "code_git_sha": git_sha(),
        "git_commit": git_sha(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "row_count": row_count,
        "schema_hash": schema_hash(columns),
        "columns": list(columns),
    }
    if extra:
        payload.update(extra)
    if path.suffix in {".yaml", ".yml"}:
        atomic_write_text(path, yaml.safe_dump(payload, sort_keys=False))
    else:
        atomic_write_text(path, json.dumps(payload, indent=2) + "\n")
    return payload
