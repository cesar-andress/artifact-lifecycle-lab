"""E1 short report summarizing census outputs."""

from __future__ import annotations

from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text


def render_report(
    *,
    census_dir: Path,
    fig1_csv: Path,
    table1_csv: Path,
    n_registry_repos: int,
    n_repos_with_matches: int,
    n_path_rows: int,
    cohort_note: str | None = None,
) -> str:
    lines = [
        "# E1 — Repository Adoption Census",
        "",
    ]
    if cohort_note:
        lines.extend(
            [
                "## Cohort interpretation",
                f"> {cohort_note}",
                "",
            ]
        )
    lines.extend(
        [
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
        "make e1-pilot   # bounded development pilot",
        "make e1         # full pilot registry",
        "make paper      # copy exports to ../paper/",
        "```",
        "",
        ]
    )
    return "\n".join(lines)


def write_report(text: str, path: Path) -> None:
    atomic_write_text(path, text)
