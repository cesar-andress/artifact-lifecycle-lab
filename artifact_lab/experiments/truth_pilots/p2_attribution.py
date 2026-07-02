"""P2 — Agent Attribution Pilot (TOSEM go/no-go)."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import asdict
from io import StringIO
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.truth_pilots.attribution import AttributionCandidate, scan_commit_attribution
from artifact_lab.experiments.truth_pilots.sample import load_instruction_commits_from_l1
from artifact_lab.experiments.truth_pilots.verify_refs import commit_message, commit_metadata
from artifact_lab.ingest.git_utils import clone_bare, remove_clone


def _write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        atomic_write_text(path, "")
        return
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    atomic_write_text(path, buffer.getvalue())


def _attribution_markdown(
    *,
    n_commits: int,
    class_counts: Counter[str],
    signature_counts: Counter[str],
    agent_authored: int,
    agent_coauthored: int,
    example_rows: list[AttributionCandidate],
    files_with_signal: int,
    n_files: int,
) -> str:
    agent_total = agent_authored + agent_coauthored
    signal_rate = (agent_total / n_commits * 100.0) if n_commits else 0.0
    lines = [
        "# P2 — Agent Attribution Pilot",
        "",
        "## Scope",
        f"- Commits scanned (from L1 instruction-file events): **{n_commits}**",
        f"- Instruction files touched: **{n_files}**",
        f"- Files with ≥1 agent signal: **{files_with_signal}** ({100 * files_with_signal / n_files:.1f}%)" if n_files else "",
        "",
        "## Candidate counts",
        f"- Candidate agent-authored commits: **{agent_authored}**",
        f"- Candidate agent-co-authored commits: **{agent_coauthored}**",
        f"- Combined agent signal rate: **{signal_rate:.1f}%**",
        "",
        "## Attribution classes",
        "",
        "| class | count |",
        "|-------|------:|",
    ]
    for cls in sorted(class_counts):
        lines.append(f"| {cls} | {class_counts[cls]} |")

    lines.extend(
        [
            "",
            "## Signature types",
            "",
            "| signature_type | count |",
            "|----------------|------:|",
        ]
    )
    for sig in sorted(signature_counts):
        lines.append(f"| {sig} | {signature_counts[sig]} |")

    lines.extend(
        [
            "",
            "## Example candidates",
            "",
        ]
    )
    for cand in example_rows[:8]:
        lines.append(
            f"- `{cand.commit_sha[:8]}` {cand.instruction_path} — **{cand.attribution_class}** ({cand.signature_type}): {cand.evidence[:100]}"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "- Deterministic heuristics only (Co-Authored-By, bot accounts, tool strings).",
            "- L1 supplies commit SHAs; git supplies messages and author emails.",
            "- Signal strength is a pilot estimate, not population prevalence.",
            "",
        ]
    )
    return "\n".join(lines)


def run_p2_attribution_pilot(
    *,
    l1_paths: list[Path],
    scratch_dir: Path,
    output_dir: Path,
    clone_timeout: int = 180,
) -> tuple[Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    attribution_md = output_dir / "agent_attribution.md"
    candidates_csv = output_dir / "agent_commit_candidates.csv"
    summary_csv = output_dir / "agent_attribution_summary.csv"

    l1_commits = load_instruction_commits_from_l1(l1_paths)
    clone_cache: dict[str, Path] = {}
    candidates: list[AttributionCandidate] = []

    try:
        for touch in l1_commits:
            if touch.repo_id not in clone_cache:
                clone_path = scratch_dir / f"p2_{touch.repo_id}"
                clone_bare(touch.repo_url, clone_path, timeout=clone_timeout)
                clone_cache[touch.repo_id] = clone_path
            repo_dir = clone_cache[touch.repo_id]

            author_name, author_email, commit_ts = commit_metadata(
                repo_dir, touch.commit_sha, timeout=clone_timeout
            )
            if not author_name:
                author_name = touch.author_name
            if not commit_ts:
                commit_ts = str(int(touch.commit_time.timestamp()))
            body = commit_message(repo_dir, touch.commit_sha, timeout=clone_timeout)
            candidates.append(
                scan_commit_attribution(
                    repo_id=touch.repo_id,
                    repo_url=touch.repo_url,
                    instruction_path=touch.instruction_path,
                    family_group=touch.family_group,
                    commit_sha=touch.commit_sha,
                    commit_time=commit_ts,
                    author_name=author_name,
                    author_email=author_email,
                    commit_message=body,
                )
            )
    finally:
        for clone_path in clone_cache.values():
            remove_clone(clone_path)

    _write_csv([asdict(c) for c in candidates], candidates_csv)

    class_counts = Counter(c.attribution_class for c in candidates)
    signature_counts = Counter(c.signature_type for c in candidates if c.attribution_class != "human")
    agent_coauthored = class_counts.get("agent_coauthored", 0)
    agent_authored = class_counts.get("bot_author", 0) + class_counts.get("agent_signature_in_message", 0)

    by_file: dict[tuple[str, str], list[AttributionCandidate]] = defaultdict(list)
    for cand in candidates:
        by_file[(cand.repo_id, cand.instruction_path)].append(cand)
    files_with_signal = sum(
        1 for rows in by_file.values() if any(r.attribution_class != "human" for r in rows)
    )

    summary_rows = [
        {
            "metric": "commits_scanned",
            "value": len(candidates),
        },
        {
            "metric": "instruction_files_touched",
            "value": len(by_file),
        },
        {
            "metric": "candidate_agent_authored",
            "value": agent_authored,
        },
        {
            "metric": "candidate_agent_coauthored",
            "value": agent_coauthored,
        },
        {
            "metric": "files_with_agent_signal",
            "value": files_with_signal,
        },
        {
            "metric": "signal_rate_pct",
            "value": round((agent_authored + agent_coauthored) / len(candidates) * 100, 2) if candidates else 0,
        },
    ]
    for cls, count in sorted(class_counts.items()):
        summary_rows.append({"metric": f"class_{cls}", "value": count})
    for sig, count in sorted(signature_counts.items()):
        summary_rows.append({"metric": f"signature_{sig}", "value": count})
    _write_csv(summary_rows, summary_csv)

    examples = [c for c in candidates if c.attribution_class != "human"][:8]
    atomic_write_text(
        attribution_md,
        _attribution_markdown(
            n_commits=len(candidates),
            class_counts=class_counts,
            signature_counts=signature_counts,
            agent_authored=agent_authored,
            agent_coauthored=agent_coauthored,
            example_rows=examples,
            files_with_signal=files_with_signal,
            n_files=len(by_file),
        ),
    )
    return attribution_md, candidates_csv, summary_csv
