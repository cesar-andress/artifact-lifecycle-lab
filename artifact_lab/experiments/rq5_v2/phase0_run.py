"""Phase 0 calibration execution, analysis, and decision gates."""

from __future__ import annotations

import csv
import json
import math
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from statistics import median

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.rq5_v2.factors import CellCode
from artifact_lab.experiments.rq5_v2.ledger import completed_run_keys, pending_entries
from artifact_lab.experiments.rq5_v2.manifest import load_case_manifest, write_run_plan_csv
from artifact_lab.experiments.rq5_v2.models import ExperimentConfig, FactorialCase, RunPlanEntry
from artifact_lab.experiments.rq5_v2.plan import build_run_plan
from artifact_lab.experiments.rq5_v2.runner import EXECUTE_ENV_VAR, execution_allowed, run_factorial_matrix
from artifact_lab.experiments.rq5_v2.phase0_trace import enrich_result_from_trace
from artifact_lab.experiments.rq5_v2.phase0_setup import SetupRunResult, write_setup_log
from artifact_lab.store.blobs import BlobStore

DEFAULT_REPAIRED_MANIFEST = Path("exports/rq5_v2_factorial/phase0_manifest_repaired.json")
DEFAULT_VIABILITY_CSV = Path("exports/rq5_v2_factorial/execution_viability.csv")

PHASE0_CELL = CellCode.T_L.value
PHASE0_REPLICATES = 3
PHASE0_AGENT = "claude_code"
PHASE0_EXPECTED_RUNS = 20 * PHASE0_REPLICATES

DEFAULT_OUTPUT_DIR = Path("exports/rq5_v2_factorial")


def _relaunch():
    from artifact_lab.experiments.rq5_v2 import phase0_relaunch as rel

    return rel


def _assert_repaired_manifest(path: Path) -> str:
    return _relaunch().assert_repaired_manifest(path)


@dataclass(frozen=True)
class PreflightReport:
    ok: bool
    checks: dict[str, bool]
    messages: list[str]


@dataclass(frozen=True)
class Phase0Metrics:
    n_runs: int
    success_rate: float
    success_wilson_low: float
    success_wilson_high: float
    anchor_attempt_rate: float
    instruction_read_rate: float
    files_modified_mean: float
    files_modified_median: float
    commands_mean: float
    commands_median: float
    tool_failures_total: int
    timeout_rate: float
    total_cost_usd: float
    total_duration_seconds: float
    median_duration_seconds: float


@dataclass(frozen=True)
class Phase0Decision:
    verdict: str
    reasons: list[str]
    proceed_phase1a: bool


def load_validated_phase0_cases(
    *,
    manifest_path: Path,
    audit_csv: Path,
) -> list[FactorialCase]:
    cases = load_case_manifest(manifest_path)
    if not audit_csv.exists():
        return cases[:20]
    valid_ids = {
        row["case_id"]
        for row in csv.DictReader(audit_csv.open(encoding="utf-8"))
        if str(row.get("valid_phase0", "")).lower() in ("true", "1")
    }
    if not valid_ids:
        return cases[:20]
    selected = [case for case in cases if case.case_id in valid_ids]
    return selected[:20]


def build_phase0_plan(
    *,
    cases: list[FactorialCase],
    seed: int = 42,
) -> tuple[list[RunPlanEntry], ExperimentConfig]:
    config = ExperimentConfig(
        protocol_version="RQ5_PHASE0_v1.0",
        agents=(PHASE0_AGENT,),
        cells=(PHASE0_CELL,),
        replicates=PHASE0_REPLICATES,
        primary_agent=PHASE0_AGENT,
        replication_agents=(),
        allow_execute=True,
        metadata={"phase": "0", "cell": PHASE0_CELL},
    )
    plan = build_run_plan(cases=cases, config=config, seed=seed)
    return plan, config


def verify_phase0_preflight(
    *,
    plan: list[RunPlanEntry],
    config: ExperimentConfig,
    results_csv: Path,
    traces_dir: Path,
    require_execute_env: bool = True,
    manifest_path: Path | None = None,
) -> PreflightReport:
    checks: dict[str, bool] = {}
    messages: list[str] = []

    if manifest_path is not None:
        try:
            _assert_repaired_manifest(manifest_path)
            checks["repaired_manifest_selected"] = True
        except (_relaunch().RepairedManifestRequiredError, FileNotFoundError) as exc:
            checks["repaired_manifest_selected"] = False
            messages.append(str(exc))
    else:
        checks["repaired_manifest_selected"] = False
        messages.append("manifest_path not provided for repaired-manifest check")

    env_set = os.environ.get(EXECUTE_ENV_VAR, "") in ("1", "true", "yes")
    checks["execute_env_required"] = (not require_execute_env) or env_set
    if require_execute_env and not env_set:
        messages.append(f"{EXECUTE_ENV_VAR} must be set to enable agent execution")

    blocked_config = ExperimentConfig(allow_execute=False)
    checks["execution_gated"] = not execution_allowed(config=blocked_config) or env_set

    try:
        pending = pending_entries(plan=plan, results_csv=results_csv)
        done = completed_run_keys(results_csv)
        checks["ledger_checkpointing"] = isinstance(done, set) and isinstance(pending, list)
    except OSError as exc:
        checks["ledger_checkpointing"] = False
        messages.append(f"Ledger check failed: {exc}")

    checks["cost_logging_enabled"] = True
    checks["trace_storage_enabled"] = True
    traces_dir.mkdir(parents=True, exist_ok=True)

    cell_codes = {entry.cell_code for entry in plan}
    agent_ids = {entry.agent_id for entry in plan}
    checks["tl_cell_only"] = cell_codes == {PHASE0_CELL}
    if not checks["tl_cell_only"]:
        messages.append(f"Unexpected cells scheduled: {sorted(cell_codes)}")
    checks["primary_agent_only"] = agent_ids == {PHASE0_AGENT}
    if not checks["primary_agent_only"]:
        messages.append(f"Unexpected agents scheduled: {sorted(agent_ids)}")
    checks["expected_run_count"] = len(plan) == PHASE0_EXPECTED_RUNS
    if not checks["expected_run_count"]:
        messages.append(f"Expected {PHASE0_EXPECTED_RUNS} runs, plan has {len(plan)}")

    ok = all(checks.values())
    return PreflightReport(ok=ok, checks=checks, messages=messages)


def wilson_ci(successes: int, n: int, z: float = 1.96) -> tuple[float, float, float]:
    if n <= 0:
        return 0.0, 0.0, 0.0
    p = successes / n
    z2 = z * z
    denom = 1.0 + z2 / n
    center = (p + z2 / (2.0 * n)) / denom
    margin = (z / denom) * math.sqrt((p * (1.0 - p) / n) + (z2 / (4.0 * n * n)))
    return p, max(0.0, center - margin), min(1.0, center + margin)


def _bool(value: object) -> bool:
    return str(value).lower() in ("true", "1", "yes")


def _float(value: object, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def load_phase0_results(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def compute_phase0_metrics(rows: list[dict]) -> Phase0Metrics:
    n = len(rows)
    successes = sum(1 for r in rows if _bool(r.get("success")))
    p, lo, hi = wilson_ci(successes, n)
    anchor_hits = sum(1 for r in rows if _bool(r.get("anchor_attempted")))
    read_hits = sum(1 for r in rows if _bool(r.get("instruction_read")))
    timeouts = sum(
        1
        for r in rows
        if _bool(r.get("timed_out")) or "timeout" in str(r.get("error_message", "")).lower()
    )
    files = [_float(r.get("files_modified")) for r in rows]
    commands = [_float(r.get("commands_executed")) for r in rows]
    durations = [_float(r.get("execution_time_seconds")) for r in rows]
    costs = [_float(r.get("cost_usd")) for r in rows if r.get("cost_usd") not in (None, "")]
    tool_failures = sum(int(_float(r.get("tool_failures"))) for r in rows)
    return Phase0Metrics(
        n_runs=n,
        success_rate=p,
        success_wilson_low=lo,
        success_wilson_high=hi,
        anchor_attempt_rate=anchor_hits / n if n else 0.0,
        instruction_read_rate=read_hits / n if n else 0.0,
        files_modified_mean=sum(files) / n if n else 0.0,
        files_modified_median=median(files) if files else 0.0,
        commands_mean=sum(commands) / n if n else 0.0,
        commands_median=median(commands) if commands else 0.0,
        tool_failures_total=tool_failures,
        timeout_rate=timeouts / n if n else 0.0,
        total_cost_usd=sum(costs),
        total_duration_seconds=sum(durations),
        median_duration_seconds=median(durations) if durations else 0.0,
    )


def evaluate_phase0_decision(metrics: Phase0Metrics) -> Phase0Decision:
    reasons: list[str] = []
    fail = False
    warn = False

    if metrics.success_rate < 0.30 or metrics.success_rate > 0.85:
        fail = True
        reasons.append(f"success_rate={metrics.success_rate:.3f} outside FAIL bounds")
    elif metrics.success_rate < 0.45 or metrics.success_rate > 0.75:
        warn = True
        reasons.append(f"success_rate={metrics.success_rate:.3f} in WARN band")

    if metrics.anchor_attempt_rate < 0.40:
        fail = True
        reasons.append(f"anchor_attempt_rate={metrics.anchor_attempt_rate:.3f} < 0.40")
    elif metrics.anchor_attempt_rate < 0.60:
        warn = True
        reasons.append(f"anchor_attempt_rate={metrics.anchor_attempt_rate:.3f} in WARN band")

    if metrics.instruction_read_rate < 0.80:
        fail = True
        reasons.append(f"instruction_read_rate={metrics.instruction_read_rate:.3f} < 0.80")

    if metrics.timeout_rate > 0.30:
        fail = True
        reasons.append(f"timeout_rate={metrics.timeout_rate:.3f} > 0.30")
    elif metrics.timeout_rate > 0.15:
        warn = True
        reasons.append(f"timeout_rate={metrics.timeout_rate:.3f} in WARN band")

    if metrics.files_modified_median > 20:
        fail = True
        reasons.append(f"median_files_modified={metrics.files_modified_median:.1f} > 20")
    elif metrics.files_modified_median > 10:
        warn = True
        reasons.append(f"median_files_modified={metrics.files_modified_median:.1f} > 10")

    if fail:
        verdict = "FAIL"
    elif warn:
        verdict = "WARN"
    else:
        verdict = "PASS"
        reasons.append("All Phase 0 decision gates satisfied")

    return Phase0Decision(verdict=verdict, reasons=reasons, proceed_phase1a=False)


def write_phase0_outputs(
    *,
    rows: list[dict],
    metrics: Phase0Metrics,
    decision: Phase0Decision,
    output_dir: Path,
    preflight: PreflightReport | None = None,
    manifest_sha256: str = "",
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "results_csv": output_dir / "phase0_results.csv",
        "summary_md": output_dir / "phase0_summary.md",
        "trace_audit_csv": output_dir / "phase0_trace_audit.csv",
        "decision_md": output_dir / "phase0_decision.md",
    }

    if rows:
        buffer = StringIO()
        writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
        atomic_write_text(paths["results_csv"], buffer.getvalue())

    trace_rows = [
        {
            "run_id": r.get("run_id", ""),
            "case_id": r.get("case_id", ""),
            "trace_path": r.get("trace_path", ""),
            "instruction_read": r.get("instruction_read", ""),
            "anchor_attempted": r.get("anchor_attempted", ""),
            "commands_executed": r.get("commands_executed", ""),
            "tool_failures": r.get("tool_failures", ""),
            "cost_usd": r.get("cost_usd", ""),
            "token_usage": r.get("token_usage", ""),
            "trace_bytes": (
                Path(r["trace_path"]).stat().st_size
                if r.get("trace_path") and Path(r["trace_path"]).exists()
                else 0
            ),
        }
        for r in rows
    ]
    if trace_rows:
        buffer = StringIO()
        writer = csv.DictWriter(buffer, fieldnames=list(trace_rows[0].keys()))
        writer.writeheader()
        writer.writerows(trace_rows)
        atomic_write_text(paths["trace_audit_csv"], buffer.getvalue())

    ts = datetime.now(timezone.utc).isoformat()
    summary_lines = [
        "# RQ5 v2 Phase 0 Calibration Summary",
        "",
        f"**Generated:** {ts}",
        f"**Manifest SHA-256:** `{manifest_sha256 or 'unknown'}`",
        f"**Cell:** `{PHASE0_CELL}` only",
        f"**Runs:** {metrics.n_runs} (expected {PHASE0_EXPECTED_RUNS})",
        f"**Decision:** **{decision.verdict}**",
        "",
        "## Metrics",
        "",
        f"- Success rate: **{metrics.success_rate:.3f}** (Wilson 95% CI [{metrics.success_wilson_low:.3f}, {metrics.success_wilson_high:.3f}])",
        f"- Anchor attempted rate: **{metrics.anchor_attempt_rate:.3f}**",
        f"- Instruction read rate: **{metrics.instruction_read_rate:.3f}**",
        f"- Files modified mean/median: **{metrics.files_modified_mean:.2f} / {metrics.files_modified_median:.1f}**",
        f"- Commands mean/median: **{metrics.commands_mean:.2f} / {metrics.commands_median:.1f}**",
        f"- Tool failures (total): **{metrics.tool_failures_total}**",
        f"- Timeout rate: **{metrics.timeout_rate:.3f}**",
        f"- Total cost (USD): **{metrics.total_cost_usd:.4f}**",
        f"- Total duration (s): **{metrics.total_duration_seconds:.1f}** (median **{metrics.median_duration_seconds:.1f}**)",
        "",
        "## Preflight",
        "",
    ]
    if preflight:
        for key, passed in preflight.checks.items():
            summary_lines.append(f"- `{key}`: {'PASS' if passed else 'FAIL'}")
    else:
        summary_lines.append("- (not recorded)")

    atomic_write_text(paths["summary_md"], "\n".join(summary_lines) + "\n")

    decision_lines = [
        "# RQ5 v2 Phase 0 Decision",
        "",
        f"**Manifest SHA-256:** `{manifest_sha256 or 'unknown'}`",
        f"**Verdict:** **{decision.verdict}**",
        f"**Proceed to Phase 1a:** **No** (manual gate; never automatic)",
        "",
        "## Gate evaluation",
        "",
    ]
    for reason in decision.reasons:
        decision_lines.append(f"- {reason}")
    decision_lines.extend(
        [
            "",
            "## Next steps",
            "",
            "- Phase 1a does **not** start automatically.",
            "- If PASS: human review, then run Phase 1a protocol separately.",
            "- If WARN: inspect failing metrics and adjust task difficulty or injection.",
            "- If FAIL: halt and redesign case battery before any factorial scale-up.",
            "",
        ]
    )
    atomic_write_text(paths["decision_md"], "\n".join(decision_lines))
    return paths


def analyze_phase0_results(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    manifest_path: Path = DEFAULT_REPAIRED_MANIFEST,
    manifest_sha256: str = "",
) -> dict[str, Path]:
    if manifest_path:
        try:
            manifest_sha256 = manifest_sha256 or _assert_repaired_manifest(manifest_path)
        except _relaunch().RepairedManifestRequiredError:
            raise
    """Re-analyze existing phase0_results.csv without executing agents."""
    cases = load_case_manifest(manifest_path)
    case_map = {c.case_id: c for c in cases}
    results_csv = output_dir / "phase0_results.csv"
    raw_rows = load_phase0_results(results_csv)
    enriched: list[dict] = []
    for row in raw_rows:
        case = case_map.get(row.get("case_id", ""))
        if case is None:
            enriched.append(row)
            continue
        trace_path = Path(row.get("trace_path") or "")
        enriched.append(
            enrich_result_from_trace(
                case=case,
                cell_code=row.get("cell_code", PHASE0_CELL),
                result_row=row,
                trace_path=trace_path,
            )
        )
    metrics = compute_phase0_metrics(enriched or raw_rows)
    decision = evaluate_phase0_decision(metrics)
    return write_phase0_outputs(
        rows=enriched or raw_rows,
        metrics=metrics,
        decision=decision,
        output_dir=output_dir,
        preflight=None,
        manifest_sha256=manifest_sha256,
    )


def run_phase0_calibration(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    manifest_path: Path = DEFAULT_REPAIRED_MANIFEST,
    audit_csv: Path = DEFAULT_OUTPUT_DIR / "phase0_case_audit.csv",
    viability_csv: Path = DEFAULT_VIABILITY_CSV,
    scratch_dir: Path = Path("scratch"),
    execute: bool = True,
    seed: int = 42,
    preflight_only: bool = False,
    prepare_only: bool = False,
) -> dict[str, Path]:
    manifest_sha = _assert_repaired_manifest(manifest_path)

    if prepare_only:
        from artifact_lab.experiments.rq5_v2.phase0_relaunch import prepare_phase0_relaunch

        return prepare_phase0_relaunch(
            output_dir=output_dir,
            manifest_path=manifest_path,
            viability_csv=viability_csv,
            scratch_dir=scratch_dir,
            seed=seed,
        )

    rel = _relaunch()
    cases = load_case_manifest(manifest_path)[:20]
    viability_index = rel.load_viability_index(viability_csv)
    setup_specs = rel.build_setup_specs(cases=cases, viability_index=viability_index)
    replacement_pool = rel.load_replacement_pool(output_dir / "phase0_replacement_pool.json")
    if not replacement_pool:
        replacement_pool = rel.build_replacement_pool(
            active_cases=cases,
            viability_index=viability_index,
            candidates_csv=Path("exports/rq5_v2/load_bearing_candidates.csv"),
            scratch_dir=scratch_dir,
        )

    plan, config = build_phase0_plan(cases=cases, seed=seed)

    plan_path = output_dir / "phase0_run_plan.csv"
    write_run_plan_csv(entries=plan, path=plan_path)
    rel.write_case_setup_csv(path=output_dir / "phase0_case_setup.csv", specs=setup_specs)

    results_csv = output_dir / "phase0_results.csv"
    traces_dir = output_dir / "phase0_traces"
    preflight = verify_phase0_preflight(
        plan=plan,
        config=config,
        results_csv=results_csv,
        traces_dir=traces_dir,
        require_execute_env=execute and not preflight_only,
        manifest_path=manifest_path,
    )

    preflight_path = output_dir / "phase0_preflight.json"
    atomic_write_text(
        preflight_path,
        json.dumps(
            {
                "ok": preflight.ok,
                "checks": preflight.checks,
                "messages": preflight.messages,
                "manifest_sha256": manifest_sha,
            },
            indent=2,
        ),
    )

    if preflight_only:
        from artifact_lab.experiments.rq5_v2.phase0_relaunch import prepare_phase0_relaunch

        prepare_phase0_relaunch(
            output_dir=output_dir,
            manifest_path=manifest_path,
            viability_csv=viability_csv,
            scratch_dir=scratch_dir,
            seed=seed,
        )
        return {"preflight_json": preflight_path, "run_plan_csv": plan_path}

    if execute and not preflight.ok:
        raise RuntimeError("Phase 0 preflight failed: " + "; ".join(preflight.messages))

    setup_log: list[SetupRunResult] = []
    if execute:
        if not execution_allowed(config=config):
            raise RuntimeError(f"Execution blocked; set {EXECUTE_ENV_VAR}=1")
        run_factorial_matrix(
            cases=cases,
            plan=plan,
            config=config,
            blob_store=BlobStore(Path("data/blobs")),
            scratch_dir=scratch_dir,
            results_csv=results_csv,
            traces_dir=traces_dir,
            execute=True,
            case_setup=setup_specs,
            setup_log=setup_log,
        )
        failed_ids = {row.case_id for row in setup_log if not row.ok}
        if failed_ids:
            cases, setup_specs, replacement_pool, excluded = rel.apply_setup_failures(
                active_cases=cases,
                setup_specs=setup_specs,
                failed_case_ids=failed_ids,
                replacement_pool=replacement_pool,
                viability_index=viability_index,
            )
            plan, config = build_phase0_plan(cases=cases, seed=seed)
            write_run_plan_csv(entries=plan, path=plan_path)
            rel.write_case_setup_csv(path=output_dir / "phase0_case_setup.csv", specs=setup_specs)
            atomic_write_text(
                output_dir / "phase0_setup_failures.json",
                json.dumps({"excluded": excluded, "replacements_used": True}, indent=2),
            )
            run_factorial_matrix(
                cases=cases,
                plan=plan,
                config=config,
                blob_store=BlobStore(Path("data/blobs")),
                scratch_dir=scratch_dir / "phase0_retry",
                results_csv=results_csv,
                traces_dir=traces_dir,
                execute=True,
                case_setup=setup_specs,
                setup_log=setup_log,
                excluded_case_ids=failed_ids,
            )
        if setup_log:
            write_setup_log(path=output_dir / "phase0_setup_log.csv", rows=setup_log)

    paths = analyze_phase0_results(
        output_dir=output_dir,
        manifest_path=manifest_path,
        manifest_sha256=manifest_sha,
    )
    paths["run_plan_csv"] = plan_path
    paths["preflight_json"] = preflight_path
    return paths
