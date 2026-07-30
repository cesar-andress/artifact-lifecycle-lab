"""Export RQ5 v2 load-bearing candidate tasks (no agent execution)."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.truth_decay.born_stale_context import build_blob_index
from artifact_lab.experiments.truth_decay.rq5_v2.load_bearing import build_load_bearing_candidates
from artifact_lab.experiments.truth_pilots.gates_common import (
    DEFAULT_L1_PATHS,
    DEFAULT_RQ1_LONGITUDINAL,
    load_longitudinal_rows,
    load_repo_urls_from_l1,
)
from artifact_lab.store.blobs import BlobStore

DEFAULT_RQ5_V2_EXPORT = Path("exports/rq5_v2")


def _write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        atomic_write_text(path, "")
        return
    fieldnames = list(rows[0].keys())
    buffer = StringIO()
    import csv

    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    atomic_write_text(path, buffer.getvalue())


def _summary_markdown(*, candidates: list, output_csv: Path) -> str:
    from collections import Counter

    roles = Counter(c.role for c in candidates)
    diff = Counter(c.difficulty for c in candidates)
    repos = len({c.repository for c in candidates})
    avg_success = sum(c.estimated_success_rate for c in candidates) / len(candidates) if candidates else 0.0

    lines = [
        "# RQ5 v2 — Load-Bearing Candidate Export",
        "",
        "Automatic identification of instruction-file references that are **genuinely load-bearing**",
        "(must be edited, executed, or inspected to solve the task). Contextual-only mentions are rejected.",
        "",
        "**No agent runs.** Dataset construction only.",
        "",
        f"- Output CSV: `{output_csv}`",
        f"- Candidate count: **{len(candidates)}**",
        f"- Unique repositories: **{repos}**",
        f"- Mean estimated success rate: **{avg_success:.3f}**",
        "",
        "## Load-bearing roles",
        "",
        "| Role | Count |",
        "|------|------:|",
    ]
    for role in ("edit", "execute", "inspect"):
        lines.append(f"| {role} | {roles.get(role, 0)} |")

    lines.extend(
        [
            "",
            "## Difficulty",
            "",
            "| Difficulty | Count |",
            "|------------|------:|",
        ]
    )
    for d in ("easy", "medium", "hard"):
        lines.append(f"| {d} | {diff.get(d, 0)} |")

    lines.extend(
        [
            "",
            "## Selection rules",
            "",
            "1. Reference must be **VERIFIED** at the pinned commit (mechanical panel check).",
            "2. Instruction blob (L1b) must be recoverable.",
            "3. Reference must appear in **actionable** context: edit / execute / inspect verbs near the path.",
            "4. Reject: Related files / See also sections, passive mentions, peripheral docs without imperatives.",
            "",
            "## Protocol",
            "",
            "See `docs/RQ5_V2_PROTOCOL.md` for the full factorial experiment design.",
            "",
        ]
    )
    return "\n".join(lines)


def run_rq5_v2_candidate_export(
    *,
    longitudinal_csv: Path = DEFAULT_RQ1_LONGITUDINAL,
    l1_paths: list[Path] | None = None,
    blobs_dir: Path = Path("data/blobs"),
    output_dir: Path = DEFAULT_RQ5_V2_EXPORT,
    min_candidates: int = 100,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "candidates_csv": output_dir / "load_bearing_candidates.csv",
        "summary_md": output_dir / "load_bearing_candidates_summary.md",
    }

    l1 = list(l1_paths or DEFAULT_L1_PATHS)
    rows = load_longitudinal_rows(longitudinal_csv)
    repo_urls = load_repo_urls_from_l1(l1)
    blob_index = build_blob_index(l1)
    blob_store = BlobStore(blobs_dir)

    candidates = build_load_bearing_candidates(
        rows=rows,
        repo_urls=repo_urls,
        blob_index=blob_index,
        blob_store=blob_store,
        min_candidates=min_candidates,
    )

    export_rows: list[dict] = []
    for idx, c in enumerate(candidates, start=1):
        row = {
            "candidate_id": f"lbv2_{idx:04d}",
            "repository": c.repository,
            "task": c.task,
            "reference": c.reference,
            "why_load_bearing": c.why_load_bearing,
            "difficulty": c.difficulty,
            "estimated_success_rate": c.estimated_success_rate,
            "repo_id": c.repo_id,
            "repo_url": c.repo_url,
            "instruction_path": c.instruction_path,
            "commit_sha": c.commit_sha,
            "reference_type": c.reference_type,
            "role": c.role,
            "confidence": c.confidence,
            "context_snippet": c.context_snippet,
        }
        export_rows.append(row)

    _write_csv(export_rows, paths["candidates_csv"])
    atomic_write_text(
        paths["summary_md"],
        _summary_markdown(candidates=candidates, output_csv=paths["candidates_csv"]),
    )
    return paths
