#!/usr/bin/env python3
"""Agreement analysis for one or more independent RQ2 human auditors.

Accepts deliverable schema:
  event_id,category,genuine_decay,confidence,ambiguity,notes,auditor_id,annotation_date

Also accepts legacy schema with auditor_category / counts_as_genuine_decay.
Does not overwrite raw auditor files or frozen primary labels.
"""

from __future__ import annotations

import csv
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = ROOT / "validation/rq2_second_audit/private/rq2_original_labels_private.csv"
AUDITORS_DIR = ROOT / "validation/rq2_second_audit/auditors"
OUT = ROOT / "validation/rq2_second_audit/agreement"
N = 121


def _bool_decay(v: str) -> bool | None:
    s = str(v).strip().lower()
    if s in {"yes", "true", "1", "t", "y"}:
        return True
    if s in {"no", "false", "0", "f", "n"}:
        return False
    if s in {"insufficient_evidence", "insufficient", "uncertain", ""}:
        return None
    raise ValueError(f"unrecognized genuine_decay value: {v!r}")


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


def normalize_row(row: dict[str, str]) -> dict[str, str]:
    cat = (row.get("category") or row.get("auditor_category") or "").strip()
    gd_raw = (row.get("genuine_decay") or row.get("counts_as_genuine_decay") or "").strip()
    return {
        "event_id": row["event_id"].strip(),
        "category": cat,
        "genuine_decay_raw": gd_raw,
        "confidence": (row.get("confidence") or "").strip(),
        "ambiguity": (row.get("ambiguity") or row.get("category_ambiguity") or "").strip(),
        "notes": (row.get("notes") or row.get("evidence_note") or "").strip(),
        "auditor_id": (row.get("auditor_id") or "").strip(),
        "annotation_date": (row.get("annotation_date") or "").strip(),
    }


def load_auditor(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = [normalize_row(r) for r in csv.DictReader(handle)]
    out = {r["event_id"]: r for r in rows}
    if len(out) != N:
        raise SystemExit(f"{path}: expected {N} unique ids, got {len(out)}")
    return out


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z**2 / n
    centre = p + z**2 / (2 * n)
    margin = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return ((centre - margin) / den, (centre + margin) / den)


def compare(name: str, first: dict[str, dict[str, str]], second: dict[str, dict[str, str]]) -> dict:
    ids = sorted(first)
    if set(second) != set(first):
        raise SystemExit(f"{name}: event_id mismatch vs primary")

    cats1 = [first[e]["final_category"] for e in ids]
    cats2 = [second[e]["category"] for e in ids]
    raw_agree = sum(a == b for a, b in zip(cats1, cats2))
    kappa = cohen_kappa(cats1, cats2)

    # Binary estimand: YES vs not-YES for numerator; also report IE separately
    bin1 = [_bool_decay("yes" if first[e]["is_genuine_decay"].lower() == "true" else "no") for e in ids]
    bin2_tri = [_bool_decay(second[e]["genuine_decay_raw"]) for e in ids]
    # For agreement on binary headline: map IE -> False (not counted as genuine)
    bin2 = [False if v is None else v for v in bin2_tri]
    bin_agree = sum(a == b for a, b in zip(bin1, bin2))
    tp = sum(a and b for a, b in zip(bin1, bin2))
    tn = sum((not a) and (not b) for a, b in zip(bin1, bin2))
    fp = sum((not a) and b for a, b in zip(bin1, bin2))
    fn = sum(a and (not b) for a, b in zip(bin1, bin2))
    pos_agree = (2 * tp) / (2 * tp + fp + fn) if (2 * tp + fp + fn) else float("nan")
    neg_agree = (2 * tn) / (2 * tn + fp + fn) if (2 * tn + fp + fn) else float("nan")

    yes_num = sum(1 for v in bin2_tri if v is True)
    ie_num = sum(1 for v in bin2_tri if v is None)
    no_num = sum(1 for v in bin2_tri if v is False)

    # headline-changing: second YES where first False (or vice versa)
    headline = []
    for e, a, b in zip(ids, bin1, bin2):
        if a != b:
            headline.append(
                {
                    "auditor": name,
                    "event_id": e,
                    "first_category": first[e]["final_category"],
                    "second_category": second[e]["category"],
                    "first_genuine": a,
                    "second_genuine_raw": second[e]["genuine_decay_raw"],
                    "second_genuine_counts": b,
                    "confidence": second[e]["confidence"],
                }
            )

    # confusion matrix
    labels = sorted(set(cats1) | set(cats2))
    matrix = {(a, b): 0 for a in labels for b in labels}
    for a, b in zip(cats1, cats2):
        matrix[(a, b)] += 1

    # confidence stratified
    by_conf: dict[str, list[bool]] = defaultdict(list)
    for e in ids:
        conf = second[e]["confidence"] or "(missing)"
        by_conf[conf].append(first[e]["final_category"] == second[e]["category"])

    lo, hi = wilson(yes_num, N)
    return {
        "name": name,
        "raw_agree": raw_agree,
        "raw_agree_pct": raw_agree / N,
        "kappa": kappa,
        "bin_agree": bin_agree,
        "bin_agree_pct": bin_agree / N,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "pos_agree": pos_agree,
        "neg_agree": neg_agree,
        "yes_num": yes_num,
        "no_num": no_num,
        "ie_num": ie_num,
        "wilson": (lo, hi),
        "headline": headline,
        "labels": labels,
        "matrix": matrix,
        "by_conf": by_conf,
        "cat_counts": Counter(cats2),
        "second": second,
    }


def write_matrix(path: Path, labels: list[str], matrix: dict) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        w = csv.writer(handle)
        w.writerow(["first\\second"] + labels)
        for a in labels:
            w.writerow([a] + [matrix[(a, b)] for b in labels])


def pairwise(a_name: str, a: dict, b_name: str, b: dict) -> dict:
    ids = sorted(a)
    cat = sum(1 for e in ids if a[e]["category"] == b[e]["category"])
    gd = sum(1 for e in ids if a[e]["genuine_decay_raw"] == b[e]["genuine_decay_raw"])
    # binary mapped
    ba = [False if _bool_decay(a[e]["genuine_decay_raw"]) is None else _bool_decay(a[e]["genuine_decay_raw"]) for e in ids]
    bb = [False if _bool_decay(b[e]["genuine_decay_raw"]) is None else _bool_decay(b[e]["genuine_decay_raw"]) for e in ids]
    bin_m = sum(x == y for x, y in zip(ba, bb))
    kappa_c = cohen_kappa([a[e]["category"] for e in ids], [b[e]["category"] for e in ids])
    return {
        "pair": f"{a_name}_vs_{b_name}",
        "category_agree": cat,
        "genuine_raw_agree": gd,
        "binary_mapped_agree": bin_m,
        "kappa_category": kappa_c,
    }


def main() -> int:
    if not PRIVATE.exists():
        raise SystemExit("private answer key missing; run make validation-package")
    with PRIVATE.open(encoding="utf-8", newline="") as handle:
        first = {r["event_id"]: r for r in csv.DictReader(handle)}
    if len(first) != N:
        raise SystemExit(f"private key has {len(first)} rows")

    files = sorted(AUDITORS_DIR.glob("*_rq2_second_auditor_labels.csv"))
    if not files:
        raise SystemExit(f"no auditor files in {AUDITORS_DIR}")

    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    auditors = {}
    for path in files:
        name = path.name.split("_")[0]
        second = load_auditor(path)
        auditors[name] = second
        res = compare(name, first, second)
        results.append(res)

        write_matrix(OUT / f"confusion_{name}_vs_primary.csv", res["labels"], res["matrix"])
        with (OUT / f"headline_disagreements_{name}.csv").open("w", newline="", encoding="utf-8") as handle:
            fields = [
                "auditor",
                "event_id",
                "first_category",
                "second_category",
                "first_genuine",
                "second_genuine_raw",
                "second_genuine_counts",
                "confidence",
            ]
            w = csv.DictWriter(handle, fieldnames=fields)
            w.writeheader()
            for row in res["headline"]:
                w.writerow(
                    {
                        **row,
                        "first_genuine": str(row["first_genuine"]),
                        "second_genuine_counts": str(row["second_genuine_counts"]),
                    }
                )

        # adjudication template for category or binary disagreements
        with (OUT / f"adjudication_template_{name}.csv").open(
            "w", newline="", encoding="utf-8"
        ) as handle:
            fields = [
                "event_id",
                "first_label",
                "second_label",
                "first_genuine",
                "second_genuine",
                "adjudicated_label",
                "adjudicated_counts_as_genuine_decay",
                "adjudicator",
                "rationale",
                "evidence_used",
                "date",
            ]
            w = csv.DictWriter(handle, fieldnames=fields)
            w.writeheader()
            for e in sorted(first):
                c1 = first[e]["final_category"]
                c2 = second[e]["category"]
                g1 = first[e]["is_genuine_decay"]
                g2 = second[e]["genuine_decay_raw"]
                g1b = _bool_decay("yes" if g1.lower() == "true" else "no")
                g2b = _bool_decay(g2)
                g2_counts = False if g2b is None else g2b
                if c1 != c2 or g1b != g2_counts:
                    w.writerow(
                        {
                            "event_id": e,
                            "first_label": c1,
                            "second_label": c2,
                            "first_genuine": g1,
                            "second_genuine": g2,
                            "adjudicated_label": "",
                            "adjudicated_counts_as_genuine_decay": "",
                            "adjudicator": "",
                            "rationale": "",
                            "evidence_used": "",
                            "date": "",
                        }
                    )

    # pairwise among auditors
    pair_rows = []
    names = list(auditors)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            pair_rows.append(pairwise(names[i], auditors[names[i]], names[j], auditors[names[j]]))

    # summary markdown
    md = []
    md.append("# RQ2 Independent Human Audit — Agreement Results\n\n")
    md.append("Primary frozen labels remain unchanged. Auditor files were not modified.\n\n")
    md.append("## Four estimators (binary YES counts as genuine decay)\n\n")
    md.append("| Estimator | Numerator / 121 | Notes |\n")
    md.append("|-----------|----------------:|-------|\n")
    md.append("| Original frozen (primary) | **0/121** | `is_genuine_decay` |\n")
    for res in results:
        lo, hi = res["wilson"]
        md.append(
            f"| Independent `{res['name']}` | **{res['yes_num']}/121** "
            f"({100*res['yes_num']/N:.1f}%; Wilson {100*lo:.1f}–{100*hi:.1f}%) | "
            f"NO={res['no_num']}, IE={res['ie_num']} |\n"
        )
    md.append("| Adjudicated | — | pending completed adjudication |\n")
    md.append("| Decay-favoring sensitivity | **25/121** | prespecified scenario |\n")

    md.append("\n## Agreement vs primary\n\n")
    for res in results:
        md.append(f"### Auditor `{res['name']}`\n\n")
        md.append(
            f"- Raw category agreement: **{res['raw_agree']}/121** ({res['raw_agree_pct']:.3f})\n"
        )
        md.append(f"- Cohen's κ (categories): **{res['kappa']:.3f}**\n")
        md.append(
            f"- Binary agreement (YES vs not-YES): **{res['bin_agree']}/121** "
            f"({res['bin_agree_pct']:.3f}); TP={res['tp']} TN={res['tn']} "
            f"FP={res['fp']} FN={res['fn']}\n"
        )
        md.append(f"- Positive agreement: **{res['pos_agree']}**\n")
        md.append(f"- Negative agreement: **{res['neg_agree']:.3f}**\n")
        md.append(
            f"- Headline-changing disagreements (binary): **{len(res['headline'])}** "
            f"(all are primary=False → auditor YES or mapped)\n"
        )
        md.append("- Confidence-stratified category agreement:\n")
        for conf, vals in sorted(res["by_conf"].items()):
            md.append(f"  - {conf}: {sum(vals)}/{len(vals)}\n")
        md.append(f"- Category mix: {dict(res['cat_counts'])}\n\n")

    if pair_rows:
        md.append("## Inter-auditor agreement\n\n")
        for p in pair_rows:
            md.append(
                f"- `{p['pair']}`: category {p['category_agree']}/121; "
                f"genuine_decay raw {p['genuine_raw_agree']}/121; "
                f"binary-mapped {p['binary_mapped_agree']}/121; "
                f"κ(category)={p['kappa_category']:.3f}\n"
            )

    md.append("\n## Interpretation notes\n\n")
    md.append(
        "- κ alone is not validity evidence; interpret with prevalence and binary estimand.\n"
        "- `INSUFFICIENT_EVIDENCE` is treated as **not** counting in the YES numerator "
        "(mapped to False for binary agreement with primary).\n"
        "- If an auditor is non-expert / incomplete evidence review, treat their stream as "
        "provisional and invite revision before adjudication.\n"
    )

    (OUT / "rq2_agreement_summary.md").write_text("".join(md), encoding="utf-8")

    # machine summary csv
    with (OUT / "agreement_vs_primary.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "auditor",
            "yes_numerator",
            "no",
            "insufficient_evidence",
            "category_agree",
            "kappa_category",
            "binary_agree",
            "tp",
            "tn",
            "fp",
            "fn",
            "neg_agreement",
            "headline_disagreements",
        ]
        w = csv.DictWriter(handle, fieldnames=fields)
        w.writeheader()
        for res in results:
            w.writerow(
                {
                    "auditor": res["name"],
                    "yes_numerator": res["yes_num"],
                    "no": res["no_num"],
                    "insufficient_evidence": res["ie_num"],
                    "category_agree": res["raw_agree"],
                    "kappa_category": f"{res['kappa']:.4f}",
                    "binary_agree": res["bin_agree"],
                    "tp": res["tp"],
                    "tn": res["tn"],
                    "fp": res["fp"],
                    "fn": res["fn"],
                    "neg_agreement": f"{res['neg_agree']:.4f}",
                    "headline_disagreements": len(res["headline"]),
                }
            )

    if pair_rows:
        with (OUT / "agreement_inter_auditor.csv").open("w", newline="", encoding="utf-8") as handle:
            fields = list(pair_rows[0].keys())
            w = csv.DictWriter(handle, fieldnames=fields)
            w.writeheader()
            for p in pair_rows:
                row = dict(p)
                row["kappa_category"] = f"{p['kappa_category']:.4f}"
                w.writerow(row)

    print("".join(md))
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
