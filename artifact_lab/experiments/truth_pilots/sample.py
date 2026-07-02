"""Deterministic sampling of AI instruction files from existing L1 + L1b."""

from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pyarrow.parquet as pq

from artifact_lab.protocol.detector import is_matched_path, match_pattern_id

FAMILY_GROUPS: tuple[str, ...] = (
    "AGENTS.md",
    "CLAUDE.md",
    "Cursor rules",
    "Copilot instructions",
    "GitHub instructions",
    "Skills",
    "prompt files",
)

PATTERN_TO_GROUP: dict[str, str] = {
    "agents_md": "AGENTS.md",
    "agents_dir": "AGENTS.md",
    "claude_md": "CLAUDE.md",
    "cursor_rules": "Cursor rules",
    "cursorrules": "Cursor rules",
    "copilot_instructions": "Copilot instructions",
    "github_instructions": "GitHub instructions",
    "skill_md": "Skills",
    "prompts": "prompt files",
}


@dataclass(frozen=True)
class InstructionSample:
    sample_id: int
    repo_id: str
    repo_url: str
    instruction_path: str
    family_group: str
    pattern_id: str
    blob_sha: str
    commit_sha: str
    commit_time: datetime
    extraction_wave: str
    l1_source: str


@dataclass(frozen=True)
class InstructionCommit:
    repo_id: str
    repo_url: str
    instruction_path: str
    family_group: str
    commit_sha: str
    commit_time: datetime
    author_name: str
    l1_source: str


def family_group_for_path(path: str, *, family: str = "ai_conventions_v1") -> str | None:
    pattern_id = match_pattern_id(path, family)
    if pattern_id is None:
        return None
    return PATTERN_TO_GROUP.get(pattern_id)


def _parse_commit_time(value: object) -> datetime:
    if isinstance(value, datetime):
        return value
    if hasattr(value, "isoformat"):
        return value.to_pydatetime()  # type: ignore[union-attr]
    text = str(value)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    return datetime.fromisoformat(text)


def load_instruction_candidates(
    l1_paths: list[Path],
    *,
    family: str = "ai_conventions_v1",
) -> list[dict]:
    """Latest L1 row per (repo_id, path) with non-empty blob_sha."""
    latest: dict[tuple[str, str], dict] = {}
    for l1_path in l1_paths:
        path = l1_path.resolve()
        if path.is_dir():
            parquet = path / "events.parquet"
            if not parquet.exists():
                continue
            table = pq.read_table(parquet)
        elif path.exists():
            table = pq.read_table(path)
        else:
            continue
        source_label = str(path)
        for row in table.to_pylist():
            blob_sha = (row.get("blob_sha") or "").strip()
            if not blob_sha:
                continue
            instr_path = row["path"]
            if not is_matched_path(instr_path, family):
                continue
            key = (row["repo_id"], instr_path)
            commit_time = _parse_commit_time(row["commit_time"])
            existing = latest.get(key)
            if existing is None or commit_time > existing["_commit_time"]:
                latest[key] = {**row, "_commit_time": commit_time, "_l1_source": source_label}
    return list(latest.values())


def load_instruction_commits_from_l1(
    l1_paths: list[Path],
    *,
    family: str = "ai_conventions_v1",
) -> list[InstructionCommit]:
    """All L1 events for instruction paths (deduped by repo, path, commit)."""
    seen: set[tuple[str, str, str]] = set()
    commits: list[InstructionCommit] = []
    for l1_path in l1_paths:
        path = l1_path.resolve()
        if path.is_dir():
            parquet = path / "events.parquet"
            if not parquet.exists():
                continue
            table = pq.read_table(parquet)
        elif path.exists():
            table = pq.read_table(path)
        else:
            continue
        source_label = str(path)
        for row in table.to_pylist():
            instr_path = row["path"]
            if not is_matched_path(instr_path, family):
                continue
            key = (row["repo_id"], row["commit_sha"], instr_path)
            if key in seen:
                continue
            seen.add(key)
            group = family_group_for_path(instr_path, family=family)
            commits.append(
                InstructionCommit(
                    repo_id=row["repo_id"],
                    repo_url=row["repo_url"],
                    instruction_path=instr_path,
                    family_group=group or "",
                    commit_sha=row["commit_sha"],
                    commit_time=_parse_commit_time(row["commit_time"]),
                    author_name=row.get("author_name") or "",
                    l1_source=source_label,
                )
            )
    return commits


def sample_instruction_files(
    l1_paths: list[Path],
    *,
    n: int = 400,
    n_min: int = 300,
    n_max: int = 500,
    seed: int = 42,
    family: str = "ai_conventions_v1",
    stratified: bool = True,
) -> list[InstructionSample]:
    candidates = load_instruction_candidates(l1_paths, family=family)
    if not candidates:
        return []

    if stratified:
        chosen = _sample_stratified(candidates, n=n, n_min=n_min, n_max=n_max, seed=seed, family=family)
    else:
        rng = random.Random(seed)
        n_target = min(n_max, len(candidates)) if len(candidates) > n_max else max(n_min, len(candidates))
        chosen = candidates if len(candidates) <= n_target else rng.sample(candidates, n_target)

    chosen.sort(key=lambda row: (row["repo_id"], row["path"]))
    samples: list[InstructionSample] = []
    for index, row in enumerate(chosen, start=1):
        pattern_id = match_pattern_id(row["path"], family) or ""
        group = family_group_for_path(row["path"], family=family) or ""
        samples.append(
            InstructionSample(
                sample_id=index,
                repo_id=row["repo_id"],
                repo_url=row["repo_url"],
                instruction_path=row["path"],
                family_group=group,
                pattern_id=pattern_id,
                blob_sha=row["blob_sha"],
                commit_sha=row["commit_sha"],
                commit_time=row["_commit_time"],
                extraction_wave=row.get("extraction_wave", ""),
                l1_source=row["_l1_source"],
            )
        )
    return samples


def _sample_stratified(
    candidates: list[dict],
    *,
    n: int,
    n_min: int,
    n_max: int,
    seed: int,
    family: str,
) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in candidates:
        group = family_group_for_path(row["path"], family=family)
        if group:
            grouped[group].append(row)

    active_groups = [g for g in FAMILY_GROUPS if grouped[g]]
    if not active_groups:
        return candidates[: min(n_max, len(candidates))]

    pool_size = len(candidates)
    n_target = min(n_max, max(n_min, n)) if pool_size >= n_min else pool_size
    n_target = min(n_target, pool_size)

    rng = random.Random(seed)
    chosen: list[dict] = []
    per_group = max(1, n_target // len(active_groups))
    for group in FAMILY_GROUPS:
        bucket = grouped.get(group, [])
        if not bucket:
            continue
        take = min(len(bucket), per_group)
        chosen.extend(rng.sample(bucket, take) if len(bucket) > take else list(bucket))

    chosen_ids = {id(c) for c in chosen}
    remaining = [c for c in candidates if id(c) not in chosen_ids]
    if len(chosen) < n_target and remaining:
        need = n_target - len(chosen)
        chosen.extend(rng.sample(remaining, min(need, len(remaining))))

    chosen = chosen[:n_target]
    chosen.sort(key=lambda row: (row["repo_id"], row["path"]))
    return chosen
