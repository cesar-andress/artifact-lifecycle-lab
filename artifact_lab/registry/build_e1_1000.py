"""Build the E1 1000-repository scientific cohort registry."""

from __future__ import annotations

import argparse
import csv
import random
import sys
from collections import defaultdict
from pathlib import Path

from artifact_lab.contracts.repo_id import normalize_repo_url
from artifact_lab.registry.pools import (
    STRATUM_AI_INSTRUCTION,
    STRATUM_GENERAL_OSS,
    STRATUM_MIXED_CONTROL,
    artifact_family,
    candidate_row,
    is_excluded_name,
    load_jsonl,
    star_stratum,
    topic_predicate,
)
from artifact_lab.registry.schema import (
    E1_1000_REGISTRY_COLUMNS,
    E1_1000_REGISTRY_VERSION,
    E1_1000_STRATUM_SIZES,
    E1_1000_TARGET_SIZE,
)

DEFAULT_VSDLC_ELIGIBLE = Path.home() / "papers/vsdlc/vsdlc/data/interim/eligible_repos_enriched.jsonl"
DEFAULT_SECOND_FRAME = Path.home() / "papers/vsdlc/vsdlc/data/raw/second_frame_candidates.jsonl"
DEFAULT_GENERAL_OSS = Path("data/registry/sources/general_oss_candidates.jsonl")
DEFAULT_OUTPUT = Path("data/registry/e1_1000_repos.csv")
DEFAULT_COHORT_DESIGN = Path("exports/e1_1000/cohort_design.md")
DEFAULT_SEED = 42


def _round_robin_sample(
    groups: dict[tuple[str, ...], list[dict]],
    *,
    sample_size: int,
    seed: int,
) -> list[dict]:
    keys = sorted(groups.keys())
    rng = random.Random(seed)
    rng.shuffle(keys)
    selected: list[dict] = []
    indices = dict.fromkeys(keys, 0)
    while len(selected) < sample_size:
        progressed = False
        for key in keys:
            idx = indices[key]
            if idx < len(groups[key]):
                selected.append(groups[key][idx])
                indices[key] = idx + 1
                progressed = True
                if len(selected) >= sample_size:
                    break
        if not progressed:
            break
    if len(selected) < sample_size:
        raise RuntimeError(f"could only sample {len(selected)} repos, need {sample_size}")
    return selected


def _load_instruction_candidates(vsdlc_path: Path) -> list[dict]:
    rows: list[dict] = []
    for row in load_jsonl(vsdlc_path):
        full_name = row["full_name"]
        if is_excluded_name(full_name, description=row.get("github_description")):
            continue
        rows.append(row)
    rows.sort(key=lambda item: item["repository_url"].lower())
    return rows


def _load_mixed_control_candidates(second_frame_path: Path, *, exclude_urls: set[str]) -> list[dict]:
    rows: list[dict] = []
    for row in load_jsonl(second_frame_path):
        url = normalize_repo_url(row["repository_url"])
        if url.lower() in exclude_urls:
            continue
        full_name = row["full_name"]
        if is_excluded_name(full_name, description=row.get("github_description")):
            continue
        rows.append(row)
    rows.sort(key=lambda item: item["repository_url"].lower())
    return rows


def _load_general_oss_candidates(general_oss_path: Path, *, exclude_urls: set[str]) -> list[dict]:
    rows: list[dict] = []
    for row in load_jsonl(general_oss_path):
        url = normalize_repo_url(row["repository_url"])
        if url.lower() in exclude_urls:
            continue
        full_name = row["full_name"]
        if is_excluded_name(full_name, description=row.get("github_description")):
            continue
        rows.append(row)
    rows.sort(key=lambda item: item["repository_url"].lower())
    return rows


def _instruction_registry_rows(rows: list[dict]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in rows:
        family = artifact_family(row.get("queries") or [])
        stratum = star_stratum(int(row.get("stars") or 0))
        out.append(
            candidate_row(
                repo_url=row["repository_url"],
                stars=int(row.get("stars") or 0),
                language=str(row.get("primary_language") or ""),
                pushed_at=str(row.get("pushed_at") or ""),
                source="vsdlc_instruction_frame",
                cohort_stratum=STRATUM_AI_INSTRUCTION,
                selection_stratum=f"instruction_{family}_{stratum}",
                notes=";".join(row.get("queries") or []),
            )
        )
    return out


def _general_oss_registry_rows(rows: list[dict]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in rows:
        language = str(row.get("primary_language") or row.get("language_bucket") or "unknown")
        stratum = row.get("star_stratum") or star_stratum(int(row.get("stars") or 0))
        out.append(
            candidate_row(
                repo_url=row["repository_url"],
                stars=int(row.get("stars") or 0),
                language=language,
                pushed_at=str(row.get("pushed_at") or ""),
                source="general_oss_search",
                cohort_stratum=STRATUM_GENERAL_OSS,
                selection_stratum=f"general_{language.lower()}_{stratum}",
                notes=str(row.get("search_query") or ""),
            )
        )
    return out


def _mixed_control_registry_rows(rows: list[dict]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in rows:
        predicate = topic_predicate(row.get("queries") or [])
        stratum = star_stratum(int(row.get("stars") or 0))
        language = str(row.get("primary_language") or "unknown")
        out.append(
            candidate_row(
                repo_url=row["repository_url"],
                stars=int(row.get("stars") or 0),
                language=language,
                pushed_at=str(row.get("pushed_at") or ""),
                source="vsdlc_topic_frame",
                cohort_stratum=STRATUM_MIXED_CONTROL,
                selection_stratum=f"topic_{predicate.replace(':', '_')}_{stratum}",
                notes=";".join(row.get("queries") or []),
            )
        )
    return out


def _group_instruction(rows: list[dict]) -> dict[tuple[str, ...], list[dict]]:
    groups: dict[tuple[str, ...], list[dict]] = defaultdict(list)
    for row in rows:
        family = artifact_family(row.get("queries") or [])
        stratum = star_stratum(int(row.get("stars") or 0))
        groups[(family, stratum)].append(row)
    for key in groups:
        groups[key].sort(key=lambda item: item["repository_url"].lower())
    return groups


def _group_general(rows: list[dict]) -> dict[tuple[str, ...], list[dict]]:
    groups: dict[tuple[str, ...], list[dict]] = defaultdict(list)
    for row in rows:
        language = str(row.get("primary_language") or row.get("language_bucket") or "unknown").lower()
        stratum = row.get("star_stratum") or star_stratum(int(row.get("stars") or 0))
        groups[(language, stratum)].append(row)
    for key in groups:
        groups[key].sort(key=lambda item: item["repository_url"].lower())
    return groups


def _group_mixed(rows: list[dict]) -> dict[tuple[str, ...], list[dict]]:
    groups: dict[tuple[str, ...], list[dict]] = defaultdict(list)
    for row in rows:
        predicate = topic_predicate(row.get("queries") or [])
        stratum = star_stratum(int(row.get("stars") or 0))
        groups[(predicate, stratum)].append(row)
    for key in groups:
        groups[key].sort(key=lambda item: item["repository_url"].lower())
    return groups


def build_e1_1000_registry(
    *,
    vsdlc_path: Path,
    second_frame_path: Path,
    general_oss_path: Path,
    seed: int = DEFAULT_SEED,
) -> list[dict[str, str]]:
    instruction_size = E1_1000_STRATUM_SIZES[STRATUM_AI_INSTRUCTION]
    general_size = E1_1000_STRATUM_SIZES[STRATUM_GENERAL_OSS]
    mixed_size = E1_1000_STRATUM_SIZES[STRATUM_MIXED_CONTROL]

    instruction_candidates = _load_instruction_candidates(vsdlc_path)
    instruction_selected = _round_robin_sample(
        _group_instruction(instruction_candidates),
        sample_size=instruction_size,
        seed=seed,
    )
    instruction_rows = _instruction_registry_rows(instruction_selected)
    used_urls = {row["repo_url"].lower() for row in instruction_rows}

    general_candidates = _load_general_oss_candidates(general_oss_path, exclude_urls=used_urls)
    general_selected = _round_robin_sample(
        _group_general(general_candidates),
        sample_size=general_size,
        seed=seed + 1,
    )
    general_rows = _general_oss_registry_rows(general_selected)
    used_urls.update(row["repo_url"].lower() for row in general_rows)

    mixed_candidates = _load_mixed_control_candidates(second_frame_path, exclude_urls=used_urls)
    mixed_selected = _round_robin_sample(
        _group_mixed(mixed_candidates),
        sample_size=mixed_size,
        seed=seed + 2,
    )
    mixed_rows = _mixed_control_registry_rows(mixed_selected)

    rows = instruction_rows + general_rows + mixed_rows
    rows.sort(key=lambda row: row["repo_url"].lower())
    if len(rows) != E1_1000_TARGET_SIZE:
        raise ValueError(f"built {len(rows)} rows, expected {E1_1000_TARGET_SIZE}")
    return rows


def write_registry(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(E1_1000_REGISTRY_COLUMNS))
        writer.writeheader()
        writer.writerows(rows)


def build_cohort_design_markdown(
    *,
    registry_path: Path,
    vsdlc_path: Path,
    second_frame_path: Path,
    general_oss_path: Path,
    seed: int,
) -> str:
    return "\n".join(
        [
            "# E1-1000 cohort design",
            "",
            "> **Scope warning:** This cohort supports two interpretable estimands: (1) prevalence within",
            "> the AI-instruction discovery frame, and (2) contrast against general OSS repositories.",
            "> It is **not** a GitHub-wide population sample. Adoption is measured under **head-only**",
            "> inspection (current-presence at HEAD), not full lifecycle history.",
            "",
            "## Purpose",
            "",
            "E1-1000 is the default **scientific cohort** for the TOSEM paper (RQ1–RQ3, RQ5).",
            "It replaces E1-100 as the primary inference population while preserving E1-100 as the",
            "engineering regression cohort.",
            "",
            "## Three explicit strata",
            "",
            "| Stratum | `cohort_stratum` | Size | Interpretation |",
            "|---------|------------------|------|----------------|",
            f"| AI-instruction discovery frame | `{STRATUM_AI_INSTRUCTION}` | {E1_1000_STRATUM_SIZES[STRATUM_AI_INSTRUCTION]} | Repositories discovered via GitHub **code search** on instruction-artifact path predicates (VSDLC frame). Supports enriched-frame prevalence. |",
            f"| General OSS | `{STRATUM_GENERAL_OSS}` | {E1_1000_STRATUM_SIZES[STRATUM_GENERAL_OSS]} | Repositories discovered via **repository search** on stars/language/activity only — no instruction-path predicates, no AI-topic predicates. Contrast arm. |",
            f"| Mixed / control | `{STRATUM_MIXED_CONTROL}` | {E1_1000_STRATUM_SIZES[STRATUM_MIXED_CONTROL]} | Repositories discovered via **repository search** on AI-related **topics** (metadata frame) without guaranteed instruction-artifact signals. |",
            "",
            "## Inclusion criteria (all strata)",
            "",
            "- Public GitHub repository with parseable `owner/name` URL",
            "- `stars >= 10` (instruction and mixed frames; general OSS queries start at 100 stars)",
            "- `pushed_at >= 2024-06-01` (activity floor)",
            "- Not a fork, archived repository, template, mirror, or duplicate URL",
            "- Name/topic exclusion filters: templates, boilerplates, awesome-* collections, obvious mirrors",
            "",
            "## Exclusion criteria",
            "",
            "- Forks, archived repositories, GitHub templates, mirrors",
            "- Duplicate `repo_id` or `repo_url` across the registry",
            "- Obvious collection repos (`awesome-*`, `/awesome` suffix)",
            "- Template/starter/boilerplate name patterns",
            "- Cross-stratum duplicates (deterministic deduplication by URL when building strata)",
            "",
            "## Sampling algorithm",
            "",
            f"1. **Seed:** `{seed}` (deterministic; stratum-specific derived seeds `{seed}`, `{seed + 1}`, `{seed + 2}`)",
            "2. Load candidate pools:",
            f"   - Instruction frame: `{vsdlc_path}`",
            f"   - General OSS: `{general_oss_path}`",
            f"   - Mixed/control: `{second_frame_path}`",
            "3. Group candidates within each stratum by `(family_or_language_or_topic, star_bucket)`",
            "4. Sort within groups by `repository_url` (case-insensitive)",
            "5. Shuffle group keys with stratum seed; round-robin draw one repo per group per pass",
            "6. Merge strata, sort final registry by `repo_url`",
            "",
            "## Star buckets (`selection_stratum` suffix)",
            "",
            "- `stars_small`: stars < 500",
            "- `stars_medium`: 500 ≤ stars < 5000",
            "- `stars_large`: stars ≥ 5000",
            "",
            "## Registry metadata",
            "",
            f"- Registry path: `{registry_path}`",
            f"- Registry version: `{E1_1000_REGISTRY_VERSION}`",
            f"- Target size: **{E1_1000_TARGET_SIZE}**",
            "- Extraction wave (planned): `e1_1000_v1`",
            "- Protocol family: `ai_conventions_v1`",
            "- Inspection mode: `head-only`",
            "",
            "## Expected limitations",
            "",
            "- **Not GitHub-wide prevalence:** All three strata are visibility-biased frames on public GitHub.",
            "- **Head-only adoption:** Counts reflect files present at HEAD, not deleted or historical-only artifacts.",
            "- **Discovery-frame inflation:** Instruction stratum repos were selected because convention paths were discoverable.",
            "- **General OSS is not random:** Repository search ranks by stars; language quotas are query-defined, not proportional to GitHub language share.",
            "- **Mixed/control stratum is AI-topic adjacent:** Topic predicates enrich for AI-adjacent metadata; this is a sensitivity frame, not a pure control.",
            "- **Temporal snapshot:** Registry freeze and extraction wave timestamp bound all prevalence estimates.",
            "",
            "## Dual interpretability (RQ1)",
            "",
            "Report separately:",
            "",
            f"1. **Enriched frame prevalence** — strata `{STRATUM_AI_INSTRUCTION}` (+ optionally `{STRATUM_MIXED_CONTROL}`)",
            f"2. **General OSS contrast** — stratum `{STRATUM_GENERAL_OSS}`",
            "",
            "Do not pool strata without explicit labeling. Combined cohort statistics are descriptive only.",
            "",
        ]
    )


def write_cohort_design(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="artifact_lab.registry.build_e1_1000")
    parser.add_argument("--vsdlc", type=Path, default=DEFAULT_VSDLC_ELIGIBLE)
    parser.add_argument("--second-frame", type=Path, default=DEFAULT_SECOND_FRAME)
    parser.add_argument("--general-oss", type=Path, default=DEFAULT_GENERAL_OSS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--cohort-design", type=Path, default=DEFAULT_COHORT_DESIGN)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args(argv)
    for label, path in (
        ("VSDLC eligible", args.vsdlc),
        ("second frame", args.second_frame),
        ("general OSS", args.general_oss),
    ):
        if not path.exists():
            print(f"{label} file not found: {path}", file=sys.stderr)
            return 1
    rows = build_e1_1000_registry(
        vsdlc_path=args.vsdlc,
        second_frame_path=args.second_frame,
        general_oss_path=args.general_oss,
        seed=args.seed,
    )
    write_registry(rows, args.output)
    design = build_cohort_design_markdown(
        registry_path=args.output,
        vsdlc_path=args.vsdlc,
        second_frame_path=args.second_frame,
        general_oss_path=args.general_oss,
        seed=args.seed,
    )
    write_cohort_design(args.cohort_design, design)
    print(f"wrote {len(rows)} registry rows -> {args.output}")
    print(f"wrote cohort design -> {args.cohort_design}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
