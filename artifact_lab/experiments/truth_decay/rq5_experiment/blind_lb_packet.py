"""Generate scientifically usable, outcome-blind RQ5 v1 annotation packets.

Redesign goals (TOSEM construct validity):
- concrete task briefs from pinned instruction + snapshot signals
- minimal repository context around the reference
- semantic path redaction (no substring corruption)
- never reveal absence of treated artifacts
- language translation for non-English excerpts
- exclude degenerate / non-software / unsafe-to-blind cases

Protocol: docs/RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md @ e41902c
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from artifact_lab.experiments.truth_decay.rq5_experiment.blind_lb_context import (
    BlindRepoCache,
    build_repo_context,
)
from artifact_lab.experiments.truth_decay.rq5_experiment.blind_lb_language import (
    detect_language,
    load_cache,
    text_hash,
    translate_to_english,
)
from artifact_lab.experiments.truth_decay.rq5_experiment.blind_lb_redact import (
    REF_TOKEN,
    assert_no_raw_anchors,
    corruption_markers,
    redact_paths,
)
from artifact_lab.experiments.truth_decay.rq5_experiment.blind_lb_task_brief import (
    extract_task_brief,
)
from artifact_lab.store.blobs import BlobStore

PROTOCOL_VERSION = "RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c"
PACKET_SPEC_VERSION = "rq5_v1_blind_packet_spec_v2"
DEFAULT_SEED = 42
DEFAULT_MANIFEST = Path("exports/rq5_agent_impact/rq5_case_manifest.csv")
DEFAULT_CANDIDATES = Path("exports/truth_decay_pilot/rq5_candidate_dataset.csv")
DEFAULT_OUTPUT = Path("exports/rq5_lb_blind_annotation")
DEFAULT_BLOBS = Path("data/blobs")
DEFAULT_SCRATCH = Path("scratch/rq5_blind_trees")

ARTIFACT_ALIAS = "Referenced artifact R1"

FORBIDDEN_SUBSTRINGS = (
    "condition_a",
    "condition_b",
    "condition_c",
    "born_stale",
    "confirmed_false",
    "truthful",
    "task_success",
    "failure_reason",
    "causal_role",
    "load_bearing_stratum",
    "likely_load_bearing",
    "mediation",
    "false_claim",
    "uptake_but_not_load_bearing",
    "obstacle_recovered",
    "claude_code",
    "replicate_id",
)
FORBIDDEN_TOKEN_RE = re.compile(
    r"(?i)\b(condition\s*[abc]|a/b/c|born[\s_-]?stale|confirmed[\s_-]?false|"
    r"truthful|task_success|causal_role|mediation|load_bearing_stratum)\b"
)

ABSENCE_LEAK_RE = re.compile(
    r"(?is)("
    r"\[\[REF\]\]|Referenced artifact R1"
    r").{0,40}("
    r"does not exist|doesn't exist|do not exist|is missing|not found|"
    r"no such file|cannot find|could not find|absent from"
    r")"
    r"|"
    r"("
    r"does not exist|doesn't exist|do not exist|is missing|not found|"
    r"no such file|cannot find|could not find|absent from"
    r").{0,40}("
    r"\[\[REF\]\]|Referenced artifact R1"
    r")"
)

EMIT_STATUSES = frozenset({"eligible"})


@dataclass
class EligibilityRow:
    neutral_id: str
    eligibility_status: str
    reason_code: str
    explanation: str
    sources_inspected: str
    packet_hash: str = ""
    case_id: str = ""


@dataclass
class PacketBuildResult:
    eligibility: EligibilityRow
    packet_md: str | None = None
    packet_json: dict[str, Any] | None = None
    provenance: dict[str, Any] | None = None


def stable_neutral_id(case_id: str, *, seed: int) -> str:
    payload = f"rq5v1-blind-lb|{seed}|{case_id}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def anonymous_snapshot_id(repo_id: str, commit_sha: str, *, seed: int) -> str:
    payload = f"snap|{seed}|{repo_id}|{commit_sha}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _decode_blob(raw: bytes) -> str:
    return raw.decode("utf-8", errors="replace")


def load_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_candidate_index(path: Path) -> dict[tuple[str, str, str], dict[str, str]]:
    if not path.exists():
        return {}
    index: dict[tuple[str, str, str], dict[str, str]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("snapshot_type") != "born_stale":
                continue
            key = (row["repo_id"], row["instruction_path"], row["anchor_reference"])
            index[key] = row
    return index


def treatment_ban_paths(text_a: str, text_b: str, anchor: str) -> list[str]:
    """Paths to redact: anchor + multi-segment paths unique to contrast text."""
    banned = [anchor]
    if text_b:
        path_re = re.compile(r"[A-Za-z0-9_./@+-]+(?:/[A-Za-z0-9_./@+-]+)+/?")
        for token in path_re.findall(text_b):
            if token not in text_a and len(token) >= 4 and "/" in token:
                banned.append(token)
    # Deduplicate preserving order
    out: list[str] = []
    for t in banned:
        if t and t not in out:
            out.append(t)
    return out


def leakage_hits(text: str, extra_banned: Iterable[str] = ()) -> list[str]:
    hits: list[str] = []
    lower = text.lower()
    for token in FORBIDDEN_SUBSTRINGS:
        if token in lower:
            hits.append(token)
    if FORBIDDEN_TOKEN_RE.search(text):
        hits.append("forbidden_token_pattern")
    if ABSENCE_LEAK_RE.search(text):
        hits.append("absence_statement")
    for token in extra_banned:
        if not token:
            continue
        if "/" in token and len(token) >= 4 and token in text:
            hits.append(f"banned_path:{token[:40]}")
        elif len(token) >= 8 and re.search(
            rf"(?<![A-Za-z0-9_]){re.escape(token)}(?![A-Za-z0-9_])", text
        ):
            hits.append(f"banned_token:{token[:40]}")
    for lab in ("condition A", "condition B", "condition C"):
        if lab.lower() in lower:
            hits.append(lab)
    hits.extend(corruption_markers(text))
    return sorted(set(hits))


def _refuse(
    *,
    neutral_id: str,
    case_id: str,
    status: str,
    reason_code: str,
    explanation: str,
    sources: list[str],
) -> PacketBuildResult:
    return PacketBuildResult(
        eligibility=EligibilityRow(
            neutral_id=neutral_id,
            case_id=case_id,
            eligibility_status=status,
            reason_code=reason_code,
            explanation=explanation,
            sources_inspected=";".join(sources),
        )
    )


def _enrich_excerpts(instruction_text: str, anchor: str, *, max_chars: int = 1800) -> list[str]:
    """Richer surrounding context around anchor citations."""
    lines = instruction_text.splitlines()
    hit_idxs = [i for i, ln in enumerate(lines) if anchor in ln or anchor.rstrip("/") in ln]
    if not hit_idxs:
        idx = instruction_text.find(anchor)
        if idx < 0:
            return []
        start = max(0, idx - 400)
        end = min(len(instruction_text), idx + len(anchor) + 400)
        return [instruction_text[start:end].strip()]

    blocks: list[str] = []
    for i in hit_idxs[:5]:
        lo = max(0, i - 8)
        hi = min(len(lines), i + 9)
        block = "\n".join(lines[lo:hi]).strip()
        if block and block not in blocks:
            blocks.append(block[:max_chars])
    return blocks


def _is_degenerate(excerpts: list[str], brief: str, tree: list[str], file_excerpts: list[dict[str, str]]) -> str | None:
    joined = "\n".join(excerpts)
    if len(joined) < 120 and len(file_excerpts) < 2:
        return "excerpts_too_short"
    # Isolated filename-only
    if all(len(e.strip().splitlines()) <= 1 and len(e.strip()) < 80 for e in excerpts) and len(file_excerpts) < 2:
        return "isolated_filename_excerpts"
    if len(brief) < 160:
        return "brief_too_thin"
    if len(tree) < 5 and len(file_excerpts) < 1:
        return "insufficient_repo_context"
    return None


def _redact_identity_noise(text: str, *, repo_url: str, instruction_path: str) -> str:
    """Remove repo URL / instruction path identity from emitted text."""
    out = text
    if repo_url:
        out = out.replace(repo_url, "[repository]")
        # Also https without scheme variants
        bare = repo_url.replace("https://", "").replace("http://", "")
        out = out.replace(bare, "[repository]")
    if instruction_path:
        out = redact_paths(out, [instruction_path])
        base = instruction_path.split("/")[-1]
        if base and len(base) >= 8:
            out = re.sub(
                rf"(?<![A-Za-z0-9_]){re.escape(base)}(?![A-Za-z0-9_])",
                "[[INSTRUCTION]]",
                out,
            )
    return out


def build_packet_for_case(
    row: dict[str, str],
    *,
    seed: int,
    blob_store: BlobStore,
    candidate: dict[str, str] | None,
    repo_cache: BlindRepoCache,
    translation_cache: dict[str, dict[str, str]],
) -> PacketBuildResult:
    case_id = row["case_id"]
    neutral_id = stable_neutral_id(case_id, seed=seed)
    sources: list[str] = ["rq5_case_manifest.csv", f"packet_spec:{PACKET_SPEC_VERSION}"]
    if candidate:
        sources.append("rq5_candidate_dataset.csv")

    blob_a_sha = row.get("condition_a_blob_sha", "")
    blob_b_sha = row.get("condition_b_blob_sha", "")
    anchor = row.get("anchor_reference", "")
    instruction_path = row.get("instruction_path", "")
    repo_id = row.get("repo_id", "")
    repo_url = row.get("repo_url", "")
    commit = row.get("task_commit_sha", "")

    if not blob_store.has(blob_a_sha):
        return _refuse(
            neutral_id=neutral_id,
            case_id=case_id,
            status="source_unavailable",
            reason_code="missing_instruction_blob_a",
            explanation="Pinned instruction blob missing from blob store.",
            sources=sources + [f"blob:{blob_a_sha[:12]}"],
        )

    text_a = _decode_blob(blob_store.get_text(blob_a_sha))
    sources.append(f"blob_store:{blob_a_sha[:16]}")
    text_b = ""
    if blob_store.has(blob_b_sha):
        text_b = _decode_blob(blob_store.get_text(blob_b_sha))
        sources.append("blob_store:contrast_inspected_not_emitted")

    # Language: translate instruction for English annotators.
    lang = detect_language(text_a)
    text_for_annotators, lang2 = translate_to_english(text_a, cache=translation_cache)
    lang = lang2
    if lang != "en" and text_hash(text_a) not in translation_cache:
        return _refuse(
            neutral_id=neutral_id,
            case_id=case_id,
            status="not_safe_for_blinding",
            reason_code="non_english_translation_missing",
            explanation="Instruction text is non-English and no cached professional translation is available.",
            sources=sources,
        )
    if lang != "en":
        sources.append(f"translation_cache:{lang}")

    ban_paths = treatment_ban_paths(text_a, text_b, anchor)
    if instruction_path:
        ban_paths.append(instruction_path)

    # Repository context from pinned commit.
    ctx = build_repo_context(
        repo_cache,
        repo_id=repo_id,
        repo_url=repo_url,
        commit_sha=commit,
        anchor=anchor,
        instruction_path=instruction_path,
    )
    if not ctx.available:
        return _refuse(
            neutral_id=neutral_id,
            case_id=case_id,
            status="source_unavailable",
            reason_code="repo_snapshot_unavailable",
            explanation=f"Could not materialize pinned repository tree ({ctx.reason}).",
            sources=sources + [f"git:{repo_id[:8]}"],
        )
    sources.append(f"git_tree:{commit[:12]}")

    if not ctx.is_software_repository:
        return _refuse(
            neutral_id=neutral_id,
            case_id=case_id,
            status="non_software_repository",
            reason_code="not_software_repository",
            explanation=(
                "Pinned tree lacks sufficient source/manifest signals of a software repository; "
                f"signals={ctx.software_signals}"
            ),
            sources=sources,
        )

    # Task brief from (translated) instruction + verification signal.
    brief_res = extract_task_brief(
        text_for_annotators,
        verification_command=ctx.verification_command,
        reference_alias=ARTIFACT_ALIAS,
    )
    if not brief_res.concrete:
        return _refuse(
            neutral_id=neutral_id,
            case_id=case_id,
            status="task_not_separable",
            reason_code=brief_res.reason or "task_brief_not_concrete",
            explanation="Could not derive a concrete engineering task brief from the pinned instruction.",
            sources=sources,
        )

    # Richer citation excerpts; regenerate if thin.
    raw_excerpts = _enrich_excerpts(text_for_annotators, anchor)
    if not raw_excerpts:
        # Try original-language anchor locate then translate block via full text already translated
        raw_excerpts = _enrich_excerpts(text_a, anchor)
        if raw_excerpts and lang != "en":
            # If we only have original-language windows, refuse unless translation covers full text
            # (we already translated full text_for_annotators — re-extract from it with loose match)
            raw_excerpts = _enrich_excerpts(text_for_annotators, anchor)
    if not raw_excerpts:
        return _refuse(
            neutral_id=neutral_id,
            case_id=case_id,
            status="insufficient_pre_treatment_context",
            reason_code="anchor_not_in_instruction_blob",
            explanation="Anchor citation not found in the sanitized instruction source.",
            sources=sources,
        )

    # Semantic redaction of excerpts, brief, and tree.
    redact_targets = list(ban_paths)
    # Also redact concrete resolved reference paths (path identity = treatment risk).
    redact_targets.extend(ctx.reference_path_aliases)

    def _redact(s: str) -> str:
        return _redact_identity_noise(
            redact_paths(s, redact_targets),
            repo_url=repo_url,
            instruction_path=instruction_path,
        )

    brief = _redact(brief_res.brief)
    excerpts = [_redact(e) for e in raw_excerpts]

    # Expand with surrounding instruction sections if still degenerate.
    deg = _is_degenerate(excerpts, brief, ctx.tree_excerpt, ctx.file_excerpts)
    if deg in {"excerpts_too_short", "isolated_filename_excerpts"}:
        # Pull a larger window from instruction.
        expanded = _enrich_excerpts(text_for_annotators, anchor, max_chars=3500)
        if len("\n".join(expanded)) > len("\n".join(excerpts)):
            excerpts = [_redact(e) for e in expanded]
        deg = _is_degenerate(excerpts, brief, ctx.tree_excerpt, ctx.file_excerpts)

    # File excerpts from snapshot (redact paths in content + replace original_path with alias).
    snapshot_files: list[dict[str, str]] = []
    for fe in ctx.file_excerpts:
        content = _redact(fe["content"])
        snapshot_files.append(
            {
                "file_alias": fe["alias"],
                "role": "pinned_snapshot_excerpt",
                "content": content,
            }
        )

    # Tree: redact sensitive paths; present neutrally.
    tree_lines = [_redact(p) for p in ctx.tree_excerpt]
    neighbor_lines = [_redact(p) for p in ctx.neighbor_paths[:20]]
    doc_lines = [_redact(p) for p in ctx.nearby_docs[:10]]
    config_lines = [_redact(p) for p in ctx.nearby_configs[:10]]

    # If redaction destroyed readability, refuse.
    corp = corruption_markers("\n".join(excerpts + [brief] + tree_lines))
    if corp:
        return _refuse(
            neutral_id=neutral_id,
            case_id=case_id,
            status="not_safe_for_blinding",
            reason_code="redaction_corruption",
            explanation=f"Semantic redaction produced corruption markers: {corp}",
            sources=sources,
        )

    check_blob = "\n".join(excerpts + [brief] + tree_lines)
    remaining = assert_no_raw_anchors(check_blob, [anchor, instruction_path, *ban_paths])
    if remaining:
        return _refuse(
            neutral_id=neutral_id,
            case_id=case_id,
            status="not_safe_for_blinding",
            reason_code="unsafe_path_residual",
            explanation=f"Could not fully redact path identity without leakage: {remaining[:5]}",
            sources=sources,
        )

    deg = _is_degenerate(excerpts, brief, tree_lines, snapshot_files)
    if deg:
        return _refuse(
            neutral_id=neutral_id,
            case_id=case_id,
            status="degenerate_packet",
            reason_code=deg,
            explanation="Packet remains information-poor after enrichment; excluded rather than distributed.",
            sources=sources,
        )

    role = (
        f"{ARTIFACT_ALIAS} is a repository artifact cited by the project instruction text "
        f"(reference kind: {row.get('anchor_reference_type', 'unknown')}). "
        f"Its literal path string is withheld and shown as {REF_TOKEN} so treatment assignment "
        "cannot be inferred from path identity. "
        "Use the citation excerpts, task brief, and snapshot context below to judge relevance and necessity."
    )

    path_policy = (
        "Path identity for the cited artifact and for contrast-only manipulated paths is replaced "
        f"by {REF_TOKEN} using semantic whole-path tokenization (not substring replacement). "
        "Other snapshot paths may appear when they do not reveal treatment assignment. "
        "Do not infer experimental treatment from path placeholders."
    )

    packet_json: dict[str, Any] = {
        "neutral_id": neutral_id,
        "anonymous_snapshot_id": anonymous_snapshot_id(repo_id, commit, seed=seed),
        "protocol_version": PROTOCOL_VERSION,
        "packet_spec_version": PACKET_SPEC_VERSION,
        "task_brief": brief,
        "task_brief_source": brief_res.source,
        "verification_command_observed": ctx.verification_command or "",
        "verification_evidence": ctx.verification_evidence,
        "reference_type": row.get("anchor_reference_type", ""),
        "referenced_artifact_alias": ARTIFACT_ALIAS,
        "artifact_role_description": role,
        "instruction_citation_excerpts": excerpts,
        "instruction_language_original": lang if lang != "en" else "en",
        "instruction_provided_in": "en",
        "repository_tree_excerpt": tree_lines,
        "neighbor_paths": neighbor_lines,
        "nearby_documentation_paths": doc_lines,
        "nearby_configuration_paths": config_lines,
        "snapshot_file_excerpts": snapshot_files,
        "path_policy": path_policy,
        "annotator_question": (
            f"Is {ARTIFACT_ALIAS} materially necessary for completing THIS software engineering "
            "task in THIS repository snapshot?"
        ),
    }

    packet_md = _render_packet_md(packet_json)
    combined = packet_md + "\n" + json.dumps(packet_json, sort_keys=True)
    # Leakage ban-list: multi-segment treatment paths only (not common filenames).
    extra_ban = {p for p in ban_paths if p and "/" in p and len(p) >= 4}
    if repo_url:
        extra_ban.add(repo_url)
    hits = leakage_hits(combined, extra_banned=extra_ban)
    if assert_no_raw_anchors(combined, [anchor]):
        hits.append("raw_anchor_present")
    if hits:
        return _refuse(
            neutral_id=neutral_id,
            case_id=case_id,
            status="not_safe_for_blinding",
            reason_code="leakage_or_absence_risk",
            explanation=f"Refused emit; scan hits: {', '.join(hits[:12])}",
            sources=sources,
        )

    packet_hash = sha256_text(packet_md)
    provenance = {
        "neutral_id": neutral_id,
        "protocol_version": PROTOCOL_VERSION,
        "packet_spec_version": PACKET_SPEC_VERSION,
        "seed": seed,
        "sources": sources,
        "task_brief_source": brief_res.source,
        "verification_command_observed": ctx.verification_command,
        "software_signals": ctx.software_signals,
        "n_tree_paths": len(ctx.paths),
        "n_reference_aliases_internal": len(ctx.reference_path_aliases),
        "packet_sha256": packet_hash,
        "blinding": {
            "semantic_path_redaction": True,
            "absence_statements_forbidden": True,
            "repo_url_omitted": True,
            "case_id_omitted": True,
            "outcomes_omitted": True,
            "traces_omitted": True,
            "access_model": "access_separated_private_id_map_not_cryptographically_sealed",
        },
    }

    return PacketBuildResult(
        eligibility=EligibilityRow(
            neutral_id=neutral_id,
            case_id=case_id,
            eligibility_status="eligible",
            reason_code="construct_valid_packet_v2",
            explanation="Concrete task brief + snapshot context + semantic redaction; safe to distribute.",
            sources_inspected=";".join(sources),
            packet_hash=packet_hash,
        ),
        packet_md=packet_md,
        packet_json=packet_json,
        provenance=provenance,
    )


def _fence_safe(text: str) -> str:
    """Prevent nested Markdown fences from breaking packet.md structure."""
    return text.replace("```", "'''")


def _render_packet_md(packet: dict[str, Any]) -> str:
    lines = [
        f"# Annotation packet `{packet['neutral_id']}`",
        "",
        f"Protocol: `{packet['protocol_version']}`",
        f"Packet spec: `{packet['packet_spec_version']}`",
        "",
        "Judge only with the materials below. Do not seek external repositories or experimental results.",
        "",
        "## Annotator question",
        "",
        packet["annotator_question"],
        "",
        "## Anonymous snapshot",
        "",
        f"- Snapshot ID: `{packet['anonymous_snapshot_id']}`",
        f"- Reference type: `{packet['reference_type']}`",
        f"- Artifact alias: **{packet['referenced_artifact_alias']}**",
        "",
        "## Task brief",
        "",
        packet["task_brief"],
        "",
        "## Artifact role",
        "",
        packet["artifact_role_description"],
        "",
        "## Path policy",
        "",
        packet["path_policy"],
        "",
        "## Instruction citation excerpts",
        "",
    ]
    for i, excerpt in enumerate(packet["instruction_citation_excerpts"], 1):
        lines.append(f"### Excerpt {i}")
        lines.append("")
        lines.append("```")
        lines.append(_fence_safe(excerpt))
        lines.append("```")
        lines.append("")

    lines.extend(["## Repository tree excerpt (pinned snapshot)", ""])
    if packet["repository_tree_excerpt"]:
        lines.append("```")
        lines.extend(packet["repository_tree_excerpt"])
        lines.append("```")
    else:
        lines.append("_No tree paths selected._")
    lines.append("")

    def _path_block(title: str, items: list[str]) -> None:
        lines.append(f"## {title}")
        lines.append("")
        if items:
            lines.append("```")
            lines.extend(items)
            lines.append("```")
        else:
            lines.append("_None listed in the minimal context window._")
        lines.append("")

    _path_block("Neighbouring paths", packet.get("neighbor_paths") or [])
    _path_block("Nearby documentation paths", packet.get("nearby_documentation_paths") or [])
    _path_block("Nearby configuration paths", packet.get("nearby_configuration_paths") or [])

    lines.append("## Pinned snapshot file excerpts")
    lines.append("")
    files = packet.get("snapshot_file_excerpts") or []
    if not files:
        lines.append("_No additional file excerpts included._")
        lines.append("")
    for fe in files:
        lines.append(f"### {fe['file_alias']}")
        lines.append("")
        lines.append("```")
        lines.append(_fence_safe(fe["content"]))
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def write_outputs(
    results: list[PacketBuildResult],
    *,
    output_dir: Path,
    seed: int,
) -> dict[str, Any]:
    packets_dir = output_dir / "packets"
    private_dir = output_dir / "private"
    # Clean previous packets to avoid stale corrupt packets lingering.
    if packets_dir.exists():
        import shutil

        shutil.rmtree(packets_dir)
    packets_dir.mkdir(parents=True, exist_ok=True)
    private_dir.mkdir(parents=True, exist_ok=True)

    id_map = {
        "access_model": "access_separated_not_cryptographically_sealed",
        "warning": "Never share this file with raters.",
        "protocol_version": PROTOCOL_VERSION,
        "packet_spec_version": PACKET_SPEC_VERSION,
        "seed": seed,
        "entries": [],
    }
    public_eligibility: list[dict[str, str]] = []
    private_eligibility: list[dict[str, str]] = []
    exclusions: list[dict[str, str]] = []

    emitted = 0
    for result in results:
        el = result.eligibility
        public_eligibility.append(
            {
                "neutral_id": el.neutral_id,
                "eligibility_status": el.eligibility_status,
                "reason_code": el.reason_code,
                "explanation": el.explanation,
                "sources_inspected": el.sources_inspected,
                "packet_hash": el.packet_hash,
            }
        )
        private_eligibility.append(
            {
                "neutral_id": el.neutral_id,
                "case_id": el.case_id,
                "eligibility_status": el.eligibility_status,
                "reason_code": el.reason_code,
                "explanation": el.explanation,
                "sources_inspected": el.sources_inspected,
                "packet_hash": el.packet_hash,
            }
        )
        id_map["entries"].append({"neutral_id": el.neutral_id, "case_id": el.case_id})

        if el.eligibility_status not in EMIT_STATUSES:
            exclusions.append(
                {
                    "neutral_id": el.neutral_id,
                    "eligibility_status": el.eligibility_status,
                    "reason_code": el.reason_code,
                    "explanation": el.explanation,
                }
            )

        if result.packet_md and result.packet_json and result.provenance:
            if el.eligibility_status in EMIT_STATUSES:
                case_dir = packets_dir / el.neutral_id
                case_dir.mkdir(parents=True, exist_ok=True)
                (case_dir / "packet.md").write_text(result.packet_md, encoding="utf-8")
                (case_dir / "packet.json").write_text(
                    json.dumps(result.packet_json, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                (case_dir / "provenance.json").write_text(
                    json.dumps(result.provenance, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                emitted += 1

    _write_csv(
        output_dir / "eligibility.csv",
        public_eligibility,
        fieldnames=[
            "neutral_id",
            "eligibility_status",
            "reason_code",
            "explanation",
            "sources_inspected",
            "packet_hash",
        ],
    )
    _write_csv(
        output_dir / "exclusions.csv",
        exclusions,
        fieldnames=["neutral_id", "eligibility_status", "reason_code", "explanation"],
    )
    _write_csv(
        private_dir / "eligibility_internal.csv",
        private_eligibility,
        fieldnames=[
            "neutral_id",
            "case_id",
            "eligibility_status",
            "reason_code",
            "explanation",
            "sources_inspected",
            "packet_hash",
        ],
    )
    (private_dir / "id_map.sealed.json").write_text(
        json.dumps(id_map, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (private_dir / "README.md").write_text(
        "# Private annotation control files\n\n"
        "These files map opaque `neutral_id` values to experimental `case_id` values.\n\n"
        "**Access model:** access-separated directories only — **not** cryptographically sealed.\n\n"
        "Never distribute this directory to raters.\n",
        encoding="utf-8",
    )

    template_path = output_dir / "rater_sheet_template.csv"
    _write_csv(
        template_path,
        [],
        fieldnames=[
            "neutral_id",
            "annotator_id",
            "reference_relevance",
            "material_necessity",
            "confidence",
            "justification",
            "protocol_version",
            "annotation_timestamp",
        ],
    )

    counts: dict[str, int] = {}
    for row in public_eligibility:
        counts[row["eligibility_status"]] = counts.get(row["eligibility_status"], 0) + 1

    return {
        "n_manifest": len(results),
        "n_packets_emitted": emitted,
        "n_excluded": len(exclusions),
        "eligibility_counts": counts,
        "output_dir": str(output_dir),
        "packet_spec_version": PACKET_SPEC_VERSION,
    }


def _write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def generate_packets(
    *,
    manifest_path: Path = DEFAULT_MANIFEST,
    candidates_path: Path = DEFAULT_CANDIDATES,
    output_dir: Path = DEFAULT_OUTPUT,
    blobs_dir: Path = DEFAULT_BLOBS,
    scratch_dir: Path = DEFAULT_SCRATCH,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    rows = load_manifest(manifest_path)
    candidates = load_candidate_index(candidates_path)
    blob_store = BlobStore(blobs_dir)
    repo_cache = BlindRepoCache(scratch_dir)
    translation_cache = load_cache()
    results: list[PacketBuildResult] = []
    for row in rows:
        key = (row["repo_id"], row["instruction_path"], row["anchor_reference"])
        results.append(
            build_packet_for_case(
                row,
                seed=seed,
                blob_store=blob_store,
                candidate=candidates.get(key),
                repo_cache=repo_cache,
                translation_cache=translation_cache,
            )
        )
    summary = write_outputs(results, output_dir=output_dir, seed=seed)
    write_readme(output_dir, summary=summary, seed=seed)
    return summary


def write_readme(output_dir: Path, *, summary: dict[str, Any], seed: int) -> None:
    text = f"""# RQ5 v1 blind load-bearing annotation packets (spec v2)

## Purpose

Construct-valid, outcome-blind packets so raters can answer:

> Is the referenced artifact materially necessary for completing THIS software
> engineering task in THIS repository snapshot?

Protocol: `docs/RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md` @ `e41902c`  
Packet spec: `{PACKET_SPEC_VERSION}`  
Redesign rationale: `PACKET_REDESIGN_V2.md`

## What changed vs v1 instrument

- Concrete task briefs derived from pinned instruction text (not generic pytest templates)
- Verification commands inferred from pinned manifests only
- Minimal repository tree + neighbours + docs/config + file excerpts
- Semantic whole-path redaction (no substring `[[REF]]` corruption)
- Absence statements forbidden; unsafe cases excluded as `not_safe_for_blinding`
- Non-English excerpts professionally translated via cache
- Degenerate / non-software packets excluded

## Eligibility vs Ambiguous

Eligibility is a data-preparation decision. Scientific `Ambiguous` remains an annotator label.

## Generation

```bash
make rq5-v1-blind-lb-packets
# requires network for bare clones into scratch/rq5_blind_trees/
```

Seed: {seed}

## Last generation

- Manifest cases: {summary.get("n_manifest")}
- Packets emitted: {summary.get("n_packets_emitted")}
- Excluded: {summary.get("n_excluded")}
- Counts: {json.dumps(summary.get("eligibility_counts", {}), sort_keys=True)}
"""
    (output_dir / "README.md").write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate RQ5 v1 blind LB annotation packets (v2)")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--blobs-dir", type=Path, default=DEFAULT_BLOBS)
    parser.add_argument("--scratch-dir", type=Path, default=DEFAULT_SCRATCH)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args(argv)
    summary = generate_packets(
        manifest_path=args.manifest,
        candidates_path=args.candidates,
        output_dir=args.output_dir,
        blobs_dir=args.blobs_dir,
        scratch_dir=args.scratch_dir,
        seed=args.seed,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
