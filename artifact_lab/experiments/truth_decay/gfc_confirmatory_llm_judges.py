"""Dual LLM judges for ambiguous genuine_false_claim confirmatory cases."""

from __future__ import annotations

from artifact_lab.experiments.truth_decay.born_stale_llm_judges import (
    DEFAULT_JUDGE_A_MODEL,
    DEFAULT_JUDGE_B_MODEL,
    DEFAULT_OLLAMA_URL,
    JudgeVerdict,
    _ollama_generate,
    _parse_judge_json,
    ollama_available,
)

CONFIRMATORY_LABELS = (
    "confirmed_false",
    "artifact",
    "normative",
    "anchor_issue",
    "template",
    "ambiguous",
)

CONFIRMATORY_PROMPT = """
You confirm or refute a prior `genuine_false_claim` label for a never-verified reference.

Choose exactly ONE category:
- confirmed_false: concrete in-tree path claim that is genuinely absent
- artifact: extraction or command/prose false positive, not a real path claim
- normative: prescriptive guidance, not descriptive repo inventory
- anchor_issue: wrong verification anchor (relative path / root mismatch)
- template: placeholder, example, or glob pattern
- ambiguous: insufficient evidence

Respond with JSON only:
{"category": "<one label>", "rationale": "<one sentence>"}
""".strip()

JUDGE_B_FRAMING = """
You are a skeptical auditor. Prefer artifact/template/anchor explanations over confirmed_false
unless evidence is strong. Same categories and JSON format.
""".strip()


def _parse_confirmatory_json(text: str) -> tuple[str | None, str]:
    category, rationale = _parse_judge_json(text)
    if category in CONFIRMATORY_LABELS:
        return category, rationale
    alias = {
        "extraction_artifact": "artifact",
        "template_placeholder": "template",
        "normative_prescriptive": "normative",
        "verification_anchor_mismatch": "anchor_issue",
        "genuine_false_claim": "confirmed_false",
        "external_reference": "artifact",
    }
    if category in alias:
        return alias[category], rationale
    return None, rationale


def run_confirmatory_judge(
    *,
    model: str,
    case_prompt: str,
    system_extra: str = "",
    ollama_url: str = DEFAULT_OLLAMA_URL,
    timeout: float = 120.0,
) -> JudgeVerdict:
    system = CONFIRMATORY_PROMPT
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
        category, rationale = _parse_confirmatory_json(raw)
        return JudgeVerdict(
            model=model,
            category=category,
            rationale=rationale,
            raw_response=raw[:1000],
            error=None if category else "unparseable_or_invalid_category",
        )
    except Exception as exc:  # noqa: BLE001 - surface judge transport errors
        return JudgeVerdict(
            model=model,
            category=None,
            rationale="",
            raw_response="",
            error=str(exc),
        )


def build_confirmatory_prompt(
    *,
    repo_url: str,
    instruction_path: str,
    reference_type: str,
    reference: str,
    snippet: str,
    heuristic_category: str,
    heuristic_rationale: str,
) -> str:
    return (
        f"Repository: {repo_url}\n"
        f"Instruction file: {instruction_path}\n"
        f"Reference type: {reference_type}\n"
        f"Reference text: {reference}\n"
        f"Prior label: genuine_false_claim\n"
        f"Heuristic suggestion: {heuristic_category} ({heuristic_rationale})\n"
        f"Local snippet: {snippet or '[snippet unavailable]'}\n"
    )


def adjudicate_confirmatory(
    case_prompt: str,
    *,
    judge_a_model: str = DEFAULT_JUDGE_A_MODEL,
    judge_b_model: str = DEFAULT_JUDGE_B_MODEL,
    ollama_url: str = DEFAULT_OLLAMA_URL,
    timeout: float = 120.0,
) -> tuple[JudgeVerdict, JudgeVerdict, bool]:
    judge_a = run_confirmatory_judge(model=judge_a_model, case_prompt=case_prompt, ollama_url=ollama_url, timeout=timeout)
    judge_b = run_confirmatory_judge(
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
