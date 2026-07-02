"""Smoke tests for E1 Makefile targets."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _dry_run_make(target: str) -> str:
    result = subprocess.run(
        ["make", "-n", target],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout + result.stderr


def test_make_e1_pilot_invokes_extraction():
    output = _dry_run_make("e1-pilot")
    assert "artifact_lab.ingest extract" in output
    assert "--limit" in output
    assert "--skip-slow" in output


def test_make_e1_invokes_full_extraction():
    output = _dry_run_make("e1")
    assert "artifact_lab.ingest extract" in output
    assert "--limit" not in output
    assert "artifact_lab.derive panel" in output
    assert "artifact_lab.experiments.e1_adoption_census" in output
    assert "artifact_lab.experiments.pilot_performance" in output


def test_make_paper_does_not_invoke_extraction():
    output = _dry_run_make("paper")
    assert "artifact_lab.ingest extract" not in output
    assert "artifact_lab.derive panel" not in output
    assert "artifact_lab.experiments.e1_adoption_census" not in output
    assert "figures/fig1.pdf" in output or "fig1.pdf" in output
