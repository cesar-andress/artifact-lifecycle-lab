"""Copy E1 publication outputs to the sibling paper repository."""

from __future__ import annotations

import shutil
from pathlib import Path

from artifact_lab.experiments.e1_adoption_census.export_paths import (
    DEFAULT_FIG1_CSV,
    DEFAULT_FIG1_PDF,
    DEFAULT_TABLE1,
    PAPER_FIG1_CSV,
    PAPER_FIG1_PDF,
    PAPER_TABLE1,
)


def export_to_paper_repo(*, paper_root: Path, artifact_root: Path | None = None) -> list[Path]:
    """Copy generated fig/table files into the paper repository (one-way)."""
    root = artifact_root or Path.cwd()
    copies = [
        (root / DEFAULT_FIG1_PDF, paper_root / PAPER_FIG1_PDF),
        (root / DEFAULT_FIG1_CSV, paper_root / PAPER_FIG1_CSV),
        (root / DEFAULT_TABLE1, paper_root / PAPER_TABLE1),
    ]
    written: list[Path] = []
    for src, dst in copies:
        if not src.exists():
            raise FileNotFoundError(f"missing artifact export: {src}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        written.append(dst)
    return written
