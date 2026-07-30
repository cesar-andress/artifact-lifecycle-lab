#!/usr/bin/env python3
"""Compare first vs second auditor labels (runs only when human labels exist)."""

from __future__ import annotations

import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = ROOT / "validation/rq2_second_audit/private/rq2_original_labels_private.csv"
SECOND = ROOT / "validation/rq2_second_audit/rq2_second_auditor_labels.csv"
OUT = ROOT / "validation/rq2_second_audit"


def _bool(v: str) -> bool:
    return str(v).strip().lower() in {"1", "true", "yes", "t"}


def cohen_kappa(y1: list[str], y2: list[str]) -> float:
    labels = sorted(set(y1) | set(y2))
    n = len(y1)
    if n == 0:
        return float("nan")
    mat = Counter(zip(y1, y2))
    po = sum(mat[(a, a)] for a in labels) / n
    p1 = Counter(y1)
    p2 = Counter(y2)
    pe = sum((p1[a] / n) * (p2[a] / n) for a in labels)
    if pe == 1:
        return 1.0
    return (po - pe) / (1 - pe)


def main() -> int:
    if not SECOND.exists():
        print(
            "second auditor labels not available; skipping agreement "
            f"(expected {SECOND.relative_to(ROOT)})"
        )
        return 0
    if not PRIVATE.exists():
        raise SystemExit("private answer key missing")

    with PRIVATE.open() as handle:
        first = {r["event_id"]: r for r in csv.DictReader(handle)}
    with SECOND.open() as handle:
        second_rows = list(csv.DictReader(handle))
    second = {r["event_id"]: r for r in second_rows}

    if set(first) != set(second) or len(first) != 121:
        raise SystemExit("event_id mismatch or incomplete second labels")

    # Preserve raw second file: copy timestamped snap if needed — do not modify SECOND.
    cats1 = [first[e]["final_category"] for e in sorted(first)]
    cats2 = [second[e]["auditor_category"] for e in sorted(first)]
    # Map uncertain to ambiguous for matrix optional — keep raw
    raw_agree = sum(a == b for a, b in zip(cats1, cats2)) / 121
    kappa = cohen_kappa(cats1, cats2)

    bin1 = [_bool(first[e]["is_genuine_decay"]) for e in sorted(first)]
    bin2 = [_bool(second[e]["counts_as_genuine_decay"]) for e in sorted(first)]
    bin_agree = sum(a == b for a, b in zip(bin1, bin2)) / 121
    # prevalence-robust: positive/negative agreement
    tp = sum(a and b for a, b in zip(bin1, bin2))
    tn = sum((not a) and (not b) for a, b in zip(bin1, bin2))
    fp = sum((not a) and b for a, b in zip(bin1, bin2))
    fn = sum(a and (not b) for a, b in zip(bin1, bin2))
    pos_agree = (2 * tp) / (2 * tp + fp + fn) if (2 * tp + fp + fn) else float("nan")
    neg_agree = (2 * tn) / (2 * tn + fp + fn) if (2 * tn + fp + fn) else float("nan")

    # confusion matrix
    labels = sorted(set(cats1) | set(cats2))
    matrix_path = OUT / "rq2_agreement_confusion_matrix.csv"
    with matrix_path.open("w", newline="", encoding="utf-8") as handle:
        w = csv.writer(handle)
        w.writerow(["first\\second"] + labels)
        for a in labels:
            row = [a]
            for b in labels:
                row.append(sum(1 for x, y in zip(cats1, cats2) if x == a and y == b))
            w.writerow(row)

    # disagreements changing headline numerator
    headline = []
    for e in sorted(first):
        a = _bool(first[e]["is_genuine_decay"])
        b = _bool(second[e]["counts_as_genuine_decay"])
        if a != b:
            headline.append(
                {
                    "event_id": e,
                    "first_genuine": a,
                    "second_genuine": b,
                    "first_category": first[e]["final_category"],
                    "second_category": second[e]["auditor_category"],
                    "changes_headline_numerator": True,
                }
            )
    with (OUT / "rq2_agreement_headline_disagreements.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        fields = [
            "event_id",
            "first_genuine",
            "second_genuine",
            "first_category",
            "second_category",
            "changes_headline_numerator",
        ]
        w = csv.DictWriter(handle, fieldnames=fields)
        w.writeheader()
        for r in headline:
            w.writerow({**r, "first_genuine": str(r["first_genuine"]), "second_genuine": str(r["second_genuine"])})

    # confidence-stratified
    by_conf = defaultdict(list)
    for e in sorted(first):
        conf = second[e].get("confidence", "")
        by_conf[conf].append(
            first[e]["final_category"] == second[e]["auditor_category"]
        )

    # adjudication template for disagreements
    adj_path = OUT / "rq2_disagreement_adjudication_TEMPLATE.csv"
    with adj_path.open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "event_id",
            "first_label",
            "second_label",
            "adjudicated_label",
            "first_genuine",
            "second_genuine",
            "adjudicated_counts_as_genuine_decay",
            "adjudicator",
            "rationale",
            "evidence_used",
            "date",
        ]
        w = csv.DictWriter(handle, fieldnames=fields)
        w.writeheader()
        for e in sorted(first):
            if first[e]["final_category"] != second[e]["auditor_category"] or _bool(
                first[e]["is_genuine_decay"]
            ) != _bool(second[e]["counts_as_genuine_decay"]):
                w.writerow(
                    {
                        "event_id": e,
                        "first_label": first[e]["final_category"],
                        "second_label": second[e]["auditor_category"],
                        "adjudicated_label": "",
                        "first_genuine": first[e]["is_genuine_decay"],
                        "second_genuine": second[e]["counts_as_genuine_decay"],
                        "adjudicated_counts_as_genuine_decay": "",
                        "adjudicator": "",
                        "rationale": "",
                        "evidence_used": "",
                        "date": "",
                    }
                )

    second_num = sum(bin2)
    md = []
    md.append("# RQ2 Human-Validation Agreement\n\n")
    md.append("Raw second-auditor file was left unmodified.\n\n")
    md.append(f"- Raw category agreement: **{raw_agree:.3f}** ({int(raw_agree*121)}/121)\n")
    md.append(f"- Cohen's kappa (categories): **{kappa:.3f}**\n")
    md.append(
        f"- Binary estimand agreement: **{bin_agree:.3f}** "
        f"(TP={tp}, TN={tn}, FP={fp}, FN={fn})\n"
    )
    md.append(f"- Positive agreement: **{pos_agree}**\n")
    md.append(f"- Negative agreement: **{neg_agree}**\n")
    md.append(f"- Headline-changing disagreements: **{len(headline)}**\n")
    md.append(f"- Original frozen estimate: **0/121**\n")
    md.append(f"- Independent second-auditor estimate: **{second_num}/121**\n")
    md.append("- Adjudicated estimate: *pending completed adjudication file*\n")
    md.append("\n## Confidence-stratified category agreement\n\n")
    for conf, vals in sorted(by_conf.items()):
        md.append(f"- {conf or '(missing)'}: {sum(vals)}/{len(vals)}\n")
    md.append(
        "\nKappa alone is not evidence of validity; interpret with prevalence "
        "and binary estimand agreement.\n"
    )
    (OUT / "rq2_agreement_summary.md").write_text("".join(md), encoding="utf-8")
    print("wrote agreement artifacts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
