"""Export task difficulty calibration scores and distribution figure."""

from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.task_calibration.figures import render_difficulty_distribution
from artifact_lab.experiments.task_calibration.historical import (
    historical_training_rows,
    load_historical_index,
    lookup_historical,
)
from artifact_lab.experiments.task_calibration.model import (
    CalibratorParams,
    calibration_tier,
    composite_difficulty,
    fit_calibrator,
    predict_success,
    recalibrate_to_target_band,
)
from artifact_lab.experiments.task_calibration.scoring import (
    TaskFeatures,
    extract_test_command_from_task,
    score_all_dimensions,
)

DEFAULT_CALIBRATION_EXPORT = Path("exports/task_calibration")
DEFAULT_CANDIDATES_CSV = Path("exports/rq5_v2/load_bearing_candidates.csv")
DEFAULT_RQ5_RESULTS = Path("exports/rq5_agent_impact/rq5_results.csv")
DEFAULT_RQ5_MANIFEST = Path("exports/rq5_agent_impact/rq5_case_manifest.csv")
DEFAULT_RQ5_FAILURE_MODES = Path("exports/rq5_agent_impact/rq5_failure_modes.csv")


def _write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        atomic_write_text(path, "")
        return
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()), extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    atomic_write_text(path, buffer.getvalue())


def _load_candidates(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _summary_md(
    *,
    params: CalibratorParams,
    rows: list[dict],
    output_dir: Path,
    historical_n: int,
    v1_mean_success: float,
) -> str:
    tiers = {t: sum(1 for r in rows if r["calibration_tier"] == t) for t in ("target_band", "too_hard", "too_easy")}
    mean_cal = sum(float(r["calibrated_expected_success"]) for r in rows) / len(rows) if rows else 0.0
    mean_target = (
        sum(float(r["calibrated_expected_success"]) for r in rows if r["calibration_tier"] == "target_band")
        / tiers["target_band"]
        if tiers["target_band"]
        else 0.0
    )

    return "\n".join(
        [
            "# Task Difficulty Calibration",
            "",
            "Pre-inclusion scoring pipeline for RQ5 v2. **No agent runs.**",
            "",
            f"- Candidates scored: **{len(rows)}**",
            f"- Historical training cases (RQ5 v1): **{historical_n}**",
            f"- v1 observed mean success: **{v1_mean_success:.1%}** (too low; target 40–60%)",
            f"- Calibrated mean expected success (all): **{mean_cal:.1%}**",
            f"- Mean in target band: **{mean_target:.1%}** (n={tiers['target_band']})",
            "",
            "## Inclusion tiers",
            "",
            f"| Tier | Count | Definition |",
            f"|------|------:|------------|",
            f"| target_band | {tiers['target_band']} | Expected success ∈ [0.40, 0.60] |",
            f"| too_hard | {tiers['too_hard']} | Expected success < 0.40 |",
            f"| too_easy | {tiers['too_easy']} | Expected success > 0.60 |",
            "",
            "## Scoring dimensions (0 = easy, 1 = hard)",
            "",
            "1. **Compilation complexity** — build toolchain, monorepo, scoped packages",
            "2. **Edited files estimate** — role, path type, v1 median files modified",
            "3. **Test complexity** — test command tier, e2e paths, monorepo tests",
            "4. **Dependency depth** — path depth, dependency anchors",
            "5. **Historical failures** — case/spec/repo success from RQ5 v1 pilot",
            "",
            "## Calibrator",
            "",
            f"- Weights: `{params.weights}`",
            f"- Logistic intercept: **{params.logistic_intercept:.3f}**",
            f"- Logistic slope: **{params.logistic_slope:.3f}**",
            f"- Training Brier score: **{params.training_brier:.4f}** (n={params.training_n})",
            "",
            "## Outputs",
            "",
            f"- `{output_dir / 'difficulty_scores.csv'}`",
            f"- `{output_dir / 'difficulty_distribution.pdf'}`",
            "",
            "Use `calibration_tier == target_band` rows for Phase 0 calibration pilot.",
            "",
        ]
    )


def run_task_calibration(
    *,
    candidates_csv: Path = DEFAULT_CANDIDATES_CSV,
    results_csv: Path = DEFAULT_RQ5_RESULTS,
    manifest_csv: Path = DEFAULT_RQ5_MANIFEST,
    failure_modes_csv: Path = DEFAULT_RQ5_FAILURE_MODES,
    output_dir: Path = DEFAULT_CALIBRATION_EXPORT,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "scores_csv": output_dir / "difficulty_scores.csv",
        "distribution_pdf": output_dir / "difficulty_distribution.pdf",
        "summary_md": output_dir / "calibration_summary.md",
    }

    history = load_historical_index(
        results_csv=results_csv,
        manifest_csv=manifest_csv,
        failure_modes_csv=failure_modes_csv,
    )
    training = historical_training_rows(history)
    params = fit_calibrator(training)

    v1_mean_success = (
        sum(c.success_rate for c in history.cases) / len(history.cases) if history.cases else 0.0
    )
    historical_success = [c.success_rate for c in history.cases]

    candidates = _load_candidates(candidates_csv)
    export_rows: list[dict] = []

    for row in candidates:
        test_command = extract_test_command_from_task(row.get("task", ""))
        features = TaskFeatures(
            repository=row.get("repository", ""),
            reference=row.get("reference", ""),
            instruction_path=row.get("instruction_path", ""),
            reference_type=row.get("reference_type", "path"),
            role=row.get("role", "edit"),
            test_command=test_command,
            context_snippet=row.get("context_snippet", ""),
            repo_id=row.get("repo_id", ""),
        )

        case_sr, spec_sr, repo_sr, median_files = lookup_historical(
            history,
            repo_id=features.repo_id,
            instruction_path=features.instruction_path,
            anchor_reference=features.reference,
        )

        dims = score_all_dimensions(
            features,
            historical_median_files=median_files,
            case_success_rate=case_sr,
            repo_success_rate=repo_sr,
            spec_success_rate=spec_sr,
            global_failure_rate=history.global_failure_rate,
        )
        composite = composite_difficulty(dims, weights=params.weights)
        raw_success = predict_success(composite, params)
        calibrated = recalibrate_to_target_band(raw_success, composite=composite, params=params)
        tier = calibration_tier(calibrated)

        export_rows.append(
            {
                "candidate_id": row.get("candidate_id", ""),
                "repository": features.repository,
                "reference": features.reference,
                "instruction_path": features.instruction_path,
                "role": features.role,
                "test_command": test_command,
                "compilation_complexity": round(dims.compilation_complexity, 4),
                "edited_files_estimate": round(dims.edited_files_estimate, 4),
                "test_complexity": round(dims.test_complexity, 4),
                "dependency_depth": round(dims.dependency_depth, 4),
                "historical_failure_rate": round(dims.historical_failure_rate, 4),
                "composite_difficulty": round(composite, 4),
                "raw_logistic_success": round(raw_success, 4),
                "calibrated_expected_success": round(calibrated, 4),
                "calibration_tier": tier,
                "prior_estimated_success_rate": row.get("estimated_success_rate", ""),
                "historical_match": (
                    "case"
                    if case_sr is not None
                    else ("spec" if spec_sr is not None else ("repo" if repo_sr is not None else "global"))
                ),
                "recommended_for_pilot": tier == "target_band",
            }
        )

    export_rows.sort(
        key=lambda r: (
            r["calibration_tier"] != "target_band",
            -float(r["calibrated_expected_success"]),
            r["repository"],
        )
    )

    _write_csv(export_rows, paths["scores_csv"])
    render_difficulty_distribution(
        rows=export_rows,
        path=paths["distribution_pdf"],
        historical_success=historical_success,
    )
    atomic_write_text(
        paths["summary_md"],
        _summary_md(
            params=params,
            rows=export_rows,
            output_dir=output_dir,
            historical_n=len(history.cases),
            v1_mean_success=v1_mean_success,
        ),
    )
    return paths
