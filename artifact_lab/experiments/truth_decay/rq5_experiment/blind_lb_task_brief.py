"""Derive concrete task briefs from pinned instruction text + repo signals."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class TaskBriefResult:
    brief: str
    source: str
    concrete: bool
    reason: str = ""


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
_DESC_RE = re.compile(r"(?im)^description:\s*[>|]?\s*(.+?)(?=\n[a-zA-Z_]+:|\n---|\Z)", re.S)
_NAME_RE = re.compile(r"(?im)^name:\s*[\"']?([^\"'\n]+)")


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _section(text: str, headings: tuple[str, ...], *, max_chars: int = 900) -> str | None:
    for h in headings:
        pat = re.compile(
            rf"(?im)^##\s+{re.escape(h)}\s*\n(.*?)(?=\n##\s+|\Z)",
            re.S,
        )
        m = pat.search(text)
        if m:
            body = m.group(1).strip()
            if body:
                return body[:max_chars]
    return None


def extract_task_brief(
    instruction_text: str,
    *,
    verification_command: str | None,
    reference_alias: str = "Referenced artifact R1",
) -> TaskBriefResult:
    """Build a concrete brief from instruction content. Never invent endpoints/tests."""
    if not instruction_text or not instruction_text.strip():
        return TaskBriefResult(
            brief="",
            source="empty_instruction",
            concrete=False,
            reason="empty_instruction",
        )

    text = instruction_text.strip()
    purpose_bits: list[str] = []
    source_bits: list[str] = []

    fm = _FRONTMATTER_RE.match(text)
    body_text = text
    if fm:
        block = fm.group(1)
        body_text = text[fm.end() :]
        name_m = _NAME_RE.search(block)
        desc_m = _DESC_RE.search(block)
        if name_m:
            purpose_bits.append(f"Skill/module name: {name_m.group(1).strip()}.")
            source_bits.append("frontmatter.name")
        if desc_m:
            desc = _clean(desc_m.group(1))
            if len(desc) >= 40:
                purpose_bits.append(f"Stated purpose: {desc}")
                source_bits.append("frontmatter.description")

    for heading_group, label in (
        (("Purpose", "目的", "Описание проекта", "Project description"), "purpose_section"),
        (("When to Use", "When to use", "目录用途"), "when_to_use"),
        (
            (
                "Guidelines for creating new attack techniques",
                "Rules",
                "Правила разработки скилла",
                "Commands",
                "Architecture",
                "Testing and developing locally",
            ),
            "guidance_section",
        ),
        (("Diagnostic Workflow", "Чек-лист перед завершением задачи", "Overview"), "workflow"),
    ):
        body = _section(body_text, heading_group)
        if body and len(_clean(body)) >= 40:
            purpose_bits.append(f"{label.replace('_', ' ').title()}: {_clean(body)[:700]}")
            source_bits.append(label)
        if len([b for b in purpose_bits if len(b) > 60]) >= 2:
            break

    title_m = re.search(r"(?m)^#\s+(.+)$", body_text)
    if title_m:
        purpose_bits.insert(0, f"Document title: {title_m.group(1).strip()}.")
        source_bits.append("h1_title")

    # Always try first substantial paragraphs after the title (AGENTS.md style).
    paras = [p.strip() for p in re.split(r"\n\s*\n", body_text) if len(_clean(p)) >= 60]
    for p in paras[:2]:
        # Skip pure code fences
        if p.strip().startswith("```"):
            continue
        cleaned = _clean(p)
        # Avoid duplicating an already captured section
        if any(cleaned[:80] in bit for bit in purpose_bits):
            continue
        purpose_bits.append(f"Instruction overview: {cleaned[:700]}")
        source_bits.append("paragraph")
        break

    # Bullet summary fallback: first 8 non-empty bullets
    if sum(len(b) for b in purpose_bits) < 120:
        bullets = re.findall(r"(?m)^\s*[-*]\s+(.+)$", body_text)
        bullets = [_clean(b) for b in bullets if len(_clean(b)) >= 25][:8]
        if bullets:
            purpose_bits.append("Key instruction points: " + " ".join(f"- {b}" for b in bullets)[:900])
            source_bits.append("bullets")

    if not purpose_bits:
        return TaskBriefResult(
            brief="",
            source="unparseable",
            concrete=False,
            reason="could_not_extract_task_purpose",
        )

    body = " ".join(purpose_bits)
    if len(_clean(body)) < 100:
        return TaskBriefResult(
            brief="",
            source=",".join(source_bits),
            concrete=False,
            reason="task_purpose_too_thin",
        )

    lines = [
        "Engineering task (derived only from the pinned instruction text and snapshot signals):",
        body,
        (
            f"While performing this work, the instruction cites {reference_alias}. "
            "Your annotation question is whether that cited artifact is materially necessary "
            "for completing this task in the provided snapshot."
        ),
    ]
    if verification_command:
        lines.append(
            f"Verification command observed in the pinned repository manifests: `{verification_command}`. "
            "Use this only as a snapshot signal of how the project checks work; do not assume other commands."
        )
    else:
        lines.append(
            "No automated verification command was identified from the pinned repository manifests. "
            "Judge necessity from the stated engineering task and the supplied snapshot materials only."
        )

    return TaskBriefResult(
        brief="\n\n".join(lines),
        source=",".join(dict.fromkeys(source_bits)),
        concrete=True,
        reason="derived_from_instruction",
    )
