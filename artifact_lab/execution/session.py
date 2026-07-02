"""Execution session timestamps persisted across interrupted runs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from artifact_lab.contracts.paths import EXTRACTION_SESSION_PATH
from artifact_lab.execution.atomic_io import atomic_write_text


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load(path: Path = EXTRACTION_SESSION_PATH) -> dict:
    if not path.exists():
        return {"waves": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def _save(data: dict, path: Path = EXTRACTION_SESSION_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(path, json.dumps(data, indent=2) + "\n")


def touch_wave(wave_id: str, *, path: Path = EXTRACTION_SESSION_PATH) -> str:
    """Record activity for wave; return execution_start (set once)."""
    data = _load(path)
    waves = data.setdefault("waves", {})
    entry = waves.setdefault(wave_id, {})
    now = _utc_now()
    entry.setdefault("execution_start", now)
    entry["last_activity"] = now
    _save(data, path)
    return entry["execution_start"]


def finish_wave(wave_id: str, *, path: Path = EXTRACTION_SESSION_PATH) -> str | None:
    data = _load(path)
    entry = data.get("waves", {}).get(wave_id)
    if entry is None:
        return None
    entry["execution_finish"] = _utc_now()
    _save(data, path)
    return entry["execution_finish"]


def wave_execution_start(wave_id: str, *, path: Path = EXTRACTION_SESSION_PATH) -> str | None:
    entry = _load(path).get("waves", {}).get(wave_id)
    return entry.get("execution_start") if entry else None


def wave_execution_finish(wave_id: str, *, path: Path = EXTRACTION_SESSION_PATH) -> str | None:
    entry = _load(path).get("waves", {}).get(wave_id)
    return entry.get("execution_finish") if entry else None
