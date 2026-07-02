"""Smoke tests for make paper and paper Makefile behavior."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PAPER_MAKEFILE = REPO_ROOT / "templates" / "paper" / "Makefile"


def _run_make(target: str, *, cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(
        ["make", target],
        cwd=cwd,
        env=merged,
        capture_output=True,
        text=True,
        check=False,
    )


def test_paper_pdf_skips_when_main_tex_missing(tmp_path: Path):
    paper_dir = tmp_path / "paper"
    paper_dir.mkdir()
    shutil.copy(PAPER_MAKEFILE, paper_dir / "Makefile")

    trap_latexmk = tmp_path / "latexmk-trap.sh"
    trap_latexmk.write_text("#!/bin/sh\necho latexmk should not run >&2\nexit 99\n", encoding="utf-8")
    trap_latexmk.chmod(0o755)

    result = _run_make("pdf", cwd=paper_dir, env={"LATEXMK": str(trap_latexmk)})

    assert result.returncode == 0
    assert "No main.tex found — skipping LaTeX compile" in result.stdout
    assert "latexmk should not run" not in result.stderr


def test_make_paper_succeeds_without_manuscript(tmp_path: Path):
    paper_root = tmp_path / "paper"
    exports = tmp_path / "exports" / "e1"
    exports.mkdir(parents=True)
    paper_root.mkdir()

    (exports / "fig1.pdf").write_bytes(b"%PDF-1.4\n")
    (exports / "fig1.csv").write_text("bucket,count\n", encoding="utf-8")
    (exports / "table1.csv").write_text("metric,value\n", encoding="utf-8")
    shutil.copy(PAPER_MAKEFILE, paper_root / "Makefile")

    trap_latexmk = tmp_path / "latexmk-trap.sh"
    trap_latexmk.write_text("#!/bin/sh\necho latexmk should not run >&2\nexit 99\n", encoding="utf-8")
    trap_latexmk.chmod(0o755)

    result = subprocess.run(
        [
            "make",
            "paper",
            f"PAPER_ROOT={paper_root}",
            f"FIG1_PDF={exports / 'fig1.pdf'}",
            f"FIG1_CSV={exports / 'fig1.csv'}",
            f"TABLE1={exports / 'table1.csv'}",
            f"E1_PILOT_PERF={exports / 'pilot_performance.md'}",
        ],
        cwd=REPO_ROOT,
        env={**os.environ, "LATEXMK": str(trap_latexmk)},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert (paper_root / "figures" / "fig1.pdf").exists()
    assert (paper_root / "tables" / "table1.csv").exists()
    assert "No main.tex found — skipping LaTeX compile" in result.stdout + result.stderr
    assert "latexmk should not run" not in result.stderr
