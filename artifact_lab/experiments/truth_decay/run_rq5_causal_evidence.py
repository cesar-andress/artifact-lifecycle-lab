"""Execute RQ5 causal evidence collection with real agents."""

from __future__ import annotations

import csv
from dataclasses import asdict
from io import StringIO
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.truth_decay.rq5_experiment.agents.recording import RecordingAgent
from artifact_lab.experiments.truth_decay.rq5_experiment.agents.registry import build_agents, discover_available_agent_names
from artifact_lab.experiments.truth_decay.rq5_experiment.causal_figures import (
    render_figure_effect_sizes,
    render_figure_failure_modes,
    render_figure_success,
    render_figure_trace_flow,
)
from artifact_lab.experiments.truth_decay.rq5_experiment.causal_statistics import (
    compute_causal_statistics,
    causal_statistics_to_rows,
)
from artifact_lab.experiments.truth_decay.rq5_experiment.evaluation import evaluate_run
from artifact_lab.experiments.truth_decay.rq5_experiment.models import DEFAULT_CONDITIONS_AB, AgentRunResult, ExperimentCase
from artifact_lab.experiments.truth_decay.rq5_experiment.runner import case_manifest_rows, dataset_rows
from artifact_lab.experiments.truth_decay.rq5_experiment.task_selection import select_experiment_cases
from artifact_lab.experiments.truth_decay.rq5_experiment.trace_classifier import (
    apply_trace_classifications,
    classify_run_trace,
    failure_mode_rows,
    trace_class_frequencies,
)
from artifact_lab.experiments.truth_decay.rq5_experiment.workspace import prepared_workspace, write_instruction_to_workspace
from artifact_lab.store.blobs import BlobStore

DEFAULT_CANDIDATE_CSV = Path("exports/truth_decay_pilot/rq5_candidate_dataset.csv")
DEFAULT_GFC_CSV = Path("exports/truth_decay_pilot/gfc_confirmatory_audit.csv")
DEFAULT_RQ5_CAUSAL_EXPORT = Path("exports/rq5_agent_impact")


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


def _run_key(result: AgentRunResult) -> tuple[str, str, str, int]:
    return (result.case_id, result.condition, result.agent_id, result.replicate_id)


def _load_completed_keys(path: Path) -> set[tuple[str, str, str, int]]:
    if not path.exists():
        return set()
    completed: set[tuple[str, str, str, int]] = set()
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            completed.add(
                (
                    row["case_id"],
                    row["condition"],
                    row["agent_id"],
                    int(row["replicate_id"]),
                )
            )
    return completed


def _append_result_row(path: Path, row: dict) -> None:
    exists = path.exists() and path.stat().st_size > 0
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row.keys()))
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def _result_from_row(row: dict, cases: list[ExperimentCase]) -> AgentRunResult:
    return AgentRunResult(
        agent_id=row["agent_id"],
        condition=row["condition"],
        case_id=row["case_id"],
        replicate_id=int(row["replicate_id"]),
        success=row["success"] in (True, "True", "true", "1"),
        tests_passing=row["tests_passing"] in (True, "True", "true", "1"),
        compilation_success=row["compilation_success"] in (True, "True", "true", "1"),
        execution_time_seconds=float(row["execution_time_seconds"]),
        files_modified=int(row.get("files_modified") or 0),
        tool_failures=int(row.get("tool_failures") or 0),
        iterations=int(row.get("iterations") or 0),
        commands_executed=int(row.get("commands_executed") or 0),
        repository_changes=int(row.get("repository_changes") or 0),
        read_instruction=row.get("read_instruction") in (True, "True", "true", "1"),
        followed_reference=row.get("followed_reference") in (True, "True", "true", "1"),
        ignored_reference=row.get("ignored_reference") in (True, "True", "true", "1"),
        detected_inconsistency=row.get("detected_inconsistency") in (True, "True", "true", "1"),
        repaired_reference=row.get("repaired_reference") in (True, "True", "true", "1"),
        error_message=row.get("error_message") or "",
        tool_invocations=int(row.get("tool_invocations") or 0),
        patch_size=int(row.get("patch_size") or 0),
        token_usage=int(row["token_usage"]) if row.get("token_usage") not in (None, "") else None,
        cost_usd=float(row["cost_usd"]) if row.get("cost_usd") not in (None, "") else None,
        trace_classification=row.get("trace_classification") or "",
    )


def _load_existing_results(path: Path, cases: list[ExperimentCase]) -> list[AgentRunResult]:
    if not path.exists():
        return []
    results: list[AgentRunResult] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            results.append(_result_from_row(row, cases))
    return results


def run_causal_matrix_with_checkpoint(
    *,
    cases: list[ExperimentCase],
    agents,
    scratch_dir: Path,
    traces_dir: Path,
    blob_store: BlobStore,
    results_csv: Path,
    replicates: int = 3,
    run_tests: bool = True,
    use_git_workspaces: bool = True,
    clone_timeout: int = 180,
    conditions: tuple[str, ...] = DEFAULT_CONDITIONS_AB,
) -> list[AgentRunResult]:
    completed = _load_completed_keys(results_csv)
    results = _load_existing_results(results_csv, cases)
    case_map = {case.case_id: case for case in cases}

    for case in cases:
        for condition in conditions:
            for agent in agents:
                recorder = RecordingAgent(agent, traces_dir)
                for replicate_id in range(1, replicates + 1):
                    key = (case.case_id, condition, agent.agent_id, replicate_id)
                    if key in completed:
                        continue
                    print(
                        f"rq5 run: case={case.case_id} condition={condition} "
                        f"agent={agent.agent_id} rep={replicate_id}",
                        flush=True,
                    )
                    if use_git_workspaces:
                        with prepared_workspace(
                            case=case,
                            condition=condition,
                            scratch_dir=scratch_dir,
                            blob_store=blob_store,
                            clone_timeout=clone_timeout,
                        ) as workspace:
                            raw = recorder.run(
                                case=case,
                                condition=condition,
                                workspace=workspace,
                                replicate_id=replicate_id,
                            )
                            result = evaluate_run(
                                case=case,
                                workspace=workspace,
                                agent_result=raw,
                                run_tests=run_tests,
                            )
                    else:
                        workspace = scratch_dir / f"local_{case.case_id}_{condition}_r{replicate_id}"
                        workspace.mkdir(parents=True, exist_ok=True)
                        write_instruction_to_workspace(
                            workspace=workspace,
                            case=case,
                            condition=condition,
                            blob_store=blob_store,
                        )
                        raw = recorder.run(
                            case=case,
                            condition=condition,
                            workspace=workspace,
                            replicate_id=replicate_id,
                        )
                        result = evaluate_run(
                            case=case,
                            workspace=workspace,
                            agent_result=raw,
                            run_tests=run_tests,
                        )

                    result.trace_classification = classify_run_trace(result=result, case=case)
                    results.append(result)
                    row = result.to_row()
                    row.update(
                        {
                            "spec_id": case.spec_id,
                            "repo_id": case.repo_id,
                            "repo_url": case.repo_url,
                            "instruction_path": case.instruction_path,
                            "task_commit_sha": case.task_commit_sha,
                            "anchor_reference": case.anchor_reference,
                            "confirmed_false": case.confirmed_false,
                            "test_command": case.test_command,
                        }
                    )
                    _append_result_row(results_csv, row)
                    completed.add(key)

    return apply_trace_classifications(results=results, cases=cases)


def _summary_markdown(
    *,
    cases: list[ExperimentCase],
    results: list[AgentRunResult],
    stats_rows: list,
    agents: list[str],
    replicates: int,
) -> str:
    lines = [
        "# RQ5 — Causal Evidence Summary",
        "",
        "## Design (frozen protocol)",
        "",
        "- Condition **A:** truthful instruction blob at pinned commit.",
        "- Condition **B:** confirmed-false natural instruction blob; all else identical.",
        "",
        "## Execution",
        "",
        f"- Cases: **{len(cases)}**",
        f"- Agents: **{', '.join(agents)}**",
        f"- Replicates per (case × condition × agent): **{replicates}**",
        f"- Total runs in results file: **{len(results)}**",
        "",
        "## Raw outcome counts",
        "",
    ]
    for agent in agents:
        subset = [r for r in results if r.agent_id == agent]
        if not subset:
            continue
        a_ok = sum(1 for r in subset if r.condition == "A" and r.success)
        b_ok = sum(1 for r in subset if r.condition == "B" and r.success)
        a_n = sum(1 for r in subset if r.condition == "A")
        b_n = sum(1 for r in subset if r.condition == "B")
        lines.append(f"- `{agent}`: success A={a_ok}/{a_n}, B={b_ok}/{b_n}")

    lines.extend(["", "## Statistics (descriptive only)", ""])
    for row in stats_rows:
        if row.estimand in {
            "paired_success_difference_a_minus_b",
            "mcnemar_p_value",
            "cohens_h",
            "cliffs_delta_execution_time",
        }:
            lines.append(
                f"- `{row.agent_id}` {row.estimand}: value={row.value}, "
                f"CI=[{row.ci_low}, {row.ci_high}], method={row.method}"
            )
    lines.append("")
    return "\n".join(lines)


def generate_rq5_outputs(
    *,
    cases: list[ExperimentCase],
    results: list[AgentRunResult],
    output_dir: Path,
    agent_names: list[str],
    replicates: int,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "results_csv": output_dir / "rq5_results.csv",
        "statistics_csv": output_dir / "rq5_statistics.csv",
        "summary_md": output_dir / "rq5_summary.md",
        "failure_modes_csv": output_dir / "rq5_failure_modes.csv",
        "trace_statistics_csv": output_dir / "rq5_trace_statistics.csv",
        "case_manifest_csv": output_dir / "rq5_case_manifest.csv",
        "figure_success": output_dir / "figure_success.pdf",
        "figure_failure_modes": output_dir / "figure_failure_modes.pdf",
        "figure_effect_sizes": output_dir / "figure_effect_sizes.pdf",
        "figure_trace_flow": output_dir / "figure_trace_flow.pdf",
    }

    classified = apply_trace_classifications(results=results, cases=cases)
    stats = compute_causal_statistics(classified)
    trace_stats = trace_class_frequencies(classified)
    failures = failure_mode_rows(classified)

    _write_csv(causal_statistics_to_rows(stats), paths["statistics_csv"])
    _write_csv(trace_stats, paths["trace_statistics_csv"])
    _write_csv(failures, paths["failure_modes_csv"])
    _write_csv(case_manifest_rows(cases), paths["case_manifest_csv"])
    atomic_write_text(
        paths["summary_md"],
        _summary_markdown(
            cases=cases,
            results=classified,
            stats_rows=stats,
            agents=agent_names,
            replicates=replicates,
        ),
    )

    render_figure_success(classified, paths["figure_success"])
    render_figure_failure_modes(failures, paths["figure_failure_modes"])
    render_figure_effect_sizes(stats, paths["figure_effect_sizes"])
    render_figure_trace_flow(trace_stats, paths["figure_trace_flow"])
    return paths


def run_rq5_causal_evidence(
    *,
    candidate_csv: Path = DEFAULT_CANDIDATE_CSV,
    gfc_confirmatory_csv: Path = DEFAULT_GFC_CSV,
    blobs_dir: Path = Path("data/blobs"),
    scratch_dir: Path = Path("scratch"),
    output_dir: Path = DEFAULT_RQ5_CAUSAL_EXPORT,
    agents: list[str] | None = None,
    replicates: int = 3,
    max_cases: int | None = None,
    require_p1: bool = False,
    run_tests: bool = True,
    use_git_workspaces: bool = True,
    clone_timeout: int = 180,
    resume: bool = True,
    conditions: tuple[str, ...] = DEFAULT_CONDITIONS_AB,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    traces_dir = output_dir / "traces"
    results_csv = output_dir / "rq5_results.csv"

    agent_names = agents or discover_available_agent_names()
    if not agent_names:
        raise RuntimeError("no available real agents detected; install/authenticate claude or copilot CLI")

    blob_store = BlobStore(blobs_dir)
    cases = select_experiment_cases(
        candidate_csv=candidate_csv,
        gfc_confirmatory_csv=gfc_confirmatory_csv,
        max_cases=max_cases,
        require_p1=require_p1,
        results_csv_for_traces=results_csv if results_csv.exists() else None,
    )
    if not cases:
        raise RuntimeError("no experiment cases selected")

    if resume and not results_csv.exists():
        resume = False

    agent_instances = build_agents(agent_names)
    results = run_causal_matrix_with_checkpoint(
        cases=cases,
        agents=agent_instances,
        scratch_dir=scratch_dir,
        traces_dir=traces_dir,
        blob_store=blob_store,
        results_csv=results_csv,
        replicates=replicates,
        run_tests=run_tests,
        use_git_workspaces=use_git_workspaces,
        clone_timeout=clone_timeout,
        conditions=conditions,
    )

    paths = generate_rq5_outputs(
        cases=cases,
        results=results,
        output_dir=output_dir,
        agent_names=agent_names,
        replicates=replicates,
    )
    paths["results_csv"] = results_csv

    print(
        f"rq5 causal evidence complete: cases={len(cases)} runs={len(results)} agents={agent_names}",
        flush=True,
    )
    return paths
