"""Dual local LLM judges for ambiguous born-stale references (Ollama)."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass

from artifact_lab.experiments.truth_decay.born_stale_taxonomy import TAXONOMY_LABELS

DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
DEFAULT_JUDGE_A_MODEL = "deepseek-coder-v2:lite"
DEFAULT_JUDGE_B_MODEL = "devstral:latest"

TAXONOMY_PROMPT = """
You classify why a mechanically extracted reference in machine-consumed documentation
was NEVER verified against the repository tree at any observation.

Choose exactly ONE category:
- extraction_artifact: regex false positive; not a real repository claim
- template_placeholder: example, placeholder, or generic scaffold path
- normative_prescriptive: describes desired structure, not current repo state
- pre_observation_evolution: plausible path but absent from first observable snapshot
- external_reference: package, URL, or out-of-repo dependency
- verification_anchor_mismatch: path valid only relative to doc location, not repo root
- genuine_false_claim: concrete in-repo path that appears incorrect at observation time

Respond with JSON only:
{"category": "<one label>", "rationale": "<one sentence>"}
""".strip()

JUDGE_B_FRAMING = """
You are a skeptical empirical auditor. Focus on measurement error vs maintainer error.
Same categories and JSON format as the primary judge.
""".strip()


@dataclass(frozen=True)
class JudgeVerdict:
    model: str
    category: str | None
    rationale: str
    raw_response: str
    error: str | None


def _parse_judge_json(text: str) -> tuple[str | None, str]:
    text = text.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None, text[:300]
    try:
        payload = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None, text[:300]
    category = str(payload.get("category", "")).strip().lower()
    if category not in TAXONOMY_LABELS:
        return None, str(payload.get("rationale", ""))[:300]
    return category, str(payload.get("rationale", ""))[:500]


def _ollama_generate(
    *,
    model: str,
    prompt: str,
    system: str,
    ollama_url: str,
    timeout: float,
) -> str:
    body = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.1, "num_predict": 200},
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        ollama_url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return str(payload.get("response", ""))


def run_judge(
    *,
    model: str,
    case_prompt: str,
    system_extra: str = "",
    ollama_url: str = DEFAULT_OLLAMA_URL,
    timeout: float = 120.0,
) -> JudgeVerdict:
    system = TAXONOMY_PROMPT
    if system_extra:
        system = f"{system}\n\n{system_extra}"
    try:
        raw = _ollama_generate(
            model=model,
            prompt=case_prompt,
            system=system,
            ollama_url=ollama_url,
            timeout=timeout,
        )
        category, rationale = _parse_judge_json(raw)
        return JudgeVerdict(
            model=model,
            category=category,
            rationale=rationale,
            raw_response=raw[:1000],
            error=None if category else "unparseable_or_invalid_category",
        )
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return JudgeVerdict(
            model=model,
            category=None,
            rationale="",
            raw_response="",
            error=str(exc),
        )


def build_case_prompt(
    *,
    repo_url: str,
    instruction_path: str,
    reference_type: str,
    reference: str,
    snippet: str,
    heuristic_category: str | None,
    heuristic_rationale: str,
) -> str:
    return (
        f"Repository: {repo_url}\n"
        f"Instruction file: {instruction_path}\n"
        f"Reference type: {reference_type}\n"
        f"Reference text: {reference}\n"
        f"Heuristic suggestion: {heuristic_category or 'none'} ({heuristic_rationale})\n"
        f"Local snippet: {snippet or '[snippet unavailable]'}\n"
    )


def adjudicate_with_two_judges(
    case_prompt: str,
    *,
    judge_a_model: str = DEFAULT_JUDGE_A_MODEL,
    judge_b_model: str = DEFAULT_JUDGE_B_MODEL,
    ollama_url: str = DEFAULT_OLLAMA_URL,
    timeout: float = 120.0,
) -> tuple[JudgeVerdict, JudgeVerdict, bool]:
    judge_a = run_judge(model=judge_a_model, case_prompt=case_prompt, ollama_url=ollama_url, timeout=timeout)
    judge_b = run_judge(
        model=judge_b_model,
        case_prompt=case_prompt,
        system_extra=JUDGE_B_FRAMING,
        ollama_url=ollama_url,
        timeout=timeout,
    )
    agree = (
        judge_a.category is not None
        and judge_b.category is not None
        and judge_a.category == judge_b.category
    )
    return judge_a, judge_b, agree


def ollama_available(ollama_url: str = DEFAULT_OLLAMA_URL) -> bool:
    try:
        tags_url = ollama_url.replace("/api/generate", "/api/tags")
        with urllib.request.urlopen(tags_url, timeout=3) as resp:
            return resp.status == 200
    except (urllib.error.URLError, TimeoutError):
        return False
