"""Cited vs uncited path churn contrast."""

from __future__ import annotations

import random
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from artifact_lab.experiments.truth_decay.audit_statistics import bootstrap_mean_ci
from artifact_lab.experiments.truth_decay.verify_at_commit import CommitTreeCache
from artifact_lab.ingest.git_utils import clone_bare, remove_clone, run_git
from artifact_lab.experiments.truth_pilots.gates_common import load_longitudinal_rows

FILE_REFERENCE_TYPES = frozenset({"path", "script_name"})
SKIP_REFERENCE = re.compile(r"[\*\?\<\>\{\}|]|^https?://|^node:|^path/to/|\s")


@dataclass(frozen=True)
class PathChurnPair:
    repo_id: str
    repo_url: str
    cited_path: str
    uncited_path: str
    panel_start_commit: str
    panel_end_commit: str
    cited_churn_commits: int
    uncited_churn_commits: int
    cited_verified_rate: float
    match_extension: str
    match_depth: int


@dataclass(frozen=True)
class ChurnContrastStatistics:
    n_pairs: int
    n_repos: int
    cited_mean_churn: float
    uncited_mean_churn: float
    cited_mean_churn_ci_low: float
    cited_mean_churn_ci_high: float
    uncited_mean_churn_ci_low: float
    uncited_mean_churn_ci_high: float
    mean_difference: float
    mean_difference_ci_low: float
    mean_difference_ci_high: float
    cited_more_stable_fraction: float
    cited_more_stable_ci_low: float
    cited_more_stable_ci_high: float
    cited_mean_verified_rate: float


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _path_depth(path: str) -> int:
    return len([p for p in path.strip("/").split("/") if p])


def _path_extension(path: str) -> str:
    if "." not in path.rstrip("/"):
        return ""
    return path.rstrip("/").rsplit(".", 1)[-1].lower()


def _eligible_cited_reference(reference: str, reference_type: str) -> bool:
    if reference_type not in FILE_REFERENCE_TYPES:
        return False
    if not reference or SKIP_REFERENCE.search(reference):
        return False
    if reference.endswith("/"):
        return False
    return True


def collect_cited_path_trajectories(
    longitudinal_rows: list[dict],
) -> dict[tuple[str, str], dict]:
    """Map (repo_id, reference) -> panel metadata and verification stats."""
    trajectories: dict[tuple[str, str], dict] = {}
    for row in longitudinal_rows:
        if not _eligible_cited_reference(row["reference"], row["reference_type"]):
            continue
        key = (row["repo_id"], row["reference"])
        entry = trajectories.setdefault(
            key,
            {
                "repo_url": row["repo_url"],
                "commits": [],
                "commit_times": [],
                "verified": 0,
                "total": 0,
            },
        )
        if row.get("reference_removed"):
            continue
        entry["total"] += 1
        if row.get("state") == "VERIFIED":
            entry["verified"] += 1
        entry["commits"].append(row["commit"])
        entry["commit_times"].append(row["commit_time"])

    for entry in trajectories.values():
        if entry["commits"]:
            pairs = sorted(zip(entry["commit_times"], entry["commits"]))
            entry["panel_start_commit"] = pairs[0][1]
            entry["panel_end_commit"] = pairs[-1][1]
            entry["panel_start_time"] = pairs[0][0]
            entry["panel_end_time"] = pairs[-1][0]
            entry["verified_rate"] = entry["verified"] / entry["total"] if entry["total"] else 0.0
    return trajectories


def _repo_panel_bounds(longitudinal_rows: list[dict]) -> dict[str, tuple[str, str]]:
    bounds: dict[str, list[str]] = defaultdict(list)
    for row in longitudinal_rows:
        bounds[row["repo_id"]].append(row["commit_time"])
    out: dict[str, tuple[str, str]] = {}
    for repo_id, times in bounds.items():
        ordered = sorted(times)
        out[repo_id] = (ordered[0], ordered[-1])
    return out


def _churn_in_window(
    repo_dir: Path,
    path: str,
    *,
    start_commit: str,
    end_commit: str,
    timeout: int = 120,
) -> int:
    proc = run_git(
        ["git", "log", "--follow", "--format=%H", f"{start_commit}^..{end_commit}", "--", path],
        cwd=repo_dir,
        timeout=timeout,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        proc = run_git(
            ["git", "log", "--follow", "--format=%H", f"{start_commit}..{end_commit}", "--", path],
            cwd=repo_dir,
            timeout=timeout,
        )
    if proc.returncode != 0:
        return 0
    return len({line.strip() for line in proc.stdout.splitlines() if line.strip()})


def _pick_uncited_control(
    *,
    tree_paths: set[str],
    cited_paths: set[str],
    target_path: str,
    rng: random.Random,
) -> str | None:
    ext = _path_extension(target_path)
    depth = _path_depth(target_path)
    candidates = [
        p
        for p in tree_paths
        if p not in cited_paths
        and _path_extension(p) == ext
        and abs(_path_depth(p) - depth) <= 1
        and not p.endswith("/")
        and not SKIP_REFERENCE.search(p)
    ]
    if not candidates:
        candidates = [
            p
            for p in tree_paths
            if p not in cited_paths
            and abs(_path_depth(p) - depth) <= 1
            and not p.endswith("/")
            and not SKIP_REFERENCE.search(p)
        ]
    if not candidates:
        return None
    return rng.choice(sorted(candidates))


def build_cited_uncited_pairs(
    *,
    longitudinal_csv: Path,
    scratch_dir: Path,
    max_cited_per_repo: int = 40,
    seed: int = 42,
    clone_timeout: int = 180,
) -> list[PathChurnPair]:
    rows = load_longitudinal_rows(longitudinal_csv)
    trajectories = collect_cited_path_trajectories(rows)
    by_repo: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for repo_id, reference in trajectories:
        by_repo[repo_id].append((repo_id, reference))

    rng = random.Random(seed)
    pairs: list[PathChurnPair] = []
    clone_cache: dict[str, Path] = {}
    tree_caches: dict[str, CommitTreeCache] = {}

    try:
        for repo_id, refs in sorted(by_repo.items()):
            sampled = refs
            if len(sampled) > max_cited_per_repo:
                sampled = rng.sample(refs, max_cited_per_repo)

            repo_url = trajectories[sampled[0]]["repo_url"]
            if repo_id not in clone_cache:
                clone_path = scratch_dir / f"churn_{repo_id}"
                clone_bare(repo_url, clone_path, timeout=clone_timeout)
                clone_cache[repo_id] = clone_path
                tree_caches[repo_id] = CommitTreeCache(clone_path, timeout=clone_timeout)

            repo_dir = clone_cache[repo_id]
            tree_cache = tree_caches[repo_id]
            cited_paths = {reference for _, reference in refs}

            for _, cited_path in sampled:
                meta = trajectories[(repo_id, cited_path)]
                anchor_commit = meta["panel_start_commit"]
                tree_paths = tree_cache.paths_at(anchor_commit)
                uncited = _pick_uncited_control(
                    tree_paths=tree_paths,
                    cited_paths=cited_paths,
                    target_path=cited_path,
                    rng=rng,
                )
                if not uncited:
                    continue
                cited_churn = _churn_in_window(
                    repo_dir,
                    cited_path,
                    start_commit=meta["panel_start_commit"],
                    end_commit=meta["panel_end_commit"],
                )
                uncited_churn = _churn_in_window(
                    repo_dir,
                    uncited,
                    start_commit=meta["panel_start_commit"],
                    end_commit=meta["panel_end_commit"],
                )
                pairs.append(
                    PathChurnPair(
                        repo_id=repo_id,
                        repo_url=repo_url,
                        cited_path=cited_path,
                        uncited_path=uncited,
                        panel_start_commit=meta["panel_start_commit"],
                        panel_end_commit=meta["panel_end_commit"],
                        cited_churn_commits=cited_churn,
                        uncited_churn_commits=uncited_churn,
                        cited_verified_rate=meta["verified_rate"],
                        match_extension=_path_extension(cited_path),
                        match_depth=_path_depth(cited_path),
                    )
                )
    finally:
        for clone_path in clone_cache.values():
            remove_clone(clone_path)

    return pairs


def compute_churn_contrast_statistics(pairs: list[PathChurnPair]) -> ChurnContrastStatistics:
    if not pairs:
        return ChurnContrastStatistics(
            n_pairs=0,
            n_repos=0,
            cited_mean_churn=0.0,
            uncited_mean_churn=0.0,
            cited_mean_churn_ci_low=0.0,
            cited_mean_churn_ci_high=0.0,
            uncited_mean_churn_ci_low=0.0,
            uncited_mean_churn_ci_high=0.0,
            mean_difference=0.0,
            mean_difference_ci_low=0.0,
            mean_difference_ci_high=0.0,
            cited_more_stable_fraction=0.0,
            cited_more_stable_ci_low=0.0,
            cited_more_stable_ci_high=0.0,
            cited_mean_verified_rate=0.0,
        )

    cited_vals = [float(p.cited_churn_commits) for p in pairs]
    uncited_vals = [float(p.uncited_churn_commits) for p in pairs]
    diffs = [c - u for c, u in zip(cited_vals, uncited_vals)]
    stable_flags = [1.0 if c <= u else 0.0 for c, u in zip(cited_vals, uncited_vals)]

    cited_mean, cited_lo, cited_hi = bootstrap_mean_ci(cited_vals)
    uncited_mean, uncited_lo, uncited_hi = bootstrap_mean_ci(uncited_vals)
    diff_mean, diff_lo, diff_hi = bootstrap_mean_ci(diffs)
    stable_mean, stable_lo, stable_hi = bootstrap_mean_ci(stable_flags)
    verified_mean = sum(p.cited_verified_rate for p in pairs) / len(pairs)

    return ChurnContrastStatistics(
        n_pairs=len(pairs),
        n_repos=len({p.repo_id for p in pairs}),
        cited_mean_churn=round(cited_mean, 4),
        uncited_mean_churn=round(uncited_mean, 4),
        cited_mean_churn_ci_low=round(cited_lo, 4),
        cited_mean_churn_ci_high=round(cited_hi, 4),
        uncited_mean_churn_ci_low=round(uncited_lo, 4),
        uncited_mean_churn_ci_high=round(uncited_hi, 4),
        mean_difference=round(diff_mean, 4),
        mean_difference_ci_low=round(diff_lo, 4),
        mean_difference_ci_high=round(diff_hi, 4),
        cited_more_stable_fraction=round(stable_mean, 4),
        cited_more_stable_ci_low=round(stable_lo, 4),
        cited_more_stable_ci_high=round(stable_hi, 4),
        cited_mean_verified_rate=round(verified_mean, 4),
    )
