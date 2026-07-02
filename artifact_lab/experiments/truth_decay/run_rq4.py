"""RQ4 — multi-state lifecycle dynamics after birth."""

from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.truth_decay.rq4_figures import (
    render_figure_deletion_latency,
    render_figure_lifecycle_diagram,
    render_figure_repair_latency,
    render_figure_state_occupancy,
    render_figure_transition_matrix,
)
from artifact_lab.experiments.truth_decay.rq4_multistate import (
    build_multistate_table,
    build_reference_lifecycle_records,
    compute_state_occupancy,
    lifecycle_records_to_rows,
    transition_probability_rows,
    compute_phase_transitions,
    first_transition_probability_rows,
)
from artifact_lab.experiments.truth_pilots.gates_common import (
    DEFAULT_RQ1_LONGITUDINAL,
    load_longitudinal_rows,
)

DEFAULT_RQ4_EXPORT = Path("exports/truth_decay_pilot")


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
    n_trajectories: int,
    table_rows: list[dict],
    transition_rows: list[dict],
    first_rows: list[dict],
    occupancy_rows: list[dict],
) -> str:
    def _lat(latency_type: str, stat: str) -> str:
        for r in table_rows:
            if r.get("section") == "repair_latency" and r.get("latency_type") == latency_type and r.get("statistic") == stat:
                return str(r.get("value_days", "—"))
        for r in table_rows:
            if r.get("section") == "deletion_latency" and r.get("latency_type") == latency_type and r.get("statistic") == stat:
                return str(r.get("value_days", "—"))
        return "—"

    lines = [
        "# RQ4 — Lifecycle Dynamics After Birth",
        "",
        "## Research question",
        "",
        "**RQ4:** What are the lifecycle dynamics of machine-consumable specifications after birth?",
        "",
        "> This analysis models the reference panel as a **multi-state process**, not a survival",
        "> half-life. Primary estimands are **transition probabilities**, **state occupancy**,",
        "> and **latencies** between lifecycle phases.",
        "",
        "## Lifecycle model",
        "",
        "```",
        "Birth → Operational → Integrity loss → Repair → Deletion",
        "          ↘ Unverifiable (parallel branch at birth)",
        "```",
        "",
        "Mechanical observation states map to lifecycle phases:",
        "",
        "| Mechanical | Lifecycle phase |",
        "|------------|-----------------|",
        "| VERIFIED | operational |",
        "| MISSING | integrity_loss |",
        "| REPAIRED | repair |",
        "| DELETED | deletion |",
        "| UNVERIFIABLE | unverifiable |",
        "",
        f"- Reference trajectories: **{n_trajectories:,}**",
        "",
        "## First transition probabilities (at birth)",
        "",
        "| To phase | Count | P(to \\| birth) |",
        "|----------|------:|---------------:|",
    ]
    for r in first_rows:
        lines.append(f"| {r['to_phase']} | {r['count']:,} | {r['probability']:.3f} |")

    lines.extend(
        [
            "",
            "## Key transition probabilities (post-birth)",
            "",
            "| From | To | P(to \\| from) |",
            "|------|-----|--------------:|",
        ]
    )
    key_edges = [
        ("operational", "integrity_loss"),
        ("integrity_loss", "repair"),
        ("repair", "operational"),
        ("integrity_loss", "deletion"),
        ("operational", "deletion"),
    ]
    trans_lookup = {(r["from_phase"], r["to_phase"]): r for r in transition_rows}
    for a, b in key_edges:
        r = trans_lookup.get((a, b))
        if r:
            lines.append(f"| {a} | {b} | {r['probability']:.3f} |")

    lines.extend(
        [
            "",
            "## State occupancy (person-time)",
            "",
            "| Phase | Person-days | Proportion |",
            "|-------|------------:|-----------:|",
        ]
    )
    for r in occupancy_rows:
        lines.append(
            f"| {r['lifecycle_phase']} | {r['person_days']:,.0f} | {r['occupancy_proportion']:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Latencies (days)",
            "",
            "| Latency | n | Median | Mean | p90 |",
            "|---------|--:|-------:|-----:|----:|",
            f"| Integrity loss → repair | {_lat('integrity_loss_to_repair', 'n')} | "
            f"{_lat('integrity_loss_to_repair', 'median')} | {_lat('integrity_loss_to_repair', 'mean')} | "
            f"{_lat('integrity_loss_to_repair', 'p90')} |",
            f"| Birth → deletion | {_lat('birth_to_deletion', 'n')} | "
            f"{_lat('birth_to_deletion', 'median')} | {_lat('birth_to_deletion', 'mean')} | "
            f"{_lat('birth_to_deletion', 'p90')} |",
            f"| Operational → deletion | {_lat('operational_to_deletion', 'n')} | "
            f"{_lat('operational_to_deletion', 'median')} | {_lat('operational_to_deletion', 'mean')} | "
            f"{_lat('operational_to_deletion', 'p90')} |",
            "",
            "## Method notes",
            "",
            "- **No survival model as primary result** — RQ2 KM curves are complementary, not RQ4 headline.",
            "- Transition probabilities are **empirical row proportions** conditional on departing a phase.",
            "- State occupancy weights commit intervals; last observation contributes zero tail dwell.",
            "- Repair latency: first integrity_loss commit → first repair commit (REPAIRED phase).",
            "- Born-stale references enter at **integrity_loss** at birth; post-verification decay is a separate path.",
            "",
            "## Threats to validity",
            "",
            "1. **Irregular panel spacing:** commit-sampled observations under-estimate brief phases.",
            "2. **Mechanical states ≠ semantic lifecycle:** VERIFIED is tree membership only.",
            "3. **DELETED conflates file death and reference removal** from instruction text.",
            "4. **Repair detection:** MISSING→VERIFIED is labeled REPAIRED; silent fixes may be missed.",
            "5. **Born-stale mass:** ~80% of verifiable refs never reach operational; occupancy skews to integrity_loss.",
            "6. **No competing-risks adjustment:** transitions treated as nominal phase changes.",
            "7. **Pilot cohort selection** limits generalization.",
            "",
            "## Outputs",
            "",
            "- `rq4_multistate.csv` — trajectories + aggregate multi-state table",
            "- `figure_rq4_lifecycle_diagram.pdf`",
            "- `figure_rq4_transition_matrix.pdf`",
            "- `figure_rq4_state_occupancy.pdf`",
            "- `figure_rq4_repair_latency.pdf`",
            "- `figure_rq4_deletion_latency.pdf`",
            "",
        ]
    )
    return "\n".join(lines)


def run_rq4_lifecycle_analysis(
    *,
    longitudinal_csv: Path = DEFAULT_RQ1_LONGITUDINAL,
    output_dir: Path = DEFAULT_RQ4_EXPORT,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "multistate_csv": output_dir / "rq4_multistate.csv",
        "summary_md": output_dir / "rq4_summary.md",
        "fig_lifecycle": output_dir / "figure_rq4_lifecycle_diagram.pdf",
        "fig_transitions": output_dir / "figure_rq4_transition_matrix.pdf",
        "fig_occupancy": output_dir / "figure_rq4_state_occupancy.pdf",
        "fig_repair": output_dir / "figure_rq4_repair_latency.pdf",
        "fig_deletion": output_dir / "figure_rq4_deletion_latency.pdf",
    }

    rows = load_longitudinal_rows(longitudinal_csv)
    records = build_reference_lifecycle_records(rows)
    table_rows = build_multistate_table(rows, records)
    counts = compute_phase_transitions(rows)
    transition_rows = transition_probability_rows(counts)
    first_rows = first_transition_probability_rows(counts)
    occupancy_rows = compute_state_occupancy(rows)

    combined = lifecycle_records_to_rows(records) + table_rows
    _write_csv(combined, paths["multistate_csv"])
    atomic_write_text(
        paths["summary_md"],
        _summary_markdown(
            n_trajectories=len(records),
            table_rows=table_rows,
            transition_rows=transition_rows,
            first_rows=first_rows,
            occupancy_rows=occupancy_rows,
        ),
    )

    diagram_input = first_rows + transition_rows
    render_figure_lifecycle_diagram(diagram_input, paths["fig_lifecycle"])
    render_figure_transition_matrix(transition_rows, paths["fig_transitions"])
    render_figure_state_occupancy(occupancy_rows, paths["fig_occupancy"])
    render_figure_repair_latency(records, paths["fig_repair"])
    render_figure_deletion_latency(records, paths["fig_deletion"])

    return paths
