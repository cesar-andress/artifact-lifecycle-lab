"""Agent protocol for RQ5 v2 factorial runs."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from artifact_lab.experiments.rq5_v2.models import FactorialCase, FactorialRunResult


class FactorialAgent(Protocol):
    agent_id: str

    @staticmethod
    def is_available() -> bool: ...

    def run(
        self,
        *,
        case: FactorialCase,
        cell_code: str,
        workspace: Path,
        replicate_id: int,
        run_id: str,
    ) -> FactorialRunResult: ...
