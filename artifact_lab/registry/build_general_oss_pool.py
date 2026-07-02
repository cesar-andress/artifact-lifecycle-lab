"""Build frozen general-OSS candidate pool via GitHub repository search."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from artifact_lab.registry.pools import is_excluded_name, star_stratum

DEFAULT_OUTPUT = Path("data/registry/sources/general_oss_candidates.jsonl")
GITHUB_API = "https://api.github.com/search/repositories"

# Repository search only — no instruction-path or AI-topic predicates.
GENERAL_OSS_QUERIES: tuple[tuple[str, str], ...] = (
    ("stars:100..500 language:Python pushed:>=2024-06-01 fork:false archived:false", "python"),
    ("stars:501..5000 language:Python pushed:>=2024-06-01 fork:false archived:false", "python"),
    ("stars:5001..50000 language:Python pushed:>=2024-06-01 fork:false archived:false", "python"),
    ("stars:100..500 language:JavaScript pushed:>=2024-06-01 fork:false archived:false", "javascript"),
    ("stars:501..5000 language:JavaScript pushed:>=2024-06-01 fork:false archived:false", "javascript"),
    ("stars:5001..50000 language:JavaScript pushed:>=2024-06-01 fork:false archived:false", "javascript"),
    ("stars:100..500 language:TypeScript pushed:>=2024-06-01 fork:false archived:false", "typescript"),
    ("stars:501..5000 language:TypeScript pushed:>=2024-06-01 fork:false archived:false", "typescript"),
    ("stars:5001..50000 language:TypeScript pushed:>=2024-06-01 fork:false archived:false", "typescript"),
    ("stars:100..500 language:Go pushed:>=2024-06-01 fork:false archived:false", "go"),
    ("stars:501..5000 language:Go pushed:>=2024-06-01 fork:false archived:false", "go"),
    ("stars:5001..50000 language:Go pushed:>=2024-06-01 fork:false archived:false", "go"),
    ("stars:100..500 language:Rust pushed:>=2024-06-01 fork:false archived:false", "rust"),
    ("stars:501..5000 language:Rust pushed:>=2024-06-01 fork:false archived:false", "rust"),
    ("stars:5001..50000 language:Rust pushed:>=2024-06-01 fork:false archived:false", "rust"),
    ("stars:100..500 language:Java pushed:>=2024-06-01 fork:false archived:false", "java"),
    ("stars:501..5000 language:Java pushed:>=2024-06-01 fork:false archived:false", "java"),
    ("stars:5001..50000 language:Java pushed:>=2024-06-01 fork:false archived:false", "java"),
    ("stars:100..500 language:C++ pushed:>=2024-06-01 fork:false archived:false", "cpp"),
    ("stars:501..5000 language:C++ pushed:>=2024-06-01 fork:false archived:false", "cpp"),
    ("stars:5001..50000 language:C++ pushed:>=2024-06-01 fork:false archived:false", "cpp"),
    ("stars:100..500 language:C# pushed:>=2024-06-01 fork:false archived:false", "csharp"),
    ("stars:501..5000 language:C# pushed:>=2024-06-01 fork:false archived:false", "csharp"),
    ("stars:5001..50000 language:C# pushed:>=2024-06-01 fork:false archived:false", "csharp"),
    ("stars:100..500 language:Ruby pushed:>=2024-06-01 fork:false archived:false", "ruby"),
    ("stars:501..5000 language:Ruby pushed:>=2024-06-01 fork:false archived:false", "ruby"),
    ("stars:5001..50000 language:Ruby pushed:>=2024-06-01 fork:false archived:false", "ruby"),
)


def _fetch_search_page(query: str, *, page: int, per_page: int) -> list[dict]:
    params = urllib.parse.urlencode(
        {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": per_page,
            "page": page,
        }
    )
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "artifact-lifecycle-lab"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(f"{GITHUB_API}?{params}", headers=headers)
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.load(response)
    return payload.get("items") or []


def build_general_oss_candidates(*, pages_per_query: int = 2, per_page: int = 100) -> list[dict]:
    candidates: dict[str, dict] = {}
    for query, language_bucket in GENERAL_OSS_QUERIES:
        for page in range(1, pages_per_query + 1):
            try:
                items = _fetch_search_page(query, page=page, per_page=per_page)
            except urllib.error.HTTPError as exc:
                raise RuntimeError(f"GitHub search failed for {query!r}: {exc}") from exc
            for item in items:
                full_name = item["full_name"]
                if is_excluded_name(full_name, description=item.get("description")):
                    continue
                if item.get("fork") or item.get("archived") or item.get("is_template"):
                    continue
                if item.get("mirror_url"):
                    continue
                url = item["html_url"].rstrip("/")
                stars = int(item.get("stargazers_count") or 0)
                candidates[url.lower()] = {
                    "full_name": full_name,
                    "repository_url": url,
                    "stars": stars,
                    "pushed_at": item.get("pushed_at") or "",
                    "primary_language": item.get("language") or language_bucket,
                    "github_description": item.get("description") or "",
                    "github_topics": item.get("topics") or [],
                    "search_query": query,
                    "language_bucket": language_bucket,
                    "star_stratum": star_stratum(stars),
                }
            time.sleep(0.5)
    return sorted(candidates.values(), key=lambda row: row["repository_url"].lower())


def write_general_oss_candidates(rows: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="artifact_lab.registry.build_general_oss_pool")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--pages-per-query", type=int, default=2)
    args = parser.parse_args(argv)
    rows = build_general_oss_candidates(pages_per_query=args.pages_per_query)
    write_general_oss_candidates(rows, args.output)
    print(f"wrote {len(rows)} general OSS candidates -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
