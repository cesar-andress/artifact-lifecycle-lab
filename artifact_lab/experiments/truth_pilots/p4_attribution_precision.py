"""Gate P4 — Agent attribution precision audit (human-review worksheet)."""

from __future__ import annotations

import csv
import random
import re
from collections import Counter
from pathlib import Path

from artifact_lab.execution.atomic_io import atomic_write_text
from artifact_lab.experiments.truth_pilots.gates_common import write_csv

PRECISION_KILL_THRESHOLD = 0.80

DEPENDENCY_BOT_PATTERNS = (
    re.compile(r"dependabot", re.IGNORECASE),
    re.compile(r"renovate", re.IGNORECASE),
    re.compile(r"github-actions", re.IGNORECASE),
    re.compile(r"security-bot", re.IGNORECASE),
    re.compile(r"snyk-bot", re.IGNORECASE),
)

AGENT_TOOL_LABELS = ("claude", "cursor", "copilot", "openai", "aider", "devin", "codeium")


def _is_dependency_bot(author_name: str, author_email: str, evidence: str) -> bool:
    combined = f"{author_name} {author_email} {evidence}"
    return any(pat.search(combined) for pat in DEPENDENCY_BOT_PATTERNS)


def categorize_signature(
    *,
    attribution_class: str,
    signature_type: str,
    author_name: str,
    author_email: str,
    evidence: str,
) -> tuple[str, bool]:
    """Return (signature_category, counts_as_agent_maintenance)."""
    combined = f"{author_name} {author_email} {evidence}"

    if re.search(r"dependabot", combined, re.I):
        return "dependabot_renovate_security_bot", False
    if re.search(r"renovate", combined, re.I):
        return "dependabot_renovate_security_bot", False
    if re.search(r"github-actions|security-bot|snyk-bot", combined, re.I):
        return "dependabot_renovate_security_bot", False

    evidence_lower = evidence.lower()

    if attribution_class == "agent_coauthored" or signature_type == "co_authored_by":
        return "co_authored_by_trailer", True

    for label in ("claude", "cursor", "copilot"):
        if label in evidence_lower:
            return f"{label}_signature", True

    if attribution_class == "agent_signature_in_message":
        for label in ("openai", "aider", "devin", "codeium"):
            if label in evidence_lower:
                return "generic_automation", True
        return "generic_automation", True

    if attribution_class == "bot_author":
        return "bot_author", False

    return "unclassified", False


def load_agent_candidates(candidates_csv: Path) -> list[dict]:
    rows: list[dict] = []
    with candidates_csv.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("attribution_class", "human") == "human":
                continue
            rows.append(row)
    return rows


def sample_candidates(
    candidates: list[dict],
    *,
    n: int = 200,
    seed: int = 42,
) -> list[dict]:
    if len(candidates) <= n:
        return list(candidates)
    rng = random.Random(seed)
    by_category: dict[str, list[dict]] = {}
    for row in candidates:
        cat, _ = categorize_signature(
            attribution_class=row["attribution_class"],
            signature_type=row.get("signature_type", ""),
            author_name=row.get("author_name", ""),
            author_email=row.get("author_email", ""),
            evidence=row.get("evidence", ""),
        )
        by_category.setdefault(cat, []).append(row)

    chosen: list[dict] = []
    per_cat = max(1, n // max(1, len(by_category)))
    for bucket in by_category.values():
        take = min(len(bucket), per_cat)
        chosen.extend(rng.sample(bucket, take) if len(bucket) > take else bucket)

    remaining = [c for c in candidates if c not in chosen]
    if len(chosen) < n and remaining:
        need = n - len(chosen)
        chosen.extend(rng.sample(remaining, min(need, len(remaining))))
    chosen.sort(key=lambda r: (r["repo_id"], r["commit_sha"]))
    return chosen[:n]


def build_gold_worksheet(sampled: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for index, row in enumerate(sampled, start=1):
        category, counts = categorize_signature(
            attribution_class=row["attribution_class"],
            signature_type=row.get("signature_type", ""),
            author_name=row.get("author_name", ""),
            author_email=row.get("author_email", ""),
            evidence=row.get("evidence", ""),
        )
        evidence = row.get("evidence", "")
        rows.append(
            {
                "worksheet_id": index,
                "repo_id": row["repo_id"],
                "repo_url": row.get("repo_url", ""),
                "instruction_path": row["instruction_path"],
                "commit_sha": row["commit_sha"],
                "commit_time": row.get("commit_time", ""),
                "author_name": row.get("author_name", ""),
                "author_email": row.get("author_email", ""),
                "attribution_class": row["attribution_class"],
                "signature_category": category,
                "counts_as_agent_maintenance": "yes" if counts else "no",
                "evidence": evidence[:500],
                "human_label": "",
                "reviewer_notes": "",
            }
        )
    return rows


def _precision_markdown(
    *,
    total_flagged: int,
    sampled: int,
    worksheet: list[dict],
) -> str:
    category_counts: Counter[str] = Counter(r["signature_category"] for r in worksheet)
    agent_maint = sum(1 for r in worksheet if r["counts_as_agent_maintenance"] == "yes")
    excluded = sum(1 for r in worksheet if r["counts_as_agent_maintenance"] == "no")

    lines = [
        "# Gate P4 — Agent Attribution Precision Audit",
        "",
        "## Scope",
        f"- Total non-human flagged commits (P2): **{total_flagged}**",
        f"- Human-review worksheet sample: **{sampled}**",
        "",
        "## Category separation (reviewer objection closure)",
        "",
        "Dependabot/Renovate/security bots **do not** count as agent maintenance.",
        "",
        "| signature_category | count | agent maintenance? |",
        "|--------------------|------:|:------------------:|",
    ]
    for cat, count in category_counts.most_common():
        maint_rows = [r for r in worksheet if r["signature_category"] == cat]
        maintenance = maint_rows[0]["counts_as_agent_maintenance"] if maint_rows else "review"
        lines.append(f"| {cat} | {count} | {maintenance} |")

    lines.extend(
        [
            "",
            "## Breakdown",
            "- **Claude/Cursor/Copilot signatures:** "
            + str(sum(1 for r in worksheet if r["signature_category"].endswith("_signature"))),
            "- **Co-Authored-By trailers:** "
            + str(sum(1 for r in worksheet if r["signature_category"] == "co_authored_by_trailer")),
            "- **Bot authors:** "
            + str(sum(1 for r in worksheet if r["signature_category"] == "bot_author")),
            "- **Generic automation:** "
            + str(sum(1 for r in worksheet if r["signature_category"] == "generic_automation")),
            "- **Dependabot/Renovate/security bots (excluded):** "
            + str(
                sum(
                    1
                    for r in worksheet
                    if r["signature_category"] == "dependabot_renovate_security_bot"
                )
            ),
            "",
            "## Agent maintenance vs excluded bots (worksheet sample)",
            f"- Counts as agent maintenance (auto): **{agent_maint}**",
            f"- Excluded dependency/security bots (auto): **{excluded}**",
            "",
            "## Precision gate",
            "- **Human labels required** — fill `human_label` in `agent_attribution_gold_worksheet.csv`",
            "  (`agent` / `human` / `ambiguous`).",
            f"- Kill criterion: precision < **{PRECISION_KILL_THRESHOLD:.0%}** on agent-maintenance subset.",
            "- Precision = (human_label=agent among counts_as_agent_maintenance=yes) / reviewed agent-maintenance rows.",
            "",
            "## Gate status",
            "**PENDING HUMAN REVIEW** — worksheet exported; auto-summary complete.",
            "",
        ]
    )
    return "\n".join(lines)


def run_p4_attribution_precision_gate(
    *,
    output_dir: Path,
    candidates_csv: Path,
    n_sample: int = 200,
    seed: int = 42,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    worksheet_csv = output_dir / "agent_attribution_gold_worksheet.csv"
    report_md = output_dir / "p4_attribution_precision.md"

    all_flagged = load_agent_candidates(candidates_csv)
    sampled_rows = sample_candidates(all_flagged, n=n_sample, seed=seed)
    worksheet = build_gold_worksheet(sampled_rows)
    write_csv(worksheet, worksheet_csv)

    atomic_write_text(
        report_md,
        _precision_markdown(
            total_flagged=len(all_flagged),
            sampled=len(worksheet),
            worksheet=worksheet,
        ),
    )
    return report_md, worksheet_csv
