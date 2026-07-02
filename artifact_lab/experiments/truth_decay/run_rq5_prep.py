"""RQ5 experimental preparation — build candidate corpus (no agent runs)."""

from __future__ import annotations

import csv
from collections import Counter
from io import StringIO
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.truth_decay.born_stale_context import build_blob_index
from artifact_lab.experiments.truth_decay.rq5_candidates import (
    build_rq5_candidate_snapshots,
    snapshots_to_rows,
)
from artifact_lab.experiments.truth_pilots.gates_common import (
    DEFAULT_L1_PATHS,
    DEFAULT_PILOT_EXPORT,
    DEFAULT_RQ1_LONGITUDINAL,
    load_longitudinal_rows,
    load_p1_sample_keys,
    load_repo_urls_from_l1,
)
from artifact_lab.store.blobs import BlobStore

DEFAULT_RQ5_EXPORT = Path("exports/truth_decay_pilot")
DEFAULT_REFERENCE_SUMMARY = DEFAULT_PILOT_EXPORT / "reference_summary.csv"


def _write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        atomic_write_text(path, "")
        return
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    atomic_write_text(path, buffer.getvalue())


def _load_family_groups(summary_csv: Path) -> dict[tuple[str, str], str]:
    groups: dict[tuple[str, str], str] = {}
    if not summary_csv.exists():
        return groups
    with summary_csv.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            groups[(row["repo_id"], row["instruction_path"])] = row.get("family_group", "")
    return groups


def _summary_markdown(
    *,
    snapshots: list,
    spec_count: int,
) -> str:
    by_type = Counter(s.snapshot_type for s in snapshots)
    eligible = Counter(s.snapshot_type for s in snapshots if s.experimental_eligible)
    paired = sum(
        1
        for s in snapshots
        if s.snapshot_type == "degraded"
        and s.paired_truthful_commit_sha
        and s.paired_truthful_blob_sha
    )
    p1_eligible = sum(1 for s in snapshots if s.experimental_eligible and s.p1_sample)

    lines = [
        "# RQ5 — Experimental Preparation Corpus",
        "",
        "## Scope",
        "",
        "Deterministic preparation layer for future causal agent experiments.",
        "**No LLM runs. No benchmarking. No perturbation synthesis.**",
        "",
        "Each row in `rq5_candidate_dataset.csv` is a **natural snapshot** of one",
        "machine-consumable specification (`repo_id`, `instruction_path`) paired with",
        "repository state at a pinned `commit_sha`.",
        "",
        "## Corpus size",
        "",
        f"- Machine-consumable specifications (instruction files): **{spec_count:,}**",
        f"- Candidate snapshot rows: **{len(snapshots):,}**",
        "",
        "### Snapshots by type",
        "",
        "| Snapshot type | Identified | Experiment-eligible |",
        "|---------------|----------:|--------------------:|",
    ]
    for st in ("truthful", "born_stale", "repaired", "degraded"):
        lines.append(f"| {st} | {by_type.get(st, 0):,} | {eligible.get(st, 0):,} |")

    lines.extend(
        [
            "",
            f"- Degraded snapshots with paired pre-rot truthful commit: **{paired}**",
            f"- P1-sample eligible snapshots: **{p1_eligible}**",
            "",
            "## Snapshot definitions (natural, observational)",
            "",
            "| Type | Selection rule | Protocol mapping |",
            "|------|----------------|------------------|",
            "| **truthful** | Latest commit maximizing verified/verifiable ratio (>0) | Condition A |",
            "| **born_stale** | Earliest commit with verifiable ref never VERIFIED in panel | Condition B (integrity loss at birth) |",
            "| **degraded** | Earliest `VERIFIED→MISSING` transition in panel | Condition B (post-verification loss) |",
            "| **repaired** | Earliest `REPAIRED` state in panel | Post-repair observational stratum |",
            "",
            "## Pairing fields",
            "",
            "- **Repository state:** `commit_sha`, `task_commit_sha` (identical pin), `blob_sha`",
            "- **Issue availability:** deterministic text/stale-reference heuristics (no GitHub API)",
            "- **Task availability:** verified reference anchors + test-command/path signals in spec text",
            "- **Truthful pair:** `paired_truthful_commit_sha` / `paired_truthful_blob_sha` for B-type snapshots",
            "",
            "## Eligibility guardrails",
            "",
            "- Requires recoverable L1b instruction blob",
            "- Requires ≥1 verifiable reference at snapshot",
            "- B-type snapshots require issue-availability heuristic pass",
            "- All types require task-availability heuristic pass",
            "- **Build/test smoke check:** not run in this milestone (`build_check_pending` in validation doc)",
            "",
            "## Reproducibility",
            "",
            "- Inputs: `reference_longitudinal.csv`, L1 events parquet, L1b blobs, P1 `reference_summary.csv`",
            "- IDs: `spec_id = sha256(repo_id|instruction_path)[:16]`,",
            "  `snapshot_id = sha256(spec_id|snapshot_type|commit_sha)[:16]`",
            "- Re-run: `make truth-decay-rq5-prep`",
            "",
            "## Outputs",
            "",
            "- `rq5_candidate_dataset.csv`",
            "- `rq5_summary.md` (this file)",
            "- `rq5_protocol_validation.md`",
            "",
        ]
    )
    return "\n".join(lines)


def _protocol_validation_markdown(
    *,
    snapshots: list,
    spec_count: int,
) -> str:
    eligible = [s for s in snapshots if s.experimental_eligible]
    degraded_eligible = [s for s in eligible if s.snapshot_type == "degraded"]
    truthful_eligible = [s for s in eligible if s.snapshot_type == "truthful"]
    p1_degraded = [s for s in degraded_eligible if s.p1_sample]

    rot_cases = len(degraded_eligible)
    kill_rot = rot_cases < 10

    lines = [
        "# RQ5 Protocol Validation — Preparation Milestone",
        "",
        "**Protocol:** `protocol/RQ5_AGENT_IMPACT_EXPERIMENT_v1.md`",
        "**Milestone status:** Preparation only — case manifest generation, no agent execution",
        "",
        "## Checklist vs frozen protocol",
        "",
        "| Requirement | Status | Evidence |",
        "|-------------|--------|----------|",
        "| No artificial rot | PASS | All B-type snapshots use historical blobs at natural commits |",
        "| Observed rot source | PASS | Degraded snapshots from `VERIFIED→MISSING` in longitudinal panel |",
        "| Condition A truthful blob | PASS | `truthful` snapshots + `paired_truthful_*` for degraded |",
        "| Condition B observed-rot blob | PASS | `born_stale` / `degraded` snapshots at integrity-loss commits |",
        "| Fixed task context (design) | PARTIAL | `task_commit_sha` pinned; task prompt/rubric not implemented |",
        "| Instruction text recoverable | "
        + ("PASS" if all(s.blob_available for s in eligible) else "FAIL")
        + f" | {sum(1 for s in eligible if s.blob_available)}/{len(eligible)} eligible rows |",
        "| Verifiable rot reference | "
        + ("PASS" if degraded_eligible else "WARN")
        + f" | {rot_cases} eligible degraded snapshots |",
        "| Repository build/test smoke | PENDING | Not executed — clone+test harness absent |",
        "| Agent runs | N/A | Explicitly out of scope |",
        "| Trace logging | N/A | Future implementation |",
        "",
        "## Kill criteria (pre-flight)",
        "",
        f"| Criterion | Threshold | Current | Pass |",
        f"|-----------|-----------|---------|------|",
        f"| Valid observed-rot cases | ≥10 | {rot_cases} | {'NO' if kill_rot else 'YES'} |",
        f"| P1∩degraded eligible | ≥10 (pilot target) | {len(p1_degraded)} | {'NO' if len(p1_degraded) < 10 else 'YES'} |",
        f"| Truthful eligible specs | ≥10 | {len(truthful_eligible)} | {'YES' if len(truthful_eligible) >= 10 else 'NO'} |",
        "",
        "## Threats to validity (preparation)",
        "",
        "1. **Issue availability proxy** — text-pattern heuristics, not live GitHub Issues API.",
        "2. **Task availability proxy** — no compile/test execution; verified-reference anchors only.",
        "3. **Born-stale vs degraded** — distinct snapshot types; do not merge in causal analysis.",
        "4. **Mechanical VERIFIED** — tree membership, not semantic correctness.",
        "5. **Pilot selection** — P1 sample is judgment sample; cluster by `repo_id` in analysis.",
        "6. **Build gate absent** — eligible ≠ runnable until smoke checks implemented.",
        "",
        "## Recommended pilot draw (deterministic)",
        "",
        "1. Filter `experimental_eligible=true` AND `snapshot_type=degraded`.",
        "2. Restrict to `p1_sample=true`.",
        "3. Sort by `snapshot_id` ascending; take first 20–30 rows.",
        "4. Join truthful snapshot for same `spec_id` (Condition A) via paired fields.",
        "5. Record `build_check_pending` until CI harness lands.",
        "",
        "## Corpus statistics",
        "",
        f"- Specifications in panel: {spec_count:,}",
        f"- Total snapshot rows: {len(snapshots):,}",
        f"- Experiment-eligible rows: {len(eligible):,}",
        "",
    ]
    return "\n".join(lines)


def run_rq5_preparation(
    *,
    longitudinal_csv: Path = DEFAULT_RQ1_LONGITUDINAL,
    l1_paths: list[Path] | None = None,
    blobs_dir: Path = Path("data/blobs"),
    reference_summary_csv: Path = DEFAULT_REFERENCE_SUMMARY,
    output_dir: Path = DEFAULT_RQ5_EXPORT,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "dataset_csv": output_dir / "rq5_candidate_dataset.csv",
        "summary_md": output_dir / "rq5_summary.md",
        "validation_md": output_dir / "rq5_protocol_validation.md",
    }

    l1 = list(l1_paths or DEFAULT_L1_PATHS)
    rows = load_longitudinal_rows(longitudinal_csv)
    repo_urls = load_repo_urls_from_l1(l1)
    blob_index = build_blob_index(l1)
    family_groups = _load_family_groups(reference_summary_csv)
    p1_keys = load_p1_sample_keys(reference_summary_csv) if reference_summary_csv.exists() else set()

    blob_store = BlobStore(blobs_dir)

    snapshots = build_rq5_candidate_snapshots(
        rows=rows,
        repo_urls=repo_urls,
        blob_index=blob_index,
        blob_store=blob_store,
        family_by_spec=family_groups,
        p1_keys=p1_keys,
    )

    spec_count = len({(r["repo_id"], r["instruction_path"]) for r in rows if not r.get("reference_removed")})
    _write_csv(snapshots_to_rows(snapshots), paths["dataset_csv"])
    atomic_write_text(paths["summary_md"], _summary_markdown(snapshots=snapshots, spec_count=spec_count))
    atomic_write_text(
        paths["validation_md"],
        _protocol_validation_markdown(snapshots=snapshots, spec_count=spec_count),
    )
    return paths
