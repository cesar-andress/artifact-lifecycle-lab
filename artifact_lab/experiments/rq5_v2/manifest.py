"""Manifest serialization for frozen RQ5 v2 experiment state."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from io import StringIO
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.rq5_v2.models import ExperimentConfig, FactorialCase, RunPlanEntry


def case_to_dict(case: FactorialCase) -> dict:
    payload = asdict(case)
    payload["cells"] = {code: asdict(cell) for code, cell in case.cells.items()}
    return payload


def case_from_dict(payload: dict) -> FactorialCase:
    from artifact_lab.experiments.rq5_v2.models import FactorialCell

    cells_raw = payload.pop("cells")
    cells = {code: FactorialCell(**cell) for code, cell in cells_raw.items()}
    payload.setdefault("execution_cwd", ".")
    return FactorialCase(cells=cells, **payload)


def write_case_manifest(*, cases: list[FactorialCase], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(path, json.dumps([case_to_dict(c) for c in cases], indent=2))


def load_case_manifest(path: Path) -> list[FactorialCase]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [case_from_dict(item) for item in data]


def write_config(*, config: ExperimentConfig, path: Path) -> None:
    atomic_write_text(path, json.dumps(asdict(config), indent=2))


def load_config(path: Path) -> ExperimentConfig:
    data = json.loads(path.read_text(encoding="utf-8"))
    return ExperimentConfig(**data)


def write_run_plan_csv(*, entries: list[RunPlanEntry], path: Path) -> None:
    if not entries:
        atomic_write_text(path, "")
        return
    rows = [asdict(e) for e in entries]
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    atomic_write_text(path, buffer.getvalue())


def load_run_plan_csv(path: Path) -> list[RunPlanEntry]:
    if not path.exists():
        return []
    entries: list[RunPlanEntry] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            entries.append(RunPlanEntry(**row))
    return entries


def write_experiment_bundle(
    *,
    cases: list[FactorialCase],
    plan: list[RunPlanEntry],
    config: ExperimentConfig,
    output_dir: Path,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "case_manifest": output_dir / "factorial_case_manifest.json",
        "run_plan_csv": output_dir / "run_plan.csv",
        "config_json": output_dir / "experiment_config.json",
        "summary_md": output_dir / "experiment_plan_summary.md",
    }
    write_case_manifest(cases=cases, path=paths["case_manifest"])
    write_run_plan_csv(entries=plan, path=paths["run_plan_csv"])
    write_config(config=config, path=paths["config_json"])
    atomic_write_text(
        paths["summary_md"],
        _plan_summary(cases=cases, plan=plan, config=config, output_dir=output_dir),
    )
    return paths


def _plan_summary(
    *,
    cases: list[FactorialCase],
    plan: list[RunPlanEntry],
    config: ExperimentConfig,
    output_dir: Path,
) -> str:
    repos = len({c.repository for c in cases})
    return "\n".join(
        [
            "# RQ5 v2 Factorial — Experiment Plan",
            "",
            "**Infrastructure only. No agent runs executed.**",
            "",
            f"- Protocol: `{config.protocol_version}`",
            f"- Cases: **{len(cases)}** ({repos} repositories)",
            f"- Cells per case: **{len(config.cells)}** ({', '.join(config.cells)})",
            f"- Agents: **{', '.join(config.agents)}**",
            f"- Replicates: **{config.replicates}**",
            f"- Planned runs: **{len(plan)}** (expected {config.expected_runs(len(cases))})",
            f"- Execute allowed: **{config.allow_execute}**",
            "",
            "## Factors",
            "",
            "| Factor | Levels |",
            "|--------|--------|",
            "| A — Instruction | present, absent |",
            "| B — Reference truth | truthful, false (when present) |",
            "| C — Load-bearing | yes, no (when present) |",
            "",
            "## Outputs",
            "",
            f"- `{output_dir / 'factorial_case_manifest.json'}`",
            f"- `{output_dir / 'run_plan.csv'}`",
            f"- `{output_dir / 'experiment_config.json'}`",
            "",
        ]
    )
