"""P1 — Reference Density Pilot (TOSEM go/no-go)."""

from __future__ import annotations

import csv
import statistics
from collections import Counter, defaultdict
from dataclasses import asdict
from io import StringIO
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.truth_pilots.references import extract_references
from artifact_lab.experiments.truth_pilots.sample import InstructionSample, sample_instruction_files
from artifact_lab.experiments.truth_pilots.verify_refs import ReferenceAuditRow, audit_references_for_sample
from artifact_lab.ingest.git_utils import clone_bare, remove_clone
from artifact_lab.store.blobs import BlobStore

VERIFIABLE_TYPES = frozenset({"path", "directory", "script_name", "dependency"})


def _write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        atomic_write_text(path, "")
        return
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    atomic_write_text(path, buffer.getvalue())


def _example_label(status: str) -> str:
    if status == "verified":
        return "true"
    if status == "missing":
        return "false"
    return "ambiguous"


def _pick_examples(audit_rows: list[ReferenceAuditRow], *, per_label: int = 5) -> list[ReferenceAuditRow]:
    buckets: dict[str, list[ReferenceAuditRow]] = defaultdict(list)
    for row in audit_rows:
        label = _example_label(row.verification_status)
        if len(buckets[label]) < per_label:
            buckets[label].append(row)
    picked: list[ReferenceAuditRow] = []
    for label in ("true", "false", "ambiguous"):
        picked.extend(buckets[label])
    return picked


def _density_markdown(
    *,
    samples: list[InstructionSample],
    summary_rows: list[dict],
    audit_rows: list[ReferenceAuditRow],
    extraction_failures: int,
    status_counts: Counter[str],
    type_counts: Counter[str],
    group_counts: Counter[str],
) -> str:
    n_files = len(samples)
    with_verifiable = sum(1 for row in summary_rows if int(row["verifiable_references"]) > 0)
    refs_per_file = [int(row["total_references"]) for row in summary_rows]
    verifiable_per_file = [int(row["verifiable_references"]) for row in summary_rows]
    median_refs = statistics.median(refs_per_file) if refs_per_file else 0.0
    median_verifiable = statistics.median(verifiable_per_file) if verifiable_per_file else 0.0

    lines = [
        "# P1 — Reference Density Pilot",
        "",
        "## Scope",
        f"- Instruction files sampled: **{n_files}**",
        f"- Stratified across: AGENTS.md, CLAUDE.md, Cursor rules, Copilot, GitHub instructions, Skills, prompts",
        f"- Extraction failures (missing blob): **{extraction_failures}**",
        "",
        "## Density",
        f"- Files with ≥1 verifiable reference: **{with_verifiable}** ({100 * with_verifiable / n_files:.1f}%)" if n_files else "- Files with ≥1 verifiable reference: **0**",
        f"- Median references per file: **{median_refs:.1f}**",
        f"- Median verifiable references per file: **{median_verifiable:.1f}**",
        "",
        "## Sampled files by family group",
        "",
        "| family group | count |",
        "|--------------|------:|",
    ]
    for group in sorted(group_counts):
        lines.append(f"| {group} | {group_counts[group]} |")

    lines.extend(
        [
            "",
            "## Verification outcomes",
            "",
            "| status | count |",
            "|--------|------:|",
        ]
    )
    for status in sorted(status_counts):
        lines.append(f"| {status} | {status_counts[status]} |")

    verified = status_counts.get("verified", 0)
    missing = status_counts.get("missing", 0)
    verifiable = verified + missing
    precision = (verified / verifiable * 100.0) if verifiable else 0.0
    lines.extend(
        [
            "",
            f"**Path/directory/script/dependency precision proxy** (verified / (verified + missing)): **{precision:.1f}%**",
            "",
            "## References by type",
            "",
            "| type | count |",
            "|------|------:|",
        ]
    )
    for ref_type in sorted(type_counts):
        lines.append(f"| {ref_type} | {type_counts[ref_type]} |")

    lines.extend(
        [
            "",
            "## Interpretation",
            "- Verifiable types: path, directory, script_name, dependency.",
            "- Commands are extracted but typically `ambiguous` (unverifiable) in this pilot.",
            "- `false` (missing) references are candidates for truth-decay measurement at scale.",
            "",
        ]
    )
    return "\n".join(lines)


def run_p1_reference_density_pilot(
    *,
    l1_paths: list[Path],
    blobs_dir: Path,
    scratch_dir: Path,
    output_dir: Path,
    n_samples: int = 400,
    n_min: int = 300,
    n_max: int = 500,
    seed: int = 42,
    clone_timeout: int = 180,
) -> tuple[Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    density_md = output_dir / "reference_density.md"
    examples_csv = output_dir / "reference_examples.csv"
    summary_csv = output_dir / "reference_summary.csv"

    samples = sample_instruction_files(
        l1_paths,
        n=n_samples,
        n_min=n_min,
        n_max=n_max,
        seed=seed,
    )
    blob_store = BlobStore(blobs_dir)
    audit_rows: list[ReferenceAuditRow] = []
    summary_rows: list[dict] = []
    clone_cache: dict[str, Path] = {}
    extraction_failures = 0
    group_counts = Counter(s.family_group for s in samples)

    try:
        for sample in samples:
            try:
                text = blob_store.get_text(sample.blob_sha).decode("utf-8", errors="replace")
            except FileNotFoundError:
                extraction_failures += 1
                summary_rows.append(
                    {
                        "sample_id": sample.sample_id,
                        "repo_id": sample.repo_id,
                        "instruction_path": sample.instruction_path,
                        "family_group": sample.family_group,
                        "pattern_id": sample.pattern_id,
                        "total_references": 0,
                        "verifiable_references": 0,
                        "verified": 0,
                        "missing": 0,
                        "unverifiable": 0,
                        "extraction_ok": "false",
                    }
                )
                continue

            references = extract_references(text)
            if sample.repo_id not in clone_cache:
                clone_path = scratch_dir / f"p1_{sample.repo_id}"
                clone_bare(sample.repo_url, clone_path, timeout=clone_timeout)
                clone_cache[sample.repo_id] = clone_path
            repo_dir = clone_cache[sample.repo_id]
            file_audit = audit_references_for_sample(
                sample_id=sample.sample_id,
                repo_id=sample.repo_id,
                repo_url=sample.repo_url,
                instruction_path=sample.instruction_path,
                references=references,
                repo_dir=repo_dir,
                timeout=clone_timeout,
            )
            audit_rows.extend(file_audit)
            status_by = Counter(r.verification_status for r in file_audit)
            verifiable = sum(1 for r in file_audit if r.reference_type in VERIFIABLE_TYPES)
            summary_rows.append(
                {
                    "sample_id": sample.sample_id,
                    "repo_id": sample.repo_id,
                    "instruction_path": sample.instruction_path,
                    "family_group": sample.family_group,
                    "pattern_id": sample.pattern_id,
                    "total_references": len(references),
                    "verifiable_references": verifiable,
                    "verified": status_by.get("verified", 0),
                    "missing": status_by.get("missing", 0),
                    "unverifiable": status_by.get("unverifiable", 0),
                    "extraction_ok": "true",
                }
            )
    finally:
        for clone_path in clone_cache.values():
            remove_clone(clone_path)

    examples = _pick_examples(audit_rows)
    example_rows = [
        {
            "sample_id": row.sample_id,
            "repo_id": row.repo_id,
            "instruction_path": row.instruction_path,
            "reference_type": row.reference_type,
            "reference_text": row.reference_text,
            "example_label": _example_label(row.verification_status),
            "verification_status": row.verification_status,
            "evidence": row.evidence,
        }
        for row in examples
    ]
    _write_csv(example_rows, examples_csv)
    _write_csv(summary_rows, summary_csv)

    status_counts = Counter(row.verification_status for row in audit_rows)
    type_counts = Counter(row.reference_type for row in audit_rows)
    atomic_write_text(
        density_md,
        _density_markdown(
            samples=samples,
            summary_rows=summary_rows,
            audit_rows=audit_rows,
            extraction_failures=extraction_failures,
            status_counts=status_counts,
            type_counts=type_counts,
            group_counts=group_counts,
        ),
    )
    return density_md, examples_csv, summary_csv
