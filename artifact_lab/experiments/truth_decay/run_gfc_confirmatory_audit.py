"""Run confirmatory audit of born-stale genuine_false_claim labels."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import asdict
from io import StringIO
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.truth_decay.audit_statistics import wilson_interval
from artifact_lab.experiments.truth_decay.born_stale_llm_judges import (
    DEFAULT_JUDGE_A_MODEL,
    DEFAULT_JUDGE_B_MODEL,
    ollama_available,
)
from artifact_lab.experiments.truth_decay.gfc_confirmatory import (
    CATEGORY_LETTERS,
    CONFIRMATORY_CATEGORIES,
    ConfirmatoryRecord,
    classify_gfc_confirmatory,
    load_genuine_false_claim_rows,
    needs_confirmatory_llm,
    record_to_row,
)
from artifact_lab.experiments.truth_decay.gfc_confirmatory_figures import render_figure_gfc_confirmatory
from artifact_lab.experiments.truth_decay.gfc_confirmatory_llm_judges import (
    adjudicate_confirmatory,
    build_confirmatory_prompt,
)

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


def _example_rows(records: list[ConfirmatoryRecord], *, per_category: int = 12) -> list[dict]:
    by_cat: dict[str, list[ConfirmatoryRecord]] = defaultdict(list)
    for record in records:
        by_cat[record.final_category].append(record)
    out: list[dict] = []
    for cat in CONFIRMATORY_CATEGORIES:
        for record in by_cat.get(cat, [])[:per_category]:
            row = asdict(record)
            row["example_category"] = cat
            out.append(row)
    return out


def _summary_markdown(
    *,
    records: list[ConfirmatoryRecord],
    llm_enabled: bool,
    llm_adjudicated: int,
    disagreements: int,
) -> str:
    total = len(records)
    by_cat = Counter(r.final_category for r in records)
    confirmed = by_cat.get("confirmed_false", 0)
    prop = confirmed / total if total else 0.0
    lo, hi = wilson_interval(confirmed, total)

    lines = [
        "# Born-Stale Confirmatory Audit — `genuine_false_claim`",
        "",
        "## Purpose",
        "",
        "Second-pass validation of **1,405** references previously labeled `genuine_false_claim`",
        "in the born-stale autopsy. Determines how many are **confirmed false path claims**",
        "versus measurement artifacts (template, anchor, extraction, normative).",
        "",
        "## Cohort",
        "",
        f"- Prior `genuine_false_claim` references audited: **{total}**",
        f"- LLM dual-judge enabled: **{'yes' if llm_enabled else 'no'}**",
        f"- References sent to LLM judges: **{llm_adjudicated}**",
        f"- Judge disagreements (unresolved): **{disagreements}**",
        "",
        "## Confirmed-false rate",
        "",
        f"- **Confirmed false (A):** {confirmed} ({100 * prop:.1f}%)",
        f"- Wilson 95% CI: **{100 * lo:.1f}%–{100 * hi:.1f}%**",
        f"- Adjusted born-stale false-claim rate (17,747 cohort): **{100 * confirmed / 17747:.2f}%**",
        "",
        "## Confirmatory taxonomy",
        "",
        "| Letter | Category | Count | % |",
        "|--------|----------|------:|--:|",
    ]
    for cat in CONFIRMATORY_CATEGORIES:
        n = by_cat.get(cat, 0)
        lines.append(f"| {CATEGORY_LETTERS[cat]} | `{cat}` | {n} | {100 * n / total:.1f}% |")

    lines.extend(
        [
            "",
            "## Protocol",
            "",
            "1. Deterministic confirmatory heuristics override prior LLM `genuine_false_claim` when",
            "   template/glob, command-like, anchor, normative, or extraction signals fire.",
            f"2. Dual LLM judges (`{DEFAULT_JUDGE_A_MODEL}`, `{DEFAULT_JUDGE_B_MODEL}`) only for",
            "   `ambiguous` cases.",
            "3. Disagreements remain `ambiguous`; never silently merged.",
            "",
            "## Implications",
            "",
            "- The raw born-stale `genuine_false_claim` rate (7.9%) is an **upper bound**.",
            "- Reviewer-facing false-claim construct should use **confirmed_false** with CI.",
            "",
            "## Outputs",
            "",
            "- `gfc_confirmatory_audit.csv`",
            "- `gfc_confirmatory_examples.csv`",
            "- `gfc_confirmatory_disagreements.csv`",
            "- `figure_gfc_confirmatory.pdf`",
            "",
        ]
    )
    return "\n".join(lines)


def run_gfc_confirmatory_audit(
    *,
    taxonomy_csv: Path = DEFAULT_EXPORT / "born_stale_taxonomy.csv",
    output_dir: Path = DEFAULT_EXPORT,
    enable_llm: bool = True,
    max_llm_cases: int | None = None,
    ollama_url: str = "http://127.0.0.1:11434/api/generate",
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "audit_csv": output_dir / "gfc_confirmatory_audit.csv",
        "summary_md": output_dir / "gfc_confirmatory_summary.md",
        "examples_csv": output_dir / "gfc_confirmatory_examples.csv",
        "disagreements_csv": output_dir / "gfc_confirmatory_disagreements.csv",
        "figure": output_dir / "figure_gfc_confirmatory.pdf",
    }

    source_rows = load_genuine_false_claim_rows(taxonomy_csv)
    llm_ok = enable_llm and ollama_available(ollama_url)
    llm_count = 0
    disagreement_count = 0
    records: list[ConfirmatoryRecord] = []

    print(f"gfc confirmatory audit: cohort={len(source_rows)}, llm_enabled={llm_ok}", flush=True)

    for idx, row in enumerate(source_rows, start=1):
        category, confidence, rules, rationale = classify_gfc_confirmatory(
            reference_type=row["reference_type"],
            reference=row["reference"],
            instruction_path=row["instruction_path"],
            n_observations=int(row.get("n_observations") or 0),
            first_change_type=row.get("first_change_type") or "",
            repeated_repo_count=int(row.get("repeated_repo_count") or 1),
            repeated_file_count=int(row.get("repeated_file_count") or 1),
            snippet=row.get("snippet") or "",
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

        if needs_confirmatory_llm(category=category, confidence=confidence) and llm_ok and (
            max_llm_cases is None or llm_count < max_llm_cases
        ):
            prompt = build_confirmatory_prompt(
                repo_url=row.get("repo_url") or "",
                instruction_path=row["instruction_path"],
                reference_type=row["reference_type"],
                reference=row["reference"],
                snippet=row.get("snippet") or "",
                heuristic_category=category,
                heuristic_rationale=rationale,
            )
            ja, jb, agree = adjudicate_confirmatory(prompt, ollama_url=ollama_url)
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
        elif needs_confirmatory_llm(category=category, confidence=confidence) and not llm_ok:
            final_category = category if category != "ambiguous" else "ambiguous"
            status = "llm_unavailable"
        elif needs_confirmatory_llm(category=category, confidence=confidence):
            final_category = category if category != "ambiguous" else "ambiguous"
            status = "llm_quota_exceeded"

        records.append(
            ConfirmatoryRecord(
                repo_id=row["repo_id"],
                repo_url=row.get("repo_url") or "",
                instruction_path=row["instruction_path"],
                reference_type=row["reference_type"],
                reference=row["reference"],
                first_commit=row.get("first_commit") or "",
                first_change_type=row.get("first_change_type") or "",
                n_observations=int(row.get("n_observations") or 0),
                repeated_repo_count=int(row.get("repeated_repo_count") or 1),
                repeated_file_count=int(row.get("repeated_file_count") or 1),
                snippet_available=str(row.get("snippet_available", "")).lower() == "true",
                snippet=(row.get("snippet") or "")[:300],
                prior_final_category=row.get("final_category") or "",
                prior_adjudication_status=row.get("adjudication_status") or "",
                prior_judge_a_category=row.get("judge_a_category") or "",
                prior_judge_b_category=row.get("judge_b_category") or "",
                heuristic_category=category,
                heuristic_confidence=confidence,
                heuristic_rules=";".join(rules),
                heuristic_rationale=rationale,
                adjudication_status=status,
                final_category=final_category,
                category_letter=CATEGORY_LETTERS.get(final_category, "F"),
                is_confirmed_false=final_category == "confirmed_false",
                judge_a_model=judge_a_model,
                judge_a_category=judge_a_cat,
                judge_a_rationale=judge_a_rat,
                judge_b_model=judge_b_model,
                judge_b_category=judge_b_cat,
                judge_b_rationale=judge_b_rat,
                judge_agreement=judge_agreement,
            )
        )

        if idx % 200 == 0:
            print(f"processed {idx}/{len(source_rows)} (llm={llm_count})", flush=True)

    audit_rows = [record_to_row(r) for r in records]
    disagreement_rows = [row for row in audit_rows if row["adjudication_status"] == "llm_disagreement"]

    _write_csv(audit_rows, paths["audit_csv"])
    _write_csv(disagreement_rows, paths["disagreements_csv"])
    _write_csv(_example_rows(records), paths["examples_csv"])
    atomic_write_text(
        paths["summary_md"],
        _summary_markdown(
            records=records,
            llm_enabled=llm_ok,
            llm_adjudicated=llm_count,
            disagreements=disagreement_count,
        ),
    )
    render_figure_gfc_confirmatory(Counter(r.final_category for r in records), paths["figure"])

    confirmed = sum(1 for r in records if r.is_confirmed_false)
    print(f"gfc confirmatory complete: confirmed_false={confirmed}/{len(records)}", flush=True)
    return paths
