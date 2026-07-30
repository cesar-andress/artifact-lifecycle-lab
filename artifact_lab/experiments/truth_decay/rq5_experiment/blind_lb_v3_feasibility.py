"""RQ5 v1 → annotation-instrument v3 feasibility audit.

Determines whether any of the 35 RQ5 v1 cases admit a construct-valid
blind load-bearing annotation with an *independent* task oracle.

Does not generate distributable packets.
Does not classify scientific load-bearing labels.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from artifact_lab.experiments.truth_decay.rq5_experiment.blind_lb_packet import (
    DEFAULT_SEED,
    stable_neutral_id,
)

DEFAULT_MANIFEST = Path("exports/rq5_agent_impact/rq5_case_manifest.csv")
DEFAULT_CANDIDATES = Path("exports/truth_decay_pilot/rq5_candidate_dataset.csv")
DEFAULT_OUTPUT = Path("exports/rq5_lb_blind_annotation/v3_feasibility")
DEFAULT_ID_MAP = Path("exports/rq5_lb_blind_annotation/private/id_map.sealed.json")

# Generic prompt used for all RQ5 v1 cases — not an independent oracle.
GENERIC_INSTRUCTION_COUPLED_PROMPT = (
    "Complete the bounded coding task described in the project instruction file"
)

NON_SE_REPO_MARKERS = {
    "affiliate-skills": "affiliate_content_skill_pack",
}

ECOSYSTEM_HINTS: list[tuple[str, str]] = [
    (r"\.py$|pytest|pyproject|prefect|dagster|pydantic|physicsnemo|fastmcp", "python"),
    (r"\.ts$|\.tsx$|\.js$|package\.json|wp-calypso|dify|copilotkit|next\.js|vscode", "javascript_typescript"),
    (r"\.go$|go\.mod|stratus-red-team", "go"),
    (r"\.swift$|xcode", "swift"),
    (r"\.java$|\.kt$|gradle", "jvm"),
    (r"\.rs$|cargo", "rust"),
    (r"affiliate|content.?calendar|commission", "content_skill_markdown"),
]


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def load_candidate_index(path: Path) -> dict[tuple[str, str, str], dict[str, str]]:
    index: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in load_csv(path):
        if row.get("snapshot_type") != "born_stale":
            continue
        key = (row["repo_id"], row["instruction_path"], row["anchor_reference"])
        index[key] = row
    return index


def load_neutral_ids(id_map_path: Path, *, seed: int, case_ids: list[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    if id_map_path.exists():
        data = json.loads(id_map_path.read_text(encoding="utf-8"))
        for entry in data.get("entries", []):
            mapping[entry["case_id"]] = entry["neutral_id"]
    for case_id in case_ids:
        mapping.setdefault(case_id, stable_neutral_id(case_id, seed=seed))
    return mapping


def infer_ecosystem(repo_name: str, instruction_path: str, anchor: str) -> str:
    blob = f"{repo_name} {instruction_path} {anchor}".lower()
    for pattern, eco in ECOSYSTEM_HINTS:
        if re.search(pattern, blob, flags=re.I):
            return eco
    return "unknown"


def infer_repo_type(repo_name: str, ecosystem: str) -> str:
    if repo_name in NON_SE_REPO_MARKERS:
        return "content_skill_pack"
    if ecosystem == "content_skill_markdown":
        return "content_skill_pack"
    if ecosystem != "unknown":
        return "software_repository"
    return "uncertain"


def is_genuine_se_task(task_oracle_source: str, repo_type: str, task_text: str) -> bool:
    """Operational SE gate — requires independent oracle AND SE substance."""
    if task_oracle_source in {
        "",
        "none",
        "instruction_file",
        "instruction_derived_summary",
        "generic_instruction_coupled_prompt",
    }:
        return False
    if repo_type == "content_skill_pack":
        return False
    text = (task_text or "").lower()
    non_se = (
        "social media",
        "affiliate",
        "commission",
        "content calendar",
        "atomiz",
        "copywriting",
        "marketing campaign",
    )
    if any(x in text for x in non_se) and not any(
        y in text for y in ("fix", "implement", "test", "build", "debug", "refactor")
    ):
        return False
    se_cues = (
        "implement",
        "fix",
        "bug",
        "test",
        "build",
        "deploy",
        "refactor",
        "debug",
        "configure",
        "failing",
        "compile",
        "lint",
        "migrate",
    )
    return any(cue in text for cue in se_cues)


def classify_task_oracle(row: dict[str, str], candidate: dict[str, str] | None) -> dict[str, str]:
    """Return oracle metadata. RQ5 v1 has no independent stored oracle."""
    prompt = row.get("task_prompt", "")
    # Candidate issue/task flags are heuristics over the instruction, not GitHub issues.
    cand_task = (candidate or {}).get("task_availability", "")
    cand_task_reason = (candidate or {}).get("task_availability_reason", "")
    cand_issue = (candidate or {}).get("issue_availability", "")
    cand_issue_reason = (candidate or {}).get("issue_availability_reason", "")

    independent_artifact_on_disk = False
    # Explicitly reject candidate heuristic flags as oracles.
    if GENERIC_INSTRUCTION_COUPLED_PROMPT.lower() in prompt.lower():
        source = "generic_instruction_coupled_prompt"
        text = prompt.strip()
        independent = False
        independence_note = (
            "Manifest task_prompt is DEFAULT_TASK_PROMPT coupled to the project instruction file; "
            "not an issue/PR/failing-test/benchmark oracle."
        )
    else:
        source = "unknown_prompt"
        text = prompt.strip()
        independent = False
        independence_note = "Unrecognized prompt; no independent oracle artifact located."

    return {
        "task_oracle_source": source,
        "task_oracle_text": text,
        "task_oracle_independent_of_instruction": "false",
        "task_oracle_predates_or_independent": "false",
        "candidate_task_availability_flag": cand_task,
        "candidate_task_availability_reason": cand_task_reason,
        "candidate_issue_availability_flag": cand_issue,
        "candidate_issue_availability_reason": cand_issue_reason,
        "candidate_flags_are_independent_oracles": "false",
        "independent_task_oracle_artifact_on_disk": "true" if independent_artifact_on_disk else "false",
        "task_oracle_independence_note": independence_note,
        "has_independent_task_oracle": "true" if independent else "false",
    }


def classify_circularity(oracle: dict[str, str]) -> dict[str, str]:
    if oracle["has_independent_task_oracle"] != "true":
        return {
            "circularity_class": "circular",
            "circularity_evidence": (
                "Task definition is the generic instruction-coupled prompt and/or would disappear "
                "if the treated instruction were removed; no independent issue/PR/test/benchmark oracle. "
                f"oracle_source={oracle['task_oracle_source']}; "
                f"note={oracle['task_oracle_independence_note']}"
            ),
        }
    return {
        "circularity_class": "independent",
        "circularity_evidence": "Independent task oracle recorded.",
    }


def classify_reidentification(repo_url: str, instruction_path: str, anchor: str) -> dict[str, str]:
    repo_name = repo_url.rstrip("/").split("/")[-1]
    owner = repo_url.rstrip("/").split("/")[-2] if "/" in repo_url.rstrip("/") else ""
    identifiers = []
    for label, value, cls in [
        ("repo_name", repo_name, "necessary_but_identifying"),
        ("owner", owner, "necessary_but_identifying"),
        ("repo_url", repo_url, "non_redactable" if repo_url else "generic_and_safe"),
        ("instruction_path", instruction_path, "aliasable_without_semantic_loss"),
        ("anchor", anchor, "aliasable_without_semantic_loss" if len(anchor) >= 3 else "uncertain"),
    ]:
        identifiers.append(f"{label}:{cls}:{value}")

    distinctive = {
        "wp-calypso",
        "dify",
        "copilotkit",
        "prefect",
        "dagster",
        "vscode",
        "next.js",
        "affiliate-skills",
        "automattic",
        "stratus-red-team",
        "physicsnemo",
        "pydantic-ai",
        "fastmcp",
        "newspack-workspace",
        "ayaya_miliastra_editor",
        "2030ai-claudecode-allecosystem-sync",
    }
    critical = repo_name.lower() in distinctive or any(
        d in instruction_path.lower() or d in anchor.lower() for d in distinctive
    )
    # Without an independent task, anonymization cannot rescue eligibility; still record risk.
    if critical:
        risk = "unresolved_critical"
        anonymizable = "false"
        note = (
            "Repository/ecosystem names are highly distinctive; tree/docs typically retain "
            "re-identifying tokens even after name redaction (adversarial search likely succeeds)."
        )
    else:
        risk = "uncertain"
        anonymizable = "uncertain"
        note = "Re-identification risk not cleared; requires adversarial packet test if ever packetized."

    return {
        "reidentification_risk": risk,
        "repository_identity_anonymizable": anonymizable,
        "identifier_classifications": "|".join(identifiers),
        "reidentification_note": note,
    }


def assess_r1_presentability(anchor: str, anchor_type: str) -> dict[str, str]:
    """Conservative assessment without claiming absence in rater text."""
    # Short/numeric/dir stubs and absolute host paths are usually not safely presentable.
    a = anchor.strip()
    if not a:
        return {
            "r1_exists_in_pinned_snapshot": "uncertain",
            "r1_content_safely_presentable": "false",
            "substitutability_context_sufficient": "false",
            "r1_presentability_reason": "referenced_artifact_unavailable",
        }
    if a in {"1/", "2/"} or a.startswith("cd ") or a.startswith("/etc/"):
        return {
            "r1_exists_in_pinned_snapshot": "uncertain",
            "r1_content_safely_presentable": "false",
            "substitutability_context_sufficient": "false",
            "r1_presentability_reason": "referenced_artifact_not_safely_presentable",
        }
    if a.startswith("@") or a.endswith("/") and len(a) <= 5:
        return {
            "r1_exists_in_pinned_snapshot": "uncertain",
            "r1_content_safely_presentable": "false",
            "substitutability_context_sufficient": "false",
            "r1_presentability_reason": "referenced_artifact_not_safely_presentable",
        }
    # Default for v1 audit: even if file-like, R1 presentability is moot without independent task.
    return {
        "r1_exists_in_pinned_snapshot": "uncertain",
        "r1_content_safely_presentable": "uncertain",
        "substitutability_context_sufficient": "uncertain",
        "r1_presentability_reason": "not_assessed_past_oracle_gate",
    }


def eligibility_verdict(row: dict[str, str]) -> tuple[str, str]:
    """Gate order: independent oracle → SE → circularity → R1 → anonymization."""
    if row["has_independent_task_oracle"] != "true":
        return "ineligible", "no_independent_task_oracle"
    if row["is_genuine_software_engineering_task"] != "true":
        return "ineligible", "not_software_engineering_task"
    if row["circularity_class"] != "independent":
        return "ineligible", f"circularity_{row['circularity_class']}"
    if row["r1_content_safely_presentable"] != "true":
        return "ineligible", row.get("r1_presentability_reason") or "referenced_artifact_not_safely_presentable"
    if row["substitutability_context_sufficient"] != "true":
        return "ineligible", "insufficient_substitutability_context"
    if row["repository_identity_anonymizable"] != "true":
        return "ineligible", "repository_not_anonymizable"
    if row["reidentification_risk"] == "unresolved_critical":
        return "ineligible", "unresolved_critical_reidentification_risk"
    return "eligible", "passes_all_v3_gates"


def audit_case(
    row: dict[str, str],
    *,
    candidate: dict[str, str] | None,
    neutral_id: str,
) -> dict[str, str]:
    repo_url = row.get("repo_url", "")
    repo_name = repo_url.rstrip("/").split("/")[-1]
    instruction_path = row.get("instruction_path", "")
    anchor = row.get("anchor_reference", "")
    anchor_type = row.get("anchor_reference_type", "")
    ecosystem = infer_ecosystem(repo_name, instruction_path, anchor)
    repo_type = infer_repo_type(repo_name, ecosystem)
    oracle = classify_task_oracle(row, candidate)
    se = is_genuine_se_task(
        oracle["task_oracle_source"],
        repo_type,
        oracle["task_oracle_text"],
    )
    circ = classify_circularity(oracle)
    reid = classify_reidentification(repo_url, instruction_path, anchor)
    r1 = assess_r1_presentability(anchor, anchor_type)

    out: dict[str, str] = {
        "neutral_id": neutral_id,
        "case_id_internal": row["case_id"],
        "pinned_commit_sha": row.get("task_commit_sha", ""),
        "repo_id": row.get("repo_id", ""),
        "repo_name_internal": repo_name,
        "repository_type": repo_type,
        "primary_ecosystem": ecosystem,
        "instruction_path_internal": instruction_path,
        "referenced_artifact_r1_internal": anchor,
        "r1_reference_type": anchor_type,
        "experimental_selection_pool": "born_stale_confirmed_false_with_truthful_pair",
        "protocol_condition_pool": (candidate or {}).get("protocol_condition", ""),
        "confirmed_false": row.get("confirmed_false", ""),
        "is_genuine_software_engineering_task": "true" if se else "false",
        "sufficient_repository_context_presentable": "uncertain",
        **oracle,
        **circ,
        **reid,
        **r1,
    }
    status, reason = eligibility_verdict(out)
    out["eligibility_verdict"] = status
    out["exclusion_reason"] = reason if status != "eligible" else ""
    out["eligible_boolean"] = "true" if status == "eligible" else "false"
    return out


REELigibility_FIELDS = [
    "neutral_id",
    "case_id_internal",
    "pinned_commit_sha",
    "repo_id",
    "repo_name_internal",
    "repository_type",
    "primary_ecosystem",
    "instruction_path_internal",
    "referenced_artifact_r1_internal",
    "r1_reference_type",
    "task_oracle_source",
    "task_oracle_text",
    "task_oracle_independent_of_instruction",
    "task_oracle_predates_or_independent",
    "has_independent_task_oracle",
    "independent_task_oracle_artifact_on_disk",
    "candidate_task_availability_flag",
    "candidate_task_availability_reason",
    "candidate_issue_availability_flag",
    "candidate_issue_availability_reason",
    "candidate_flags_are_independent_oracles",
    "is_genuine_software_engineering_task",
    "circularity_class",
    "r1_exists_in_pinned_snapshot",
    "r1_content_safely_presentable",
    "substitutability_context_sufficient",
    "sufficient_repository_context_presentable",
    "repository_identity_anonymizable",
    "reidentification_risk",
    "experimental_selection_pool",
    "protocol_condition_pool",
    "confirmed_false",
    "eligibility_verdict",
    "eligible_boolean",
    "exclusion_reason",
]

CIRCULARITY_FIELDS = [
    "neutral_id",
    "case_id_internal",
    "circularity_class",
    "task_oracle_source",
    "has_independent_task_oracle",
    "circularity_evidence",
]

REID_FIELDS = [
    "neutral_id",
    "case_id_internal",
    "repo_name_internal",
    "reidentification_risk",
    "repository_identity_anonymizable",
    "identifier_classifications",
    "reidentification_note",
]


def run_audit(
    *,
    manifest_path: Path = DEFAULT_MANIFEST,
    candidates_path: Path = DEFAULT_CANDIDATES,
    output_dir: Path = DEFAULT_OUTPUT,
    id_map_path: Path = DEFAULT_ID_MAP,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    rows = load_csv(manifest_path)
    candidates = load_candidate_index(candidates_path)
    neutral_ids = load_neutral_ids(
        id_map_path, seed=seed, case_ids=[r["case_id"] for r in rows]
    )

    audited: list[dict[str, str]] = []
    for row in rows:
        key = (row["repo_id"], row["instruction_path"], row["anchor_reference"])
        audited.append(
            audit_case(
                row,
                candidate=candidates.get(key),
                neutral_id=neutral_ids[row["case_id"]],
            )
        )

    write_csv(output_dir / "case_reeligibility_v3.csv", audited, REELigibility_FIELDS)
    write_csv(
        output_dir / "circularity_audit_v3.csv",
        audited,
        CIRCULARITY_FIELDS,
    )
    write_csv(
        output_dir / "reidentification_risk_v3.csv",
        audited,
        REID_FIELDS,
    )

    summary = summarize(audited)
    (output_dir / "feasibility_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def summarize(audited: list[dict[str, str]]) -> dict[str, Any]:
    n = len(audited)
    indep = sum(1 for r in audited if r["has_independent_task_oracle"] == "true")
    se = sum(1 for r in audited if r["is_genuine_software_engineering_task"] == "true")
    r1_ok = sum(1 for r in audited if r["r1_content_safely_presentable"] == "true")
    anon = sum(1 for r in audited if r["repository_identity_anonymizable"] == "true")
    circ_indep = sum(1 for r in audited if r["circularity_class"] == "independent")
    eligible = sum(1 for r in audited if r["eligible_boolean"] == "true")
    excl = Counter(r["exclusion_reason"] for r in audited if r["eligible_boolean"] != "true")
    repos = Counter(r["repo_name_internal"] for r in audited)
    repo_types = Counter(r["repository_type"] for r in audited)
    arms = Counter(r["protocol_condition_pool"] for r in audited)
    circularity = Counter(r["circularity_class"] for r in audited)

    if eligible >= 30 and indep == eligible:
        verdict = "FEASIBLE_AS_CONFIRMATORY_ANNOTATION"
    elif 1 <= eligible < 30:
        verdict = "FEASIBLE_ONLY_AS_EXPLORATORY_CASE_STUDY"
    else:
        verdict = "NOT_FEASIBLE_WITH_CURRENT_RQ5_V1_DATA"

    return {
        "n_manifest_cases": n,
        "n_independent_task_oracles": indep,
        "n_genuine_se_tasks": se,
        "n_circularity_independent": circ_indep,
        "n_r1_safely_presentable": r1_ok,
        "n_anonymizable": anon,
        "n_eligible_all_criteria": eligible,
        "exclusions_by_reason": dict(excl),
        "repository_cluster_counts": dict(repos),
        "repository_type_counts": dict(repo_types),
        "protocol_condition_pool_counts": dict(arms),
        "circularity_counts": dict(circularity),
        "feasibility_verdict": verdict,
        "note": (
            "RQ5 v1 selected born_stale confirmed_false pairs with a generic "
            "instruction-coupled task prompt; candidate issue/task flags are not "
            "independent oracles. A/B/C arms are runtime overlays on the same case pool."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="RQ5 v1 annotation instrument v3 feasibility audit")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--id-map", type=Path, default=DEFAULT_ID_MAP)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args(argv)
    summary = run_audit(
        manifest_path=args.manifest,
        candidates_path=args.candidates,
        output_dir=args.output_dir,
        id_map_path=args.id_map,
        seed=args.seed,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
