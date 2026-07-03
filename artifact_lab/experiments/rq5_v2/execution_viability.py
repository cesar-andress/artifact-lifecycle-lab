"""Execution Viability preflight gate (before task calibration; no agents)."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from io import StringIO
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.rq5_v2.execution_viability_checks import (
    RepoSignals,
    SmokeResult,
    ViabilityCheckResult,
    check_clone,
    check_ecosystem_supported,
    check_historical_failures,
    check_lockfile_consistency,
    check_package_manager_consistency,
    check_test_command_exists,
    detect_ecosystem,
    heuristic_smoke_from_error_patterns,
    infer_go_module_root,
    infer_install_command,
    resolve_test_command,
    run_live_smoke,
    score_from_smoke,
)
from artifact_lab.experiments.rq5_v2.phase0_provenance import collect_provenance, provenance_block
from artifact_lab.experiments.rq5_v2.repo_tree import RepoTreeCache

DEFAULT_CANDIDATES_CSV = Path("exports/rq5_v2/load_bearing_candidates.csv")
DEFAULT_OUTPUT_DIR = Path("exports/rq5_v2")
PHASE0_TOOLCHAIN_AUDIT = Path("exports/rq5_v2_factorial/phase0_toolchain_failure_audit.csv")
PHASE0_MANIFEST = Path("exports/rq5_v2_factorial/factorial_case_manifest.json")

CHECK_WEIGHTS: dict[str, float] = {
    "clone": 0.12,
    "deps_install": 0.13,
    "test_command_exists": 0.10,
    "test_starts": 0.15,
    "baseline_tests_execute": 0.18,
    "timeout": 0.05,
    "missing_binaries": 0.05,
    "package_manager_consistency": 0.07,
    "lockfile_consistency": 0.05,
    "ecosystem_supported": 0.05,
    "historical_execution_failures": 0.05,
}

CLASSIFICATIONS = ("READY", "MINOR_SETUP", "REQUIRES_MANUAL_FIX", "DROP")


@dataclass(frozen=True)
class ViabilityRow:
    candidate_id: str
    repo: str
    score: float
    failure_reason: str
    recommended_action: str
    classification: str
    test_command: str
    ecosystem: str


def _load_candidates(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _phase0_repo_outcomes(
    *,
    toolchain_audit: Path,
) -> tuple[dict[str, float], dict[str, int]]:
    """Return (failure_rate, success_count) per repository from Phase 0 audit."""
    if not toolchain_audit.exists():
        return {}, {}
    rows = list(csv.DictReader(toolchain_audit.open(encoding="utf-8")))
    by_repo_fail: dict[str, list[str]] = defaultdict(list)
    success_count: dict[str, int] = defaultdict(int)
    for row in rows:
        repo = row.get("repository", "")
        if not repo:
            continue
        if row.get("success", "").lower() in ("true", "1"):
            success_count[repo] += 1
            continue
        by_repo_fail[repo].append(row.get("failure_class", ""))
    rates: dict[str, float] = {}
    env_classes = {
        "missing test runner",
        "wrong working directory",
        "invalid test command",
        "timeout",
        "infrastructure/API/tool error",
        "missing dependency",
        "package install required",
    }
    for repo, failures in by_repo_fail.items():
        env_n = sum(1 for f in failures if f in env_classes)
        rates[repo] = env_n / max(len(failures), 1)
    return rates, dict(success_count)


def _aggregate_score(checks: dict[str, ViabilityCheckResult]) -> float:
    total = 0.0
    for name, weight in CHECK_WEIGHTS.items():
        check = checks.get(name)
        if check is None:
            continue
        total += weight * check.score
    return round(min(1.0, max(0.0, total)), 4)


def _primary_failure_reason(checks: dict[str, ViabilityCheckResult]) -> str:
    failing = [c for c in checks.values() if not c.passed and c.name != "historical_execution_failures"]
    failing.sort(key=lambda c: CHECK_WEIGHTS.get(c.name, 0), reverse=True)
    if failing:
        return f"{failing[0].name}: {failing[0].detail}"
    hist = checks.get("historical_execution_failures")
    if hist and not hist.passed:
        return hist.detail
    return ""


def classify_viability(*, score: float, checks: dict[str, ViabilityCheckResult]) -> tuple[str, str]:
    clone = checks.get("clone")
    cmd = checks.get("test_command_exists")
    eco = checks.get("ecosystem_supported")
    deps = checks.get("deps_install")
    test_exec = checks.get("baseline_tests_execute")

    if clone and not clone.passed:
        return "DROP", "exclude: repository cannot be cloned"
    if cmd and cmd.score <= 0.2:
        return "DROP", "exclude: invalid or missing test command"
    if eco and not eco.passed:
        return "DROP", "exclude: unsupported ecosystem"

    if score >= 0.85 and cmd and cmd.passed and (test_exec and test_exec.passed):
        return "READY", "proceed to task calibration"
    if score >= 0.80 and cmd and cmd.passed and test_exec and test_exec.passed:
        return "READY", "proceed to task calibration (baseline confirmed)"
    if score >= 0.85 and cmd and cmd.passed and checks.get("test_starts") and checks["test_starts"].passed:
        return "READY", "proceed to task calibration (tests start; baseline not confirmed)"

    if score >= 0.60 or (deps and not deps.passed and deps.detail):
        return "MINOR_SETUP", "add preflight install or fix test cwd before calibration"

    if score >= 0.35:
        return "REQUIRES_MANUAL_FIX", "fix test_command, module root, or repo setup manually"

    return "DROP", "exclude from calibration battery"


def evaluate_candidate(
    *,
    candidate: dict,
    repo_signals: RepoSignals,
    historical_rate: float,
    historical_successes: int,
    smoke: SmokeResult | None,
    use_heuristic_smoke: bool,
) -> tuple[dict[str, ViabilityCheckResult], str, str]:
    test_command = resolve_test_command(candidate)
    ecosystem = detect_ecosystem(test_command, repo_signals.paths)
    test_cwd = infer_go_module_root(repo_signals.paths) or "."

    checks: dict[str, ViabilityCheckResult] = {
        "clone": check_clone(repo_signals),
        "test_command_exists": check_test_command_exists(test_command),
        "ecosystem_supported": check_ecosystem_supported(ecosystem),
        "lockfile_consistency": check_lockfile_consistency(ecosystem=ecosystem, paths=repo_signals.paths),
        "package_manager_consistency": check_package_manager_consistency(
            test_command=test_command, paths=repo_signals.paths
        ),
        "historical_execution_failures": check_historical_failures(
            repository=candidate.get("repository", ""), historical_rate=historical_rate
        ),
    }

    if smoke is None and use_heuristic_smoke:
        smoke = heuristic_smoke_from_error_patterns(
            test_command=test_command,
            ecosystem=ecosystem,
            paths=repo_signals.paths,
            historical_rate=historical_rate,
            historical_successes=historical_successes,
        )
    checks.update(score_from_smoke(smoke))
    return checks, test_command, ecosystem


def run_execution_viability(
    *,
    candidates_csv: Path = DEFAULT_CANDIDATES_CSV,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    scratch_dir: Path = Path("scratch"),
    toolchain_audit: Path = PHASE0_TOOLCHAIN_AUDIT,
    manifest_path: Path = PHASE0_MANIFEST,
    enable_clone: bool = True,
    enable_smoke: bool = False,
    max_smoke: int = 0,
    clone_timeout: int = 120,
    repo_root: Path | None = None,
) -> dict[str, Path]:
    """
    Score all candidates for execution viability (no agent execution).

    enable_clone: bare-clone + path index (deduped by repo_id)
    enable_smoke: run install + test smoke in worktree (expensive; capped by max_smoke)
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    candidates = _load_candidates(candidates_csv)
    historical, historical_successes = _phase0_repo_outcomes(toolchain_audit=toolchain_audit)

    tree_cache = RepoTreeCache(scratch_dir=scratch_dir / "viability_trees", clone_timeout=clone_timeout)
    repo_signals_cache: dict[str, RepoSignals] = {}
    smoke_cache: dict[tuple[str, str, str], SmokeResult] = {}
    smoke_count = 0

    audit_detail_rows: list[dict] = []
    summary_rows: list[ViabilityRow] = []

    for candidate in candidates:
        cid = candidate.get("candidate_id", "")
        repo = candidate.get("repository", "")
        repo_id = candidate.get("repo_id", "")
        repo_url = candidate.get("repo_url", "")
        commit_sha = candidate.get("commit_sha", "")

        if repo_id not in repo_signals_cache:
            if enable_clone and repo_url:
                try:
                    paths = tree_cache.paths_at(
                        repo_id=repo_id, repo_url=repo_url, commit_sha=commit_sha
                    )
                    repo_signals_cache[repo_id] = RepoSignals(clone_ok=True, paths=paths)
                except Exception as exc:  # noqa: BLE001 — record clone failure
                    repo_signals_cache[repo_id] = RepoSignals(
                        clone_ok=False, paths=set(), clone_error=str(exc)[:200]
                    )
            else:
                repo_signals_cache[repo_id] = RepoSignals(clone_ok=False, paths=set(), clone_error="clone disabled")

        repo_sig = repo_signals_cache[repo_id]
        test_command = resolve_test_command(candidate)
        ecosystem = detect_ecosystem(test_command, repo_sig.paths)
        hist_rate = historical.get(repo, 0.0)
        hist_ok = historical_successes.get(repo, 0)

        smoke: SmokeResult | None = None
        smoke_key = (repo_id, commit_sha, test_command)
        if enable_smoke and smoke_count < max_smoke and repo_sig.clone_ok:
            if smoke_key not in smoke_cache:
                # Live smoke requires worktree — skip in default batch; heuristic fills gap
                install_cmd = infer_install_command(
                    ecosystem=ecosystem,
                    paths=repo_sig.paths,
                    test_cwd=infer_go_module_root(repo_sig.paths) or ".",
                )
                smoke_cache[smoke_key] = run_live_smoke(
                    workspace=scratch_dir / f"viability_smoke_{repo_id}",
                    test_command=test_command,
                    install_command=install_cmd,
                ) if (scratch_dir / f"viability_smoke_{repo_id}").is_dir() else None
                if smoke_cache[smoke_key] is not None:
                    smoke_count += 1
            smoke = smoke_cache.get(smoke_key)

        checks, test_command, ecosystem = evaluate_candidate(
            candidate=candidate,
            repo_signals=repo_sig,
            historical_rate=hist_rate,
            historical_successes=hist_ok,
            smoke=smoke,
            use_heuristic_smoke=not enable_smoke,
        )
        score = _aggregate_score(checks)
        failure_reason = _primary_failure_reason(checks)
        classification, action = classify_viability(score=score, checks=checks)

        summary_rows.append(
            ViabilityRow(
                candidate_id=cid,
                repo=repo,
                score=score,
                failure_reason=failure_reason,
                recommended_action=action,
                classification=classification,
                test_command=test_command,
                ecosystem=ecosystem,
            )
        )
        for name, check in checks.items():
            audit_detail_rows.append(
                {
                    "candidate_id": cid,
                    "repository": repo,
                    "check": name,
                    "score": f"{check.score:.3f}",
                    "passed": check.passed,
                    "detail": check.detail[:200],
                }
            )

    csv_path = output_dir / "execution_viability.csv"
    buffer = StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=[
            "candidate_id",
            "repo",
            "score",
            "failure_reason",
            "recommended_action",
            "classification",
            "test_command",
            "ecosystem",
        ],
    )
    writer.writeheader()
    for row in summary_rows:
        writer.writerow(
            {
                "candidate_id": row.candidate_id,
                "repo": row.repo,
                "score": f"{row.score:.4f}",
                "failure_reason": row.failure_reason,
                "recommended_action": row.recommended_action,
                "classification": row.classification,
                "test_command": row.test_command,
                "ecosystem": row.ecosystem,
            }
        )
    atomic_write_text(csv_path, buffer.getvalue())

    detail_path = output_dir / "execution_viability_checks.csv"
    if audit_detail_rows:
        buf2 = StringIO()
        w2 = csv.DictWriter(buf2, fieldnames=list(audit_detail_rows[0].keys()))
        w2.writeheader()
        w2.writerows(audit_detail_rows)
        atomic_write_text(detail_path, buf2.getvalue())

    md_path = output_dir / "execution_viability_summary.md"
    atomic_write_text(
        md_path,
        render_viability_summary(
            rows=summary_rows,
            provenance=collect_provenance(
                manifest_path=manifest_path if manifest_path.exists() else candidates_csv,
                script_paths=[Path(__file__), Path(__file__).with_name("execution_viability_checks.py")],
                cwd=repo_root or Path.cwd(),
            ),
            historical=historical,
            phase0_toolchain_audit=toolchain_audit,
        ),
    )

    return {"viability_csv": csv_path, "checks_csv": detail_path, "summary_md": md_path}


def render_viability_summary(
    *,
    rows: list[ViabilityRow],
    provenance: dict,
    historical: dict[str, float],
    phase0_toolchain_audit: Path,
) -> str:
    n = len(rows)
    by_class = Counter(r.classification for r in rows)
    ready = by_class.get("READY", 0)
    minor = by_class.get("MINOR_SETUP", 0)
    manual = by_class.get("REQUIRES_MANUAL_FIX", 0)
    drop = by_class.get("DROP", 0)

    # Estimate infrastructure failure reduction if gate enforced (READY + MINOR_SETUP only)
    allowed = ready + minor
    filtered_pct = 100 * allowed / n if n else 0.0

    phase0_env_rate = 1.0
    if phase0_toolchain_audit.exists():
        audit = list(csv.DictReader(phase0_toolchain_audit.open(encoding="utf-8")))
        fails = [r for r in audit if r.get("success", "").lower() not in ("true", "1")]
        env = sum(
            1
            for r in fails
            if r.get("failure_class")
            in {
                "missing test runner",
                "wrong working directory",
                "invalid test command",
                "timeout",
            }
        )
        phase0_env_rate = env / max(len(fails), 1)

    # Repos in phase0 with failures vs READY in viability
    phase0_repos = set(historical.keys())
    ready_repos = {r.repo for r in rows if r.classification == "READY"}
    blocked_repos = phase0_repos - ready_repos

    lines = [
        "# Execution Viability Preflight Summary",
        "",
        "**Purpose:** mandatory gate before task calibration. No agent execution.",
        "",
        provenance_block(provenance),
        "",
        "## Cohort classification",
        "",
        f"- Candidates scored: **{n}**",
        f"- **READY**: {ready} ({100 * ready / n:.1f}%)" if n else "",
        f"- **MINOR_SETUP**: {minor} ({100 * minor / n:.1f}%)" if n else "",
        f"- **REQUIRES_MANUAL_FIX**: {manual} ({100 * manual / n:.1f}%)" if n else "",
        f"- **DROP**: {drop} ({100 * drop / n:.1f}%)" if n else "",
        "",
        "## Expected infrastructure-failure reduction",
        "",
        f"- Observed Phase 0 environment/toolchain failure rate (executed sample): **{100 * phase0_env_rate:.1f}%**",
        f"- Candidates passing READY or MINOR_SETUP gate: **{allowed}** ({filtered_pct:.1f}% of pool)",
        "",
        "If calibration and factorial selection draw only from **READY ∪ MINOR_SETUP**:",
        "",
        (
            f"- **Estimated reduction** in infrastructure-class failures: "
            f"**{100 * phase0_env_rate:.0f}% → ~{100 * phase0_env_rate * max(0.0, 1 - filtered_pct / 100) * 0.35:.0f}%** "
            "(conservative; assumes MINOR_SETUP fixes succeed)"
        ),
        "",
        f"- Phase 0 repos with toolchain failures not marked READY: **{len(blocked_repos)}**",
        "",
        "> This is an execution-environment projection, not a scientific success-rate claim.",
        "",
        "## Diagnosis (Phase 0 cross-check)",
        "",
    ]

    if historical:
        for repo, rate in sorted(historical.items(), key=lambda x: -x[1])[:10]:
            cls = next((r.classification for r in rows if r.repo == repo), "—")
            lines.append(f"- `{repo}`: phase0 env failure rate **{rate:.0%}** → viability **{cls}**")
    else:
        lines.append("- No Phase 0 toolchain audit history merged.")

    lines.extend(["", "## Recommended pipeline insertion", ""])
    lines.extend(
        [
            "```",
            "truth-decay-rq5-v2-candidates",
            "  ↓",
            "rq5-v2-execution-viability   ← this gate",
            "  ↓",
            "task-calibration (READY + MINOR_SETUP only)",
            "  ↓",
            "rq5-v2-factorial-plan",
            "```",
            "",
        ]
    )

    top_failures = Counter(r.failure_reason.split(":")[0] for r in rows if r.failure_reason)
    lines.append("## Top failure modes")
    lines.append("")
    for reason, count in top_failures.most_common(8):
        lines.append(f"- **{reason}**: {count}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Execution Viability preflight (no agents)")
    parser.add_argument("--candidates-csv", type=Path, default=DEFAULT_CANDIDATES_CSV)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--scratch-dir", type=Path, default=Path("scratch"))
    parser.add_argument("--no-clone", action="store_true", help="Skip git clone (heuristic only)")
    parser.add_argument("--smoke", action="store_true", help="Run live install+test smoke (requires worktrees)")
    parser.add_argument("--max-smoke", type=int, default=0)
    args = parser.parse_args()

    paths = run_execution_viability(
        candidates_csv=args.candidates_csv,
        output_dir=args.output_dir,
        scratch_dir=args.scratch_dir,
        enable_clone=not args.no_clone,
        enable_smoke=args.smoke,
        max_smoke=args.max_smoke,
    )
    for label, path in paths.items():
        print(f"{label} -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
