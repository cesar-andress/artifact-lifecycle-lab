"""Execution-environment audit for Phase 0 toolchain failures (read-only)."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from io import StringIO
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.rq5_v2.manifest import load_case_manifest
from artifact_lab.experiments.rq5_v2.models import FactorialCase
from artifact_lab.experiments.rq5_v2.phase0_provenance import collect_provenance, provenance_block
from artifact_lab.experiments.rq5_v2.phase0_run import DEFAULT_OUTPUT_DIR
from artifact_lab.experiments.rq5_v2.phase0_trace import parse_trace_events

FAILURE_CLASSES = (
    "missing test runner",
    "missing dependency",
    "package install required",
    "wrong working directory",
    "invalid test command",
    "timeout",
    "agent edit error",
    "actual test failure after valid execution",
    "infrastructure/API/tool error",
    "unknown",
)

AUDIT_FIELDS = (
    "run_id",
    "case_id",
    "repository",
    "ecosystem",
    "cell_code",
    "test_command",
    "success",
    "failure_class",
    "evidence",
    "preflight_preventable",
    "exclude_case_recommended",
    "recommended_fix",
)


@dataclass(frozen=True)
class ToolchainFailureRow:
    run_id: str
    case_id: str
    repository: str
    ecosystem: str
    cell_code: str
    test_command: str
    success: bool
    failure_class: str
    evidence: str
    preflight_preventable: str
    exclude_case_recommended: str
    recommended_fix: str


def _bool(value: object) -> bool:
    return str(value).lower() in ("true", "1", "yes")


def _resolve_trace_path(row: dict, traces_dir: Path) -> Path:
    raw = str(row.get("trace_path") or "").strip()
    if raw:
        trace_path = Path(raw)
        if trace_path.is_file():
            return trace_path
        if not trace_path.is_absolute():
            candidate = Path.cwd() / trace_path
            if candidate.is_file():
                return candidate
    return traces_dir / f"{row.get('run_id', '')}.jsonl"


def _trace_evidence(trace_path: Path, *, max_chars: int = 400) -> str:
    if not trace_path.is_file():
        return "(no trace file)"
    events, _ = parse_trace_events(trace_path)
    commands: list[str] = []
    for event in events:
        if event.event_type in {"shell_command", "Bash"}:
            cmd = str((event.payload or {}).get("command", ""))
            if cmd:
                commands.append(cmd)
    if commands:
        return ("trace shell: " + " | ".join(commands[-3:]))[:max_chars]
    return f"(trace bytes={trace_path.stat().st_size})"


def _log_evidence(run_id: str, log_text: str) -> str:
    if not log_text:
        return ""
    hits = [ln.strip() for ln in log_text.splitlines() if run_id in ln]
    return hits[-1][:200] if hits else ""


def classify_toolchain_failure(
    *,
    row: dict,
    case: FactorialCase | None,
    trace_path: Path,
    log_text: str = "",
) -> ToolchainFailureRow:
    run_id = str(row.get("run_id", ""))
    case_id = str(row.get("case_id", ""))
    repository = case.repository if case else ""
    ecosystem = case.ecosystem if case else ""
    test_command = case.test_command if case else ""
    cell_code = str(row.get("cell_code", ""))
    success = _bool(row.get("success"))
    err = (row.get("error_message") or "").strip()
    err_lower = err.lower()
    trace_ev = _trace_evidence(trace_path)
    log_ev = _log_evidence(run_id, log_text)
    evidence_parts = [p for p in (err[:300], trace_ev, log_ev) if p]
    evidence = " // ".join(evidence_parts)[:500]

    if success:
        return ToolchainFailureRow(
            run_id=run_id,
            case_id=case_id,
            repository=repository,
            ecosystem=ecosystem,
            cell_code=cell_code,
            test_command=test_command,
            success=True,
            failure_class="",
            evidence="tests passed with files modified",
            preflight_preventable="n/a",
            exclude_case_recommended="no",
            recommended_fix="none",
        )

    failure_class = "unknown"
    preflight = "unknown"
    exclude = "review"
    fix = "manual review required"

    if _bool(row.get("timed_out")) or "timeout" in err_lower:
        failure_class = "timeout"
        preflight = "partial"
        exclude = "no"
        fix = "increase test timeout or reduce compile scope; verify test_command targets fast smoke subset"

    elif any(t in err_lower for t in ("invalid api key", "authentication", "not logged in")):
        failure_class = "infrastructure/API/tool error"
        preflight = "yes"
        exclude = "no"
        fix = "fix agent API credentials before experiment batch"

    elif "clone" in err_lower or "network" in err_lower or "connection refused" in err_lower:
        failure_class = "infrastructure/API/tool error"
        preflight = "yes"
        exclude = "no"
        fix = "verify git clone and network in workspace prep"

    elif re.search(r"command not found|not found\n?$|: not found", err_lower) and any(
        t in err_lower for t in ("vitest", "jest", "pytest", "cargo", "go", "yarn", "npm", "mvn")
    ):
        if "vitest" in err_lower or "jest" in err_lower:
            failure_class = "missing test runner"
            fix = f"replace bare runner with ecosystem entrypoint (e.g. npm test / npx vitest); was `{test_command}`"
        else:
            failure_class = "missing test runner"
            fix = f"install runner or use package.json script; was `{test_command}`"
        preflight = "yes"
        exclude = "no"

    elif "error command" in err_lower and "not found" in err_lower:
        failure_class = "invalid test command"
        preflight = "yes"
        exclude = "no"
        fix = f"package.json lacks test script; pick valid script from repo or drop case; was `{test_command}`"

    elif "cannot find module" in err_lower or "module not found" in err_lower or "enoent" in err_lower:
        failure_class = "missing dependency"
        preflight = "yes"
        exclude = "no"
        fix = "run package install in workspace before agent (npm ci / yarn install / go mod download)"

    elif "npm err" in err_lower or "need to run npm install" in err_lower or "node_modules" in err_lower:
        failure_class = "package install required"
        preflight = "yes"
        exclude = "no"
        fix = "add preflight `npm ci` or `yarn install` for workspace"

    elif "go: cannot find main module" in err_lower or "no go files" in err_lower:
        failure_class = "wrong working directory"
        preflight = "yes"
        exclude = "no"
        fix = f"run `{test_command}` from Go module root (backend/ or subdir), not repo root"

    elif "collected 0 items" in err_lower or "no tests ran" in err_lower:
        failure_class = "invalid test command"
        preflight = "yes"
        exclude = "review"
        if "artifact-lifecycle-lab" in err:
            failure_class = "wrong working directory"
            fix = "pytest picked up lab root pyproject.toml; constrain cwd to case repo submodule with tests"
        else:
            fix = f"`{test_command}` finds zero tests in this repo/commit; choose repo-specific smoke command"
        preflight = "yes"

    elif err_lower.startswith("compiling ") or ("compiling " in err_lower and "error" not in err_lower[:120]):
        failure_class = "timeout"
        preflight = "partial"
        exclude = "no"
        fix = "cargo test compile exceeded capture/time; use smaller crate target or longer timeout with preflight compile"

    elif "error[" in err_lower or "failed to compile" in err_lower or "compilation failed" in err_lower:
        if not _bool(row.get("compilation_success", True)):
            failure_class = "agent edit error"
            preflight = "no"
            exclude = "no"
            fix = "agent introduced compile error; task difficulty not environment"
        else:
            failure_class = "actual test failure after valid execution"
            preflight = "no"
            exclude = "no"
            fix = "environment executed; failure is substantive test/agent outcome"

    elif _bool(row.get("decoy_path_touched")) and not _bool(row.get("anchor_path_touched")):
        failure_class = "agent edit error"
        preflight = "no"
        exclude = "no"
        fix = "agent edited decoy path instead of load-bearing anchor"

    elif int(str(row.get("files_modified") or "0")) == 0:
        failure_class = "agent edit error"
        preflight = "no"
        exclude = "no"
        fix = "no file changes despite instruction; agent did not attempt repair edit"

    elif "failed" in err_lower or "assert" in err_lower or "error:" in err_lower:
        failure_class = "actual test failure after valid execution"
        preflight = "no"
        exclude = "no"
        fix = "tests executed; classify as task/agent outcome not toolchain"

    elif not err and not _bool(row.get("tests_passing")):
        failure_class = "unknown"
        preflight = "unknown"
        exclude = "review"
        fix = "empty error_message with tests_passing=false; inspect trace"

    # Bare command names like "Vitest" without path
    if failure_class == "unknown" and test_command.strip().lower() in {
        "vitest",
        "jest",
        "pytest",
        "go test",
        "cargo test",
    }:
        if test_command.strip() == "Vitest":
            failure_class = "invalid test command"
            preflight = "yes"
            exclude = "no"
            fix = "calibration extracted bare `Vitest` token; replace with npm/yarn script"

    return ToolchainFailureRow(
        run_id=run_id,
        case_id=case_id,
        repository=repository,
        ecosystem=ecosystem,
        cell_code=cell_code,
        test_command=test_command,
        success=success,
        failure_class=failure_class,
        evidence=evidence,
        preflight_preventable=preflight,
        exclude_case_recommended=exclude,
        recommended_fix=fix,
    )


def audit_toolchain_failures(
    *,
    rows: list[dict],
    cases: dict[str, FactorialCase],
    traces_dir: Path,
    log_text: str = "",
) -> list[ToolchainFailureRow]:
    out: list[ToolchainFailureRow] = []
    for row in rows:
        case = cases.get(row.get("case_id", ""))
        trace_path = _resolve_trace_path(row, traces_dir)
        out.append(
            classify_toolchain_failure(row=row, case=case, trace_path=trace_path, log_text=log_text)
        )
    return out


@dataclass(frozen=True)
class CaseQualityVerdict:
    case_id: str
    repository: str
    test_command: str
    ecosystem: str
    runs: int
    successes: int
    dominant_failure: str
    valid_toolchain: str
    category: str
    recommendation: str


def summarize_case_quality(audit_rows: list[ToolchainFailureRow]) -> list[CaseQualityVerdict]:
    by_case: dict[str, list[ToolchainFailureRow]] = defaultdict(list)
    for row in audit_rows:
        by_case[row.case_id].append(row)

    verdicts: list[CaseQualityVerdict] = []
    for case_id, rows in sorted(by_case.items()):
        successes = sum(1 for r in rows if r.success)
        fails = [r for r in rows if not r.success]
        fail_classes = Counter(r.failure_class for r in fails)
        dominant = fail_classes.most_common(1)[0][0] if fail_classes else ""
        repo = rows[0].repository
        cmd = rows[0].test_command
        eco = rows[0].ecosystem

        if successes == len(rows) and len(rows) > 0:
            valid = "yes"
            category = "valid toolchain"
            rec = "keep"
        elif successes > 0:
            valid = "partial"
            category = "mixed execution environment"
            rec = "keep; investigate inconsistent failures"
        elif dominant in {
            "missing test runner",
            "invalid test command",
            "wrong working directory",
            "package install required",
            "missing dependency",
        }:
            valid = "no"
            category = "invalid toolchain"
            rec = rows[0].recommended_fix
        elif dominant == "infrastructure/API/tool error":
            valid = "no"
            category = "infrastructure failure"
            rec = "fix infrastructure; do not drop case yet"
        elif dominant == "actual test failure after valid execution":
            valid = "yes"
            category = "valid toolchain"
            rec = "keep; low success reflects task difficulty"
        elif dominant == "agent edit error":
            valid = "yes"
            category = "valid toolchain"
            rec = "keep; failures are agent/task not environment"
        elif dominant == "timeout":
            valid = "partial"
            category = "requires setup command"
            rec = "add compile/install preflight or longer timeout"
        else:
            valid = "unknown"
            category = "review required"
            rec = fails[0].recommended_fix if fails else "pending runs"

        exclude_votes = sum(1 for r in fails if r.exclude_case_recommended == "yes")
        if valid == "no" and len(fails) >= 3 and exclude_votes == 0:
            if dominant in ("invalid test command", "wrong working directory"):
                rec = f"fix test_command before drop: {rec}"

        verdicts.append(
            CaseQualityVerdict(
                case_id=case_id,
                repository=repo,
                test_command=cmd,
                ecosystem=eco,
                runs=len(rows),
                successes=successes,
                dominant_failure=dominant,
                valid_toolchain=valid,
                category=category,
                recommendation=rec,
            )
        )
    return verdicts


def _md_table(headers: list[str], table_rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in table_rows:
        lines.append("| " + " | ".join(str(c).replace("|", "\\|") for c in row) + " |")
    return "\n".join(lines)


def render_toolchain_summary(
    *,
    audit_rows: list[ToolchainFailureRow],
    case_verdicts: list[CaseQualityVerdict],
    provenance: dict,
    total_cases_in_manifest: int,
) -> str:
    failed = [r for r in audit_rows if not r.success]
    class_counts = Counter(r.failure_class for r in failed)
    n_runs = len(audit_rows)
    n_ok = sum(1 for r in audit_rows if r.success)

    env_fail_classes = {
        "missing test runner",
        "missing dependency",
        "package install required",
        "wrong working directory",
        "invalid test command",
        "infrastructure/API/tool error",
        "timeout",
    }
    env_fails = sum(class_counts.get(c, 0) for c in env_fail_classes)
    task_fails = sum(
        class_counts.get(c, 0)
        for c in ("agent edit error", "actual test failure after valid execution")
    )

    lines = [
        "# Phase 0 Toolchain Failure Audit",
        "",
        "**Scope:** execution-environment audit only — not a scientific reinterpretation of success.",
        "",
        provenance_block(provenance),
        "",
        "## Executive summary",
        "",
        f"- Runs audited: **{n_runs}**",
        f"- Successes: **{n_ok}** ({100 * n_ok / n_runs:.1f}%)" if n_runs else "- Runs audited: **0**",
        f"- Failed runs: **{len(failed)}**",
        f"- Environment/toolchain-class failures: **{env_fails}** ({100 * env_fails / max(len(failed), 1):.1f}% of failures)",
        f"- Task/agent-class failures: **{task_fails}** ({100 * task_fails / max(len(failed), 1):.1f}% of failures)",
        "",
    ]

    if n_runs and env_fails > task_fails:
        lines.append(
            "> **Diagnosis:** low success rate is **primarily driven by broken or mis-specified execution environments**, not task difficulty."
        )
    elif n_runs and task_fails > env_fails:
        lines.append(
            "> **Diagnosis:** failures are **more consistent with task/agent outcomes** under runnable environments."
        )
    else:
        lines.append("> **Diagnosis:** mixed; see per-case breakdown.")

    lines.extend(["", "## Failure class distribution", ""])
    for cls in FAILURE_CLASSES:
        c = class_counts.get(cls, 0)
        if c:
            lines.append(f"- **{cls}**: {c} ({100 * c / max(len(failed), 1):.1f}%)")

    lines.extend(["", "## Revised Phase 0 case-quality report", ""])

    def _cases_where(pred) -> list[CaseQualityVerdict]:
        return [v for v in case_verdicts if pred(v)]

    sections = [
        ("Cases with valid toolchain", lambda v: v.valid_toolchain == "yes"),
        ("Cases with invalid toolchain", lambda v: v.valid_toolchain == "no"),
        ("Cases requiring setup command", lambda v: v.category == "requires setup command"),
        (
            "Cases requiring different test command",
            lambda v: v.dominant_failure in ("invalid test command", "missing test runner", "wrong working directory"),
        ),
        ("Cases to drop", lambda v: v.recommendation.startswith("drop")),
        ("Cases to keep", lambda v: v.recommendation == "keep" or v.valid_toolchain == "yes"),
    ]

    for title, pred in sections:
        items = _cases_where(pred)
        lines.append(f"### {title} ({len(items)})")
        lines.append("")
        if not items:
            lines.append("- *(none in current sample)*")
        else:
            for v in items:
                lines.append(
                    f"- `{v.case_id[:12]}` **{v.repository}** — `{v.test_command}` "
                    f"({v.successes}/{v.runs} ok; {v.dominant_failure or 'n/a'}) — {v.recommendation}"
                )
        lines.append("")

    pending = total_cases_in_manifest - len(case_verdicts)
    if pending > 0:
        lines.append(f"### Cases pending execution ({pending})")
        lines.append("")
        lines.append(f"- {pending} manifest cases have no completed runs in the ledger yet.")
        lines.append("")

    lines.extend(["", "## Per-case detail", ""])
    table = [
        [
            v.case_id[:12],
            v.repository[:28],
            v.test_command[:24],
            f"{v.successes}/{v.runs}",
            v.valid_toolchain,
            v.dominant_failure[:28] if v.dominant_failure else "—",
        ]
        for v in case_verdicts
    ]
    lines.append(_md_table(["case_id", "repository", "test_command", "ok/runs", "valid", "dominant failure"], table))
    lines.append("")
    return "\n".join(lines)


def run_toolchain_failure_audit(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    manifest_path: Path | None = None,
    repo_root: Path | None = None,
) -> dict[str, Path]:
    output_dir = Path(output_dir)
    manifest_path = manifest_path or output_dir / "factorial_case_manifest.json"
    repo_root = repo_root or Path.cwd()
    results_csv = output_dir / "phase0_results.csv"
    traces_dir = output_dir / "phase0_traces"
    run_log = output_dir / "phase0_run.log"
    _trace_audit = output_dir / "phase0_trace_audit.csv"

    log_text = run_log.read_text(encoding="utf-8", errors="replace") if run_log.exists() else ""
    if _trace_audit.exists():
        _trace_audit.stat()

    cases_list = load_case_manifest(manifest_path)
    cases = {c.case_id: c for c in cases_list}
    rows: list[dict] = []
    if results_csv.exists():
        with results_csv.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))

    provenance = collect_provenance(
        manifest_path=manifest_path,
        script_paths=[Path(__file__)],
        cwd=repo_root,
    )

    audit_rows = audit_toolchain_failures(rows=rows, cases=cases, traces_dir=traces_dir, log_text=log_text)
    case_verdicts = summarize_case_quality(audit_rows)

    csv_path = output_dir / "phase0_toolchain_failure_audit.csv"
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(AUDIT_FIELDS))
    writer.writeheader()
    for row in audit_rows:
        writer.writerow(
            {
                "run_id": row.run_id,
                "case_id": row.case_id,
                "repository": row.repository,
                "ecosystem": row.ecosystem,
                "cell_code": row.cell_code,
                "test_command": row.test_command,
                "success": row.success,
                "failure_class": row.failure_class,
                "evidence": row.evidence,
                "preflight_preventable": row.preflight_preventable,
                "exclude_case_recommended": row.exclude_case_recommended,
                "recommended_fix": row.recommended_fix,
            }
        )
    atomic_write_text(csv_path, buffer.getvalue())

    md_path = output_dir / "phase0_toolchain_failure_summary.md"
    atomic_write_text(
        md_path,
        render_toolchain_summary(
            audit_rows=audit_rows,
            case_verdicts=case_verdicts,
            provenance=provenance,
            total_cases_in_manifest=len(cases_list),
        ),
    )

    return {"audit_csv": csv_path, "summary_md": md_path}


def main() -> int:
    paths = run_toolchain_failure_audit()
    for label, path in paths.items():
        print(f"{label} -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
