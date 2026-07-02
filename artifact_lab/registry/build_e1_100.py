"""Build the E1 100-repository scientific cohort registry."""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

from artifact_lab.contracts.repo_id import repo_id_from_url, normalize_repo_url
from artifact_lab.registry.schema import E1_100_REGISTRY_COLUMNS

DEFAULT_PILOT_REGISTRY = Path("data/registry/pilot_repos.csv")
DEFAULT_OUTPUT = Path("data/registry/e1_100_repos.csv")
DEFAULT_VSDLC_ELIGIBLE = Path.home() / "papers/vsdlc/vsdlc/data/interim/eligible_repos_enriched.jsonl"

EXCLUDE_NAME_RE = re.compile(
    r"(template|boilerplate|cookiecutter|starter-kit|awesome-|/awesome$|-awesome$)",
    re.IGNORECASE,
)

PILOT_ENRICHMENT: dict[str, dict[str, str | int]] = {
    "https://github.com/continuedev/continue": {
        "stars": 28000,
        "language": "TypeScript",
        "pushed_at": "2025-06-15T00:00:00",
    },
    "https://github.com/pydantic/pydantic-ai": {
        "stars": 12000,
        "language": "Python",
        "pushed_at": "2025-06-15T00:00:00",
    },
    "https://github.com/langchain-ai/langchain": {
        "stars": 110000,
        "language": "Python",
        "pushed_at": "2025-06-15T00:00:00",
    },
    "https://github.com/all-hands-ai/openhands": {
        "stars": 60000,
        "language": "Python",
        "pushed_at": "2025-06-15T00:00:00",
    },
    "https://github.com/anthropics/claude-code": {
        "stars": 15000,
        "language": "TypeScript",
        "pushed_at": "2025-06-15T00:00:00",
    },
    "https://github.com/dagster-io/dagster": {
        "stars": 13000,
        "language": "Python",
        "pushed_at": "2025-06-15T00:00:00",
    },
    "https://github.com/modelcontextprotocol/servers": {
        "stars": 7000,
        "language": "Python",
        "pushed_at": "2025-06-15T00:00:00",
    },
    "https://github.com/aider-ai/aider": {
        "stars": 25000,
        "language": "Python",
        "pushed_at": "2025-06-15T00:00:00",
    },
    "https://github.com/open-webui/open-webui": {
        "stars": 90000,
        "language": "Python",
        "pushed_at": "2025-06-15T00:00:00",
    },
    "https://github.com/astral-sh/ruff": {
        "stars": 40000,
        "language": "Rust",
        "pushed_at": "2025-06-15T00:00:00",
    },
    "https://github.com/django/django": {
        "stars": 83000,
        "language": "Python",
        "pushed_at": "2025-06-15T00:00:00",
    },
    "https://github.com/tiangolo/fastapi": {
        "stars": 86000,
        "language": "Python",
        "pushed_at": "2025-06-15T00:00:00",
    },
    "https://github.com/vercel/next.js": {
        "stars": 130000,
        "language": "JavaScript",
        "pushed_at": "2025-06-15T00:00:00",
    },
    "https://github.com/microsoft/vscode": {
        "stars": 170000,
        "language": "TypeScript",
        "pushed_at": "2025-06-15T00:00:00",
    },
    "https://github.com/crewaiinc/crewai": {
        "stars": 30000,
        "language": "Python",
        "pushed_at": "2025-06-15T00:00:00",
    },
    "https://github.com/langgenius/dify": {
        "stars": 60000,
        "language": "Python",
        "pushed_at": "2025-06-15T00:00:00",
    },
    "https://github.com/prefecthq/prefect": {
        "stars": 22646,
        "language": "Python",
        "pushed_at": "2025-06-15T00:00:00",
    },
}


def _parse_owner_name(repo_url: str) -> tuple[str, str]:
    normalized = normalize_repo_url(repo_url)
    match = re.match(r"https://github\.com/([^/]+)/([^/]+)$", normalized)
    if not match:
        raise ValueError(f"cannot parse owner/name from {repo_url!r}")
    return match.group(1), match.group(2)


def _artifact_family(queries: list[str]) -> str:
    joined = " ".join(queries).lower()
    if ".cursor/rules" in joined or "cursor/rules" in joined:
        return "cursor_rules"
    if "agents.md" in joined:
        return "agents_md"
    if "claude.md" in joined:
        return "claude_md"
    if "copilot" in joined:
        return "copilot"
    if "prompt" in joined:
        return "prompts"
    if ".rules" in joined or "/rules" in joined:
        return "rules"
    return "other"


def _star_stratum(stars: int) -> str:
    if stars < 500:
        return "stars_small"
    if stars < 5000:
        return "stars_medium"
    return "stars_large"


def _pilot_stratum(seed_pool: str) -> str:
    if seed_pool.strip().lower() == "ai_adopter":
        return "pilot_ai_adopter"
    return "pilot_general_oss"


def _load_pilot_rows(pilot_path: Path) -> list[dict[str, str]]:
    with pilot_path.open(encoding="utf-8", newline="") as handle:
        pilot_raw = list(csv.DictReader(handle))
    rows: list[dict[str, str]] = []
    for item in pilot_raw:
        repo_url = normalize_repo_url(item["repo_url"])
        owner, name = _parse_owner_name(repo_url)
        enrichment = PILOT_ENRICHMENT.get(repo_url, {})
        rows.append(
            {
                "repo_id": repo_id_from_url(repo_url),
                "repo_url": repo_url,
                "owner": owner,
                "name": name,
                "source": "pilot_repos.csv",
                "stars": str(enrichment.get("stars", item.get("stars", ""))),
                "language": str(enrichment.get("language", item.get("language", ""))),
                "pushed_at": str(enrichment.get("pushed_at", item.get("pushed_at", ""))),
                "selection_stratum": _pilot_stratum(item.get("seed_pool", "")),
                "notes": item.get("notes", ""),
            }
        )
    return rows


def _load_vsdlc_candidates(vsdlc_path: Path, *, exclude_urls: set[str]) -> list[dict]:
    candidates: list[dict] = []
    with vsdlc_path.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            url = normalize_repo_url(row["repository_url"])
            if url in exclude_urls:
                continue
            full_name = row["full_name"]
            if EXCLUDE_NAME_RE.search(full_name):
                continue
            candidates.append(row)
    return candidates


def _sample_vsdlc_rows(candidates: list[dict], *, sample_size: int, seed: int) -> list[dict[str, str]]:
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in candidates:
        family = _artifact_family(row.get("queries") or [])
        stratum = _star_stratum(int(row.get("stars") or 0))
        groups[(family, stratum)].append(row)
    for key in groups:
        groups[key].sort(key=lambda item: item["full_name"].lower())

    keys = sorted(groups.keys())
    rng = random.Random(seed)
    rng.shuffle(keys)

    selected: list[dict] = []
    indices = dict.fromkeys(keys, 0)
    while len(selected) < sample_size:
        progressed = False
        for key in keys:
            idx = indices[key]
            if idx < len(groups[key]):
                selected.append(groups[key][idx])
                indices[key] = idx + 1
                progressed = True
                if len(selected) >= sample_size:
                    break
        if not progressed:
            break

    if len(selected) < sample_size:
        raise RuntimeError(f"could only sample {len(selected)} VSDLC repos, need {sample_size}")

    rows: list[dict[str, str]] = []
    for row in selected:
        repo_url = normalize_repo_url(row["repository_url"])
        owner, name = _parse_owner_name(repo_url)
        family = _artifact_family(row.get("queries") or [])
        stratum = _star_stratum(int(row.get("stars") or 0))
        rows.append(
            {
                "repo_id": repo_id_from_url(repo_url),
                "repo_url": repo_url,
                "owner": owner,
                "name": name,
                "source": "vsdlc_eligible",
                "stars": str(int(row.get("stars") or 0)),
                "language": str(row.get("primary_language") or ""),
                "pushed_at": str(row.get("pushed_at") or ""),
                "selection_stratum": f"vsdlc_{family}_{stratum}",
                "notes": ";".join(row.get("queries") or []),
            }
        )
    rows.sort(key=lambda item: item["repo_url"])
    return rows


def build_e1_100_registry(
    *,
    pilot_path: Path,
    vsdlc_path: Path,
    output_path: Path,
    seed: int = 42,
    target_size: int = 100,
) -> list[dict[str, str]]:
    pilot_rows = _load_pilot_rows(pilot_path)
    exclude_urls = {row["repo_url"] for row in pilot_rows}
    vsdlc_sample_size = target_size - len(pilot_rows)
    if vsdlc_sample_size < 0:
        raise ValueError("pilot registry larger than target cohort size")
    candidates = _load_vsdlc_candidates(vsdlc_path, exclude_urls=exclude_urls)
    vsdlc_rows = _sample_vsdlc_rows(candidates, sample_size=vsdlc_sample_size, seed=seed)
    rows = pilot_rows + vsdlc_rows
    if len(rows) != target_size:
        raise ValueError(f"built {len(rows)} rows, expected {target_size}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(E1_100_REGISTRY_COLUMNS))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="artifact_lab.registry.build_e1_100")
    parser.add_argument("--pilot", type=Path, default=DEFAULT_PILOT_REGISTRY)
    parser.add_argument("--vsdlc", type=Path, default=DEFAULT_VSDLC_ELIGIBLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args(argv)
    if not args.vsdlc.exists():
        print(f"VSDLC eligible file not found: {args.vsdlc}", file=sys.stderr)
        return 1
    rows = build_e1_100_registry(
        pilot_path=args.pilot,
        vsdlc_path=args.vsdlc,
        output_path=args.output,
        seed=args.seed,
    )
    print(f"wrote {len(rows)} registry rows -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
