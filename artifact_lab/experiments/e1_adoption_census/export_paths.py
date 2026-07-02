"""Publication export paths (artifact-internal defaults)."""

from __future__ import annotations

from pathlib import Path

E1_EXPORT_DIR = Path("exports/e1")
E1_100_EXPORT_DIR = Path("exports/e1_100")

DEFAULT_FIG1_CSV = E1_EXPORT_DIR / "fig1.csv"
DEFAULT_FIG1_PDF = E1_EXPORT_DIR / "fig1.pdf"
DEFAULT_TABLE1 = E1_EXPORT_DIR / "table1.csv"
DEFAULT_REPORT = E1_EXPORT_DIR / "e1_census.md"

E1_100_FIG1_CSV = E1_100_EXPORT_DIR / "fig1.csv"
E1_100_FIG1_PDF = E1_100_EXPORT_DIR / "fig1.pdf"
E1_100_TABLE1 = E1_100_EXPORT_DIR / "table1.csv"
E1_100_REPORT = E1_100_EXPORT_DIR / "e1_census.md"
E1_100_PERFORMANCE = E1_100_EXPORT_DIR / "pilot_performance.md"
E1_100_COHORT_SUMMARY = E1_100_EXPORT_DIR / "cohort_summary.md"

PAPER_FIG1_CSV = Path("figures/fig1.csv")
PAPER_FIG1_PDF = Path("figures/fig1.pdf")
PAPER_TABLE1 = Path("tables/table1.csv")
