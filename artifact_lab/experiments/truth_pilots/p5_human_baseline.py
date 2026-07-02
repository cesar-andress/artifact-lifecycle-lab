"""Gate P5 — Human documentation baseline feasibility."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.truth_pilots.gates_common import (
    DEFAULT_L1_PATHS,
    VERIFIABLE_REFERENCE_TYPES,
    load_p1_sample_keys,
    load_repo_urls_from_l1,
    write_csv,
)
from artifact_lab.experiments.truth_pilots.references import extract_references
from artifact_lab.experiments.truth_decay.verify_at_commit import CommitTreeCache, verify_reference_at_commit
from artifact_lab.ingest.git_utils import blob_at_commit, clone_bare, remove_clone

HUMAN_DOC_PATHS = ("README.md", "CONTRIBUTING.md")


def _example_label(status: str) -> str:
    if status == "verified":
        return "true"
    if status == "missing":
        return "false"
    return "ambiguous"


def run_p5_human_baseline_gate(
    *,
    output_dir: Path,
    p1_summary_csv: Path,
    machine_summary_csv: Path,
    l1_paths: list[Path],
    scratch_dir: Path,
    clone_timeout: int = 180,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_md = output_dir / "human_doc_baseline.md"
    examples_csv = output_dir / "human_doc_reference_examples.csv"

    import csv

    p1_keys = load_p1_sample_keys(p1_summary_csv)
    repo_urls = load_repo_urls_from_l1(l1_paths)

    machine_stats: dict[str, list[int]] = {}
    with machine_summary_csv.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rid = row["repo_id"]
            machine_stats.setdefault(rid, []).append(int(row.get("verifiable_references", 0)))

    unique_repos = sorted(set(rid for rid, _ in p1_keys))
    clone_cache: dict[str, Path] = {}
    tree_caches: dict[str, CommitTreeCache] = {}

    file_rows: list[dict] = []
    example_rows: list[dict] = []

    try:
        for repo_id in unique_repos:
            repo_url = repo_urls.get(repo_id, "")
            if not repo_url:
                continue
            if repo_id not in clone_cache:
                clone_path = scratch_dir / f"p5_{repo_id}"
                clone_bare(repo_url, clone_path, timeout=clone_timeout)
                clone_cache[repo_id] = clone_path
                tree_caches[repo_id] = CommitTreeCache(clone_path, timeout=clone_timeout)

            repo_dir = clone_cache[repo_id]
            tree_cache = tree_caches[repo_id]

            for doc_path in HUMAN_DOC_PATHS:
                content = blob_at_commit(repo_dir, "HEAD", doc_path, timeout=clone_timeout)
                if content is None:
                    continue
                text = content.decode("utf-8", errors="replace")
                refs = extract_references(text)
                verifiable = [r for r in refs if r.reference_type in VERIFIABLE_REFERENCE_TYPES]
                verified = missing = unverifiable = 0
                for ref in refs:
                    status, evidence = verify_reference_at_commit(
                        ref,
                        repo_dir=repo_dir,
                        commit_sha="HEAD",
                        tree_cache=tree_cache,
                        timeout=clone_timeout,
                    )
                    if status == "verified":
                        verified += 1
                    elif status == "missing":
                        missing += 1
                    else:
                        unverifiable += 1
                    if len(example_rows) < 30:
                        example_rows.append(
                            {
                                "repo_id": repo_id,
                                "doc_path": doc_path,
                                "reference_type": ref.reference_type,
                                "reference_text": ref.reference_text,
                                "example_label": _example_label(status),
                                "verification_status": status,
                                "evidence": evidence[:200],
                            }
                        )

                ambiguity = unverifiable / len(refs) if refs else 0.0
                file_rows.append(
                    {
                        "repo_id": repo_id,
                        "doc_path": doc_path,
                        "total_references": len(refs),
                        "verifiable_references": len(verifiable),
                        "verified": verified,
                        "missing": missing,
                        "unverifiable": unverifiable,
                        "extraction_ambiguity_ratio": round(ambiguity, 4),
                    }
                )
    finally:
        for clone_path in clone_cache.values():
            remove_clone(clone_path)

    write_csv(example_rows, examples_csv)

    n_sampled = len(file_rows)
    n_with_verifiable = sum(1 for r in file_rows if int(r["verifiable_references"]) > 0)
    median_density = 0.0
    if file_rows:
        densities = [int(r["total_references"]) for r in file_rows]
        import statistics

        median_density = float(statistics.median(densities))

    machine_median = 0.0
    if machine_stats:
        import statistics

        per_repo = [sum(v) for v in machine_stats.values()]
        machine_median = float(statistics.median(per_repo))

    viable = n_with_verifiable >= max(5, n_sampled * 0.2) and n_sampled >= 10
    gate = "PASS" if viable else "FAIL"

    lines = [
        "# Gate P5 — Human Documentation Baseline Feasibility",
        "",
        "## Scope",
        f"- Repositories (P1 cohort): **{len(unique_repos)}**",
        f"- Human doc files sampled (README.md / CONTRIBUTING.md): **{n_sampled}**",
        "",
        "## Human-facing doc metrics",
        f"- Files with ≥1 verifiable reference: **{n_with_verifiable}** ({100 * n_with_verifiable / n_sampled:.1f}%)" if n_sampled else "- Files with ≥1 verifiable reference: **0**",
        f"- Median reference density (human docs): **{median_density:.1f}**",
        f"- Median verifiable references per repo (machine docs, P1): **{machine_median:.1f}**",
        "",
        "## Extraction ambiguity",
        "Ambiguity ratio = unverifiable / total references (commands dominate).",
        "",
    ]
    if file_rows:
        mean_amb = sum(float(r["extraction_ambiguity_ratio"]) for r in file_rows) / len(file_rows)
        lines.append(f"- Mean ambiguity ratio: **{mean_amb:.1%}**")

    by_path = Counter(r["doc_path"] for r in file_rows)
    lines.extend(["", "### Files by type", ""])
    for path, count in by_path.most_common():
        lines.append(f"- `{path}`: {count}")

    lines.extend(
        [
            "",
            "## Comparative RQ feasibility",
            f"- Machine vs human doc comparison technically viable: **{'Yes' if viable else 'No'}**",
            "- Requires matched repos with both instruction files (P1) and human docs present.",
            "",
            f"## Gate verdict: **{gate}**",
            "",
        ]
    )
    atomic_write_text(report_md, "\n".join(lines))
    return report_md, examples_csv
