"""Run pre-scaling validation gates P3, P4, P5."""

from __future__ import annotations

from pathlib import Path

from artifact_lab.experiments.truth_pilots.gates_common import (
    DEFAULT_L1_PATHS,
    DEFAULT_PILOT_EXPORT,
    DEFAULT_RQ1_LONGITUDINAL,
)
from artifact_lab.experiments.truth_pilots.p3_rot_incidence import run_p3_rot_incidence_gate
from artifact_lab.experiments.truth_pilots.p4_attribution_precision import run_p4_attribution_precision_gate
from artifact_lab.experiments.truth_pilots.p5_human_baseline import run_p5_human_baseline_gate


def run_pre_scaling_gates(
    *,
    output_dir: Path = DEFAULT_PILOT_EXPORT,
    l1_paths: list[Path] | None = None,
    blobs_dir: Path = Path("data/blobs"),
    scratch_dir: Path = Path("scratch"),
    longitudinal_csv: Path = DEFAULT_RQ1_LONGITUDINAL,
    clone_timeout: int = 180,
) -> dict[str, Path]:
    l1 = l1_paths or [p for p in DEFAULT_L1_PATHS if p.exists() and (p.is_dir() or p.stat().st_size > 100)]
    p1_summary = output_dir / "reference_summary.csv"
    candidates = output_dir / "agent_commit_candidates.csv"

    outputs: dict[str, Path] = {}

    p3_md, p3_csv = run_p3_rot_incidence_gate(
        output_dir=output_dir,
        p1_summary_csv=p1_summary,
        longitudinal_csv=longitudinal_csv if longitudinal_csv.exists() else None,
        l1_paths=l1,
        blobs_dir=blobs_dir,
        scratch_dir=scratch_dir,
        clone_timeout=clone_timeout,
    )
    outputs["p3_report"] = p3_md
    outputs["p3_events"] = p3_csv

    p4_md, p4_csv = run_p4_attribution_precision_gate(
        output_dir=output_dir,
        candidates_csv=candidates,
    )
    outputs["p4_report"] = p4_md
    outputs["p4_worksheet"] = p4_csv

    p5_md, p5_csv = run_p5_human_baseline_gate(
        output_dir=output_dir,
        p1_summary_csv=p1_summary,
        machine_summary_csv=p1_summary,
        l1_paths=l1,
        scratch_dir=scratch_dir,
        clone_timeout=clone_timeout,
    )
    outputs["p5_report"] = p5_md
    outputs["p5_examples"] = p5_csv

    return outputs
