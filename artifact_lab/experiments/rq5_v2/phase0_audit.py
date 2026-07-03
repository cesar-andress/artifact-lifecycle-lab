"""Phase 0 calibration plan audit for RQ5 v2 factorial cases (design-only, no agents)."""

from __future__ import annotations

import csv
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from artifact_lab.experiments.rq5_v2.factors import CellCode
from artifact_lab.experiments.rq5_v2.manifest import load_case_manifest
from artifact_lab.experiments.rq5_v2.models import FactorialCase
from artifact_lab.experiments.truth_pilots.verify_refs import _path_exists
from artifact_lab.ingest.git_utils import clone_bare, list_paths_at_commit

DEFAULT_MANIFEST = Path("exports/rq5_v2_factorial/factorial_case_manifest.json")
DEFAULT_CALIBRATION = Path("exports/task_calibration/difficulty_scores.csv")
DEFAULT_CANDIDATES = Path("exports/rq5_v2/load_bearing_candidates.csv")
DEFAULT_OUTPUT_DIR = Path("exports/rq5_v2_factorial")

SUCCESS_BAND = (0.40, 0.60)
MAX_CASES_PER_REPO = 3
ECOSYSTEM_DOMINANCE_THRESHOLD = 0.75
MIN_ECOSYSTEMS = 2
REQUIRED_CELLS = tuple(c.value for c in CellCode)

PATH_SYNTAX = re.compile(r"^[\w./\-]+$")
TYPO_SUFFIXES = (".missing", "-missing")
LEAK_PATTERNS = (
    re.compile(r"\badd (?:a )?type hint\b", re.I),
    re.compile(r"\bfix off-by-one\b", re.I),
    re.compile(r"\bminimal bounded change:\s*\S+", re.I),
)


@dataclass
class CaseAuditRow:
    case_id: str
    candidate_id: str
    repository: str
    repo_id: str
    ecosystem: str
    commit_sha: str
    anchor_path_true: str
    anchor_path_false: str
    decoy_path: str
    load_bearing_role: str
    calibrated_expected_success: float
    estimated_success_rate: float | None
    repairability_score: float | None
    checks: dict[str, bool] = field(default_factory=dict)
    failure_reasons: list[str] = field(default_factory=list)
    reviewer_accept: bool = False
    valid_phase0: bool = False

    def record(self, name: str, passed: bool, *, reason: str = "") -> None:
        self.checks[name] = passed
        if not passed and reason:
            self.failure_reasons.append(f"{name}: {reason}")


def _load_csv_index(path: Path, key: str) -> dict[str, dict]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as handle:
        return {row[key]: row for row in csv.DictReader(handle) if row.get(key)}


def _float(value: object) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def path_resolves(path: str, tree_paths: set[str]) -> bool:
    if not path or path.startswith("@"):
        return False
    return _path_exists(path.strip().strip("`"), tree_paths)


def _normalize_path(path: str) -> str:
    return path.strip().strip("`").strip("/")


def false_path_syntactically_plausible(true_path: str, false_path: str) -> tuple[bool, str]:
    """RQ5 v2.1: non-resolving plausible sibling, not typo/deleted/renamed/external."""
    true_path = _normalize_path(true_path)
    false_path = _normalize_path(false_path)

    if false_path.startswith(("http://", "https://", "mailto:")):
        return False, "external URL class"
    if not PATH_SYNTAX.match(false_path):
        return False, "invalid path syntax"
    if false_path == true_path:
        return False, "identical to true path"
    if any(false_path.endswith(s) for s in TYPO_SUFFIXES):
        return False, "uses .missing/-missing suffix (excluded false-reference class)"
    if false_path in true_path or true_path in false_path:
        if false_path.replace("_", "") == true_path.replace("_", ""):
            return False, "typo-class single-token edit"

    if "/" in true_path:
        true_parent = true_path.rsplit("/", 1)[0]
        false_parent = false_path.rsplit("/", 1)[0] if "/" in false_path else ""
        if true_parent != false_parent:
            return False, "false path not in same directory as true path"
    elif "/" in false_path:
        return False, "directory depth mismatch"

    true_name = true_path.rsplit("/", 1)[-1]
    false_name = false_path.rsplit("/", 1)[-1]
    if _levenshtein(true_name, false_name) <= 1:
        return False, "typo-class filename (edit distance ≤ 1)"

    return True, ""


def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            curr.append(min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost))
        prev = curr
    return prev[-1]


def lb_task_load_bearing(case: FactorialCase) -> tuple[bool, str]:
    for code in (CellCode.T_L, CellCode.F_L):
        cell = case.get_cell(code.value)
        prompt = cell.task_prompt
        prompt_lower = prompt.lower()
        anchor = cell.cited_anchor
        decoy = case.decoy_path
        if anchor not in prompt:
            return False, f"{code.value} task prompt missing cited anchor"
        if f"modify `{decoy}`" in prompt_lower or f"modify {decoy.lower()}" in prompt_lower:
            return False, f"{code.value} task prompt targets decoy instead of anchor"
        if " only " in prompt_lower and (
            f"`{decoy}`" in prompt or f" {decoy} " in prompt or prompt.rstrip().endswith(decoy)
        ):
            return False, f"{code.value} task prompt restricts to decoy (PB pattern)"
        if not cell.load_bearing:
            return False, f"{code.value} load_bearing flag false"
    return True, ""


def pb_task_peripheral(case: FactorialCase) -> tuple[bool, str]:
    for code in (CellCode.T_P, CellCode.F_P):
        cell = case.get_cell(code.value)
        prompt = cell.task_prompt.lower()
        decoy = case.decoy_path.lower()
        if decoy not in prompt:
            return False, f"{code.value} task prompt missing decoy path"
        if "only" not in prompt:
            return False, f"{code.value} task prompt missing 'only' decoy constraint"
        if cell.load_bearing:
            return False, f"{code.value} load_bearing flag true"
    return True, ""


def task_text_leaks_answer(case: FactorialCase) -> tuple[bool, str]:
    for code in CellCode:
        cell = case.get_cell(code.value)
        prompt = cell.task_prompt
        for pattern in LEAK_PATTERNS:
            if pattern.search(prompt):
                return False, f"{code.value} contains prescriptive solution hint"
        if code in (CellCode.F_L, CellCode.F_P):
            if case.anchor_path_true in prompt and case.anchor_path_false not in prompt:
                return False, f"{code.value} leaks true anchor path"
    return True, ""


def all_cells_feasible(case: FactorialCase, tree_paths: set[str]) -> tuple[bool, str]:
    for code in REQUIRED_CELLS:
        if code not in case.cells:
            return False, f"missing cell {code}"
        cell = case.get_cell(code)

        if code == CellCode.N.value:
            if cell.instruction_blob_sha:
                return False, "N cell has non-empty instruction blob"
            continue

        if not cell.instruction_blob_sha:
            return False, f"{code} missing instruction blob"
        exists = path_resolves(cell.cited_anchor, tree_paths)
        if exists != cell.mechanical_truth:
            return False, f"{code} mechanical_truth mismatch (exists={exists})"

        if code in (CellCode.T_P.value, CellCode.F_P.value):
            if not path_resolves(case.decoy_path, tree_paths):
                return False, f"{code} decoy path missing at commit"

    return True, ""


def get_repo_tree(
    *,
    repo_id: str,
    repo_url: str,
    commit_sha: str,
    scratch_dir: Path,
    clone_timeout: int = 180,
) -> set[str]:
    clone_path = scratch_dir / f"phase0_audit_{repo_id}"
    if not clone_path.exists():
        clone_bare(repo_url, clone_path, timeout=clone_timeout)
    paths = list_paths_at_commit(clone_path, commit_sha, timeout=clone_timeout)
    if paths:
        return paths
    return list_paths_at_commit(clone_path, "HEAD", timeout=clone_timeout)


def audit_case(
    case: FactorialCase,
    *,
    tree_paths: set[str],
    calibration_row: dict | None,
    candidate_row: dict | None,
    repo_case_counts: Counter[str],
    path_dup_keys: set[tuple[str, str, str]],
) -> CaseAuditRow:
    cal = calibration_row or {}
    cand = candidate_row or {}
    est = _float(cand.get("estimated_success_rate"))
    repair = _float(getattr(case, "repairability_score", None))
    if repair is None:
        repair = _float(cand.get("repairability_score") or cal.get("repairability_score"))
    success_rate = case.calibrated_expected_success

    row = CaseAuditRow(
        case_id=case.case_id,
        candidate_id=case.candidate_id,
        repository=case.repository,
        repo_id=case.repo_id,
        ecosystem=case.ecosystem,
        commit_sha=case.commit_sha,
        anchor_path_true=case.anchor_path_true,
        anchor_path_false=case.anchor_path_false,
        decoy_path=case.decoy_path,
        load_bearing_role=case.load_bearing_role,
        calibrated_expected_success=success_rate,
        estimated_success_rate=est,
        repairability_score=repair,
    )

    row.record(
        "true_anchor_resolves",
        path_resolves(case.anchor_path_true, tree_paths),
        reason="true anchor not in commit tree",
    )
    row.record(
        "false_anchor_not_resolves",
        not path_resolves(case.anchor_path_false, tree_paths),
        reason="false anchor resolves at commit",
    )

    plausible, plausible_reason = false_path_syntactically_plausible(
        case.anchor_path_true, case.anchor_path_false
    )
    row.record("false_anchor_plausible", plausible, reason=plausible_reason)

    row.record(
        "decoy_distinct_from_true",
        case.decoy_path.strip() != case.anchor_path_true.strip(),
        reason="decoy equals true anchor",
    )
    row.record(
        "decoy_resolves",
        path_resolves(case.decoy_path, tree_paths),
        reason="decoy path missing at commit",
    )

    lb_ok, lb_reason = lb_task_load_bearing(case)
    row.record("lb_by_construction", lb_ok, reason=lb_reason)

    pb_ok, pb_reason = pb_task_peripheral(case)
    row.record("pb_by_construction", pb_ok, reason=pb_reason)

    leak_ok, leak_reason = task_text_leaks_answer(case)
    row.record("no_task_leak", leak_ok, reason=leak_reason)

    in_band_cal = SUCCESS_BAND[0] <= success_rate <= SUCCESS_BAND[1]
    row.record(
        "success_rate_in_band",
        in_band_cal,
        reason=f"calibrated_expected_success={success_rate:.4f} outside {SUCCESS_BAND}",
    )
    if est is not None:
        in_band_est = SUCCESS_BAND[0] <= est <= SUCCESS_BAND[1]
        row.checks["estimated_success_rate_in_band"] = in_band_est
    else:
        row.checks["estimated_success_rate_in_band"] = in_band_cal

    row.record(
        "repairability_score_present",
        repair is not None,
        reason="repairability_score absent from case manifest",
    )

    dup_key = (case.repo_id, case.anchor_path_true, case.commit_sha)
    row.record(
        "not_duplicated_repo_path",
        dup_key not in path_dup_keys,
        reason="duplicate repo_id+anchor+commit",
    )

    repo_count = repo_case_counts[case.repo_id]
    row.record(
        "repo_case_cap",
        repo_count <= MAX_CASES_PER_REPO,
        reason=f"repo has {repo_count} cases (max {MAX_CASES_PER_REPO})",
    )

    cells_ok, cells_reason = all_cells_feasible(case, tree_paths)
    row.record("all_cells_feasible", cells_ok, reason=cells_reason)

    # Ecosystem balance is cohort-level; marked True here, adjusted in summary pass
    row.record("ecosystem_balance_cohort", True)

    core_checks = [
        "true_anchor_resolves",
        "false_anchor_not_resolves",
        "false_anchor_plausible",
        "decoy_distinct_from_true",
        "decoy_resolves",
        "lb_by_construction",
        "pb_by_construction",
        "no_task_leak",
        "success_rate_in_band",
        "repairability_score_present",
        "not_duplicated_repo_path",
        "repo_case_cap",
        "all_cells_feasible",
    ]
    row.valid_phase0 = all(row.checks.get(c, False) for c in core_checks)
    row.reviewer_accept = row.valid_phase0

    return row


def _ecosystem_balance_ok(rows: list[CaseAuditRow]) -> tuple[bool, str]:
    if not rows:
        return False, "no cases"
    counts = Counter(r.ecosystem for r in rows)
    if len(counts) < MIN_ECOSYSTEMS:
        return False, f"fewer than {MIN_ECOSYSTEMS} ecosystems ({dict(counts)})"
    total = len(rows)
    dominant = max(counts.values()) / total
    if dominant > ECOSYSTEM_DOMINANCE_THRESHOLD:
        top = counts.most_common(1)[0]
        return False, f"{top[0]} dominates at {top[1]}/{total} ({dominant:.0%})"
    return True, ""


def _verdict(valid_count: int) -> str:
    if valid_count >= 20:
        return "PASS"
    if valid_count >= 12:
        return "WARN"
    return "FAIL"


def audit_phase0_plan(
    *,
    manifest_path: Path = DEFAULT_MANIFEST,
    calibration_csv: Path = DEFAULT_CALIBRATION,
    candidates_csv: Path = DEFAULT_CANDIDATES,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    scratch_dir: Path = Path("scratch"),
    clone_timeout: int = 180,
) -> dict[str, Path]:
    cases = load_case_manifest(manifest_path)
    calibration = _load_csv_index(calibration_csv, "candidate_id")
    candidates = _load_csv_index(candidates_csv, "candidate_id")

    repo_case_counts = Counter(c.repo_id for c in cases)
    path_dup_keys: set[tuple[str, str, str]] = set()
    seen_path_keys: set[tuple[str, str, str]] = set()
    for case in cases:
        key = (case.repo_id, case.anchor_path_true, case.commit_sha)
        if key in seen_path_keys:
            path_dup_keys.add(key)
        seen_path_keys.add(key)

    tree_cache: dict[tuple[str, str], set[str]] = {}
    audit_rows: list[CaseAuditRow] = []

    for case in cases:
        cache_key = (case.repo_id, case.commit_sha)
        if cache_key not in tree_cache:
            tree_cache[cache_key] = get_repo_tree(
                repo_id=case.repo_id,
                repo_url=case.repo_url,
                commit_sha=case.commit_sha,
                scratch_dir=scratch_dir,
                clone_timeout=clone_timeout,
            )
        row = audit_case(
            case,
            tree_paths=tree_cache[cache_key],
            calibration_row=calibration.get(case.candidate_id),
            candidate_row=candidates.get(case.candidate_id),
            repo_case_counts=repo_case_counts,
            path_dup_keys=path_dup_keys,
        )
        audit_rows.append(row)

    eco_ok, eco_reason = _ecosystem_balance_ok(audit_rows)
    for row in audit_rows:
        row.checks["ecosystem_balance_cohort"] = eco_ok
        if not eco_ok:
            row.failure_reasons.append(f"ecosystem_balance_cohort: {eco_reason}")
            row.valid_phase0 = False
            row.reviewer_accept = False

    valid_count = sum(1 for r in audit_rows if r.valid_phase0)
    verdict = _verdict(valid_count)

    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "phase0_case_audit.csv"
    md_path = output_dir / "phase0_plan_audit.md"
    _write_case_csv(audit_rows, csv_path)
    _write_summary_md(
        audit_rows=audit_rows,
        verdict=verdict,
        valid_count=valid_count,
        total=len(cases),
        eco_ok=eco_ok,
        eco_reason=eco_reason,
        md_path=md_path,
        manifest_path=manifest_path,
    )
    return {"case_audit_csv": csv_path, "plan_audit_md": md_path}


def _write_case_csv(rows: list[CaseAuditRow], path: Path) -> None:
    fieldnames = [
        "case_id",
        "candidate_id",
        "repository",
        "repo_id",
        "ecosystem",
        "commit_sha",
        "anchor_path_true",
        "anchor_path_false",
        "decoy_path",
        "load_bearing_role",
        "calibrated_expected_success",
        "estimated_success_rate",
        "repairability_score",
        "valid_phase0",
        "reviewer_accept",
        "failure_reasons",
    ] + [
        "true_anchor_resolves",
        "false_anchor_not_resolves",
        "false_anchor_plausible",
        "decoy_distinct_from_true",
        "decoy_resolves",
        "lb_by_construction",
        "pb_by_construction",
        "no_task_leak",
        "success_rate_in_band",
        "estimated_success_rate_in_band",
        "repairability_score_present",
        "not_duplicated_repo_path",
        "repo_case_cap",
        "ecosystem_balance_cohort",
        "all_cells_feasible",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "case_id": row.case_id,
                    "candidate_id": row.candidate_id,
                    "repository": row.repository,
                    "repo_id": row.repo_id,
                    "ecosystem": row.ecosystem,
                    "commit_sha": row.commit_sha,
                    "anchor_path_true": row.anchor_path_true,
                    "anchor_path_false": row.anchor_path_false,
                    "decoy_path": row.decoy_path,
                    "load_bearing_role": row.load_bearing_role,
                    "calibrated_expected_success": f"{row.calibrated_expected_success:.4f}",
                    "estimated_success_rate": (
                        f"{row.estimated_success_rate:.4f}"
                        if row.estimated_success_rate is not None
                        else ""
                    ),
                    "repairability_score": (
                        f"{row.repairability_score:.4f}" if row.repairability_score is not None else ""
                    ),
                    "valid_phase0": row.valid_phase0,
                    "reviewer_accept": row.reviewer_accept,
                    "failure_reasons": "; ".join(row.failure_reasons),
                    **{k: row.checks.get(k, False) for k in fieldnames if k in row.checks},
                }
            )


def _write_summary_md(
    *,
    audit_rows: list[CaseAuditRow],
    verdict: str,
    valid_count: int,
    total: int,
    eco_ok: bool,
    eco_reason: str,
    md_path: Path,
    manifest_path: Path,
) -> None:
    invalid = [r for r in audit_rows if not r.valid_phase0]
    reason_counter: Counter[str] = Counter()
    for row in invalid:
        for reason in row.failure_reasons:
            check = reason.split(":", 1)[0]
            reason_counter[check] += 1

    eco_dist = Counter(r.ecosystem for r in audit_rows)
    repo_dist = Counter(r.repository for r in audit_rows)
    valid_eco = Counter(r.ecosystem for r in audit_rows if r.valid_phase0)
    difficulty = [r.calibrated_expected_success for r in audit_rows]
    repair_present = sum(1 for r in audit_rows if r.checks.get("repairability_score_present"))
    role_dist = Counter(r.load_bearing_role for r in audit_rows)

    lines = [
        "# RQ5 v2 Phase 0 Plan Audit",
        "",
        "**Status:** Design-only audit (no agent execution)",
        f"**Manifest:** `{manifest_path}`",
        f"**Protocol:** `docs/RQ5_V2_PROTOCOL.md` v2.1 (Phase 0 = 20 calibration cases, T+L band)",
        "",
        "## Verdict",
        "",
        f"**{verdict}** — `{valid_count}` / `{total}` cases valid for Phase 0 calibration.",
        "",
        "| Threshold | Result |",
        "|-----------|--------|",
        "| PASS (≥ 20 valid) | " + ("✓" if verdict == "PASS" else "✗") + " |",
        "| WARN (12–19 valid) | " + ("✓" if verdict == "WARN" else "—") + " |",
        "| FAIL (< 12 valid) | " + ("✓" if verdict == "FAIL" else "—") + " |",
        "",
        "## Summary counts",
        "",
        f"- **valid_phase0_cases:** {valid_count}",
        f"- **invalid_cases:** {total - valid_count}",
        f"- **reviewer_accept_cases:** {sum(1 for r in audit_rows if r.reviewer_accept)}",
        "",
        "### Reasons for invalidity",
        "",
    ]
    if reason_counter:
        for check, count in reason_counter.most_common():
            lines.append(f"- `{check}`: {count} case(s)")
    else:
        lines.append("- (none)")

    lines.extend(
        [
            "",
            "### Ecosystem distribution (all / valid)",
            "",
        ]
    )
    for eco, count in eco_dist.most_common():
        lines.append(f"- **{eco}:** {count} total, {valid_eco.get(eco, 0)} valid")
    lines.append(f"- **Cohort balance gate:** {'PASS' if eco_ok else 'FAIL'} — {eco_reason or 'ok'}")

    lines.extend(["", "### Repository distribution", ""])
    for repo, count in repo_dist.most_common():
        lines.append(f"- `{repo}`: {count} case(s)")

    lines.extend(
        [
            "",
            "### Difficulty distribution (`calibrated_expected_success`)",
            "",
            f"- min: {min(difficulty):.4f}",
            f"- max: {max(difficulty):.4f}",
            f"- mean: {sum(difficulty) / len(difficulty):.4f}",
            f"- in band [{SUCCESS_BAND[0]}, {SUCCESS_BAND[1]}]: "
            f"{sum(1 for d in difficulty if SUCCESS_BAND[0] <= d <= SUCCESS_BAND[1])}/{len(difficulty)}",
            "",
            "### Repairability distribution",
            "",
            f"- cases with `repairability_score`: {repair_present}/{total}",
            "",
            "### Load-bearing role distribution",
            "",
        ]
    )
    for role, count in role_dist.most_common():
        lines.append(f"- `{role}`: {count}")

    lines.extend(
        [
            "",
            "## Per-case results",
            "",
            "| case_id | repo | valid | reviewer | top failure |",
            "|---------|------|-------|----------|-------------|",
        ]
    )
    for row in audit_rows:
        top_fail = row.failure_reasons[0].split(":", 1)[0] if row.failure_reasons else "—"
        lines.append(
            f"| `{row.case_id}` | `{row.repository}` | {row.valid_phase0} | "
            f"{row.reviewer_accept} | {top_fail} |"
        )

    lines.extend(
        [
            "",
            "## Reviewer-facing notes",
            "",
            "1. **False-reference construct:** Non-resolving plausible sibling paths per RQ5 v2.1.",
            "2. **Phase 0 scope:** Full 5-cell factorial is planned in infrastructure; Phase 0 "
            "execution uses **T+L only** per protocol — this audit validates case *construction* "
            "for the full battery.",
            "3. **Success gate:** `calibrated_expected_success` is authoritative; raw "
            "`estimated_success_rate` is informational only.",
            "4. **Operational load-bearing gate** (≥ 60% anchor attempt) requires agent runs and "
            "is out of scope for this design audit.",
            "",
        ]
    )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
