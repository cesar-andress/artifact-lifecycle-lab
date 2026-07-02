"""Agent attribution join and maintenance regime classification for RQ3."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from artifact_lab.experiments.truth_pilots.p4_attribution_precision import categorize_signature

MaintenanceRegime = str  # human_only | agent_assisted | agent_dominated | unknown

AGENT_DOMINATED_THRESHOLD = 0.5


def load_attribution_index(candidates_csv: Path) -> dict[tuple[str, str, str], dict]:
    """Index attribution rows by (repo_id, instruction_path, commit_sha)."""
    index: dict[tuple[str, str, str], dict] = {}
    with candidates_csv.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            sha = row["commit_sha"].strip()
            key = (row["repo_id"], row["instruction_path"], sha)
            index[key] = row
    return index


def is_agent_maintenance(row: dict) -> bool:
    _, counts = categorize_signature(
        attribution_class=row.get("attribution_class", "human"),
        signature_type=row.get("signature_type", "none"),
        author_name=row.get("author_name", ""),
        author_email=row.get("author_email", ""),
        evidence=row.get("evidence", ""),
    )
    return counts


def classify_maintenance_regime(
    *,
    agent_commits: int,
    human_commits: int,
    unknown_commits: int,
) -> MaintenanceRegime:
    """File-level regime from commit attribution tallies (observational, not causal)."""
    labeled = agent_commits + human_commits
    if labeled == 0:
        return "unknown"
    share = agent_commits / labeled
    if share == 0:
        return "human_only"
    if share >= AGENT_DOMINATED_THRESHOLD:
        return "agent_dominated"
    return "agent_assisted"


def build_file_regimes(
    longitudinal_rows: list[dict],
    attribution_index: dict[tuple[str, str, str], dict],
) -> dict[tuple[str, str], MaintenanceRegime]:
    """Assign each instruction file a maintenance regime from its commit attribution mix."""
    commits_by_file: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in longitudinal_rows:
        if row.get("reference_removed"):
            continue
        key = (row["repo_id"], row["instruction_path"])
        commits_by_file[key].add(row["commit"])

    regimes: dict[tuple[str, str], MaintenanceRegime] = {}
    for file_key, commits in commits_by_file.items():
        agent_n = human_n = 0
        for commit in commits:
            att = attribution_index.get((file_key[0], file_key[1], commit))
            if att is None:
                continue
            if is_agent_maintenance(att):
                agent_n += 1
            elif att.get("attribution_class") == "human":
                human_n += 1
        unknown_n = len(commits) - agent_n - human_n
        regimes[file_key] = classify_maintenance_regime(
            agent_commits=agent_n,
            human_commits=human_n,
            unknown_commits=unknown_n,
        )
    return regimes


def lookup_commit_attribution(
    repo_id: str,
    instruction_path: str,
    commit_sha: str,
    attribution_index: dict[tuple[str, str, str], dict],
) -> dict | None:
    return attribution_index.get((repo_id, instruction_path, commit_sha))
