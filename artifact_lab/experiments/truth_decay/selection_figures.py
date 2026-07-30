"""Publication figures for the selection observational study."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from artifact_lab.execution.atomic_io import atomic_replace
from artifact_lab.experiments.truth_decay.selection_study import (
    METRIC_LABELS,
    MetricEffectEstimate,
    SelectionMatchPair,
    survival_records,
)


def _save(fig, path: Path) -> None:
    tmp = path.with_name(path.name + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(tmp, format="pdf", bbox_inches="tight", dpi=300)
    atomic_replace(tmp, path)


def _kaplan_meier_curve(records: list[tuple[float, int]]) -> tuple[list[float], list[float]]:
    if not records:
        return [], []
    data = sorted(records, key=lambda item: item[0])
    unique_times = sorted({t for t, _ in data})
    at_risk = len(data)
    survival = 1.0
    times: list[float] = [0.0]
    probs: list[float] = [1.0]
    for t in unique_times:
        d_i = sum(1 for time, event in data if time == t and event == 1)
        c_i = sum(1 for time, event in data if time == t and event == 0)
        if at_risk <= 0:
            break
        if d_i > 0:
            survival *= 1 - d_i / at_risk
        times.append(t)
        probs.append(survival)
        at_risk -= d_i + c_i
    return times, probs


def render_figure_selection_churn(
    pairs: list[SelectionMatchPair],
    path: Path,
) -> None:
    ref_vals = [float(p.ref_churn_commits) for p in pairs]
    ctrl_vals = [float(p.ctrl_churn_commits) for p in pairs]
    fig, ax = plt.subplots(figsize=(7, 5))
    data = [ref_vals, ctrl_vals]
    positions = [1, 2]
    parts = ax.violinplot(data, positions=positions, showmeans=True, showmedians=True)
    for body in parts["bodies"]:
        body.set_alpha(0.7)
    ax.boxplot(data, positions=positions, widths=0.15, patch_artist=True)
    ax.set_xticks(positions, ["Referenced paths", "Matched controls"])
    ax.set_ylabel("Git commits touching path (panel window)")
    ax.set_title("Selection study — commit churn")
    ax.grid(True, axis="y", alpha=0.3)
    _save(fig, path)
    plt.close(fig)


def render_figure_selection_survival(
    pairs: list[SelectionMatchPair],
    path: Path,
) -> None:
    ref_records = survival_records(pairs, group="referenced")
    ctrl_records = survival_records(pairs, group="control")
    ref_t, ref_s = _kaplan_meier_curve(ref_records)
    ctrl_t, ctrl_s = _kaplan_meier_curve(ctrl_records)

    fig, ax = plt.subplots(figsize=(7, 5))
    if ref_t:
        ax.step(ref_t, ref_s, where="post", label="Referenced paths", color="#2E86AB", linewidth=2)
    if ctrl_t:
        ax.step(ctrl_t, ctrl_s, where="post", label="Matched controls", color="#A23B72", linewidth=2)
    ax.set_xlabel("Days since panel start")
    ax.set_ylabel("Survival (file present at panel end)")
    ax.set_ylim(0.0, 1.05)
    ax.set_title("Selection study — panel-end survival")
    ax.legend()
    ax.grid(True, alpha=0.3)
    _save(fig, path)
    plt.close(fig)


def render_figure_selection_matched_effect(
    effects: list[MetricEffectEstimate],
    path: Path,
) -> None:
    labels = [METRIC_LABELS.get(e.metric, e.metric) for e in effects]
    diffs = [e.mean_difference for e in effects]
    lo = [e.mean_difference - e.mean_difference_ci_low for e in effects]
    hi = [e.mean_difference_ci_high - e.mean_difference for e in effects]
    y_pos = list(range(len(effects)))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.errorbar(
        diffs,
        y_pos,
        xerr=[lo, hi],
        fmt="o",
        color="#1B4332",
        ecolor="#40916C",
        capsize=4,
        markersize=8,
    )
    ax.axvline(0.0, color="#C0392B", linestyle="--", linewidth=1.5)
    ax.set_yticks(y_pos, labels)
    ax.set_xlabel("Paired mean difference (referenced − control)")
    ax.set_title("Selection study — matched-pair effects with 95% bootstrap CIs")
    ax.grid(True, axis="x", alpha=0.3)
    _save(fig, path)
    plt.close(fig)
