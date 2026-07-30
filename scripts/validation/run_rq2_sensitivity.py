#!/usr/bin/env python3
"""Prespecified RQ2 audit-rule sensitivity (scenarios locked in protocol)."""

from __future__ import annotations

import csv
import hashlib
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "exports" / "truth_decay_pilot" / "rq2_failure_audit.csv"
OUT = ROOT / "validation" / "rq2_sensitivity"
SECOND = ROOT / "validation" / "rq2_second_audit" / "rq2_second_auditor_labels.csv"
ADJ = ROOT / "validation" / "rq2_second_audit" / "rq2_disagreement_adjudication.csv"
N = 121


def event_id(row: dict[str, str]) -> str:
    key = "|".join(
        [
            row["repo_id"],
            row["instruction_path"],
            row["reference_type"],
            row["reference"],
            row["failure_commit"],
        ]
    )
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def _bool(v: str) -> bool:
    return str(v).strip().lower() in {"1", "true", "yes", "t"}


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z**2 / n
    centre = p + z**2 / (2 * n)
    margin = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return ((centre - margin) / den, (centre + margin) / den)


def load_audit() -> list[dict[str, str]]:
    with SRC.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != N:
        raise SystemExit(f"expected {N} rows, got {len(rows)}")
    for row in rows:
        row["_event_id"] = event_id(row)
    return rows


def scenario_primary(row: dict[str, str]) -> bool:
    return _bool(row["is_genuine_decay"]) or row["final_category"] == "genuine_decay"


def scenario_decay_favoring(row: dict[str, str]) -> bool:
    if row["final_category"] in {
        "genuine_decay",
        "ambiguous",
        "verification_anchor_issue",
    }:
        return True
    if _bool(row["returned_after_missing"]):
        return True
    if _bool(row["basename_collision_verified"]):
        return True
    return False


def scenario_high_specificity(row: dict[str, str]) -> bool:
    return row["final_category"] == "genuine_decay"


def load_second_labels() -> dict[str, bool] | None:
    if not SECOND.exists():
        return None
    with SECOND.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    out = {r["event_id"]: _bool(r["counts_as_genuine_decay"]) for r in rows}
    if len(out) != N:
        raise SystemExit(f"second auditor labels incomplete: {len(out)}/{N}")
    return out


def load_adjudicated() -> dict[str, bool] | None:
    if not ADJ.exists():
        return None
    with ADJ.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    # Expect columns event_id, adjudicated_counts_as_genuine_decay
    key = "adjudicated_counts_as_genuine_decay"
    if rows and key not in rows[0]:
        key = "adjudicated_is_genuine_decay"
    out = {r["event_id"]: _bool(r[key]) for r in rows}
    if len(out) != N:
        # adjudication may cover disagreements only — not a full scenario
        return None
    return out


def compose_categories(rows: list[dict[str, str]], mask: list[bool]) -> str:
    c = Counter()
    for row, flag in zip(rows, mask):
        if flag:
            c["counted_as_genuine"] += 1
        else:
            c[row["final_category"]] += 1
    return "; ".join(f"{k}={v}" for k, v in sorted(c.items()))


def main() -> int:
    rows = load_audit()
    primary_mask = [scenario_primary(r) for r in rows]
    if sum(primary_mask) != 0:
        raise SystemExit("PRIMARY FREEZE VIOLATION: expected 0 genuine decay")

    scenarios: list[tuple[str, list[bool], str]] = [
        (
            "primary_frozen",
            primary_mask,
            "Frozen is_genuine_decay / final_category==genuine_decay",
        ),
        (
            "decay_favoring",
            [scenario_decay_favoring(r) for r in rows],
            "ambiguous + verification_anchor_issue + returned_after_missing + basename_collision → genuine",
        ),
        (
            "high_specificity",
            [scenario_high_specificity(r) for r in rows],
            "Only unequivocal final_category==genuine_decay",
        ),
    ]

    second = load_second_labels()
    if second is not None:
        scenarios.append(
            (
                "second_auditor",
                [second[r["_event_id"]] for r in rows],
                "Independent human counts_as_genuine_decay",
            )
        )
    adj = load_adjudicated()
    if adj is not None:
        scenarios.append(
            (
                "adjudicated",
                [adj[r["_event_id"]] for r in rows],
                "Adjudicated binary estimand for all 121 events",
            )
        )

    OUT.mkdir(parents=True, exist_ok=True)
    summary_rows = []
    change_rows = []

    for name, mask, rationale in scenarios:
        k = sum(mask)
        lo, hi = wilson(k, N)
        summary_rows.append(
            {
                "scenario": name,
                "numerator": k,
                "denominator": N,
                "percentage": f"{100 * k / N:.2f}",
                "wilson_lo": f"{100 * lo:.2f}",
                "wilson_hi": f"{100 * hi:.2f}",
                "category_composition": compose_categories(rows, mask),
                "rationale": rationale,
                "available": "yes",
            }
        )
        for row, pflag, mflag in zip(rows, primary_mask, mask):
            if pflag != mflag:
                change_rows.append(
                    {
                        "scenario": name,
                        "event_id": row["_event_id"],
                        "repo_id": row["repo_id"],
                        "repo_url": row["repo_url"],
                        "reference": row["reference"],
                        "frozen_final_category": row["final_category"],
                        "primary_genuine": str(pflag),
                        "scenario_genuine": str(mflag),
                        "returned_after_missing": row["returned_after_missing"],
                        "basename_collision_verified": row["basename_collision_verified"],
                        "change_direction": (
                            "primary_false_to_genuine" if mflag and not pflag else "primary_genuine_to_false"
                        ),
                    }
                )

    # Record unavailable human scenarios explicitly
    for missing_name, path in [
        ("second_auditor", SECOND),
        ("adjudicated", ADJ),
    ]:
        if missing_name not in {s[0] for s in scenarios}:
            summary_rows.append(
                {
                    "scenario": missing_name,
                    "numerator": "",
                    "denominator": N,
                    "percentage": "",
                    "wilson_lo": "",
                    "wilson_hi": "",
                    "category_composition": "",
                    "rationale": f"Not computed; missing {path.relative_to(ROOT)}",
                    "available": "no",
                }
            )

    scen_path = OUT / "rq2_sensitivity_scenarios.csv"
    with scen_path.open("w", newline="", encoding="utf-8") as handle:
        fields = list(summary_rows[0].keys())
        w = csv.DictWriter(handle, fieldnames=fields)
        w.writeheader()
        w.writerows(summary_rows)

    chg_path = OUT / "rq2_sensitivity_case_changes.csv"
    with chg_path.open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "scenario",
            "event_id",
            "repo_id",
            "repo_url",
            "reference",
            "frozen_final_category",
            "primary_genuine",
            "scenario_genuine",
            "returned_after_missing",
            "basename_collision_verified",
            "change_direction",
        ]
        w = csv.DictWriter(handle, fieldnames=fields)
        w.writeheader()
        w.writerows(change_rows)

    available = [r for r in summary_rows if r["available"] == "yes"]
    nums = [int(r["numerator"]) for r in available]
    md = []
    md.append("# RQ2 Audit-Rule Sensitivity Summary\n")
    md.append("Scenarios were locked in `docs/VALIDATION_EXTENSION_PROTOCOL.md` before aggregates were computed.\n")
    md.append("## Scenario estimates\n")
    md.append("| Scenario | Estimate | Wilson 95% CI | Available |\n")
    md.append("|----------|---------:|---------------|-----------|\n")
    for r in summary_rows:
        if r["available"] == "yes":
            md.append(
                f"| `{r['scenario']}` | {r['numerator']}/{r['denominator']} ({r['percentage']}%) "
                f"| {r['wilson_lo']}–{r['wilson_hi']}% | yes |\n"
            )
        else:
            md.append(f"| `{r['scenario']}` | — | — | no |\n")
    md.append("\n## Robust range (available scenarios)\n")
    md.append(f"- Minimum numerator: **{min(nums)}/{N}**\n")
    md.append(f"- Maximum numerator: **{max(nums)}/{N}**\n")
    md.append(
        "- Primary frozen estimate remains **0/121**; sensitivity does not replace it.\n"
    )
    md.append("\n## Case changes vs primary\n")
    md.append(f"- Total changed case-rows across scenarios: **{len(change_rows)}**\n")
    by = Counter(r["scenario"] for r in change_rows)
    for scen, n in sorted(by.items()):
        md.append(f"- `{scen}`: {n} events reclassified relative to primary\n")
    md.append("\n## Interpretation guardrail\n")
    md.append(
        "If any available scenario is non-zero, report it plainly. The robust claim is the "
        "range across prespecified scenarios, not the literal zero alone.\n"
    )
    if second is None:
        md.append(
            "\n**Note:** `second_auditor` and `adjudicated` scenarios await real human labels; "
            "they were not simulated.\n"
        )
    (OUT / "rq2_sensitivity_summary.md").write_text("".join(md), encoding="utf-8")

    print(f"wrote {scen_path}")
    print(f"wrote {chg_path}")
    print(f"range={min(nums)}-{max(nums)} / {N}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
