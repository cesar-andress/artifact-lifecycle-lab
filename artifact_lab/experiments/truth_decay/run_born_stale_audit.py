"""Run born-stale audit on RQ1 longitudinal output."""

from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.truth_decay.born_stale_audit import (
    audit_summary_markdown,
    build_born_stale_records,
    collect_born_stale_trajectories,
    example_rows,
    summarize_by_repo,
    summarize_by_type,
)
from artifact_lab.experiments.truth_pilots.gates_common import DEFAULT_RQ1_LONGITUDINAL, load_longitudinal_rows

DEFAULT_EXPORT = Path("exports/truth_decay_pilot")


def _write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        atomic_write_text(path, "")
        return
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    atomic_write_text(path, buffer.getvalue())


def run_born_stale_audit(
    *,
    longitudinal_csv: Path = DEFAULT_RQ1_LONGITUDINAL,
    output_dir: Path = DEFAULT_EXPORT,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    audit_md = output_dir / "born_stale_audit.md"
    examples_csv = output_dir / "born_stale_examples.csv"
    by_repo_csv = output_dir / "born_stale_by_repo.csv"
    by_type_csv = output_dir / "born_stale_by_type.csv"

    rows = load_longitudinal_rows(longitudinal_csv)
    never_verified, meta = collect_born_stale_trajectories(rows)
    records = build_born_stale_records(never_verified, rows)
    by_type = summarize_by_type(records)
    by_repo = summarize_by_repo(records)

    atomic_write_text(
        audit_md,
        audit_summary_markdown(meta=meta, records=records, by_type=by_type, by_repo=by_repo),
    )
    _write_csv(example_rows(records), examples_csv)
    _write_csv(by_repo, by_repo_csv)
    _write_csv(by_type, by_type_csv)

    return {
        "audit_md": audit_md,
        "examples_csv": examples_csv,
        "by_repo_csv": by_repo_csv,
        "by_type_csv": by_type_csv,
    }
