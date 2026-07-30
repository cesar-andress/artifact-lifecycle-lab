"""Matched observational study: referenced paths vs comparable repo controls."""

from __future__ import annotations

import math
import random
import subprocess
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from artifact_lab.experiments.truth_decay.audit_statistics import (
    bootstrap_mean_ci,
    paired_cohens_d,
    permutation_test_sign_flip,
)
from artifact_lab.experiments.truth_decay.cited_uncited_churn import (
    SKIP_REFERENCE,
    collect_cited_path_trajectories,
)
from artifact_lab.experiments.truth_decay.verify_at_commit import CommitTreeCache
from artifact_lab.ingest.git_utils import clone_bare, remove_clone, run_git
from artifact_lab.experiments.truth_pilots.gates_common import load_longitudinal_rows

METRIC_CHURN = "churn_commits"
METRIC_LIFETIME = "lifetime_days"
METRIC_RENAME = "rename_count"
METRIC_DELETION = "deletion"
METRIC_SURVIVAL = "survival_panel_end"

METRIC_LABELS = {
    METRIC_CHURN: "Commit churn (panel window)",
    METRIC_LIFETIME: "Active lifetime (days, panel window)",
    METRIC_RENAME: "Rename events (panel window)",
    METRIC_DELETION: "Deletion before panel end",
    METRIC_SURVIVAL: "Survival until panel end",
}

# Lower diff favors referenced stability for churn/rename/deletion; higher for lifetime/survival.
STABILITY_DIRECTION = {
    METRIC_CHURN: "lower",
    METRIC_LIFETIME: "higher",
    METRIC_RENAME: "lower",
    METRIC_DELETION: "lower",
    METRIC_SURVIVAL: "higher",
}


@dataclass(frozen=True)
class PathFeatures:
    path: str
    extension: str
    depth: int
    size_bytes: int | None
    creation_ts: int | None


@dataclass(frozen=True)
class PathPanelMetrics:
    lifetime_days: float
    churn_commits: int
    rename_count: int
    deleted: bool
    survived_panel: bool


@dataclass(frozen=True)
class PanelActivityCatalog:
    """Per-path git activity within a panel window (built from one repo-wide log)."""

    churn_commits: dict[str, int]
    last_touch_ts: dict[str, int]
    rename_count: dict[str, int]


@dataclass(frozen=True)
class SelectionMatchPair:
    repo_id: str
    repo_url: str
    referenced_path: str
    control_path: str
    panel_start_commit: str
    panel_end_commit: str
    panel_start_time: str
    panel_end_time: str
    panel_duration_days: float
    match_extension: str
    match_depth_diff: int
    match_size_ratio: float | None
    match_creation_days_diff: float | None
    match_score: float
    ref_lifetime_days: float
    ref_churn_commits: int
    ref_rename_count: int
    ref_deleted: bool
    ref_survived_panel: bool
    ctrl_lifetime_days: float
    ctrl_churn_commits: int
    ctrl_rename_count: int
    ctrl_deleted: bool
    ctrl_survived_panel: bool


@dataclass(frozen=True)
class MetricEffectEstimate:
    metric: str
    n_pairs: int
    referenced_mean: float
    control_mean: float
    mean_difference: float
    mean_difference_ci_low: float
    mean_difference_ci_high: float
    cohens_d: float
    permutation_p_value: float
    referenced_favorable_fraction: float
    referenced_favorable_ci_low: float
    referenced_favorable_ci_high: float
    alternative: str


@dataclass
class SelectionStudyStatistics:
    n_pairs: int
    n_repos: int
    metrics: list[MetricEffectEstimate] = field(default_factory=list)


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _path_depth(path: str) -> int:
    return len([p for p in path.strip("/").split("/") if p])


def _path_extension(path: str) -> str:
    if "." not in path.rstrip("/"):
        return ""
    return path.rstrip("/").rsplit(".", 1)[-1].lower()


def _panel_duration_days(start_time: str, end_time: str) -> float:
    delta = _parse_time(end_time) - _parse_time(start_time)
    return max(delta.total_seconds() / 86400.0, 0.0)


def _tree_sizes_at_commit(
    repo_dir: Path,
    commit_sha: str,
    *,
    timeout: int = 120,
) -> dict[str, int] | None:
    proc = _git_call(
        ["git", "ls-tree", "-r", "-l", commit_sha],
        repo_dir,
        timeout=timeout,
    )
    if proc is None or proc.returncode != 0:
        return None
    sizes: dict[str, int] = {}
    for line in proc.stdout.splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        try:
            sizes[parts[-1]] = int(parts[3])
        except ValueError:
            continue
    return sizes


def _file_size_at_commit(
    repo_dir: Path,
    commit_sha: str,
    path: str,
    *,
    size_index: dict[str, int] | None = None,
    timeout: int = 60,
) -> int | None:
    if size_index is not None:
        return size_index.get(path)
    proc = run_git(
        ["git", "ls-tree", "-l", commit_sha, "--", path],
        cwd=repo_dir,
        timeout=timeout,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    parts = proc.stdout.strip().split()
    if len(parts) < 4:
        return None
    try:
        return int(parts[3])
    except ValueError:
        return None


CREATION_TIMEOUT = 45
METRICS_TIMEOUT = 90


def _git_call(args: list[str], repo_dir: Path, *, timeout: int) -> subprocess.CompletedProcess[str] | None:
    try:
        return run_git(args, cwd=repo_dir, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None


def _build_creation_index(
    repo_dir: Path,
    *,
    timeout: int = CREATION_TIMEOUT,
) -> dict[str, int]:
    """Map path -> unix timestamp of first add (reverse git log, one call per repo)."""
    proc = _git_call(
        [
            "git",
            "log",
            "--all",
            "--diff-filter=A",
            "--name-only",
            "--format=%at",
            "--reverse",
        ],
        repo_dir,
        timeout=timeout,
    )
    if proc is None or proc.returncode != 0 or not proc.stdout.strip():
        return {}
    index: dict[str, int] = {}
    current_ts: int | None = None
    for line in proc.stdout.splitlines():
        stripped = line.strip()
        if not stripped:
            current_ts = None
            continue
        try:
            current_ts = int(stripped)
            continue
        except ValueError:
            pass
        if current_ts is not None and stripped not in index:
            index[stripped] = current_ts
    return index


def _creation_timestamp(
    repo_dir: Path,
    path: str,
    *,
    cache: dict[str, int | None],
    creation_index: dict[str, int] | None = None,
    timeout: int = CREATION_TIMEOUT,
) -> int | None:
    if creation_index is not None and path in creation_index:
        return creation_index[path]
    if path in cache:
        return cache[path]
    proc = _git_call(
        ["git", "log", "--diff-filter=A", "--follow", "--format=%at", "--", path],
        repo_dir,
        timeout=timeout,
    )
    if proc is None or proc.returncode != 0 or not proc.stdout.strip():
        cache[path] = None
        return None
    try:
        ts = int(proc.stdout.strip().splitlines()[-1].strip())
    except (ValueError, IndexError):
        cache[path] = None
        return None
    cache[path] = ts
    return ts


def _path_features(
    repo_dir: Path,
    path: str,
    anchor_commit: str,
    *,
    creation_cache: dict[str, int | None],
    creation_index: dict[str, int] | None = None,
    timeout: int = 120,
) -> PathFeatures:
    return PathFeatures(
        path=path,
        extension=_path_extension(path),
        depth=_path_depth(path),
        size_bytes=_file_size_at_commit(repo_dir, anchor_commit, path, timeout=timeout),
        creation_ts=_creation_timestamp(
            repo_dir,
            path,
            cache=creation_cache,
            creation_index=creation_index,
            timeout=timeout,
        ),
    )


def _match_score(reference: PathFeatures, candidate: PathFeatures) -> float:
    depth_penalty = abs(reference.depth - candidate.depth) * 2.0
    if reference.size_bytes is not None and candidate.size_bytes is not None:
        size_penalty = abs(
            math.log1p(reference.size_bytes) - math.log1p(candidate.size_bytes)
        )
    else:
        size_penalty = 3.0
    if reference.creation_ts is not None and candidate.creation_ts is not None:
        age_penalty = abs(reference.creation_ts - candidate.creation_ts) / (86400.0 * 30.0)
    else:
        age_penalty = 6.0
    return depth_penalty + size_penalty + age_penalty


def _match_metadata(reference: PathFeatures, candidate: PathFeatures) -> tuple[int, float | None, float | None, float]:
    size_ratio: float | None = None
    if reference.size_bytes and candidate.size_bytes and candidate.size_bytes > 0:
        size_ratio = reference.size_bytes / candidate.size_bytes
    creation_diff: float | None = None
    if reference.creation_ts is not None and candidate.creation_ts is not None:
        creation_diff = abs(reference.creation_ts - candidate.creation_ts) / 86400.0
    return (
        abs(reference.depth - candidate.depth),
        size_ratio,
        creation_diff,
        _match_score(reference, candidate),
    )


def _activity_in_window(
    repo_dir: Path,
    path: str,
    *,
    start_commit: str,
    end_commit: str,
    timeout: int = METRICS_TIMEOUT,
) -> tuple[int, int | None]:
    """Return (churn_commits, last_touch_unix_ts) within the panel window."""
    rev_range = f"{start_commit}^..{end_commit}"
    proc = _git_call(
        ["git", "log", "--format=%H|%at", rev_range, "--", path],
        repo_dir,
        timeout=timeout,
    )
    if proc is None or proc.returncode != 0 or not proc.stdout.strip():
        rev_range = f"{start_commit}..{end_commit}"
        proc = _git_call(
            ["git", "log", "--format=%H|%at", rev_range, "--", path],
            repo_dir,
            timeout=timeout,
        )
    if proc is None or proc.returncode != 0 or not proc.stdout.strip():
        return 0, None
    commits: set[str] = set()
    timestamps: list[int] = []
    for line in proc.stdout.splitlines():
        if "|" not in line:
            continue
        sha, ts_raw = line.split("|", 1)
        sha = sha.strip()
        if not sha:
            continue
        commits.add(sha)
        try:
            timestamps.append(int(ts_raw.strip()))
        except ValueError:
            continue
    return len(commits), (max(timestamps) if timestamps else None)


def _churn_in_window(
    repo_dir: Path,
    path: str,
    *,
    start_commit: str,
    end_commit: str,
    timeout: int = 120,
) -> int:
    churn, _ = _activity_in_window(
        repo_dir,
        path,
        start_commit=start_commit,
        end_commit=end_commit,
        timeout=timeout,
    )
    return churn


def _rename_count_in_window(
    repo_dir: Path,
    path: str,
    *,
    start_commit: str,
    end_commit: str,
    timeout: int = METRICS_TIMEOUT,
) -> int:
    proc = _git_call(
        [
            "git",
            "log",
            "--name-status",
            f"{start_commit}^..{end_commit}",
            "--format=",
            "--",
            path,
        ],
        repo_dir,
        timeout=timeout,
    )
    if proc is None or proc.returncode != 0 or not proc.stdout.strip():
        proc = _git_call(
            [
                "git",
                "log",
                "--name-status",
                f"{start_commit}..{end_commit}",
                "--format=",
                "--",
                path,
            ],
            repo_dir,
            timeout=timeout,
        )
    if proc is None or proc.returncode != 0:
        return 0
    return sum(1 for line in proc.stdout.splitlines() if line.startswith("R"))


def _last_touch_ts_in_window(
    repo_dir: Path,
    path: str,
    *,
    start_commit: str,
    end_commit: str,
    timeout: int = 120,
) -> int | None:
    _, last_ts = _activity_in_window(
        repo_dir,
        path,
        start_commit=start_commit,
        end_commit=end_commit,
        timeout=timeout,
    )
    return last_ts


def _build_panel_activity_catalog(
    repo_dir: Path,
    *,
    start_commit: str,
    end_commit: str,
    timeout: int = METRICS_TIMEOUT,
) -> PanelActivityCatalog:
    """Build per-path churn/rename/touch stats from one repo-wide panel log."""
    commit_sets: dict[str, set[str]] = defaultdict(set)
    last_touch: dict[str, int] = {}
    renames: dict[str, int] = defaultdict(int)

    for rev_range in (f"{start_commit}^..{end_commit}", f"{start_commit}..{end_commit}"):
        proc = _git_call(
            [
                "git",
                "log",
                "--name-status",
                f"--format=COMMIT:%H|%at",
                rev_range,
            ],
            repo_dir,
            timeout=timeout,
        )
        if proc is None or proc.returncode != 0 or not proc.stdout.strip():
            continue

        current_sha: str | None = None
        current_ts: int | None = None
        for line in proc.stdout.splitlines():
            if line.startswith("COMMIT:"):
                payload = line[len("COMMIT:") :]
                if "|" not in payload:
                    continue
                sha, ts_raw = payload.split("|", 1)
                current_sha = sha.strip()
                try:
                    current_ts = int(ts_raw.strip())
                except ValueError:
                    current_ts = None
                continue
            if not line.strip() or current_sha is None or current_ts is None:
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            status = parts[0]
            if status.startswith("R") and len(parts) >= 3:
                old_path, new_path = parts[1], parts[2]
                for touched in (old_path, new_path):
                    commit_sets[touched].add(current_sha)
                    last_touch[touched] = max(last_touch.get(touched, 0), current_ts)
                    renames[touched] += 1
            else:
                path = parts[-1]
                commit_sets[path].add(current_sha)
                last_touch[path] = max(last_touch.get(path, 0), current_ts)
        break

    return PanelActivityCatalog(
        churn_commits={path: len(shas) for path, shas in commit_sets.items()},
        last_touch_ts=last_touch,
        rename_count=dict(renames),
    )


def _path_panel_metrics_from_catalog(
    path: str,
    *,
    catalog: PanelActivityCatalog,
    panel_start_time: str,
    panel_end_time: str,
    panel_duration_days: float,
    tree_at_end: set[str],
) -> PathPanelMetrics:
    survived = path in tree_at_end
    deleted = not survived
    churn = catalog.churn_commits.get(path, 0)
    renames = catalog.rename_count.get(path, 0) if churn > 0 else 0
    last_ts = catalog.last_touch_ts.get(path)
    start_dt = _parse_time(panel_start_time)
    end_dt = _parse_time(panel_end_time)
    if last_ts is not None:
        last_dt = datetime.fromtimestamp(last_ts, tz=start_dt.tzinfo)
        lifetime = max((last_dt - start_dt).total_seconds() / 86400.0, 0.0)
    elif survived:
        lifetime = panel_duration_days
    else:
        lifetime = panel_duration_days * 0.5
    lifetime = min(lifetime, (end_dt - start_dt).total_seconds() / 86400.0)
    return PathPanelMetrics(
        lifetime_days=round(lifetime, 4),
        churn_commits=churn,
        rename_count=renames,
        deleted=deleted,
        survived_panel=survived,
    )


def _candidate_pool(
    *,
    tree_paths: set[str],
    cited_paths: set[str],
    target: PathFeatures,
) -> list[str]:
    candidates = [
        p
        for p in tree_paths
        if p not in cited_paths
        and _path_extension(p) == target.extension
        and abs(_path_depth(p) - target.depth) <= 1
        and not p.endswith("/")
        and not SKIP_REFERENCE.search(p)
    ]
    if candidates:
        return sorted(candidates)
    return sorted(
        p
        for p in tree_paths
        if p not in cited_paths
        and abs(_path_depth(p) - target.depth) <= 1
        and not p.endswith("/")
        and not SKIP_REFERENCE.search(p)
    )


def _passes_caliper(reference: PathFeatures, candidate: PathFeatures) -> bool:
    if reference.creation_ts is not None and candidate.creation_ts is not None:
        age_days = abs(reference.creation_ts - candidate.creation_ts) / 86400.0
        if age_days > 365.0:
            return False
    if (
        reference.size_bytes is not None
        and candidate.size_bytes is not None
        and reference.size_bytes > 0
        and candidate.size_bytes > 0
    ):
        ratio = reference.size_bytes / candidate.size_bytes
        if ratio < 0.1 or ratio > 10.0:
            return False
    return True


def _cached_path_features(
    repo_dir: Path,
    path: str,
    anchor_commit: str,
    *,
    creation_cache: dict[str, int | None],
    feature_cache: dict[tuple[str, str], PathFeatures],
    creation_index: dict[str, int] | None = None,
    size_index: dict[str, int] | None = None,
    timeout: int = 120,
) -> PathFeatures:
    key = (anchor_commit, path)
    if key not in feature_cache:
        feature_cache[key] = PathFeatures(
            path=path,
            extension=_path_extension(path),
            depth=_path_depth(path),
            size_bytes=_file_size_at_commit(
                repo_dir,
                anchor_commit,
                path,
                size_index=size_index,
                timeout=timeout,
            ),
            creation_ts=_creation_timestamp(
                repo_dir,
                path,
                cache=creation_cache,
                creation_index=creation_index,
                timeout=timeout,
            ),
        )
    return feature_cache[key]


def _match_score_without_age(reference: PathFeatures, candidate: PathFeatures) -> float:
    depth_penalty = abs(reference.depth - candidate.depth) * 2.0
    if reference.size_bytes is not None and candidate.size_bytes is not None:
        size_penalty = abs(
            math.log1p(reference.size_bytes) - math.log1p(candidate.size_bytes)
        )
    else:
        size_penalty = 3.0
    return depth_penalty + size_penalty


def _pick_matched_control(
    *,
    repo_dir: Path,
    tree_paths: set[str],
    cited_paths: set[str],
    target: PathFeatures,
    anchor_commit: str,
    creation_cache: dict[str, int | None],
    feature_cache: dict[tuple[str, str], PathFeatures],
    creation_index: dict[str, int] | None = None,
    size_index: dict[str, int] | None,
    used_controls: set[str],
    rng: random.Random,
    timeout: int = 120,
    shortlist_size: int = 10,
) -> PathFeatures | None:
    pool = [
        p
        for p in _candidate_pool(tree_paths=tree_paths, cited_paths=cited_paths, target=target)
        if p not in used_controls
    ]
    if not pool:
        return None
    if len(pool) > 100:
        pool = rng.sample(sorted(pool), 100)

    shortlist: list[tuple[float, str]] = []
    for candidate_path in pool:
        if size_index is not None:
            size_bytes = size_index.get(candidate_path)
            provisional = PathFeatures(
                path=candidate_path,
                extension=_path_extension(candidate_path),
                depth=_path_depth(candidate_path),
                size_bytes=size_bytes,
                creation_ts=None,
            )
            shortlist.append((_match_score_without_age(target, provisional), candidate_path))
        else:
            shortlist.append((abs(target.depth - _path_depth(candidate_path)) * 2.0, candidate_path))

    shortlist.sort(key=lambda item: (item[0], item[1]))
    finalists = [path for _, path in shortlist[: min(shortlist_size, len(shortlist))]]

    scored: list[tuple[float, str]] = []
    feature_by_path: dict[str, PathFeatures] = {}
    for candidate_path in finalists:
        features = _cached_path_features(
            repo_dir,
            candidate_path,
            anchor_commit,
            creation_cache=creation_cache,
            feature_cache=feature_cache,
            creation_index=creation_index,
            size_index=size_index,
            timeout=timeout,
        )
        if not _passes_caliper(target, features):
            continue
        feature_by_path[candidate_path] = features
        scored.append((_match_score(target, features), candidate_path))

    if not scored:
        for candidate_path in finalists:
            features = _cached_path_features(
                repo_dir,
                candidate_path,
                anchor_commit,
                creation_cache=creation_cache,
                feature_cache=feature_cache,
                creation_index=creation_index,
                size_index=size_index,
                timeout=timeout,
            )
            feature_by_path[candidate_path] = features
            scored.append((_match_score(target, features), candidate_path))

    if not scored:
        fallback_path = finalists[0]
        feature_by_path[fallback_path] = _cached_path_features(
            repo_dir,
            fallback_path,
            anchor_commit,
            creation_cache=creation_cache,
            feature_cache=feature_cache,
            creation_index=creation_index,
            size_index=size_index,
            timeout=timeout,
        )
        scored.append((_match_score(target, feature_by_path[fallback_path]), fallback_path))

    scored.sort(key=lambda item: (item[0], item[1]))
    best_score = scored[0][0]
    tied = [path for score, path in scored if abs(score - best_score) < 1e-9]
    chosen = rng.choice(tied)
    return feature_by_path[chosen]


def _metric_values(pair: SelectionMatchPair, metric: str, *, group: str) -> float:
    prefix = "ref" if group == "referenced" else "ctrl"
    if metric == METRIC_CHURN:
        return float(getattr(pair, f"{prefix}_churn_commits"))
    if metric == METRIC_LIFETIME:
        return float(getattr(pair, f"{prefix}_lifetime_days"))
    if metric == METRIC_RENAME:
        return float(getattr(pair, f"{prefix}_rename_count"))
    if metric == METRIC_DELETION:
        return 1.0 if getattr(pair, f"{prefix}_deleted") else 0.0
    if metric == METRIC_SURVIVAL:
        return 1.0 if getattr(pair, f"{prefix}_survived_panel") else 0.0
    raise ValueError(f"unknown metric: {metric}")


def _paired_differences(pairs: list[SelectionMatchPair], metric: str) -> list[float]:
    return [
        _metric_values(pair, metric, group="referenced") - _metric_values(pair, metric, group="control")
        for pair in pairs
    ]


def _favorable_fraction(pairs: list[SelectionMatchPair], metric: str) -> list[float]:
    direction = STABILITY_DIRECTION[metric]
    flags: list[float] = []
    for pair in pairs:
        ref_val = _metric_values(pair, metric, group="referenced")
        ctrl_val = _metric_values(pair, metric, group="control")
        if direction == "lower":
            flags.append(1.0 if ref_val <= ctrl_val else 0.0)
        else:
            flags.append(1.0 if ref_val >= ctrl_val else 0.0)
    return flags


def _permutation_alternative(metric: str) -> str:
    direction = STABILITY_DIRECTION[metric]
    if direction == "lower":
        return "less"
    return "greater"


def compute_selection_statistics(
    pairs: list[SelectionMatchPair],
    *,
    seed: int = 42,
) -> SelectionStudyStatistics:
    if not pairs:
        return SelectionStudyStatistics(n_pairs=0, n_repos=0, metrics=[])

    metrics: list[MetricEffectEstimate] = []
    for metric in (
        METRIC_LIFETIME,
        METRIC_CHURN,
        METRIC_RENAME,
        METRIC_DELETION,
        METRIC_SURVIVAL,
    ):
        ref_vals = [_metric_values(p, metric, group="referenced") for p in pairs]
        ctrl_vals = [_metric_values(p, metric, group="control") for p in pairs]
        diffs = [r - c for r, c in zip(ref_vals, ctrl_vals)]
        ref_mean, _, _ = bootstrap_mean_ci(ref_vals, seed=seed)
        ctrl_mean, _, _ = bootstrap_mean_ci(ctrl_vals, seed=seed)
        diff_mean, diff_lo, diff_hi = bootstrap_mean_ci(diffs, seed=seed)
        favorable = _favorable_fraction(pairs, metric)
        fav_mean, fav_lo, fav_hi = bootstrap_mean_ci(favorable, seed=seed)
        metrics.append(
            MetricEffectEstimate(
                metric=metric,
                n_pairs=len(pairs),
                referenced_mean=round(ref_mean, 4),
                control_mean=round(ctrl_mean, 4),
                mean_difference=round(diff_mean, 4),
                mean_difference_ci_low=round(diff_lo, 4),
                mean_difference_ci_high=round(diff_hi, 4),
                cohens_d=round(paired_cohens_d(diffs), 4),
                permutation_p_value=round(
                    permutation_test_sign_flip(
                        diffs,
                        seed=seed,
                        alternative=_permutation_alternative(metric),
                    ),
                    6,
                ),
                referenced_favorable_fraction=round(fav_mean, 4),
                referenced_favorable_ci_low=round(fav_lo, 4),
                referenced_favorable_ci_high=round(fav_hi, 4),
                alternative=_permutation_alternative(metric),
            )
        )

    return SelectionStudyStatistics(
        n_pairs=len(pairs),
        n_repos=len({p.repo_id for p in pairs}),
        metrics=metrics,
    )


def build_selection_pairs(
    *,
    longitudinal_csv: Path,
    scratch_dir: Path,
    max_referenced_per_repo: int | None = None,
    seed: int = 42,
    clone_timeout: int = 600,
) -> list[SelectionMatchPair]:
    rows = load_longitudinal_rows(longitudinal_csv)
    trajectories = collect_cited_path_trajectories(rows)
    by_repo: dict[str, list[str]] = defaultdict(list)
    for repo_id, reference in trajectories:
        by_repo[repo_id].append(reference)

    rng = random.Random(seed)
    pairs: list[SelectionMatchPair] = []
    clone_cache: dict[str, Path] = {}
    tree_caches: dict[str, CommitTreeCache] = {}
    processed = 0

    try:
        for repo_id, references in sorted(by_repo.items()):
            unique_refs = sorted(set(references))
            sampled = unique_refs
            if max_referenced_per_repo is not None and len(sampled) > max_referenced_per_repo:
                sampled = rng.sample(sampled, max_referenced_per_repo)

            print(
                f"selection study: repo {repo_id} ({len(sampled)} referenced paths)",
                flush=True,
            )
            repo_url = trajectories[(repo_id, sampled[0])]["repo_url"]
            if repo_id not in clone_cache:
                clone_path = scratch_dir / f"selection_{repo_id}"
                clone_bare(repo_url, clone_path, timeout=clone_timeout)
                clone_cache[repo_id] = clone_path
                tree_caches[repo_id] = CommitTreeCache(clone_path, timeout=clone_timeout)

            repo_dir = clone_cache[repo_id]
            tree_cache = tree_caches[repo_id]
            cited_paths = set(unique_refs)
            creation_cache: dict[str, int | None] = {}

            print(
                f"selection study: indexing creation timestamps for {repo_id}",
                flush=True,
            )
            creation_index = _build_creation_index(
                repo_dir,
                timeout=min(clone_timeout, 300),
            )

            panel_groups: dict[tuple[str, str, str, str], list[str]] = defaultdict(list)
            for referenced_path in sampled:
                meta = trajectories[(repo_id, referenced_path)]
                panel_groups[
                    (
                        meta["panel_start_commit"],
                        meta["panel_end_commit"],
                        meta["panel_start_time"],
                        meta["panel_end_time"],
                    )
                ].append(referenced_path)

            activity_catalog_cache: dict[tuple[str, str], PanelActivityCatalog] = {}
            for (start_commit, end_commit, _start_time, _end_time) in panel_groups:
                panel_key = (start_commit, end_commit)
                if panel_key in activity_catalog_cache:
                    continue
                print(
                    f"selection study: building commit activity catalog for {repo_id} "
                    f"(panel {start_commit[:8]}..{end_commit[:8]})",
                    flush=True,
                )
                activity_catalog_cache[panel_key] = _build_panel_activity_catalog(
                    repo_dir,
                    start_commit=start_commit,
                    end_commit=end_commit,
                    timeout=min(clone_timeout, 300),
                )

            for (start_commit, end_commit, start_time, end_time), group_refs in panel_groups.items():
                panel_duration = _panel_duration_days(start_time, end_time)
                tree_at_start = tree_cache.paths_at(start_commit)
                tree_at_end = tree_cache.paths_at(end_commit)
                size_index = _tree_sizes_at_commit(
                    repo_dir,
                    start_commit,
                    timeout=min(clone_timeout, 120),
                )
                activity_catalog = activity_catalog_cache[(start_commit, end_commit)]
                feature_cache: dict[tuple[str, str], PathFeatures] = {}
                used_controls: set[str] = set()

                def panel_metrics(path: str) -> PathPanelMetrics:
                    return _path_panel_metrics_from_catalog(
                        path,
                        catalog=activity_catalog,
                        panel_start_time=start_time,
                        panel_end_time=end_time,
                        panel_duration_days=panel_duration,
                        tree_at_end=tree_at_end,
                    )

                for referenced_path in sorted(group_refs):
                    if referenced_path not in tree_at_start:
                        continue

                    target = _cached_path_features(
                        repo_dir,
                        referenced_path,
                        start_commit,
                        creation_cache=creation_cache,
                        feature_cache=feature_cache,
                        creation_index=creation_index,
                        size_index=size_index,
                        timeout=clone_timeout,
                    )
                    control = _pick_matched_control(
                        repo_dir=repo_dir,
                        tree_paths=tree_at_start,
                        cited_paths=cited_paths,
                        target=target,
                        anchor_commit=start_commit,
                        creation_cache=creation_cache,
                        feature_cache=feature_cache,
                        creation_index=creation_index,
                        size_index=size_index,
                        used_controls=used_controls,
                        rng=rng,
                        timeout=clone_timeout,
                    )
                    if control is None:
                        continue
                    used_controls.add(control.path)

                    depth_diff, size_ratio, creation_diff, score = _match_metadata(target, control)
                    ref_metrics = panel_metrics(referenced_path)
                    ctrl_metrics = panel_metrics(control.path)
                    pairs.append(
                        SelectionMatchPair(
                            repo_id=repo_id,
                            repo_url=repo_url,
                            referenced_path=referenced_path,
                            control_path=control.path,
                            panel_start_commit=start_commit,
                            panel_end_commit=end_commit,
                            panel_start_time=start_time,
                            panel_end_time=end_time,
                            panel_duration_days=round(panel_duration, 4),
                            match_extension=target.extension,
                            match_depth_diff=depth_diff,
                            match_size_ratio=round(size_ratio, 4) if size_ratio is not None else None,
                            match_creation_days_diff=round(creation_diff, 4)
                            if creation_diff is not None
                            else None,
                            match_score=round(score, 4),
                            ref_lifetime_days=ref_metrics.lifetime_days,
                            ref_churn_commits=ref_metrics.churn_commits,
                            ref_rename_count=ref_metrics.rename_count,
                            ref_deleted=ref_metrics.deleted,
                            ref_survived_panel=ref_metrics.survived_panel,
                            ctrl_lifetime_days=ctrl_metrics.lifetime_days,
                            ctrl_churn_commits=ctrl_metrics.churn_commits,
                            ctrl_rename_count=ctrl_metrics.rename_count,
                            ctrl_deleted=ctrl_metrics.deleted,
                            ctrl_survived_panel=ctrl_metrics.survived_panel,
                        )
                    )
                    processed += 1
                    if processed % 50 == 0:
                        print(
                            f"selection study: {processed} matched pairs built "
                            f"(repo={repo_id}, panel={start_commit[:8]})",
                            flush=True,
                        )
    finally:
        for clone_path in clone_cache.values():
            remove_clone(clone_path)

    return pairs


def survival_records(
    pairs: list[SelectionMatchPair],
    *,
    group: str,
) -> list[tuple[float, int]]:
    """Kaplan-Meier inputs: (duration_days, event=1 if deleted before panel end)."""
    records: list[tuple[float, int]] = []
    prefix = "ref" if group == "referenced" else "ctrl"
    for pair in pairs:
        deleted = getattr(pair, f"{prefix}_deleted")
        duration = getattr(pair, f"{prefix}_lifetime_days")
        records.append((duration, 1 if deleted else 0))
    return records
