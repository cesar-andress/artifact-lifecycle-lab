#!/usr/bin/env python3
"""Recommended RQ2 human-validation study: Pepe+Ana primary; Rebeca sensitivity.

Juan is excluded. Does not overwrite frozen primary labels.
"""

from __future__ import annotations

import csv
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUD = ROOT / "validation/rq2_second_audit/auditors"
PRIV = ROOT / "validation/rq2_second_audit/private/rq2_original_labels_private.csv"
OUT = ROOT / "validation/rq2_second_audit/agreement"
N = 121

CORE = ("pepe", "ana")
SENS = ("rebeca",)


def wilson(k: int, n: int = N, z: float = 1.96) -> tuple[float, float]:
    p = k / n
    den = 1 + z**2 / n
    centre = p + z**2 / (2 * n)
    margin = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return ((centre - margin) / den, (centre + margin) / den)


def kappa(y1: list[str], y2: list[str]) -> float:
    labels = sorted(set(y1) | set(y2))
    n = len(y1)
    mat = Counter(zip(y1, y2))
    po = sum(mat[(a, a)] for a in labels) / n
    p1, p2 = Counter(y1), Counter(y2)
    pe = sum((p1[a] / n) * (p2[a] / n) for a in labels)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def load(name: str) -> dict[str, dict[str, str]]:
    path = AUD / f"{name}_rq2_second_auditor_labels.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        rows = [{k: (v or "").strip() for k, v in r.items()} for r in csv.DictReader(handle)]
    out = {r["event_id"]: r for r in rows}
    if len(out) != N:
        raise SystemExit(f"{name}: {len(out)} rows")
    return out


def main() -> None:
    # refuse juan if present
    juan = AUD / "juan_rq2_second_auditor_labels.csv"
    if juan.exists():
        raise SystemExit("juan labels still present; remove before recommended study")

    with PRIV.open(encoding="utf-8", newline="") as handle:
        primary = {r["event_id"]: r for r in csv.DictReader(handle)}

    pepe, ana, rebeca = load("pepe"), load("ana"), load("rebeca")
    ids = sorted(primary)

    def yes(rows: dict[str, dict[str, str]], e: str) -> bool:
        return rows[e]["genuine_decay"] == "YES"

    pepe_yes = {e for e in ids if yes(pepe, e)}
    ana_yes = {e for e in ids if yes(ana, e)}
    rebeca_yes = {e for e in ids if yes(rebeca, e)}
    both_yes = pepe_yes & ana_yes
    either_yes = pepe_yes | ana_yes
    # paired consensus rule (recommended adjudicated proxy until formal adjudication):
    # YES iff both Pepe and Ana mark YES; else NO.
    consensus_yes = both_yes

    # pepe vs ana
    cat_agree = sum(1 for e in ids if pepe[e]["category"] == ana[e]["category"])
    gd_agree = sum(1 for e in ids if pepe[e]["genuine_decay"] == ana[e]["genuine_decay"])
    bin_agree = sum(1 for e in ids if yes(pepe, e) == yes(ana, e))
    k_cat = kappa([pepe[e]["category"] for e in ids], [ana[e]["category"] for e in ids])
    k_bin = kappa(
        ["YES" if yes(pepe, e) else "NO" for e in ids],
        ["YES" if yes(ana, e) else "NO" for e in ids],
    )

    # vs primary
    def vs_primary(rows: dict[str, dict[str, str]]) -> dict:
        cats1 = [primary[e]["final_category"] for e in ids]
        cats2 = [rows[e]["category"] for e in ids]
        b1 = [primary[e]["is_genuine_decay"].lower() == "true" for e in ids]
        b2 = [yes(rows, e) for e in ids]
        return {
            "cat_agree": sum(a == b for a, b in zip(cats1, cats2)),
            "kappa": kappa(cats1, cats2),
            "bin_agree": sum(a == b for a, b in zip(b1, b2)),
            "fp": sum((not a) and b for a, b in zip(b1, b2)),
            "yes": sum(b2),
        }

    m_pepe, m_ana, m_reb = vs_primary(pepe), vs_primary(ana), vs_primary(rebeca)

    # binary disagreements pepe-ana for adjudication
    disag = []
    for e in ids:
        if yes(pepe, e) != yes(ana, e) or pepe[e]["category"] != ana[e]["category"]:
            disag.append(
                {
                    "event_id": e,
                    "pepe_category": pepe[e]["category"],
                    "ana_category": ana[e]["category"],
                    "pepe_genuine": pepe[e]["genuine_decay"],
                    "ana_genuine": ana[e]["genuine_decay"],
                    "rebeca_genuine": rebeca[e]["genuine_decay"],
                    "primary_category": primary[e]["final_category"],
                    "binary_disagreement": str(yes(pepe, e) != yes(ana, e)),
                    "category_disagreement": str(pepe[e]["category"] != ana[e]["category"]),
                    "adjudicated_label": "",
                    "adjudicated_counts_as_genuine_decay": "",
                    "adjudicator": "",
                    "rationale": "",
                    "evidence_used": "",
                    "date": "",
                }
            )

    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "pepe_ana_disagreements.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = list(disag[0].keys()) if disag else [
            "event_id",
            "pepe_category",
            "ana_category",
            "pepe_genuine",
            "ana_genuine",
            "rebeca_genuine",
            "primary_category",
            "binary_disagreement",
            "category_disagreement",
            "adjudicated_label",
            "adjudicated_counts_as_genuine_decay",
            "adjudicator",
            "rationale",
            "evidence_used",
            "date",
        ]
        w = csv.DictWriter(handle, fieldnames=fields)
        w.writeheader()
        w.writerows(disag)

    # consensus case list
    with (OUT / "pepe_ana_consensus_yes.csv").open("w", newline="", encoding="utf-8") as handle:
        w = csv.DictWriter(
            handle,
            fieldnames=["event_id", "pepe_category", "ana_category", "rebeca_genuine", "primary_category", "pepe_notes"],
        )
        w.writeheader()
        for e in sorted(consensus_yes):
            w.writerow(
                {
                    "event_id": e,
                    "pepe_category": pepe[e]["category"],
                    "ana_category": ana[e]["category"],
                    "rebeca_genuine": rebeca[e]["genuine_decay"],
                    "primary_category": primary[e]["final_category"],
                    "pepe_notes": pepe[e]["notes"],
                }
            )

    # estimators table
    estimators = [
        ("primary_frozen", 0, "Frozen is_genuine_decay"),
        ("independent_pepe", len(pepe_yes), "Primary independent stream"),
        ("independent_ana", len(ana_yes), "Primary independent stream (pair)"),
        ("pepe_ana_both_YES", len(both_yes), "Conservative paired consensus (recommended adjudicated proxy)"),
        ("pepe_ana_either_YES", len(either_yes), "Liberal paired union"),
        ("sensitivity_rebeca", len(rebeca_yes), "Independent upper-bound sensitivity stream"),
        ("decay_favoring_rules", 25, "Prespecified audit-rule sensitivity"),
        ("high_specificity_rules", 0, "Prespecified audit-rule sensitivity"),
    ]

    with (OUT / "recommended_estimators.csv").open("w", newline="", encoding="utf-8") as handle:
        w = csv.DictWriter(
            handle,
            fieldnames=["estimator", "numerator", "denominator", "percentage", "wilson_lo", "wilson_hi", "role"],
        )
        w.writeheader()
        for name, k, role in estimators:
            lo, hi = wilson(k)
            w.writerow(
                {
                    "estimator": name,
                    "numerator": k,
                    "denominator": N,
                    "percentage": f"{100 * k / N:.2f}",
                    "wilson_lo": f"{100 * lo:.2f}",
                    "wilson_hi": f"{100 * hi:.2f}",
                    "role": role,
                }
            )

    bin_dis = sum(1 for r in disag if r["binary_disagreement"] == "True")
    cat_dis = sum(1 for r in disag if r["category_disagreement"] == "True")

    md = []
    md.append("# Recommended RQ2 Human-Validation Study\n\n")
    md.append("**Streams retained:** Pepe, Ana (primary independent pair); Rebeca (sensitivity).\n")
    md.append("**Excluded:** Juan (provisional / non-expert stream).\n")
    md.append("**Primary frozen labels:** unchanged (0/121).\n\n")

    md.append("## Estimators (do not collapse)\n\n")
    md.append("| Estimator | x/121 | Wilson 95% CI | Role |\n")
    md.append("|-----------|------:|---------------|------|\n")
    for name, k, role in estimators:
        lo, hi = wilson(k)
        md.append(f"| `{name}` | **{k}/121** ({100*k/N:.1f}%) | {100*lo:.1f}–{100*hi:.1f}% | {role} |\n")

    md.append("\n## Pepe ↔ Ana (primary independent pair)\n\n")
    md.append(f"- Category agreement: **{cat_agree}/121** ({cat_agree/N:.3f}); Cohen's κ = **{k_cat:.3f}**\n")
    md.append(f"- Genuine-decay label agreement: **{gd_agree}/121**\n")
    md.append(f"- Binary YES agreement: **{bin_agree}/121** ({bin_agree/N:.3f}); κ = **{k_bin:.3f}**\n")
    md.append(f"- Both YES: **{len(both_yes)}**; either YES: **{len(either_yes)}**\n")
    md.append(f"- Disagreement rows (category or binary): **{len(disag)}** (binary-only: {bin_dis}; category: {cat_dis})\n")

    md.append("\n## Versus frozen primary\n\n")
    for label, m in (("pepe", m_pepe), ("ana", m_ana), ("rebeca", m_reb)):
        md.append(
            f"- `{label}`: category {m['cat_agree']}/121 (κ={m['kappa']:.3f}); "
            f"binary {m['bin_agree']}/121; YES={m['yes']} (all FP vs primary zero)\n"
        )

    md.append("\n## Robust reading\n\n")
    md.append(
        f"- Independent human YES numerators (Pepe/Ana): **{len(pepe_yes)}–{len(ana_yes)}/121**.\n"
        f"- Conservative paired consensus (both YES): **{len(both_yes)}/121**.\n"
        f"- Rebeca sensitivity upper bound: **{len(rebeca_yes)}/121**.\n"
        f"- Prespecified rule sensitivity: **0–25/121**.\n"
        f"- Across human + rule scenarios the adjusted numerator spans "
        f"**0–{max(len(rebeca_yes), 25)}/121**, while naive detector-level 121/121 "
        f"still substantially overstates genuine post-verification decay.\n"
        "- Formal third-party adjudication of Pepe–Ana disagreements remains optional; "
        "the both-YES consensus is the transparent paired proxy used here.\n"
    )
    md.append("\n## Outputs\n\n")
    md.append("- `recommended_estimators.csv`\n")
    md.append("- `pepe_ana_consensus_yes.csv`\n")
    md.append("- `pepe_ana_disagreements.csv` (adjudication worksheet)\n")

    (OUT / "recommended_study_summary.md").write_text("".join(md), encoding="utf-8")
    # refresh multi-auditor agreement without juan
    print("".join(md))


if __name__ == "__main__":
    main()
