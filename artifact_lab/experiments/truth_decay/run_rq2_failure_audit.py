"""Run RQ2 post-verification failure audit."""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import asdict
from io import StringIO
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.truth_decay.born_stale_context import (
    build_blob_index,
    load_snippet_for_trajectory,
)
from artifact_lab.experiments.truth_decay.born_stale_llm_judges import (
    DEFAULT_JUDGE_A_MODEL,
    DEFAULT_JUDGE_B_MODEL,
    ollama_available,
)
from artifact_lab.experiments.truth_decay.rq2_failure_audit import (
    CATEGORY_LETTERS,
    FAILURE_CATEGORIES,
    FailureAuditRecord,
    build_failure_audit_records,
    classify_failure_context,
    load_survival_failures,
    needs_rq2_llm_adjudication,
    record_to_row,
)
from artifact_lab.experiments.truth_decay.rq2_failure_llm_judges import (
    adjudicate_rq2_failure,
    build_rq2_failure_prompt,
)
from artifact_lab.experiments.truth_decay.rq2_failure_statistics import (
    compute_audit_statistics,
    load_born_stale_repo_counts,
)
from artifact_lab.experiments.truth_pilots.gates_common import (
    DEFAULT_L1_PATHS,
    DEFAULT_RQ1_LONGITUDINAL,
    load_longitudinal_rows,
    _csv_bool,
)
from artifact_lab.store.blobs import BlobStore

DEFAULT_EXPORT = Path("exports/truth_decay_pilot")
VERIFIED_COHORT_SIZE = 4521


def _write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        atomic_write_text(path, "")
        return
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    atomic_write_text(path, buffer.getvalue())


def _summary_markdown(
    *,
    records: list[FailureAuditRecord],
    stats,
    llm_enabled: bool,
    llm_adjudicated: int,
    disagreements: int,
) -> str:
    total = len(records)
    by_cat = Counter(r.final_category for r in records)
    by_status = Counter(r.adjudication_status for r in records)

    lines = [
        "# RQ2 Post-Verification Failure Audit",
        "",
        "## Purpose",
        "",
        "Validate whether the **121** RQ2 `first_missing` events after at least one",
        "`VERIFIED` observation are genuine reference decay or verification/measurement artifacts.",
        "",
        "## Cohort",
        "",
        f"- Post-verification failures audited: **{total}**",
        f"- Verified-at-least-once cohort (RQ2 denominator): **{stats.verified_cohort_size}**",
        f"- LLM dual-judge enabled: **{'yes' if llm_enabled else 'no'}**",
        f"- References sent to LLM judges: **{llm_adjudicated}**",
        f"- Judge disagreements (unresolved): **{disagreements}**",
        "",
        "## Adjusted decay metrics",
        "",
        f"- Raw post-verification failures: **{stats.n_failures}**",
        f"- Adjusted genuine post-verification decay: **{stats.n_genuine_adjusted}**",
        f"- Genuine-decay proportion among failures: **{100 * stats.genuine_proportion:.1f}%**",
        f"  (Wilson 95% CI: {100 * stats.genuine_proportion_ci_low:.1f}%–{100 * stats.genuine_proportion_ci_high:.1f}%)",
        f"- Adjusted decay rate (vs verified cohort): **{100 * stats.adjusted_decay_rate:.2f}%**",
        f"  (Wilson 95% CI: {100 * stats.adjusted_decay_rate_ci_low:.2f}%–{100 * stats.adjusted_decay_rate_ci_high:.2f}%)",
        "",
        "## Born-false vs post-verification decay ratio",
        "",
        f"- Born-stale raw cohort: **{stats.born_stale_raw}**",
        f"- Born-stale adjusted genuine-false: **{stats.born_stale_genuine_adjusted}**",
        f"- Raw ratio (born-stale raw / post failures): **{stats.raw_ratio_born_to_post:.2f}**",
        f"- Adjusted ratio (born genuine-false / post genuine decay): **{stats.adjusted_ratio_born_to_post:.2f}**",
        f"- Bootstrap 95% CI (clustered by repository): **{stats.bootstrap_ratio_ci_low:.2f}–{stats.bootstrap_ratio_ci_high:.2f}**",
        "",
        "## Taxonomy (deterministic first, dual LLM for ambiguous)",
        "",
        "| Letter | Category | Count | % |",
        "|--------|----------|------:|--:|",
    ]
    for cat in FAILURE_CATEGORIES:
        n = by_cat.get(cat, 0)
        letter = CATEGORY_LETTERS[cat]
        lines.append(f"| {letter} | `{cat}` | {n} | {100 * n / total:.1f}% |")

    lines.extend(
        [
            "",
            "## Adjudication status",
            "",
        ]
    )
    for status, n in sorted(by_status.items(), key=lambda x: -x[1]):
        lines.append(f"- **{status}:** {n} ({100 * n / total:.1f}%)")

    lines.extend(
        [
            "",
            "## Protocol",
            "",
            "1. **Deterministic heuristics** reuse born-stale taxonomy with post-verification signals",
            "   (`ever_repaired`, `returned_after_missing`, basename collision at failure commit).",
            f"2. **Dual LLM judges** (`{DEFAULT_JUDGE_A_MODEL}`, `{DEFAULT_JUDGE_B_MODEL}`) only when",
            "   heuristic confidence is insufficient or category is `ambiguous`.",
            "3. **Disagreements** remain `ambiguous`; rows copied to `rq2_failure_audit_disagreements.csv`.",
            "",
            "## Limitations",
            "",
            "- Does not modify RQ2 survival outputs or prior datasets.",
            "- Snippet context depends on L1/L1b blob availability at first observation commit.",
            "- Genuine decay requires semantic judgment for path moves vs deletions.",
            "",
            "## Outputs",
            "",
            "- `rq2_failure_audit.csv`",
            "- `rq2_failure_audit_summary.md`",
            "- `rq2_failure_audit_disagreements.csv`",
            "",
        ]
    )
    return "\n".join(lines)


def run_rq2_failure_audit(
    *,
    survival_csv: Path = DEFAULT_EXPORT / "rq2_survival.csv",
    longitudinal_csv: Path = DEFAULT_RQ1_LONGITUDINAL,
    born_stale_taxonomy_csv: Path = DEFAULT_EXPORT / "born_stale_taxonomy.csv",
    l1_paths: list[Path] | None = None,
    blobs_dir: Path = Path("data/blobs"),
    output_dir: Path = DEFAULT_EXPORT,
    enable_llm: bool = True,
    max_llm_cases: int | None = None,
    ollama_url: str = "http://127.0.0.1:11434/api/generate",
    verified_cohort_size: int = VERIFIED_COHORT_SIZE,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "audit_csv": output_dir / "rq2_failure_audit.csv",
        "summary_md": output_dir / "rq2_failure_audit_summary.md",
        "disagreements_csv": output_dir / "rq2_failure_audit_disagreements.csv",
    }

    failures = load_survival_failures(survival_csv)
    if len(failures) != 121:
        print(f"warning: expected 121 failures, found {len(failures)}", flush=True)

    rows = load_longitudinal_rows(longitudinal_csv)
    prepared = build_failure_audit_records(survival_failures=failures, longitudinal_rows=rows)

    l1 = l1_paths if l1_paths else [p for p in DEFAULT_L1_PATHS if p.exists()]
    blob_index = build_blob_index(l1) if l1 else {}
    blob_store = BlobStore(blobs_dir)

    llm_ok = enable_llm and ollama_available(ollama_url)
    llm_count = 0
    disagreement_count = 0
    records: list[FailureAuditRecord] = []

    print(f"rq2 failure audit: cohort={len(prepared)}, llm_enabled={llm_ok}", flush=True)

    for idx, ctx in enumerate(prepared, start=1):
        surv = ctx["survival_row"]
        snippet, snippet_ok = load_snippet_for_trajectory(
            repo_id=surv["repo_id"],
            instruction_path=surv["instruction_path"],
            commit=ctx["first_commit"],
            reference=surv["reference"],
            blob_index=blob_index,
            blob_store=blob_store,
        )
        category, confidence, rules, rationale, born = classify_failure_context(
            reference_type=surv["reference_type"],
            reference=surv["reference"],
            instruction_path=surv["instruction_path"],
            n_observations=int(surv.get("n_observations") or 0),
            first_change_type=ctx["first_change_type"],
            repeated_repo_count=ctx["repeated_repo_count"],
            repeated_file_count=ctx["repeated_file_count"],
            snippet=snippet,
            ever_repaired=_csv_bool(surv.get("ever_repaired")),
            returned_after_missing=ctx["returned_after_missing"],
            basename_collision_verified=ctx["basename_collision_verified"],
        )

        judge_a_model = judge_b_model = ""
        judge_a_cat = judge_b_cat = judge_a_rat = judge_b_rat = ""
        judge_agreement = ""
        final_category = category
        if confidence == "high":
            status = "deterministic_high"
        elif confidence == "medium":
            status = "deterministic_medium"
        else:
            status = "deterministic_low"

        if needs_rq2_llm_adjudication(
            category=category,
            confidence=confidence,
            born_verdict=born,
        ) and llm_ok and (max_llm_cases is None or llm_count < max_llm_cases):
            prompt = build_rq2_failure_prompt(
                repo_url=ctx["repo_url"],
                instruction_path=surv["instruction_path"],
                reference_type=surv["reference_type"],
                reference=surv["reference"],
                time_origin=surv["time_origin"],
                time_end=surv["time_end"],
                snippet=snippet,
                heuristic_category=category,
                heuristic_rationale=rationale,
                ever_repaired=_csv_bool(surv.get("ever_repaired")),
                returned_after_missing=ctx["returned_after_missing"],
            )
            ja, jb, agree = adjudicate_rq2_failure(prompt, ollama_url=ollama_url)
            llm_count += 1
            judge_a_model, judge_b_model = ja.model, jb.model
            judge_a_cat, judge_b_cat = ja.category or "", jb.category or ""
            judge_a_rat, judge_b_rat = ja.rationale, jb.rationale
            judge_agreement = str(agree)
            if agree and ja.category:
                final_category = ja.category
                status = "llm_agreement"
            elif ja.category and jb.category and ja.category != jb.category:
                final_category = "ambiguous"
                status = "llm_disagreement"
                disagreement_count += 1
            else:
                final_category = category if category != "ambiguous" else "ambiguous"
                status = "llm_inconclusive"
        elif needs_rq2_llm_adjudication(category=category, confidence=confidence, born_verdict=born) and not llm_ok:
            final_category = category if category != "ambiguous" else "ambiguous"
            status = "llm_unavailable"
        elif needs_rq2_llm_adjudication(category=category, confidence=confidence, born_verdict=born):
            final_category = category if category != "ambiguous" else "ambiguous"
            status = "llm_quota_exceeded"

        records.append(
            FailureAuditRecord(
                repo_id=surv["repo_id"],
                repo_url=ctx["repo_url"],
                instruction_path=surv["instruction_path"],
                reference_type=surv["reference_type"],
                reference=surv["reference"],
                time_origin=surv["time_origin"],
                time_end=surv["time_end"],
                duration_days=float(surv.get("duration_days") or 0),
                ever_repaired=_csv_bool(surv.get("ever_repaired")),
                post_failure_followup_days=(
                    float(surv["post_failure_followup_days"])
                    if surv.get("post_failure_followup_days")
                    else None
                ),
                failure_commit=ctx["failure_commit"],
                failure_transition=ctx["failure_transition"],
                verified_before_failure=True,
                returned_after_missing=ctx["returned_after_missing"],
                basename_collision_verified=ctx["basename_collision_verified"],
                n_observations=int(surv.get("n_observations") or 0),
                repeated_repo_count=ctx["repeated_repo_count"],
                repeated_file_count=ctx["repeated_file_count"],
                snippet_available=snippet_ok,
                snippet=snippet[:300],
                born_stale_heuristic_category=born.category or "",
                born_stale_heuristic_confidence=born.confidence,
                born_stale_heuristic_rules=";".join(born.rules_fired),
                heuristic_category=category,
                heuristic_confidence=confidence,
                heuristic_rules=";".join(rules),
                heuristic_rationale=rationale,
                adjudication_status=status,
                final_category=final_category,
                category_letter=CATEGORY_LETTERS.get(final_category, "G"),
                is_genuine_decay=final_category == "genuine_decay",
                judge_a_model=judge_a_model,
                judge_a_category=judge_a_cat,
                judge_a_rationale=judge_a_rat,
                judge_b_model=judge_b_model,
                judge_b_category=judge_b_cat,
                judge_b_rationale=judge_b_rat,
                judge_agreement=judge_agreement,
            )
        )

        if idx % 25 == 0:
            print(f"processed {idx}/{len(prepared)} (llm={llm_count})", flush=True)

    born_raw, born_genuine, born_by_repo_raw, born_by_repo_genuine = load_born_stale_repo_counts(
        born_stale_taxonomy_csv
    )
    stats = compute_audit_statistics(
        records=records,
        verified_cohort_size=verified_cohort_size,
        born_stale_raw=born_raw,
        born_stale_genuine_adjusted=born_genuine,
        born_by_repo_raw=born_by_repo_raw,
        born_by_repo_genuine=born_by_repo_genuine,
    )

    audit_rows = [record_to_row(r) for r in records]
    disagreement_rows = [row for row in audit_rows if row["adjudication_status"] == "llm_disagreement"]

    _write_csv(audit_rows, paths["audit_csv"])
    _write_csv(disagreement_rows, paths["disagreements_csv"])
    atomic_write_text(
        paths["summary_md"],
        _summary_markdown(
            records=records,
            stats=stats,
            llm_enabled=llm_ok,
            llm_adjudicated=llm_count,
            disagreements=disagreement_count,
        ),
    )

    print(
        f"rq2 failure audit complete: genuine_decay={stats.n_genuine_adjusted}/{stats.n_failures}, "
        f"disagreements={disagreement_count}",
        flush=True,
    )
    return paths
