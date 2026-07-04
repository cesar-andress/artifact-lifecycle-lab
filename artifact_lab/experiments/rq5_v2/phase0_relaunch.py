"""Prepare Phase 0 relaunch from repaired manifest (no agent execution)."""

from __future__ import annotations

import csv
import json
from io import StringIO
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.rq5_v2.manifest import case_to_dict, load_case_manifest, write_run_plan_csv
from artifact_lab.experiments.rq5_v2.models import FactorialCase
from artifact_lab.experiments.rq5_v2.phase0_provenance import _sha256_file
from artifact_lab.experiments.rq5_v2.repo_tree import RepoTreeCache
from artifact_lab.experiments.rq5_v2.phase0_setup import (
    CLASSIFICATION_MINOR_SETUP,
    CLASSIFICATION_READY,
    CaseSetupSpec,
    build_case_setup_spec,
)

MIN_PHASE0_CASES = 20

DEFAULT_OUTPUT_DIR = Path("exports/rq5_v2_factorial")
REPAIRED_MANIFEST_NAME = "phase0_manifest_repaired.json"
ORIGINAL_MANIFEST_NAME = "factorial_case_manifest.json"
DEFAULT_REPAIRED_MANIFEST = DEFAULT_OUTPUT_DIR / REPAIRED_MANIFEST_NAME
DEFAULT_VIABILITY_CSV = DEFAULT_OUTPUT_DIR / "execution_viability.csv"
DEFAULT_CANDIDATES = Path("exports/rq5_v2/load_bearing_candidates.csv")


class RepairedManifestRequiredError(ValueError):
    """Raised when Phase 0 is invoked with the original (unrepaired) manifest."""


def is_repaired_manifest(path: Path) -> bool:
    return path.name == REPAIRED_MANIFEST_NAME


def assert_repaired_manifest(path: Path) -> str:
    """Validate manifest selection; return SHA-256 of manifest bytes."""
    resolved = path.resolve()
    if resolved.name == ORIGINAL_MANIFEST_NAME:
        raise RepairedManifestRequiredError(
            f"Phase 0 requires `{REPAIRED_MANIFEST_NAME}`; refusing original `{ORIGINAL_MANIFEST_NAME}`"
        )
    if not is_repaired_manifest(resolved):
        raise RepairedManifestRequiredError(
            f"Phase 0 requires `{REPAIRED_MANIFEST_NAME}`; got `{resolved.name}`"
        )
    if not resolved.is_file():
        raise FileNotFoundError(f"repaired manifest not found: {resolved}")
    return _sha256_file(resolved)


def load_viability_index(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["case_id"]: row for row in csv.DictReader(handle) if row.get("case_id")}


def build_setup_specs(
    *,
    cases: list[FactorialCase],
    viability_index: dict[str, dict[str, str]],
    tree_cache: RepoTreeCache | None = None,
) -> dict[str, CaseSetupSpec]:
    specs: dict[str, CaseSetupSpec] = {}
    for case in cases:
        row = viability_index.get(case.case_id, {})
        classification = row.get("classification", CLASSIFICATION_READY)
        execution_cwd = row.get("cwd") or case.execution_cwd or "."
        paths: set[str] | None = None
        if tree_cache is not None and classification == CLASSIFICATION_MINOR_SETUP:
            paths = tree_cache.paths_at(
                repo_id=case.repo_id,
                repo_url=case.repo_url,
                commit_sha=case.commit_sha,
            )
        specs[case.case_id] = build_case_setup_spec(
            case_id=case.case_id,
            repository=case.repository,
            classification=classification,
            execution_cwd=execution_cwd,
            paths=paths,
        )
    return specs


def build_replacement_pool(
    *,
    active_cases: list[FactorialCase],
    viability_index: dict[str, dict[str, str]],
    candidates_csv: Path,
    scratch_dir: Path,
    max_pool: int = 10,
) -> list[FactorialCase]:
    active_ids = {c.case_id for c in active_cases}
    spare_ids = [
        cid
        for cid, row in viability_index.items()
        if cid not in active_ids
        and row.get("classification") in {CLASSIFICATION_READY, CLASSIFICATION_MINOR_SETUP}
    ]
    pool: list[FactorialCase] = []
    if spare_ids:
        all_cases = load_case_manifest(DEFAULT_REPAIRED_MANIFEST) if DEFAULT_REPAIRED_MANIFEST.exists() else []
        by_id = {c.case_id: c for c in all_cases}
        for cid in spare_ids:
            if cid in by_id:
                pool.append(by_id[cid])
    needed = max(0, max_pool - len(pool))
    if needed:
        try:
            from artifact_lab.experiments.rq5_v2.phase0_execution_viability import _build_replacement_cases

            pool.extend(
                _build_replacement_cases(
                    existing=active_cases,
                    kept=active_cases + pool,
                    candidates_csv=candidates_csv,
                    scratch_dir=scratch_dir / "relaunch_pool",
                    needed=needed,
                    scan_multiplier=20,
                )
            )
        except RuntimeError:
            pass
    return pool[:max_pool]


def apply_setup_failures(
    *,
    active_cases: list[FactorialCase],
    setup_specs: dict[str, CaseSetupSpec],
    failed_case_ids: set[str],
    replacement_pool: list[FactorialCase],
    viability_index: dict[str, dict[str, str]],
) -> tuple[list[FactorialCase], dict[str, CaseSetupSpec], list[FactorialCase], list[str]]:
    """Drop setup_failed cases and pull validated replacements."""
    excluded = sorted(failed_case_ids)
    kept = [c for c in active_cases if c.case_id not in failed_case_ids]
    pool = list(replacement_pool)
    while len(kept) < MIN_PHASE0_CASES and pool:
        candidate = pool.pop(0)
        if any(c.case_id == candidate.case_id for c in kept):
            continue
        kept.append(candidate)
        row = viability_index.get(candidate.case_id, {})
        setup_specs[candidate.case_id] = build_case_setup_spec(
            case_id=candidate.case_id,
            repository=candidate.repository,
            classification=row.get("classification", CLASSIFICATION_READY),
            execution_cwd=row.get("cwd") or candidate.execution_cwd or ".",
        )
    if len(kept) < MIN_PHASE0_CASES:
        raise RuntimeError(
            f"setup failures left {len(kept)} cases; need {MIN_PHASE0_CASES} after replacements"
        )
    return kept[:MIN_PHASE0_CASES], setup_specs, pool, excluded


def write_case_setup_csv(*, path: Path, specs: dict[str, CaseSetupSpec]) -> None:
    buffer = StringIO()
    fields = ("case_id", "repository", "classification", "setup_command", "execution_cwd")
    writer = csv.DictWriter(buffer, fieldnames=list(fields))
    writer.writeheader()
    for spec in specs.values():
        writer.writerow(
            {
                "case_id": spec.case_id,
                "repository": spec.repository,
                "classification": spec.classification,
                "setup_command": spec.setup_command or "",
                "execution_cwd": spec.execution_cwd,
            }
        )
    atomic_write_text(path, buffer.getvalue())


def prepare_phase0_relaunch(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    manifest_path: Path = DEFAULT_REPAIRED_MANIFEST,
    viability_csv: Path = DEFAULT_VIABILITY_CSV,
    candidates_csv: Path = DEFAULT_CANDIDATES,
    scratch_dir: Path = Path("scratch"),
    seed: int = 42,
) -> dict[str, Path]:
    """Build Phase 0 run plan and setup registry from repaired manifest (no agents)."""
    from artifact_lab.experiments.rq5_v2.phase0_run import (
        PHASE0_EXPECTED_RUNS,
        build_phase0_plan,
        verify_phase0_preflight,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_sha = assert_repaired_manifest(manifest_path)
    cases = load_case_manifest(manifest_path)
    if len(cases) < MIN_PHASE0_CASES:
        raise RuntimeError(f"repaired manifest has {len(cases)} cases; need {MIN_PHASE0_CASES}")

    viability_index = load_viability_index(viability_csv)
    tree_cache = RepoTreeCache(scratch_dir=scratch_dir / "relaunch_setup", clone_prefix="relaunch_tree")
    active_cases = cases[:MIN_PHASE0_CASES]
    setup_specs = build_setup_specs(
        cases=active_cases,
        viability_index=viability_index,
        tree_cache=tree_cache,
    )
    replacement_pool = build_replacement_pool(
        active_cases=active_cases,
        viability_index=viability_index,
        candidates_csv=candidates_csv,
        scratch_dir=scratch_dir,
    )

    plan, config = build_phase0_plan(cases=active_cases, seed=seed)
    if len(plan) != PHASE0_EXPECTED_RUNS:
        raise RuntimeError(f"expected {PHASE0_EXPECTED_RUNS} runs, got {len(plan)}")

    plan_path = output_dir / "phase0_run_plan.csv"
    write_run_plan_csv(entries=plan, path=plan_path)

    setup_csv = output_dir / "phase0_case_setup.csv"
    write_case_setup_csv(path=setup_csv, specs=setup_specs)

    pool_path = output_dir / "phase0_replacement_pool.json"
    atomic_write_text(
        pool_path,
        json.dumps([case_to_dict(c) for c in replacement_pool], indent=2),
    )

    preflight = verify_phase0_preflight(
        plan=plan,
        config=config,
        results_csv=output_dir / "phase0_results.csv",
        traces_dir=output_dir / "phase0_traces",
        require_execute_env=False,
    )
    checks = dict(preflight.checks)
    checks["repaired_manifest_selected"] = True
    checks["manifest_hash_recorded"] = bool(manifest_sha and manifest_sha != "missing")

    relaunch_path = output_dir / "phase0_relaunch.json"
    relaunch_payload = {
        "manifest_path": str(manifest_path),
        "manifest_sha256": manifest_sha,
        "viability_csv": str(viability_csv),
        "case_count": len(active_cases),
        "run_count": len(plan),
        "cell": "T+L",
        "replicates": 3,
        "agent": "claude_code",
        "replacement_pool_size": len(replacement_pool),
        "setup_minor_count": sum(
            1 for s in setup_specs.values() if s.classification == CLASSIFICATION_MINOR_SETUP
        ),
        "preflight_checks": checks,
    }
    atomic_write_text(relaunch_path, json.dumps(relaunch_payload, indent=2))

    preflight_path = output_dir / "phase0_preflight.json"
    atomic_write_text(
        preflight_path,
        json.dumps(
            {
                "ok": preflight.ok,
                "checks": checks,
                "messages": preflight.messages,
                "manifest_sha256": manifest_sha,
            },
            indent=2,
        ),
    )

    summary_path = output_dir / "phase0_relaunch_summary.md"
    atomic_write_text(
        summary_path,
        "\n".join(
            [
                "# Phase 0 Relaunch (Prepared)",
                "",
                f"- **Manifest:** `{manifest_path}`",
                f"- **Manifest SHA-256:** `{manifest_sha}`",
                f"- **Cases:** {len(active_cases)}",
                f"- **Runs:** {len(plan)} (T+L × 3 × claude_code)",
                f"- **MINOR_SETUP (setup required):** {relaunch_payload['setup_minor_count']}",
                f"- **Replacement pool:** {len(replacement_pool)} cases",
                "",
                "**Not executed.** Run `make rq5-v2-phase0-run` only when ready.",
                "",
            ]
        ),
    )

    return {
        "run_plan_csv": plan_path,
        "case_setup_csv": setup_csv,
        "relaunch_json": relaunch_path,
        "replacement_pool_json": pool_path,
        "preflight_json": preflight_path,
        "summary_md": summary_path,
    }


def load_replacement_pool(path: Path) -> list[FactorialCase]:
    from artifact_lab.experiments.rq5_v2.manifest import case_from_dict

    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [case_from_dict(item) for item in data]


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Prepare Phase 0 relaunch from repaired manifest")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_REPAIRED_MANIFEST)
    parser.add_argument("--viability-csv", type=Path, default=DEFAULT_VIABILITY_CSV)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    paths = prepare_phase0_relaunch(
        output_dir=args.output_dir,
        manifest_path=args.manifest,
        viability_csv=args.viability_csv,
        seed=args.seed,
    )
    for label, path in paths.items():
        print(f"{label} -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
