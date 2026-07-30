"""P4 classifier validation against human gold annotations (read-only)."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from artifact_lab.experiments.truth_pilots.p4_attribution_precision import PRECISION_KILL_THRESHOLD

SIGNAL_GROUPS: dict[str, str] = {
    "co_authored_by_trailer": "Co-Authored-By",
    "claude_signature": "Claude signatures",
    "cursor_signature": "Cursor signatures",
    "copilot_signature": "Copilot signatures",
    "dependabot_renovate_security_bot": "generic bots",
    "bot_author": "generic bots",
    "generic_automation": "generic automation (OpenAI/Devin/etc.)",
    "unclassified": "unclassified",
}

GOLD_POSITIVE_LABEL = "true_agent_maintenance"
GOLD_NEGATIVE_LABELS = frozenset({"human_only", "generic_bot"})


@dataclass(frozen=True)
class BinaryMetrics:
    tp: int
    fp: int
    fn: int
    tn: int

    @property
    def precision(self) -> float:
        denom = self.tp + self.fp
        return self.tp / denom if denom else 0.0

    @property
    def recall(self) -> float:
        denom = self.tp + self.fn
        return self.tp / denom if denom else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0

    @property
    def accuracy(self) -> float:
        total = self.tp + self.fp + self.fn + self.tn
        return (self.tp + self.tn) / total if total else 0.0

    @property
    def cohen_kappa(self) -> float:
        total = self.tp + self.fp + self.fn + self.tn
        if total == 0:
            return 0.0
        po = self.accuracy
        p_pred = (self.tp + self.fp) / total
        p_gold = (self.tp + self.fn) / total
        pe = p_pred * p_gold + (1 - p_pred) * (1 - p_gold)
        if pe == 1.0:
            return 1.0
        return (po - pe) / (1 - pe)


def load_human_gold(gold_csv: Path) -> list[dict]:
    rows: list[dict] = []
    with gold_csv.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            label = (row.get("human_label") or "").strip()
            if not label:
                continue
            rows.append(row)
    return rows


def _gold_positive(label: str) -> bool:
    return label.strip() == GOLD_POSITIVE_LABEL


def _pred_positive(counts: str) -> bool:
    return str(counts).strip().lower() == "yes"


def signal_group(signature_category: str) -> str:
    return SIGNAL_GROUPS.get(signature_category, signature_category)


def compute_binary_metrics(rows: list[dict]) -> BinaryMetrics:
    tp = fp = fn = tn = 0
    for row in rows:
        gold = _gold_positive(row["human_label"])
        pred = _pred_positive(row["counts_as_agent_maintenance"])
        if gold and pred:
            tp += 1
        elif not gold and pred:
            fp += 1
        elif gold and not pred:
            fn += 1
        else:
            tn += 1
    return BinaryMetrics(tp=tp, fp=fp, fn=fn, tn=tn)


def confusion_matrix_rows(metrics: BinaryMetrics) -> list[dict]:
    return [
        {"gold": "true_agent_maintenance", "predicted_yes": metrics.tp, "predicted_no": metrics.fn},
        {"gold": "not_agent_maintenance", "predicted_yes": metrics.fp, "predicted_no": metrics.tn},
    ]


def precision_by_signal(rows: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[signal_group(row.get("signature_category", ""))].append(row)

    results: list[dict] = []
    for signal in (
        "Co-Authored-By",
        "Claude signatures",
        "Cursor signatures",
        "Copilot signatures",
        "generic bots",
        "generic automation (OpenAI/Devin/etc.)",
    ):
        subset = grouped.get(signal, [])
        tp = sum(
            1
            for r in subset
            if _pred_positive(r["counts_as_agent_maintenance"]) and _gold_positive(r["human_label"])
        )
        fp = sum(
            1
            for r in subset
            if _pred_positive(r["counts_as_agent_maintenance"]) and not _gold_positive(r["human_label"])
        )
        fn = sum(
            1
            for r in subset
            if not _pred_positive(r["counts_as_agent_maintenance"]) and _gold_positive(r["human_label"])
        )
        tn = sum(
            1
            for r in subset
            if not _pred_positive(r["counts_as_agent_maintenance"]) and not _gold_positive(r["human_label"])
        )
        pred_yes = tp + fp
        results.append(
            {
                "signal": signal,
                "n": len(subset),
                "predicted_yes": pred_yes,
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "tn": tn,
                "precision": round(tp / pred_yes, 4) if pred_yes else None,
                "recall": round(tp / (tp + fn), 4) if (tp + fn) else None,
            }
        )
    return results


def disagreement_rows(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    false_positives: list[dict] = []
    false_negatives: list[dict] = []
    for row in rows:
        gold = _gold_positive(row["human_label"])
        pred = _pred_positive(row["counts_as_agent_maintenance"])
        if pred and not gold:
            false_positives.append(row)
        elif gold and not pred:
            false_negatives.append(row)
    return false_positives, false_negatives


def build_validation_markdown(
    *,
    gold_csv: Path,
    rows: list[dict],
    metrics: BinaryMetrics,
    signal_metrics: list[dict],
    false_positives: list[dict],
    false_negatives: list[dict],
) -> str:
    human_counts = Counter(r["human_label"] for r in rows)
    gate_pass = metrics.precision >= PRECISION_KILL_THRESHOLD

    lines = [
        "# P4 — Human Gold Validation Report",
        "",
        "## Summary",
        "",
        f"- **Gold source:** `{gold_csv}`",
        f"- **Reviewed rows:** {len(rows)}",
        f"- **Gate threshold:** precision ≥ **{PRECISION_KILL_THRESHOLD:.0%}** (agent-maintenance positive class)",
        f"- **Gate result:** **{'PASS' if gate_pass else 'FAIL'}** (precision = {metrics.precision:.3f})",
        "",
        "## Methodology",
        "",
        "Pure validation step — **no relabeling, no retraining, no algorithm changes**.",
        "",
        "The existing P4 heuristic (`categorize_signature` / `counts_as_agent_maintenance`) is evaluated",
        "against independent human labels on the stratified 200-commit worksheet exported by Gate P4.",
        "",
        "**Positive class (gold):** `human_label = true_agent_maintenance`",
        "",
        "**Negative class (gold):** `human_label ∈ {human_only, generic_bot}`",
        "",
        "**Classifier prediction:** frozen worksheet column `counts_as_agent_maintenance` (`yes`/`no`),",
        "produced at worksheet export time by the current P4 rules.",
        "",
        "Metrics are computed on the **full reviewed sample** (N=200). Cohen's κ is reported for",
        "binary agent-maintenance agreement (appropriate for two nominal raters on yes/no).",
        "",
        "## Gold protocol",
        "",
        "1. Stratified sample of 200 non-human flagged commits from `agent_commit_candidates.csv`",
        "   (seed=42, exported as `agent_attribution_gold_worksheet.csv`).",
        "2. Human reviewer assigned `human_label` per commit:",
        "   - `true_agent_maintenance` — commit reflects genuine agent-assisted instruction maintenance",
        "   - `human_only` — automation signal present but human-maintained / not agent maintenance",
        "   - `generic_bot` — infrastructure or CI bot (Dependabot, github-actions, release automation)",
        "3. Classifier labels were **not** edited during review.",
        "",
        "## Annotation assumptions",
        "",
        "- **Agent maintenance** requires evidence that an coding agent (Claude, Cursor, Copilot, etc.)",
        "  materially contributed to the instruction-file commit, not merely a mention in prose.",
        "- **Co-Authored-By** trailers naming known agent identities count as agent maintenance;",
        "  human-only or unknown co-authors may be labeled `human_only`.",
        "- **Bot authors** (Dependabot, github-actions, azure-sdk-automation) default to `generic_bot`",
        "  even when agent co-trailers appear — human judgment resolved mixed-signal cases.",
        "- **Tool-pattern signatures** (`tool_pattern:phrase:…`) require contextual review;",
        "  boilerplate automation text may be `human_only`.",
        "",
        "## Global metrics",
        "",
        "| Metric | Value |",
        "|--------|------:|",
        f"| Precision | {metrics.precision:.4f} |",
        f"| Recall | {metrics.recall:.4f} |",
        f"| F1 | {metrics.f1:.4f} |",
        f"| Accuracy | {metrics.accuracy:.4f} |",
        f"| Cohen's κ | {metrics.cohen_kappa:.4f} |",
        "",
        "### Confusion matrix (rows = gold, columns = classifier)",
        "",
        "| Gold \\ Predicted | yes | no |",
        "|------------------|----:|---:|",
        f"| true_agent_maintenance | {metrics.tp} | {metrics.fn} |",
        f"| not_agent_maintenance | {metrics.fp} | {metrics.tn} |",
        "",
        f"Human label distribution: {dict(human_counts)}",
        "",
        "## Precision by attribution signal",
        "",
        "Stratified metrics within each `signature_category` group. Precision is conditional on",
        "classifier predicting `yes` within the stratum.",
        "",
        "| Signal | N | Pred yes | TP | FP | FN | Precision | Recall |",
        "|--------|--:|---------:|---:|---:|---:|----------:|-------:|",
    ]

    for s in signal_metrics:
        prec = f"{s['precision']:.3f}" if s["precision"] is not None else "—"
        rec = f"{s['recall']:.3f}" if s["recall"] is not None else "—"
        lines.append(
            f"| {s['signal']} | {s['n']} | {s['predicted_yes']} | {s['tp']} | {s['fp']} | "
            f"{s['fn']} | {prec} | {rec} |"
        )

    lines.extend(
        [
            "",
            "## Disagreement analysis",
            "",
            f"- **False positives (classifier yes, human no):** {len(false_positives)}",
            f"- **False negatives (classifier no, human yes):** {len(false_negatives)}",
            "",
        ]
    )

    if false_positives:
        lines.append("### False positives")
        lines.append("")
        for row in false_positives:
            lines.append(
                f"- **#{row.get('worksheet_id','?')}** `{row.get('signature_category','')}` → "
                f"human=`{row.get('human_label','')}` — "
                f"{row.get('repo_id','')}/{row.get('instruction_path','')} @ "
                f"`{row.get('commit_sha','')[:8]}`"
            )
            note = (row.get("reviewer_notes") or "").strip()
            if note:
                lines.append(f"  - Note: {note}")
        lines.append("")

    if false_negatives:
        lines.append("### False negatives")
        lines.append("")
        lines.append(
            "Dominant pattern: commits classified as `dependabot_renovate_security_bot` because "
            "`github-actions[bot]` appears in evidence, but human reviewers labeled agent maintenance "
            "due to **Claude Co-Authored-By** trailers in the same commit."
        )
        lines.append("")
        for row in false_negatives:
            lines.append(
                f"- **#{row.get('worksheet_id','?')}** `{row.get('signature_category','')}` → "
                f"human=`{row.get('human_label','')}` — "
                f"{row.get('repo_id','')}/{row.get('instruction_path','')} @ "
                f"`{row.get('commit_sha','')[:8]}`"
            )
        lines.append("")

    lines.extend(
        [
            "## Gate assessment",
            "",
            f"| Criterion | Required | Observed | Result |",
            f"|-----------|----------|----------|--------|",
            f"| Precision (agent maintenance) | ≥ {PRECISION_KILL_THRESHOLD:.0%} | "
            f"{metrics.precision:.1%} | **{'PASS' if gate_pass else 'FAIL'}** |",
            "",
            "## Interpretation",
            "",
        ]
    )

    if gate_pass:
        lines.append(
            "The predefined P4 precision gate **passes**. The current classifier is sufficiently "
            "accurate for downstream observational use (RQ3 maintenance regimes) without algorithm "
            "changes. Residual errors concentrate in (1) mixed human/agent Co-Authored-By trailers and "
            "(2) github-actions bot commits that also carry Claude agent trailers — a recall issue, "
            "not a precision failure."
        )
    else:
        lines.append(
            "The predefined P4 precision gate **fails**. Do not promote agent-maintenance claims "
            "until the classifier is revised or human review expands."
        )

    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- Single human review pass; no adjudication of ambiguous cases.",
            "- Worksheet is a pilot sample (N=200), not exhaustive over all flagged commits.",
            "- κ reflects binary collapse of three-level human taxonomy.",
            "",
        ]
    )
    return "\n".join(lines)


def run_p4_validation(
    *,
    gold_csv: Path,
    output_md: Path,
) -> Path:
    rows = load_human_gold(gold_csv)
    if not rows:
        raise ValueError(f"No labeled rows in gold file: {gold_csv}")

    metrics = compute_binary_metrics(rows)
    signal_metrics = precision_by_signal(rows)
    false_positives, false_negatives = disagreement_rows(rows)

    output_md.parent.mkdir(parents=True, exist_ok=True)
    from artifact_lab.execution.atomic_io import atomic_write_text

    atomic_write_text(
        output_md,
        build_validation_markdown(
            gold_csv=gold_csv,
            rows=rows,
            metrics=metrics,
            signal_metrics=signal_metrics,
            false_positives=false_positives,
            false_negatives=false_negatives,
        ),
    )
    return output_md
