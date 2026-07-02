"""Test export to sibling paper repository."""

from __future__ import annotations

from pathlib import Path

from artifact_lab.experiments.e1_adoption_census.export_paper import export_to_paper_repo
from artifact_lab.experiments.e1_adoption_census.export_paths import (
    DEFAULT_FIG1_CSV,
    DEFAULT_FIG1_PDF,
    DEFAULT_TABLE1,
)


def test_export_to_paper_repo(tmp_path: Path):
    artifact = tmp_path / "artifact"
    paper = tmp_path / "paper"
    export_dir = artifact / "exports/e1"
    export_dir.mkdir(parents=True)
    (export_dir / "fig1.pdf").write_text("pdf", encoding="utf-8")
    (export_dir / "fig1.csv").write_text("csv", encoding="utf-8")
    (export_dir / "table1.csv").write_text("table", encoding="utf-8")

    written = export_to_paper_repo(paper_root=paper, artifact_root=artifact)
    assert (paper / "figures/fig1.pdf").read_text(encoding="utf-8") == "pdf"
    assert (paper / "figures/fig1.csv").read_text(encoding="utf-8") == "csv"
    assert (paper / "tables/table1.csv").read_text(encoding="utf-8") == "table"
    assert len(written) == 3
    assert DEFAULT_FIG1_PDF.name == "fig1.pdf"
    assert DEFAULT_FIG1_CSV.name == "fig1.csv"
    assert DEFAULT_TABLE1.name == "table1.csv"
