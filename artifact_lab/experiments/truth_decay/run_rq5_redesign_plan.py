"""Generate RQ5 A/B/C redesign plan from paused experiment data."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.truth_decay.rq5_experiment.task_selection import select_experiment_cases

DEFAULT_CANDIDATE_CSV = Path("exports/truth_decay_pilot/rq5_candidate_dataset.csv")
DEFAULT_GFC_CSV = Path("exports/truth_decay_pilot/gfc_confirmatory_audit.csv")
DEFAULT_OUTPUT = Path("exports/rq5_agent_impact/rq5_redesign_plan.md")
DEFAULT_RESULTS = Path("exports/rq5_agent_impact/rq5_results.csv")


def _load_run_summary(results_csv: Path) -> dict:
    if not results_csv.exists():
        return {
            "total_runs": 0,
            "by_condition": {},
            "cases": 0,
            "paired_ab": 0,
            "success_a": 0,
            "success_b": 0,
            "n_a": 0,
            "n_b": 0,
            "cost_usd": 0.0,
        }
    rows = list(csv.DictReader(results_csv.open()))
    by_cond = Counter(r["condition"] for r in rows)
    a_rows = [r for r in rows if r["condition"] == "A"]
    b_rows = [r for r in rows if r["condition"] == "B"]
    paired = len(
        set((r["case_id"], r["replicate_id"]) for r in a_rows)
        & set((r["case_id"], r["replicate_id"]) for r in b_rows)
    )
    return {
        "total_runs": len(rows),
        "by_condition": dict(by_cond),
        "cases": len(set(r["case_id"] for r in rows)),
        "paired_ab": paired,
        "success_a": sum(1 for r in a_rows if r["success"] in ("True", "true", "1")),
        "success_b": sum(1 for r in b_rows if r["success"] in ("True", "true", "1")),
        "n_a": len(a_rows),
        "n_b": len(b_rows),
        "cost_usd": round(sum(float(r.get("cost_usd") or 0) for r in rows), 2),
    }


def generate_rq5_redesign_plan(
    *,
    candidate_csv: Path = DEFAULT_CANDIDATE_CSV,
    gfc_confirmatory_csv: Path = DEFAULT_GFC_CSV,
    results_csv: Path = DEFAULT_RESULTS,
    output_path: Path = DEFAULT_OUTPUT,
    replicates: int = 3,
    agents: int = 1,
) -> Path:
    cases = select_experiment_cases(
        candidate_csv=candidate_csv,
        gfc_confirmatory_csv=gfc_confirmatory_csv,
        results_csv_for_traces=results_csv if results_csv.exists() else None,
    )
    summary = _load_run_summary(results_csv)

    strata = Counter(c.load_bearing_stratum for c in cases)
    n_cases = len(cases)
    n_conditions_abc = 3
    total_new_c = n_cases * replicates * agents
    total_full_abc = n_cases * n_conditions_abc * replicates * agents
    reusable_ab = summary["total_runs"]
    new_c_only = total_new_c
    remaining_ab = max(0, (n_cases * 2 * replicates * agents) - reusable_ab)

    load_bearing_cases = sum(1 for c in cases if c.load_bearing_stratum == "load_bearing")
    peripheral_cases = sum(1 for c in cases if c.load_bearing_stratum == "peripheral")

    min_cases_per_stratum = 12
    min_replicates = 3
    min_runs_abc = n_cases * 3 * min_replicates * agents
    min_runs_stratified = max(min_cases_per_stratum, load_bearing_cases) * 3 * min_replicates * agents
    min_runs_stratified += max(min_cases_per_stratum, peripheral_cases) * 3 * min_replicates * agents

    lines = [
        "# RQ5 Redesign Plan — A/B/C with Load-Bearing Strata",
        "",
        "**Status:** Experiment paused at partial A/B execution; do not resume A/B-only runs without Condition C.",
        "",
        "## Why the current A/B design is insufficient",
        "",
        f"- Partial results ({summary['total_runs']} runs, {summary['cases']} cases) show **near-null aggregate difference**: "
        f"success A={summary['success_a']}/{summary['n_a']} vs B={summary['success_b']}/{summary['n_b']}.",
        "- A null A−B result is **uninterpretable** without a no-instruction baseline: we cannot distinguish",
        "  (i) instruction truth having no effect from (ii) agents ignoring instructions entirely.",
        "- Task failure rates are high in both conditions (~87%), suggesting instruction content may not be the binding constraint.",
        "- Without Condition C, observed A≈B could mean false claims are peripheral, not load-bearing.",
        "",
        "## How A/B/C fixes the inference problem",
        "",
        "| Condition | Treatment | Identifies |",
        "|-----------|-----------|------------|",
        "| **A** | Truthful instruction | Upper bound when agents read and follow docs |",
        "| **B** | Confirmed-false instruction | Cost of false content *given instruction presence* |",
        "| **C** | No instruction / file removed | Baseline without machine-consumed doc |",
        "",
        "Primary contrasts:",
        "- **A − C:** effect of providing *any* truthful instruction vs none.",
        "- **B − C:** effect of providing a false instruction vs none.",
        "- **A − B:** effect of instruction *truth* holding presence fixed.",
        "",
        "Optional strata (pre-registered, not post-hoc):",
        "- **Load-bearing:** anchor on task-critical path (issue cue + verified-reference task coupling).",
        "- **Peripheral:** stale reference unlikely to bind agent behavior.",
        "",
        "Hypothesis ordering:",
        "1. If B≈C and A>C → false instructions ignored; truth matters only via presence.",
        "2. If B<C and A≈B≈C → false claims peripheral.",
        "3. If B<C and A>C → load-bearing false claims impose cost beyond missing instructions.",
        "",
        "## Candidate selection (current corpus)",
        "",
        f"- Total confirmed-false cases: **{n_cases}**",
        f"- Load-bearing stratum: **{strata.get('load_bearing', 0)}**",
        f"- Peripheral stratum: **{strata.get('peripheral', 0)}**",
        f"- Unknown stratum: **{strata.get('unknown', 0)}**",
        "",
        "Load-bearing flags use task/issue availability metadata plus partial trace uptake from completed runs.",
        "",
        "## Minimum sample size (pilot guidance)",
        "",
        f"- Full A/B/C matrix: **{n_cases} cases × 3 conditions × {replicates} replicates × {agents} agent(s) = {total_full_abc} runs**.",
        f"- Minimum for stratified pilot (≥{min_cases_per_stratum} cases per stratum): **≈{min_runs_stratified} runs**.",
        f"- McNemar / paired bootstrap on A−B requires **≥3 paired replicates** per case (already specified).",
        "- Condition C adds **50% more runs** vs A/B-only design but is required for identifiability.",
        "",
        "## Existing runs that can be reused",
        "",
        f"- **Reusable A/B runs:** {reusable_ab} ({summary.get('by_condition', {})})",
        f"- **Paired A/B replicates:** {summary['paired_ab']}",
        f"- **Cases with partial coverage:** {summary['cases']} / {n_cases}",
        f"- **Spend to date (partial):** ${summary['cost_usd']}",
        "",
        "Reuse policy:",
        "- Condition **A** and **B** runs in `rq5_results.csv` remain valid under frozen protocol (same commit, task, tests).",
        "- Do **not** discard; mark as `design_version=AB_v1` when merging into A/B/C analysis.",
        "- Condition **C** runs are **entirely new** (instruction file absent).",
        "",
        "## New runs required",
        "",
        f"- **Condition C only (complete current case set):** {new_c_only} runs",
        f"- **Remaining A/B to finish AB_v1 matrix:** up to {remaining_ab} runs (if completing all {n_cases} cases before pivot)",
        f"- **Recommended pivot:** stop new A/B-only runs; collect **{new_c_only}** Condition C runs + stratified top-up to {min_cases_per_stratum} cases per stratum.",
        "",
        "## Implementation status",
        "",
        "- Protocol updated: `protocol/RQ5_AGENT_IMPACT_EXPERIMENT_v1.md` (v1.1 A/B/C)",
        "- Runner supports Condition C via instruction file removal (`workspace.py`)",
        "- Default runner conditions remain **A/B only**; C is opt-in via `--conditions A B C`",
        "- Load-bearing flags on `ExperimentCase`: `load_bearing_stratum`, `likely_load_bearing`",
        "",
        "## Next steps (manual)",
        "",
        "1. Review stratum counts; optionally prune to balanced load-bearing/peripheral panels.",
        "2. Run Condition C only: `rq5-run --conditions C --no-resume` (separate results file recommended).",
        "3. Analyze A−C, B−C, A−B with paired/cluster bootstrap; stratify by load_bearing_stratum.",
        "4. Do not interpret AB_v1 null result as evidence of no effect.",
        "",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(output_path, "\n".join(lines))
    return output_path
