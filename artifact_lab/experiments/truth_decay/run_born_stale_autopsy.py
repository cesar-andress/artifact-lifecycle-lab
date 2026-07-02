"""Born-stale autopsy — full taxonomy decomposition."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from io import StringIO
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.truth_decay.born_stale_audit import (
    build_born_stale_records,
    collect_born_stale_trajectories,
)
from artifact_lab.experiments.truth_decay.born_stale_autopsy_figures import (
    render_figure_by_reference_type,
    render_figure_by_repository,
    render_figure_taxonomy,
)
from artifact_lab.experiments.truth_decay.born_stale_context import (
    build_blob_index,
    load_snippet_for_trajectory,
)
from artifact_lab.experiments.truth_decay.born_stale_llm_judges import (
    DEFAULT_JUDGE_A_MODEL,
    DEFAULT_JUDGE_B_MODEL,
    adjudicate_with_two_judges,
    build_case_prompt,
    ollama_available,
)
from artifact_lab.experiments.truth_decay.born_stale_taxonomy import (
    TAXONOMY_LABELS,
    classify_heuristic,
    needs_llm_adjudication,
)
from artifact_lab.experiments.truth_pilots.gates_common import DEFAULT_L1_PATHS, DEFAULT_RQ1_LONGITUDINAL, load_longitudinal_rows
from artifact_lab.store.blobs import BlobStore

DEFAULT_EXPORT = Path("exports/truth_decay_pilot")

LETTER_MAP = {
    "extraction_artifact": "A",
    "template_placeholder": "B",
    "normative_prescriptive": "C",
    "pre_observation_evolution": "D",
    "external_reference": "E",
    "genuine_false_claim": "F",
    "verification_anchor_mismatch": "G",
    "unresolved_disagreement": "U",
}


@dataclass
class AutopsyRecord:
    repo_id: str
    repo_url: str
    instruction_path: str
    reference_type: str
    reference: str
    first_commit: str
    first_change_type: str
    n_observations: int
    repeated_repo_count: int
    repeated_file_count: int
    snippet_available: bool
    snippet: str
    heuristic_category: str
    heuristic_confidence: str
    heuristic_rules: str
    heuristic_rationale: str
    adjudication_status: str
    final_category: str
    taxonomy_letter: str
    judge_a_model: str
    judge_a_category: str
    judge_a_rationale: str
    judge_b_model: str
    judge_b_category: str
    judge_b_rationale: str
    judge_agreement: str


def _write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        atomic_write_text(path, "")
        return
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    atomic_write_text(path, buffer.getvalue())


def _first_event_meta(
    rows: list[dict],
) -> dict[tuple[str, str, str, str], dict]:
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        if row.get("reference_removed"):
            continue
        key = (row["repo_id"], row["instruction_path"], row["reference_type"], row["reference"])
        grouped[key].append(row)
    meta = {}
    for key, events in grouped.items():
        events.sort(key=lambda r: r["commit_time"])
        first = events[0]
        meta[key] = {
            "first_commit": first.get("commit", ""),
            "first_change_type": first.get("change_type", ""),
        }
    return meta


def _statistics_rows(records: list[AutopsyRecord]) -> list[dict]:
    total = len(records) or 1
    by_cat = Counter(r.final_category for r in records)
    by_status = Counter(r.adjudication_status for r in records)
    rows = []
    for cat in list(TAXONOMY_LABELS) + ["unresolved_disagreement"]:
        n = by_cat.get(cat, 0)
        rows.append(
            {
                "metric": f"count_{cat}",
                "value": n,
                "pct_of_cohort": round(100 * n / total, 3),
            }
        )
    for status, n in sorted(by_status.items()):
        rows.append(
            {
                "metric": f"adjudication_{status}",
                "value": n,
                "pct_of_cohort": round(100 * n / total, 3),
            }
        )
    rows.append({"metric": "cohort_total", "value": len(records), "pct_of_cohort": 100.0})
    return rows


def _summary_markdown(
    *,
    records: list[AutopsyRecord],
    llm_enabled: bool,
    llm_adjudicated: int,
    disagreements: int,
) -> str:
    total = len(records)
    by_cat = Counter(r.final_category for r in records)
    by_conf = Counter(r.heuristic_confidence for r in records)
    by_status = Counter(r.adjudication_status for r in records)

    lines = [
        "# Born-Stale Autopsy — Taxonomy Summary",
        "",
        "## Purpose",
        "",
        "Descriptive decomposition of **17,747** verifiable references that **never** reach",
        "`VERIFIED` in the longitudinal panel. Categories explain **why** each reference",
        "failed mechanical verification from first observation — not engineering fault codes.",
        "",
        "## Cohort",
        "",
        f"- Born-stale references classified: **{total}**",
        f"- LLM dual-judge adjudication enabled: **{'yes' if llm_enabled else 'no'}**",
        f"- References sent to LLM judges: **{llm_adjudicated}**",
        f"- Judge disagreements (unresolved): **{disagreements}**",
        "",
        "## Inferred taxonomy (not hardcoded)",
        "",
        "Categories emerge from deterministic heuristics first, then dual local LLM judges",
        "when heuristic confidence is insufficient. Letter codes are illustrative only.",
        "",
        "| Letter | Category | Count | % |",
        "|--------|----------|------:|--:|",
    ]
    display_order = list(TAXONOMY_LABELS) + ["unresolved_disagreement"]
    for cat in display_order:
        n = by_cat.get(cat, 0)
        letter = LETTER_MAP.get(cat, "?")
        lines.append(f"| {letter} | `{cat}` | {n} | {100 * n / total:.1f}% |")

    lines.extend(
        [
            "",
            "## Adjudication status",
            "",
        ]
    )
    for status, n in sorted(by_status.items(), key=lambda x: -x[1]):
        note = ""
        if status == "llm_quota_exceeded":
            note = " — heuristic provisional; rerun without `--max-llm-cases` for full LLM pass"
        lines.append(f"- **{status}:** {n} ({100 * n / total:.1f}%){note}")

    lines.extend(
        [
            "",
            "## Heuristic confidence distribution",
            "",
        ]
    )
    for conf, n in sorted(by_conf.items()):
        lines.append(f"- **{conf}:** {n} ({100 * n / total:.1f}%)")

    lines.extend(
        [
            "",
            "## Documented heuristics (deterministic pass)",
            "",
            "### extraction_artifact (A)",
            "- Prose product tokens (`Node.js`), invalid path chars, URL-like paths, directory `/`",
            "- Reference fails `VALID_FILENAME` grammar without repo path structure",
            "",
            "### template_placeholder (B)",
            "- `examples/` paths, placeholder syntax (`<>`, `{}`, `path_to_`, `TODO`)",
            "- Cross-repo generic tokens (`SKILL.md`, `package.json`) with ≥3 repo repetitions",
            "",
            "### normative_prescriptive (C)",
            "- Rule/skill/cursor instruction surfaces",
            "- References to convention docs (`AGENTS.md`, `SKILL.md`) with prescriptive snippet language",
            "",
            "### pre_observation_evolution (D)",
            "- Structured path, file `change_type=modify` at first snapshot, ≥2 observations, always MISSING",
            "",
            "### external_reference (E)",
            "- Dependencies, scoped packages, URL tokens, prose external product names",
            "",
            "### verification_anchor_mismatch (G)",
            "- `./`/`../` prefixes or single-segment filenames verified from repo root only",
            "",
            "### genuine_false_claim (F)",
            "- Structured repo-like path, always MISSING, no higher-priority rule fired (low confidence)",
            "",
            "## LLM adjudication protocol",
            "",
            f"- **Judge A:** `{DEFAULT_JUDGE_A_MODEL}` (Ollama, JSON output)",
            f"- **Judge B:** `{DEFAULT_JUDGE_B_MODEL}` (skeptical framing, same taxonomy)",
            "- Trigger: heuristic confidence `low`, or medium `genuine_false_claim`, or no category",
            "- **Agreement:** `final_category` = shared label; status `llm_agreement`",
            "- **Disagreement:** `final_category` = `unresolved_disagreement`; row copied to",
            "  `born_stale_disagreements.csv`; **never silently merged**",
            "",
            "## Uncertainty and limitations",
            "",
            "1. **Snippets optional:** when L1b blob missing, heuristics use path shape only.",
            "2. **Normative vs false claim** is ambiguous without semantic interpretation.",
            "3. **Pre-observation evolution** cannot confirm path existed before panel without git archaeology.",
            "4. **LLM judges** are local, non-blinded to heuristics, and not validated against human gold.",
            "5. **Descriptive only:** no causal claims; does not modify RQ1/RQ2 datasets.",
            "6. **Repo concentration** persists — taxonomy mass may reflect template repos.",
            "",
            "## Implications",
            "",
            "- Born-stale is **heterogeneous**; a single \"staleness rate\" blends measurement error,",
            "  templates, and genuine false claims.",
            "- RQ3 (agent vs human) should stratify by taxonomy category, not aggregate born-stale.",
            "- Primary scientific construct shifts from **Truth Decay** to **initial reference validity**.",
            "",
            "## Outputs",
            "",
            "- `born_stale_taxonomy.csv` — full per-reference classification",
            "- `born_stale_statistics.csv` — aggregate counts",
            "- `born_stale_disagreements.csv` — unresolved LLM disagreements only",
            "- `born_stale_examples.csv` — stratified examples per category",
            "- `figure_born_stale_taxonomy.pdf`",
            "- `figure_born_stale_by_reference_type.pdf`",
            "- `figure_born_stale_by_repository.pdf`",
            "",
        ]
    )
    return "\n".join(lines)


def _example_rows(records: list[AutopsyRecord], *, per_category: int = 15) -> list[dict]:
    by_cat: dict[str, list[AutopsyRecord]] = defaultdict(list)
    for r in records:
        by_cat[r.final_category].append(r)
    out: list[dict] = []
    for cat in list(TAXONOMY_LABELS) + ["unresolved_disagreement"]:
        subset = by_cat.get(cat, [])[:per_category]
        for r in subset:
            row = asdict(r)
            row["example_category"] = cat
            out.append(row)
    return out


def run_born_stale_autopsy(
    *,
    longitudinal_csv: Path = DEFAULT_RQ1_LONGITUDINAL,
    l1_paths: list[Path] | None = None,
    blobs_dir: Path = Path("data/blobs"),
    output_dir: Path = DEFAULT_EXPORT,
    enable_llm: bool = True,
    max_llm_cases: int | None = None,
    ollama_url: str = "http://127.0.0.1:11434/api/generate",
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "taxonomy_csv": output_dir / "born_stale_taxonomy.csv",
        "summary_md": output_dir / "born_stale_summary.md",
        "disagreements_csv": output_dir / "born_stale_disagreements.csv",
        "examples_csv": output_dir / "born_stale_examples.csv",
        "statistics_csv": output_dir / "born_stale_statistics.csv",
        "fig_taxonomy": output_dir / "figure_born_stale_taxonomy.pdf",
        "fig_by_type": output_dir / "figure_born_stale_by_reference_type.pdf",
        "fig_by_repo": output_dir / "figure_born_stale_by_repository.pdf",
    }

    rows = load_longitudinal_rows(longitudinal_csv)
    never_verified, _ = collect_born_stale_trajectories(rows)
    audit_records = build_born_stale_records(never_verified, rows)
    event_meta = _first_event_meta(rows)

    l1 = l1_paths if l1_paths else [p for p in DEFAULT_L1_PATHS if p.exists()]
    blob_index = build_blob_index(l1) if l1 else {}
    blob_store = BlobStore(blobs_dir)

    llm_ok = enable_llm and ollama_available(ollama_url)
    llm_count = 0
    disagreement_count = 0
    autopsy: list[AutopsyRecord] = []
    total = len(audit_records)

    print(f"born-stale autopsy: cohort={total}, llm_enabled={llm_ok}", flush=True)

    for idx, rec in enumerate(audit_records, start=1):
        key = (rec.repo_id, rec.instruction_path, rec.reference_type, rec.reference)
        meta = event_meta.get(key, {"first_commit": "", "first_change_type": ""})
        snippet, snippet_ok = load_snippet_for_trajectory(
            repo_id=rec.repo_id,
            instruction_path=rec.instruction_path,
            commit=meta["first_commit"],
            reference=rec.reference,
            blob_index=blob_index,
            blob_store=blob_store,
        )
        verdict = classify_heuristic(
            reference_type=rec.reference_type,
            reference=rec.reference,
            instruction_path=rec.instruction_path,
            n_observations=rec.n_observations,
            first_change_type=meta["first_change_type"],
            repeated_repo_count=rec.repeated_repo_count,
            repeated_file_count=rec.repeated_file_count,
            snippet=snippet,
        )

        judge_a_model = judge_b_model = ""
        judge_a_cat = judge_b_cat = judge_a_rat = judge_b_rat = ""
        judge_agreement = ""
        final_category = verdict.category or ""
        if verdict.confidence == "high" and verdict.category:
            status = "deterministic_high"
        elif verdict.confidence == "medium" and verdict.category:
            status = "deterministic_medium"
        else:
            status = ""

        if needs_llm_adjudication(verdict) and llm_ok and (max_llm_cases is None or llm_count < max_llm_cases):
            prompt = build_case_prompt(
                repo_url=rec.repo_url,
                instruction_path=rec.instruction_path,
                reference_type=rec.reference_type,
                reference=rec.reference,
                snippet=snippet,
                heuristic_category=verdict.category,
                heuristic_rationale=verdict.rationale,
            )
            ja, jb, agree = adjudicate_with_two_judges(
                prompt,
                ollama_url=ollama_url,
            )
            llm_count += 1
            if llm_count % 25 == 0:
                print(f"llm adjudication progress: {llm_count} ({idx}/{total})", flush=True)
            judge_a_model, judge_b_model = ja.model, jb.model
            judge_a_cat, judge_b_cat = ja.category or "", jb.category or ""
            judge_a_rat, judge_b_rat = ja.rationale, jb.rationale
            judge_agreement = str(agree)
            if agree and ja.category:
                final_category = ja.category
                status = "llm_agreement"
            elif ja.category and jb.category and ja.category != jb.category:
                final_category = "unresolved_disagreement"
                status = "llm_disagreement"
                disagreement_count += 1
            else:
                final_category = verdict.category or "unresolved_disagreement"
                status = "llm_inconclusive"
        elif needs_llm_adjudication(verdict) and not llm_ok:
            final_category = verdict.category or "unresolved_disagreement"
            status = "llm_unavailable"
        elif needs_llm_adjudication(verdict) and max_llm_cases is not None and llm_count >= max_llm_cases:
            final_category = verdict.category or "unresolved_disagreement"
            status = "llm_quota_exceeded"
        elif not status:
            final_category = verdict.category or "unresolved_disagreement"
            status = "deterministic_fallback"

        autopsy.append(
            AutopsyRecord(
                repo_id=rec.repo_id,
                repo_url=rec.repo_url,
                instruction_path=rec.instruction_path,
                reference_type=rec.reference_type,
                reference=rec.reference,
                first_commit=meta["first_commit"],
                first_change_type=meta["first_change_type"],
                n_observations=rec.n_observations,
                repeated_repo_count=rec.repeated_repo_count,
                repeated_file_count=rec.repeated_file_count,
                snippet_available=snippet_ok,
                snippet=snippet[:300],
                heuristic_category=verdict.category or "",
                heuristic_confidence=verdict.confidence,
                heuristic_rules=";".join(verdict.rules_fired),
                heuristic_rationale=verdict.rationale,
                adjudication_status=status,
                final_category=final_category,
                taxonomy_letter=LETTER_MAP.get(final_category, "?"),
                judge_a_model=judge_a_model,
                judge_a_category=judge_a_cat,
                judge_a_rationale=judge_a_rat,
                judge_b_model=judge_b_model,
                judge_b_category=judge_b_cat,
                judge_b_rationale=judge_b_rat,
                judge_agreement=judge_agreement,
            )
        )

        if idx % 500 == 0:
            print(f"processed {idx}/{total} (llm={llm_count})", flush=True)

    taxonomy_rows = [asdict(r) for r in autopsy]
    disagreement_rows = [row for row in taxonomy_rows if row["adjudication_status"] == "llm_disagreement"]

    _write_csv(taxonomy_rows, paths["taxonomy_csv"])
    _write_csv(disagreement_rows, paths["disagreements_csv"])
    _write_csv(_statistics_rows(autopsy), paths["statistics_csv"])
    _write_csv(_example_rows(autopsy), paths["examples_csv"])
    atomic_write_text(
        paths["summary_md"],
        _summary_markdown(
            records=autopsy,
            llm_enabled=llm_ok,
            llm_adjudicated=llm_count,
            disagreements=disagreement_count,
        ),
    )

    cat_counts = Counter(r.final_category for r in autopsy)
    render_figure_taxonomy(cat_counts, paths["fig_taxonomy"])
    render_figure_by_reference_type(taxonomy_rows, paths["fig_by_type"])
    render_figure_by_repository(taxonomy_rows, paths["fig_by_repo"])

    return paths
