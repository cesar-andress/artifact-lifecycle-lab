"""Append-only write-ahead execution log for repository state transitions."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ExecutionLog:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(
        self,
        *,
        repo_id: str,
        old_state: str,
        new_state: str,
        reason: str = "",
        duration_s: float | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        record: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "repo_id": repo_id,
            "old_state": old_state,
            "new_state": new_state,
            "reason": reason,
        }
        if duration_s is not None:
            record["duration_s"] = round(duration_s, 6)
        if extra:
            record["extra"] = extra
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")

    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        records: list[dict[str, Any]] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                records.append(json.loads(line))
        return records
