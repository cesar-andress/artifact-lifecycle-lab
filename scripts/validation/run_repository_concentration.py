#!/usr/bin/env python3
"""Repository-concentration analyses on frozen born-stale / GFC exports."""

from __future__ import annotations

import csv
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[2]
BORN = ROOT / "exports" / "truth_decay_pilot" / "born_stale_taxonomy.csv"
GFC = ROOT / "exports" / "truth_decay_pilot" / "gfc_confirmatory_audit.csv"
OUT = ROOT / "validation" / "concentration"

EXPECTED = {
    "born_stale_all": 17747,
    "prior_gfc": 1405,
    "confirmed_false": 1200,
}


def _bool(v: str) -> bool:
    return str(v).strip().lower() in {"1", "true", "yes", "t"}


def quantiles(values: list[float]) -> dict[str, float]:
    if not values:
        return {"min": 0, "q1": 0, "median": 0, "q3": 0, "max": 0}
    xs = sorted(values)
    n = len(xs)

    def q(p: float) -> float:
        if n == 1:
            return xs[0]
        idx = p * (n - 1)
        lo = int(math.floor(idx))
        hi = int(math.ceil(idx))
        if lo == hi:
            return xs[lo]
        w = idx - lo
        return xs[lo] * (1 - w) + xs[hi] * w

    return {
        "min": xs[0],
        "q1": q(0.25),
        "median": median(xs),
        "q3": q(0.75),
        "max": xs[-1],
    }


def hhi(shares: list[float]) -> float:
    """HHI on proportions that sum to 1, scaled 0–10000."""
    return sum((100 * s) ** 2 for s in shares)


def top_share(counts: list[int], k: int) -> float:
    total = sum(counts)
    if total == 0:
        return 0.0
    return sum(sorted(counts, reverse=True)[:k]) / total


def analyze_cohort(
    name: str,
    rows: list[dict[str, str]],
    all_repos: set[str],
) -> tuple[list[dict], list[dict], dict]:
    by_repo: Counter[str] = Counter(r["repo_id"] for r in rows)
    # include zeros for repos in frame with no cases
    for rid in all_repos:
        by_repo.setdefault(rid, 0)
    n_cases = sum(by_repo.values())
    n_repos = len(by_repo)
    counts = list(by_repo.values())
    rates = [c / n_cases if n_cases else 0.0 for c in counts]  # share of cases
    # repo-level rate among repos that appear in this cohort's parent frame:
    # for concentration of cases we use case shares; for balanced estimand we need
    # a denominator per repo. Use each repo's total born-stale refs when provided via row flag.
    q = quantiles([float(c) for c in counts])
    shares = [c / n_cases if n_cases else 0.0 for c in sorted(counts, reverse=True)]
    summary = {
        "cohort": name,
        "n_cases": n_cases,
        "n_repos_in_frame": n_repos,
        "n_repos_with_zero": sum(1 for c in counts if c == 0),
        "median_count": q["median"],
        "iqr_low": q["q1"],
        "iqr_high": q["q3"],
        "min_count": q["min"],
        "max_count": q["max"],
        "top1_share": top_share(counts, 1),
        "top5_share": top_share(counts, 5),
        "top10_share": top_share(counts, 10),
        "hhi": hhi([c / n_cases for c in counts if n_cases]),
        "most_influential_repo": max(by_repo.items(), key=lambda kv: kv[1])[0] if by_repo else "",
    }

    count_rows = []
    for rid, c in sorted(by_repo.items(), key=lambda kv: (-kv[1], kv[0])):
        count_rows.append(
            {
                "cohort": name,
                "repo_id": rid,
                "n_cases": c,
                "share": (c / n_cases) if n_cases else 0.0,
            }
        )

    # leave-one-repo-out on pooled proportion needs a cohort-specific success definition.
    # For case-count cohorts we recompute the pooled case total share of the global
    # parent denominator when provided; otherwise LOO on the cohort total itself.
    return count_rows, [], summary


def leave_one_out_proportion(
    name: str,
    rows: list[dict[str, str]],
    success_fn,
    denom_rows: list[dict[str, str]] | None = None,
) -> list[dict]:
    """Recompute pooled proportion excluding each repository."""
    if denom_rows is None:
        denom_rows = rows
    repos = sorted({r["repo_id"] for r in denom_rows})
    out = []
    base_num = sum(1 for r in rows if success_fn(r))
    base_den = len(denom_rows)
    for rid in repos:
        num = sum(1 for r in rows if r["repo_id"] != rid and success_fn(r))
        den = sum(1 for r in denom_rows if r["repo_id"] != rid)
        prop = (num / den) if den else float("nan")
        out.append(
            {
                "cohort": name,
                "excluded_repo_id": rid,
                "numerator": num,
                "denominator": den,
                "proportion": prop,
                "delta_vs_full": prop - (base_num / base_den if base_den else float("nan")),
            }
        )
    return out


def template_cluster_sensitivity(born_rows: list[dict[str, str]]) -> list[dict]:
    """Deterministic repeated (instruction_path, reference) clusters."""
    clusters: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for r in born_rows:
        try:
            rep = int(float(r.get("repeated_repo_count") or 0))
        except ValueError:
            rep = 0
        cat = r.get("final_category") or r.get("heuristic_category") or ""
        if rep >= 5 and cat in {
            "template_placeholder",
            "extraction_artifact",
            "normative_prescriptive",
        }:
            clusters[(r["instruction_path"], r["reference"])].append(r)

    # rank clusters by size
    ranked = sorted(clusters.items(), key=lambda kv: -len(kv[1]))
    results = []
    # baseline confirmed-false among prior GFC is separate; here exclude clusters from born-stale totals
    n_all = len(born_rows)
    n_gfc = sum(1 for r in born_rows if r.get("final_category") == "genuine_false_claim")
    results.append(
        {
            "exclusion": "none",
            "n_clusters_excluded": 0,
            "n_rows_excluded": 0,
            "born_stale_remaining": n_all,
            "prior_gfc_remaining": n_gfc,
            "prior_gfc_rate_among_remaining": n_gfc / n_all if n_all else 0.0,
        }
    )
    excluded: set[int] = set()
    # identify by object id via enumeration
    row_index = {id(r): i for i, r in enumerate(born_rows)}
    for k in (1, 3, 5, 10):
        drop_idx: set[int] = set()
        for (_key, members) in ranked[:k]:
            for r in members:
                drop_idx.add(row_index[id(r)])
        rem = [r for i, r in enumerate(born_rows) if i not in drop_idx]
        n_rem = len(rem)
        gfc_rem = sum(1 for r in rem if r.get("final_category") == "genuine_false_claim")
        results.append(
            {
                "exclusion": f"top_{k}_repeated_templateish_clusters",
                "n_clusters_excluded": min(k, len(ranked)),
                "n_rows_excluded": len(drop_idx),
                "born_stale_remaining": n_rem,
                "prior_gfc_remaining": gfc_rem,
                "prior_gfc_rate_among_remaining": gfc_rem / n_rem if n_rem else 0.0,
            }
        )
        excluded |= drop_idx
    return results


def repo_balanced_rates(
    name: str,
    case_rows: list[dict[str, str]],
    denom_by_repo: dict[str, int],
) -> dict:
    """Unweighted mean/median of repo-level rates (sensitivity estimand)."""
    cases = Counter(r["repo_id"] for r in case_rows)
    rates = []
    for rid, den in denom_by_repo.items():
        if den <= 0:
            continue
        rates.append(cases.get(rid, 0) / den)
    if not rates:
        return {
            "cohort": name,
            "n_repos": 0,
            "pooled_rate": "",
            "unweighted_mean_repo_rate": "",
            "median_repo_rate": "",
        }
    pooled_num = sum(cases.get(rid, 0) for rid in denom_by_repo)
    pooled_den = sum(denom_by_repo.values())
    return {
        "cohort": name,
        "n_repos": len(rates),
        "pooled_rate": pooled_num / pooled_den if pooled_den else "",
        "unweighted_mean_repo_rate": sum(rates) / len(rates),
        "median_repo_rate": median(rates),
    }


def main() -> int:
    with BORN.open(newline="", encoding="utf-8") as handle:
        born = list(csv.DictReader(handle))
    with GFC.open(newline="", encoding="utf-8") as handle:
        gfc = list(csv.DictReader(handle))

    if len(born) != EXPECTED["born_stale_all"]:
        raise SystemExit(f"born-stale freeze violation: {len(born)}")
    prior_gfc = [r for r in born if r.get("final_category") == "genuine_false_claim"]
    if len(prior_gfc) != EXPECTED["prior_gfc"]:
        raise SystemExit(f"prior GFC freeze violation: {len(prior_gfc)}")
    if len(gfc) != EXPECTED["prior_gfc"]:
        raise SystemExit(f"gfc audit freeze violation: {len(gfc)}")
    confirmed = [r for r in gfc if _bool(r.get("is_confirmed_false", ""))]
    if len(confirmed) != EXPECTED["confirmed_false"]:
        raise SystemExit(f"confirmed-false freeze violation: {len(confirmed)}")

    all_repos = {r["repo_id"] for r in born}
    OUT.mkdir(parents=True, exist_ok=True)

    cohorts = {
        "born_stale_all": born,
        "prior_genuine_false_claim": prior_gfc,
        "confirmed_false_at_birth": confirmed,
    }
    # major categories
    for cat, n_expect in [
        ("normative_prescriptive", None),
        ("verification_anchor_mismatch", None),
        ("extraction_artifact", None),
        ("template_placeholder", None),
        ("genuine_false_claim", 1405),
    ]:
        subset = [r for r in born if r.get("final_category") == cat]
        if n_expect is not None and len(subset) != n_expect:
            raise SystemExit(f"category {cat} count {len(subset)} != {n_expect}")
        cohorts[f"born_stale_category__{cat}"] = subset

    all_count_rows: list[dict] = []
    summaries: list[dict] = []
    for name, rows in cohorts.items():
        count_rows, _, summary = analyze_cohort(name, rows, all_repos)
        all_count_rows.extend(count_rows)
        summaries.append(summary)

    # LOO for principal pooled proportions
    loo_rows: list[dict] = []
    # confirmed-false among GFC audit (1200/1405)
    loo_rows.extend(
        leave_one_out_proportion(
            "confirmed_false_among_prior_gfc",
            gfc,
            lambda r: _bool(r.get("is_confirmed_false", "")),
            denom_rows=gfc,
        )
    )
    # prior GFC among born-stale
    loo_rows.extend(
        leave_one_out_proportion(
            "prior_gfc_among_born_stale",
            born,
            lambda r: r.get("final_category") == "genuine_false_claim",
            denom_rows=born,
        )
    )

    # repo-balanced
    denom_born = Counter(r["repo_id"] for r in born)
    denom_gfc = Counter(r["repo_id"] for r in gfc)
    balanced = [
        repo_balanced_rates("prior_gfc_among_born_stale", prior_gfc, dict(denom_born)),
        repo_balanced_rates("confirmed_false_among_prior_gfc", confirmed, dict(denom_gfc)),
    ]

    tmpl = template_cluster_sensitivity(born)

    # write outputs
    with (OUT / "repository_counts.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = ["cohort", "repo_id", "n_cases", "share"]
        w = csv.DictWriter(handle, fieldnames=fields)
        w.writeheader()
        for r in all_count_rows:
            w.writerow(
                {
                    "cohort": r["cohort"],
                    "repo_id": r["repo_id"],
                    "n_cases": r["n_cases"],
                    "share": f"{r['share']:.6f}",
                }
            )

    with (OUT / "leave_one_repo_out.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "cohort",
            "excluded_repo_id",
            "numerator",
            "denominator",
            "proportion",
            "delta_vs_full",
        ]
        w = csv.DictWriter(handle, fieldnames=fields)
        w.writeheader()
        for r in loo_rows:
            w.writerow(
                {
                    **r,
                    "proportion": f"{r['proportion']:.6f}",
                    "delta_vs_full": f"{r['delta_vs_full']:.6f}",
                }
            )

    with (OUT / "template_cluster_sensitivity.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        fields = list(tmpl[0].keys())
        w = csv.DictWriter(handle, fieldnames=fields)
        w.writeheader()
        for r in tmpl:
            row = dict(r)
            row["prior_gfc_rate_among_remaining"] = f"{r['prior_gfc_rate_among_remaining']:.6f}"
            w.writerow(row)

    with (OUT / "concentration_summaries.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = list(summaries[0].keys())
        w = csv.DictWriter(handle, fieldnames=fields)
        w.writeheader()
        for s in summaries:
            row = dict(s)
            for k in ("top1_share", "top5_share", "top10_share"):
                row[k] = f"{s[k]:.6f}"
            row["hhi"] = f"{s['hhi']:.4f}"
            w.writerow(row)

    with (OUT / "repo_balanced_rates.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = list(balanced[0].keys())
        w = csv.DictWriter(handle, fieldnames=fields)
        w.writeheader()
        for r in balanced:
            out = dict(r)
            for k in ("pooled_rate", "unweighted_mean_repo_rate", "median_repo_rate"):
                if out[k] != "":
                    out[k] = f"{float(out[k]):.6f}"
            w.writerow(out)

    # markdown summary
    md = ["# Repository Concentration Summary\n\n"]
    md.append(
        "Frame: enriched E1–100 observational exports. "
        "These analyses do **not** claim external representativeness.\n\n"
    )
    md.append("## Cohort concentration\n\n")
    md.append(
        "| Cohort | Cases | Repos (zeros) | Top1 | Top5 | Top10 | HHI | Max repo |\n"
        "|--------|------:|---------------|-----:|-----:|------:|----:|----------|\n"
    )
    for s in summaries:
        if not s["cohort"].startswith("born_stale_category__") or s["cohort"].endswith(
            "genuine_false_claim"
        ):
            # show main cohorts + gfc category
            pass
        show = s["cohort"] in {
            "born_stale_all",
            "prior_genuine_false_claim",
            "confirmed_false_at_birth",
            "born_stale_category__genuine_false_claim",
            "born_stale_category__template_placeholder",
            "born_stale_category__normative_prescriptive",
            "born_stale_category__verification_anchor_mismatch",
            "born_stale_category__extraction_artifact",
        }
        if not show:
            continue
        md.append(
            f"| `{s['cohort']}` | {s['n_cases']} | {s['n_repos_in_frame']} "
            f"({s['n_repos_with_zero']} zero) | {100*s['top1_share']:.1f}% | "
            f"{100*s['top5_share']:.1f}% | {100*s['top10_share']:.1f}% | "
            f"{s['hhi']:.0f} | `{s['most_influential_repo']}` |\n"
        )

    md.append("\n## Leave-one-repository-out\n\n")
    for cohort in sorted({r["cohort"] for r in loo_rows}):
        subset = [r for r in loo_rows if r["cohort"] == cohort]
        props = [r["proportion"] for r in subset]
        # most influential = largest absolute delta
        infl = max(subset, key=lambda r: abs(r["delta_vs_full"]))
        md.append(f"### `{cohort}`\n")
        md.append(
            f"- Full-sample proportion recomputed over LOO exclusions: "
            f"min={min(props):.4f}, max={max(props):.4f}, "
            f"range={max(props)-min(props):.4f}\n"
        )
        md.append(
            f"- Most influential exclusion: `{infl['excluded_repo_id']}` "
            f"(Δ={infl['delta_vs_full']:+.4f})\n\n"
        )

    md.append("## Repository-balanced sensitivity\n\n")
    md.append(
        "Unweighted mean/median of repository-level rates (sensitivity estimand, "
        "not a population estimate).\n\n"
    )
    for r in balanced:
        md.append(
            f"- `{r['cohort']}`: pooled={float(r['pooled_rate']):.4f}, "
            f"mean_repo={float(r['unweighted_mean_repo_rate']):.4f}, "
            f"median_repo={float(r['median_repo_rate']):.4f}\n"
        )

    md.append("\n## Template-cluster sensitivity\n\n")
    md.append(
        "Deterministic clusters: exact `(instruction_path, reference)` with "
        "`repeated_repo_count >= 5` and category in "
        "{template_placeholder, extraction_artifact, normative_prescriptive}.\n\n"
    )
    for r in tmpl:
        md.append(
            f"- `{r['exclusion']}`: excluded {r['n_rows_excluded']} rows / "
            f"{r['n_clusters_excluded']} clusters; "
            f"prior GFC remaining rate={r['prior_gfc_rate_among_remaining']:.4f}\n"
        )

    (OUT / "concentration_summary.md").write_text("".join(md), encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
