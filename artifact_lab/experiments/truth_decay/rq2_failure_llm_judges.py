"""Dual LLM judges for ambiguous RQ2 post-verification failure cases."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass

from artifact_lab.experiments.truth_decay.born_stale_llm_judges import (
    DEFAULT_JUDGE_A_MODEL,
    DEFAULT_JUDGE_B_MODEL,
    DEFAULT_OLLAMA_URL,
    JudgeVerdict,
    _parse_judge_json,
    ollama_available,
    run_judge,
)

RQ2_FAILURE_LABELS = (
    "genuine_decay",
    "rename_or_move",
    "verification_anchor_issue",
    "extractor_artifact",
    "normative_or_prescriptive",
    "external_or_environmental",
    "ambiguous",
)

RQ2_TAXONOMY_PROMPT = """
You classify a post-verification reference failure in machine-consumed documentation.

The reference was VERIFIED at an earlier commit, then became MISSING (mechanical tree check failed).

Choose exactly ONE category:
- genuine_decay: was truly present, later genuinely absent or false
- rename_or_move: target likely moved/renamed; MISSING may not mean falsehood
- verification_anchor_issue: verifier used wrong base path or repo root
- extractor_artifact: extracted reference was not a real descriptive claim
- normative_or_prescriptive: reference is prescriptive/normative, not descriptive state
- external_or_environmental: depends on external package/tool/environment
- ambiguous: insufficient evidence to classify

Respond with JSON only:
{"category": "<one label>", "rationale": "<one sentence>"}
""".strip()

JUDGE_B_FRAMING = """
You are a skeptical measurement auditor. Prefer verification artifact explanations
over maintainer-fault explanations unless evidence is strong.
Same categories and JSON format.
""".strip()


def _parse_rq2_judge_json(text: str) -> tuple[str | None, str]:
    category, rationale = _parse_judge_json(text)
    if category and category not in RQ2_FAILURE_LABELS:
        from artifact_lab.experiments.truth_decay.rq2_failure_audit import map_llm_category_to_rq2

        category = map_llm_category_to_rq2(category)
    if category not in RQ2_FAILURE_LABELS:
        return None, rationale
    return category, rationale


def run_rq2_judge(
    *,
    model: str,
    case_prompt: str,
    system_extra: str = "",
    ollama_url: str = DEFAULT_OLLAMA_URL,
    timeout: float = 120.0,
) -> JudgeVerdict:
    system = RQ2_TAXONOMY_PROMPT
    if system_extra:
        system = f"{system}\n\n{system_extra}"
    try:
        from artifact_lab.experiments.truth_decay.born_stale_llm_judges import _ollama_generate

        raw = _ollama_generate(
            model=model,
            prompt=case_prompt,
            system=system,
            ollama_url=ollama_url,
            timeout=timeout,
        )
        category, rationale = _parse_rq2_judge_json(raw)
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


def build_rq2_failure_prompt(
    *,
    repo_url: str,
    instruction_path: str,
    reference_type: str,
    reference: str,
    time_origin: str,
    time_end: str,
    snippet: str,
    heuristic_category: str,
    heuristic_rationale: str,
    ever_repaired: bool,
    returned_after_missing: bool,
) -> str:
    return (
        f"Repository: {repo_url}\n"
        f"Instruction file: {instruction_path}\n"
        f"Reference type: {reference_type}\n"
        f"Reference text: {reference}\n"
        f"First VERIFIED at: {time_origin}\n"
        f"First MISSING at: {time_end}\n"
        f"Ever repaired after failure: {ever_repaired}\n"
        f"Returned to verified after missing: {returned_after_missing}\n"
        f"Heuristic suggestion: {heuristic_category} ({heuristic_rationale})\n"
        f"Local snippet: {snippet or '[snippet unavailable]'}\n"
    )


def adjudicate_rq2_failure(
    case_prompt: str,
    *,
    judge_a_model: str = DEFAULT_JUDGE_A_MODEL,
    judge_b_model: str = DEFAULT_JUDGE_B_MODEL,
    ollama_url: str = DEFAULT_OLLAMA_URL,
    timeout: float = 120.0,
) -> tuple[JudgeVerdict, JudgeVerdict, bool]:
    judge_a = run_rq2_judge(model=judge_a_model, case_prompt=case_prompt, ollama_url=ollama_url, timeout=timeout)
    judge_b = run_rq2_judge(
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
