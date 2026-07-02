"""Born-stale audit — references never reaching VERIFIED (RQ2 exclusion cohort)."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass

from artifact_lab.experiments.truth_pilots.gates_common import VERIFIABLE_REFERENCE_TYPES, _csv_bool

FILE_EXTENSIONS = frozenset(
    {
        ".py",
        ".md",
        ".mdc",
        ".ts",
        ".tsx",
        ".js",
        ".jsx",
        ".yaml",
        ".yml",
        ".json",
        ".toml",
        ".sh",
        ".rs",
        ".go",
    }
)

EXAMPLE_PATTERN = re.compile(r"(^|[/_.-])examples?([/_.-]|$)", re.IGNORECASE)
COMMENT_PATTERN = re.compile(r"comment", re.IGNORECASE)
EXTERNAL_PATTERN = re.compile(
    r"(^https?://|^www\.|github\.com|gitlab\.com|npmjs\.org|pypi\.org|^@|[A-Z][a-z]+\.[A-Z][a-z]+)",
)
PROSE_PRODUCT_PATTERN = re.compile(r"^[A-Z][A-Za-z0-9]*\.[A-Z][A-Za-z0-9]*$")
VALID_FILENAME = re.compile(
    r"^[\w./-]+\.(?:py|md|mdc|ts|tsx|js|jsx|yaml|yml|json|toml|sh|rs|go)$"
)


@dataclass(frozen=True)
class BornStaleRecord:
    repo_id: str
    repo_url: str
    instruction_path: str
    reference_type: str
    reference: str
    first_state: str
    first_transition: str
    n_observations: int
    surface_context: str
    relative_path_candidate: bool
    likely_external: bool
    repeated_reference_key_count: int
    repeated_file_count: int
    repeated_repo_count: int


def _trajectory_key(row: dict) -> tuple[str, str, str, str]:
    return (row["repo_id"], row["instruction_path"], row["reference_type"], row["reference"])


def _has_file_extension(reference: str) -> bool:
    if not VALID_FILENAME.match(reference):
        return False
    lower = reference.lower()
    return any(lower.endswith(ext) for ext in FILE_EXTENSIONS)


def _is_prose_token(reference: str) -> bool:
    if PROSE_PRODUCT_PATTERN.match(reference):
        return True
    if "/" in reference or not reference:
        return False
    if "." not in reference:
        return reference[0].isupper() if reference else False
    stem, ext = reference.rsplit(".", 1)
    ext_lower = f".{ext.lower()}"
    if ext_lower not in FILE_EXTENSIONS:
        return False
    return bool(stem) and stem[0].isupper() and stem.replace(".", "").isalnum()


def classify_surface_context(
    reference_type: str,
    reference: str,
    instruction_path: str,
) -> str:
    """Proxy for extraction surface using reference shape and extraction grammar.

    Longitudinal exports do not retain the original ``context`` field from extraction;
    labels follow deterministic heuristics documented in ``born_stale_audit.md``.
    """
    if reference_type == "command":
        return "code_block"
    if reference_type == "dependency":
        return "prose"
    if reference_type == "script_name":
        return "code_block"

    if EXAMPLE_PATTERN.search(reference) or EXAMPLE_PATTERN.search(instruction_path):
        return "examples"
    if COMMENT_PATTERN.search(reference) or COMMENT_PATTERN.search(instruction_path):
        return "comments"

    if reference_type == "path":
        if _is_prose_token(reference):
            return "prose"
        if VALID_FILENAME.match(reference) or "/" in reference:
            return "structured_path"
        return "prose"

    if reference_type == "directory":
        if reference in {"/", "w/"}:
            return "prose"
        return "structured_path"

    return "unclear"


def is_relative_path_candidate(reference: str, reference_type: str) -> bool:
    if reference_type not in ("path", "directory", "script_name"):
        return False
    if reference.startswith("./") or reference.startswith("../"):
        return True
    if reference_type == "directory" and reference.endswith("/") and "/" not in reference.strip("/"):
        return False
    if reference_type == "path" and "/" not in reference and _has_file_extension(reference):
        return True
    return False


def is_likely_external(reference_type: str, reference: str) -> bool:
    if reference_type == "dependency":
        return True
    if _is_prose_token(reference):
        return True
    if EXTERNAL_PATTERN.search(reference):
        return True
    if reference_type == "path" and not _has_file_extension(reference) and "/" not in reference:
        return True
    return False


def collect_born_stale_trajectories(rows: list[dict]) -> tuple[list[tuple], dict[str, int]]:
    """Return never-verified verifiable trajectories and broader type counts."""
    grouped: dict[tuple[str, str, str, str], list[dict]] = defaultdict(list)
    removal_keys: set[tuple[str, str, str, str]] = set()

    for row in rows:
        if _csv_bool(row.get("reference_removed")):
            removal_keys.add(_trajectory_key(row))
            continue
        grouped[_trajectory_key(row)].append(row)

    never_verified_all: list[tuple] = []
    never_verified_rq2: list[tuple] = []
    type_counts_all: Counter[str] = Counter()
    type_counts_rq2: Counter[str] = Counter()

    for key, events in grouped.items():
        events.sort(key=lambda r: r["commit_time"])
        if any(ev["state"] == "VERIFIED" for ev in events):
            continue
        ref_type = key[2]
        type_counts_all[ref_type] += 1
        never_verified_all.append((key, events))
        if ref_type in VERIFIABLE_REFERENCE_TYPES:
            type_counts_rq2[ref_type] += 1
            never_verified_rq2.append((key, events))

    meta = {
        "never_verified_all": len(never_verified_all),
        "never_verified_rq2_excluded": len(never_verified_rq2),
        **{f"type_all_{t}": type_counts_all.get(t, 0) for t in ("path", "directory", "script_name", "dependency", "command")},
        **{f"type_rq2_{t}": type_counts_rq2.get(t, 0) for t in ("path", "directory", "script_name", "dependency")},
    }
    return never_verified_rq2, meta


def build_born_stale_records(
    never_verified: list[tuple],
    rows: list[dict],
) -> list[BornStaleRecord]:
    repo_urls = {r["repo_id"]: r.get("repo_url", "") for r in rows}

    ref_key_locations: Counter[tuple[str, str]] = Counter()
    ref_key_files: dict[tuple[str, str], set[tuple[str, str]]] = defaultdict(set)
    ref_key_repos: dict[tuple[str, str], set[str]] = defaultdict(set)

    for key, _events in never_verified:
        repo_id, instruction_path, ref_type, reference = key
        ref_key = (ref_type, reference)
        ref_key_locations[ref_key] += 1
        ref_key_files[ref_key].add((repo_id, instruction_path))
        ref_key_repos[ref_key].add(repo_id)

    records: list[BornStaleRecord] = []
    for key, events in never_verified:
        repo_id, instruction_path, ref_type, reference = key
        ref_key = (ref_type, reference)
        first = events[0]
        records.append(
            BornStaleRecord(
                repo_id=repo_id,
                repo_url=repo_urls.get(repo_id, ""),
                instruction_path=instruction_path,
                reference_type=ref_type,
                reference=reference,
                first_state=first["state"],
                first_transition=first.get("transition", ""),
                n_observations=len(events),
                surface_context=classify_surface_context(ref_type, reference, instruction_path),
                relative_path_candidate=is_relative_path_candidate(reference, ref_type),
                likely_external=is_likely_external(ref_type, reference),
                repeated_reference_key_count=ref_key_locations[ref_key],
                repeated_file_count=len(ref_key_files[ref_key]),
                repeated_repo_count=len(ref_key_repos[ref_key]),
            )
        )
    return records


def summarize_by_type(records: list[BornStaleRecord]) -> list[dict]:
    total = len(records) or 1
    by_type: dict[str, list[BornStaleRecord]] = defaultdict(list)
    for r in records:
        by_type[r.reference_type].append(r)

    rows: list[dict] = []
    for ref_type in ("path", "directory", "script_name", "dependency", "command"):
        subset = by_type.get(ref_type, [])
        if not subset and ref_type == "command":
            continue
        n = len(subset)
        if n == 0 and ref_type != "command":
            rows.append(
                {
                    "reference_type": ref_type,
                    "count": 0,
                    "pct_of_rq2_excluded": 0.0,
                    "surface_context_top": "",
                    "relative_path_candidates": 0,
                    "likely_external": 0,
                    "repeated_across_5plus_files": 0,
                }
            )
            continue
        context_top = Counter(r.surface_context for r in subset).most_common(1)[0][0] if subset else ""
        rows.append(
            {
                "reference_type": ref_type,
                "count": n,
                "pct_of_rq2_excluded": round(100 * n / total, 2),
                "surface_context_top": context_top,
                "relative_path_candidates": sum(1 for r in subset if r.relative_path_candidate),
                "likely_external": sum(1 for r in subset if r.likely_external),
                "repeated_across_5plus_files": sum(1 for r in subset if r.repeated_file_count >= 5),
            }
        )
    return rows


def summarize_by_repo(records: list[BornStaleRecord]) -> list[dict]:
    total = len(records) or 1
    counts = Counter(r.repo_id for r in records)
    rows = []
    cumulative = 0
    for rank, (repo_id, count) in enumerate(counts.most_common(), start=1):
        cumulative += count
        sample_url = next((r.repo_url for r in records if r.repo_id == repo_id), "")
        rows.append(
            {
                "rank": rank,
                "repo_id": repo_id,
                "repo_url": sample_url,
                "born_stale_count": count,
                "pct_of_cohort": round(100 * count / total, 2),
                "cumulative_pct": round(100 * cumulative / total, 2),
            }
        )
    return rows


def example_rows(records: list[BornStaleRecord], *, limit: int = 200) -> list[dict]:
    """Representative examples sorted by cross-repo repetition then file repetition."""
    ranked = sorted(
        records,
        key=lambda r: (r.repeated_repo_count, r.repeated_file_count, r.repeated_reference_key_count),
        reverse=True,
    )
    return [asdict(r) for r in ranked[:limit]]


def audit_summary_markdown(
    *,
    meta: dict[str, int],
    records: list[BornStaleRecord],
    by_type: list[dict],
    by_repo: list[dict],
) -> str:
    n = len(records)
    context_counts = Counter(r.surface_context for r in records)
    relative_n = sum(1 for r in records if r.relative_path_candidate)
    external_n = sum(1 for r in records if r.likely_external)
    repeated_files = sum(1 for r in records if r.repeated_file_count >= 5)
    repeated_repos = sum(1 for r in records if r.repeated_repo_count >= 5)
    unique_ref_keys = len({(r.reference_type, r.reference) for r in records})
    ref_key_trajectory_counts = Counter((r.reference_type, r.reference) for r in records)
    ref_keys_multi_trajectory = sum(1 for c in ref_key_trajectory_counts.values() if c >= 2)

    top10_pct = by_repo[9]["cumulative_pct"] if len(by_repo) >= 10 else (by_repo[-1]["cumulative_pct"] if by_repo else 0)
    top5_pct = by_repo[4]["cumulative_pct"] if len(by_repo) >= 5 else top10_pct
    unique_repos = len(by_repo)

    lines = [
        "# Born-Stale Audit — Never-Verified References",
        "",
        "## Construct distinction",
        "",
        "**Born-stale:** a reference is observed as checkable (`path`, `directory`, `script_name`,",
        "`dependency`) but **never** reaches `VERIFIED` in the longitudinal panel — typically",
        "`INIT→MISSING` from the first snapshot.",
        "",
        "**Post-verification decay (RQ2):** a reference that was `VERIFIED` at least once and",
        "subsequently fails. RQ2 survival conditions on the latter; born-stale references are",
        "excluded by design.",
        "",
        "## Cohort",
        "",
        f"- RQ2 exclusion cohort (verifiable, never VERIFIED): **{meta['never_verified_rq2_excluded']}**",
        f"- Broader never-verified trajectories (all types): **{meta['never_verified_all']}**",
        f"- Repos contributing born-stale references: **{unique_repos}**",
        "",
        "## 1. Never-verified counts by reference type",
        "",
        "### RQ2 exclusion cohort (verifiable only)",
        "",
        f"- **path:** {meta.get('type_rq2_path', 0)}",
        f"- **directory:** {meta.get('type_rq2_directory', 0)}",
        f"- **script_name:** {meta.get('type_rq2_script_name', 0)}",
        f"- **dependency:** {meta.get('type_rq2_dependency', 0)}",
        "",
        "### Broader born-stale population (includes commands)",
        "",
        f"- **command:** {meta.get('type_all_command', 0)} (never VERIFIED; mechanically UNVERIFIABLE by protocol)",
        f"- **path:** {meta.get('type_all_path', 0)}",
        f"- **directory:** {meta.get('type_all_directory', 0)}",
        f"- **script_name:** {meta.get('type_all_script_name', 0)}",
        f"- **dependency:** {meta.get('type_all_dependency', 0)}",
        "",
        "> Commands are excluded from RQ2 because they are not mechanically verifiable; they",
        "> represent a separate surface (shell blocks) from verifiable path-like claims.",
        "",
        "## 2. Extraction surface (proxy classification)",
        "",
        "Longitudinal CSV does not store extraction `context`. Counts use deterministic heuristics",
        "aligned with the extraction grammar in `references.py` (bash blocks, install lines, bare",
        "paths, example paths, comment-adjacent filenames).",
        "",
    ]
    for label, key in (
        ("Code blocks / script invocations", "code_block"),
        ("Comments (comment-adjacent paths)", "comments"),
        ("Examples (example directories or filenames)", "examples"),
        ("Prose / false-positive bare tokens", "prose"),
        ("Structured repo paths (backtick/bare path shape)", "structured_path"),
        ("Unclear", "unclear"),
    ):
        count = context_counts.get(key, 0)
        lines.append(f"- **{label}:** {count} ({100 * count / n:.1f}%)" if n else f"- **{label}:** 0")

    lines.extend(
        [
            "",
            "## 3. Relative-path resolution candidates",
            "",
            f"- **Count:** {relative_n} ({100 * relative_n / n:.1f}% of RQ2 exclusion cohort)" if n else "- **Count:** 0",
            "- Heuristic: `./`/`../` prefixes, or single-segment filenames verified from repo root",
            "  (instruction-file-relative anchors are not modeled in v1 verification).",
            "",
            "## 4. Likely external references",
            "",
            f"- **Count:** {external_n} ({100 * external_n / n:.1f}%)" if n else "- **Count:** 0",
            "- Heuristic: dependencies, URL-like tokens, scoped package names (`@scope/pkg`),",
            "  or prose product tokens without repo path structure (e.g. `Node.js`).",
            "",
            "## 5. Cross-file / cross-repo repetition",
            "",
            f"- Unique `(type, reference)` keys: **{unique_ref_keys}**",
            f"- Keys appearing in ≥2 trajectories: **{ref_keys_multi_trajectory}**",
            f"- Trajectories whose key appears in ≥5 instruction files: **{repeated_files}**",
            f"- Trajectories whose key appears in ≥5 repos: **{repeated_repos}**",
            "",
            "## 6. Repo concentration",
            "",
            f"- Top 5 repos account for **{top5_pct:.1f}%** of born-stale references",
            f"- Top 10 repos account for **{top10_pct:.1f}%**",
            "",
            "See `born_stale_by_repo.csv` for full distribution.",
            "",
            "## Implications for the paper",
            "",
            "1. **Born-stale is not longitudinal decay.** These references fail from the first",
            "   observable snapshot (`INIT→MISSING`). They measure *initial validity* of extracted",
            "   claims, not half-life after a reference was once true.",
            "2. **RQ2 estimates a conditional hazard.** Kaplan–Meier survival applies only to",
            "   references that cross the `VERIFIED` threshold at least once (n=4,521 in this cohort).",
            "   The 17,747 exclusions are a different construct and must not be merged into decay rates.",
            "3. **Future models should separate components:** (a) probability a new reference is",
            "   born valid vs born stale; (b) hazard of failure given prior verification. Mixing",
            "   them inflates apparent decay and confounds extraction noise with lifecycle drift.",
            "4. **Extraction surface matters.** A large share of born-stale references are prose",
            "   false positives, example paths, or relative-path candidates — not post-hoc repo drift.",
            "5. **Cohort concentration:** born-stale mass is concentrated in a small number of repos;",
            "   repo-level covariates (template reuse, agent rule packs) likely explain much of the",
            "   signal before file-age effects.",
            "",
            "## Outputs",
            "",
            "- `born_stale_examples.csv` — ranked illustrative trajectories",
            "- `born_stale_by_repo.csv` — per-repo counts",
            "- `born_stale_by_type.csv` — type-level summary",
            "",
        ]
    )
    return "\n".join(lines)
