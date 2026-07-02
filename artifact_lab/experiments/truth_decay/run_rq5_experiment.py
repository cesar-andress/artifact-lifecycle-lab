"""Run RQ5 causal agent-impact experiment."""

from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.truth_decay.rq5_experiment.agents.registry import build_agents
from artifact_lab.experiments.truth_decay.rq5_experiment.figures import (
    render_figure_failure_modes,
    render_figure_success_rate,
    render_figure_trace_flow,
)
from artifact_lab.experiments.truth_decay.rq5_experiment.runner import case_manifest_rows, dataset_rows, run_experiment_matrix
from artifact_lab.experiments.truth_decay.rq5_experiment.statistics import compute_effect_sizes, effect_sizes_to_rows
from artifact_lab.experiments.truth_decay.rq5_experiment.task_selection import select_experiment_cases
from artifact_lab.experiments.truth_decay.rq5_experiment.traces import compute_trace_statistics, trace_statistics_to_rows
from artifact_lab.experiments.truth_pilots.gates_common import DEFAULT_RQ1_LONGITUDINAL
from artifact_lab.store.blobs import BlobStore

DEFAULT_RQ5_EXPERIMENT_EXPORT = Path("exports/rq5_agent_impact")
DEFAULT_CANDIDATE_CSV = Path("exports/truth_decay_pilot/rq5_candidate_dataset.csv")
DEFAULT_GFC_CSV = Path("exports/truth_decay_pilot/gfc_confirmatory_audit.csv")


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


def _summary_markdown(
    *,
    cases: list,
    results: list,
    effect_rows: list,
    trace_rows: list,
    agents: list[str],
    replicates: int,
    run_tests: bool,
    use_git_workspaces: bool,
) -> str:
    n_a = sum(1 for r in results if r.condition == "A")
    n_b = sum(1 for r in results if r.condition == "B")
    lines = [
        "# RQ5 — Causal Agent Impact Experiment",
        "",
        "## Design",
        "",
        "- **Condition A:** repository pinned at `task_commit_sha` with truthful instruction blob.",
        "- **Condition B:** same repository, same commit, same task; instruction blob swapped to",
        "  naturally occurring confirmed-false snapshot (no synthetic perturbation).",
        "- **Cases:** drawn deterministically from `rq5_candidate_dataset.csv` joined with",
        "  `gfc_confirmatory_audit.csv` (`is_confirmed_false=true`).",
        "",
        "## Execution",
        "",
        f"- Selected cases: **{len(cases)}**",
        f"- Agents: **{', '.join(agents)}**",
        f"- Replicates per (case × condition × agent): **{replicates}**",
        f"- Total runs recorded: **{len(results)}** (A={n_a}, B={n_b})",
        f"- Objective test execution: **{'enabled' if run_tests else 'disabled'}**",
        f"- Git workspaces: **{'enabled' if use_git_workspaces else 'disabled (local stub mode)'}**",
        "",
        "## Outputs",
        "",
        "- `rq5_dataset.csv` — run-level outcomes",
        "- `rq5_effect_sizes.csv` — paired success contrasts and bootstrap CIs",
        "- `rq5_trace_statistics.csv` — trace-coded behavior rates",
        "- `rq5_case_manifest.csv` — selected experimental units",
        "- `traces/` — JSONL interaction traces per run",
        "- `figure_success_rate.pdf`, `figure_failure_modes.pdf`, `figure_trace_flow.pdf`",
        "",
        "## Descriptive aggregates (no interpretation)",
        "",
    ]
    for row in effect_rows:
        lines.append(
            f"- Agent `{row['agent_id']}`: success rate A={row['success_rate_a']:.3f}, "
            f"B={row['success_rate_b']:.3f}, paired Δ={row['paired_success_difference']:.3f} "
            f"(bootstrap CI {row['paired_success_difference_ci_low']:.3f}–"
            f"{row['paired_success_difference_ci_high']:.3f}), Cohen's h={row['cohens_h']:.3f}"
        )
    if trace_rows:
        lines.extend(["", "## Trace statistics rows", "", f"- Total trace statistic rows: **{len(trace_rows)}**"])
    lines.append("")
    return "\n".join(lines)


def run_rq5_experiment(
    *,
    candidate_csv: Path = DEFAULT_CANDIDATE_CSV,
    gfc_confirmatory_csv: Path = DEFAULT_GFC_CSV,
    blobs_dir: Path = Path("data/blobs"),
    scratch_dir: Path = Path("scratch"),
    output_dir: Path = DEFAULT_RQ5_EXPERIMENT_EXPORT,
    agents: list[str] | None = None,
    replicates: int = 1,
    max_cases: int | None = None,
    require_p1: bool = False,
    run_tests: bool = False,
    use_git_workspaces: bool = False,
    clone_timeout: int = 180,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    traces_dir = output_dir / "traces"
    paths = {
        "dataset_csv": output_dir / "rq5_dataset.csv",
        "summary_md": output_dir / "rq5_summary.md",
        "effect_sizes_csv": output_dir / "rq5_effect_sizes.csv",
        "trace_statistics_csv": output_dir / "rq5_trace_statistics.csv",
        "case_manifest_csv": output_dir / "rq5_case_manifest.csv",
        "figure_success": output_dir / "figure_success_rate.pdf",
        "figure_failure_modes": output_dir / "figure_failure_modes.pdf",
        "figure_trace_flow": output_dir / "figure_trace_flow.pdf",
    }

    agent_names = agents or ["stub"]
    blob_store = BlobStore(blobs_dir)
    cases = select_experiment_cases(
        candidate_csv=candidate_csv,
        gfc_confirmatory_csv=gfc_confirmatory_csv,
        max_cases=max_cases,
        require_p1=require_p1,
    )
    if not cases:
        raise RuntimeError("no experiment cases selected; check candidate and gfc inputs")

    agent_instances = build_agents(agent_names)
    results = run_experiment_matrix(
        cases=cases,
        agents=agent_instances,
        scratch_dir=scratch_dir,
        traces_dir=traces_dir,
        blob_store=blob_store,
        replicates=replicates,
        run_tests=run_tests,
        use_git_workspaces=use_git_workspaces,
        clone_timeout=clone_timeout,
    )

    effect_rows = effect_sizes_to_rows(compute_effect_sizes(results))
    trace_rows = trace_statistics_to_rows(compute_trace_statistics(results))
    dataset = dataset_rows(cases=cases, results=results)

    _write_csv(dataset, paths["dataset_csv"])
    _write_csv(effect_rows, paths["effect_sizes_csv"])
    _write_csv(trace_rows, paths["trace_statistics_csv"])
    _write_csv(case_manifest_rows(cases), paths["case_manifest_csv"])
    atomic_write_text(
        paths["summary_md"],
        _summary_markdown(
            cases=cases,
            results=results,
            effect_rows=effect_rows,
            trace_rows=trace_rows,
            agents=agent_names,
            replicates=replicates,
            run_tests=run_tests,
            use_git_workspaces=use_git_workspaces,
        ),
    )

    render_figure_success_rate(results, paths["figure_success"])
    render_figure_failure_modes(results, paths["figure_failure_modes"])
    render_figure_trace_flow(results, paths["figure_trace_flow"])

    print(
        f"rq5 experiment complete: cases={len(cases)} runs={len(results)} agents={agent_names}",
        flush=True,
    )
    return paths
