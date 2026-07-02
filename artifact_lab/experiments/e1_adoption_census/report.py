"""E1 short report summarizing census outputs."""

from __future__ import annotations

from pathlib import Path


def render_report(
    *,
    census_dir: Path,
    fig1_csv: Path,
    table1_csv: Path,
    n_registry_repos: int,
    n_repos_with_matches: int,
    n_path_rows: int,
) -> str:
    lines = [
        "# E1 — Repository Adoption Census",
        "",
        "## Scope",
        f"- Registry repositories: {n_registry_repos}",
        f"- Repositories with matched convention files: {n_repos_with_matches}",
        f"- Matched convention paths (ever): {n_path_rows}",
        "",
        "## Reproducible datasets",
        f"- Path-level census: `{census_dir / 'path_census.csv'}`",
        f"- Repo × family census: `{census_dir / 'repo_family_census.csv'}`",
        f"- Repo-level census: `{census_dir / 'repo_census.csv'}`",
        "",
        "## Publication exports (artifact)",
        f"- Figure 1 PDF: `{fig1_csv.with_suffix('.pdf')}`",
        f"- Figure 1 data: `{fig1_csv}`",
        f"- Table 1: `{table1_csv}`",
        "",
        "## Paper repository export",
        "- `../paper/figures/fig1.pdf`",
        "- `../paper/figures/fig1.csv`",
        "- `../paper/tables/table1.csv`",
        "",
        "## Regeneration",
        "```bash",
        "make paper      # artifact-only + export to ../paper",
        "make paper-artifact  # artifact outputs only",
        "```",
        "",
    ]
    return "\n".join(lines)


def write_report(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
