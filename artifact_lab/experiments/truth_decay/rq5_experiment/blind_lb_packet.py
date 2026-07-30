"""Generate sanitized, outcome-blind annotation packets for RQ5 v1.

Pre-treatment materials only. Does not classify load-bearing scientifically.
Protocol: docs/RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md @ e41902c
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

from artifact_lab.store.blobs import BlobStore

PROTOCOL_VERSION = "RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c"
DEFAULT_SEED = 42
DEFAULT_MANIFEST = Path("exports/rq5_agent_impact/rq5_case_manifest.csv")
DEFAULT_CANDIDATES = Path("exports/truth_decay_pilot/rq5_candidate_dataset.csv")
DEFAULT_OUTPUT = Path("exports/rq5_lb_blind_annotation")
DEFAULT_BLOBS = Path("data/blobs")

# Rater-facing forbidden substrings (case-insensitive).
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

# Whole-word / token patterns that reveal experimental design.
FORBIDDEN_TOKEN_RE = re.compile(
    r"(?i)\b(condition\s*[abc]|a/b/c|born[\s_-]?stale|confirmed[\s_-]?false|"
    r"truthful|task_success|causal_role|mediation|load_bearing_stratum)\b"
)

REF_TOKEN = "[[REF]]"
ARTIFACT_ALIAS = "Referenced artifact R1"


@dataclass
class EligibilityRow:
    neutral_id: str
    eligibility_status: str
    reason_code: str
    explanation: str
    sources_inspected: str
    packet_hash: str = ""
    case_id: str = ""  # sealed/private only


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


def treatment_specific_strings(text_a: str, text_b: str, anchor: str) -> set[str]:
    """Strings that appear in B but not A (plus the anchor path) — never show to raters."""
    banned: set[str] = {anchor, anchor.rstrip("/")}
    if not text_b:
        return banned
    # Path-like tokens unique to B.
    path_re = re.compile(r"[A-Za-z0-9_./\-]+(?:/[A-Za-z0-9_./\-]+)+")
    for token in path_re.findall(text_b):
        if token not in text_a and len(token) >= 4:
            banned.add(token)
    return {t for t in banned if t}


def sanitize_text(text: str, banned: Iterable[str]) -> str:
    out = text
    # Longest first to avoid partial overlaps.
    for token in sorted({t for t in banned if t}, key=len, reverse=True):
        if token:
            out = out.replace(token, REF_TOKEN)
    return out


def extract_instruction_sentences(instruction_text: str, anchor: str) -> list[str]:
    if not instruction_text or not anchor:
        return []
    lines = instruction_text.splitlines()
    hits = [ln.strip() for ln in lines if anchor in ln or anchor.rstrip("/") in ln]
    if hits:
        return hits[:8]
    # Fallback: window around first occurrence.
    idx = instruction_text.find(anchor)
    if idx < 0:
        return []
    start = max(0, idx - 120)
    end = min(len(instruction_text), idx + len(anchor) + 120)
    return [instruction_text[start:end].strip()]


def neutral_task_brief(test_command: str, task_prompt: str) -> str:
    cmd = (test_command or "the project test command").strip()
    # Do not copy raw task_prompt if it mentions instruction-file authority in a
    # way that invites reading the treated file as the sole oracle; keep brief generic.
    return (
        "Complete a small, bounded change in the pinned repository snapshot so that "
        f"the project test command `{cmd}` passes. "
        "Use only files present in the snapshot. "
        "Judge whether Referenced artifact R1 is materially necessary for that task."
    )


def artifact_role_description(anchor_type: str, sanitized_sentences: list[str]) -> str:
    kind = {
        "path": "a file path cited by the project instruction text",
        "directory": "a directory path cited by the project instruction text",
        "command": "a command cited by the project instruction text",
        "script_name": "a script name cited by the project instruction text",
        "dependency": "a dependency cited by the project instruction text",
    }.get(anchor_type, "a repository artifact cited by the project instruction text")
    base = (
        f"{ARTIFACT_ALIAS} denotes {kind}. "
        "Its identity is withheld as a path string so treatment assignment cannot be inferred."
    )
    if sanitized_sentences:
        base += " The instruction context around the citation is provided below with the path replaced by [[REF]]."
    return base


def leakage_hits(text: str, extra_banned: Iterable[str] = ()) -> list[str]:
    hits: list[str] = []
    lower = text.lower()
    for token in FORBIDDEN_SUBSTRINGS:
        if token in lower:
            hits.append(token)
    if FORBIDDEN_TOKEN_RE.search(text):
        hits.append("forbidden_token_pattern")
    for token in extra_banned:
        if not token:
            continue
        if "/" in token or "\\" in token or token.startswith("http"):
            if token in text:
                hits.append(f"banned_path:{token[:40]}")
        elif len(token) >= 8:
            # Whole-token match for long bare names (avoid 'proj' ⊂ 'project').
            if re.search(rf"(?<![A-Za-z0-9_]){re.escape(token)}(?![A-Za-z0-9_])", text):
                hits.append(f"banned_token:{token[:40]}")
    # Raw condition labels
    for lab in ("condition A", "condition B", "condition C", "Condition A", "Condition B"):
        if lab in text:
            hits.append(lab)
    return sorted(set(hits))


def _repo_basename(repo_url: str) -> str | None:
    if not repo_url:
        return None
    name = repo_url.rstrip("/").split("/")[-1]
    if name.endswith(".git"):
        name = name[:-4]
    # Skip tiny/generic basenames that collide with English words.
    if len(name) < 8:
        return None
    return name


def build_packet_for_case(
    row: dict[str, str],
    *,
    seed: int,
    blob_store: BlobStore,
    candidate: dict[str, str] | None,
) -> PacketBuildResult:
    case_id = row["case_id"]
    neutral_id = stable_neutral_id(case_id, seed=seed)
    sources: list[str] = ["rq5_case_manifest.csv"]
    if candidate:
        sources.append("rq5_candidate_dataset.csv")

    blob_a_sha = row.get("condition_a_blob_sha", "")
    blob_b_sha = row.get("condition_b_blob_sha", "")
    anchor = row.get("anchor_reference", "")
    instruction_path = row.get("instruction_path", "")

    if not blob_store.has(blob_a_sha):
        return PacketBuildResult(
            eligibility=EligibilityRow(
                neutral_id=neutral_id,
                case_id=case_id,
                eligibility_status="source_unavailable",
                reason_code="missing_instruction_blob_a",
                explanation="Pinned instruction blob for the sanitized text source is missing from the blob store.",
                sources_inspected=";".join(sources + [f"blob:{blob_a_sha[:12]}"]),
            )
        )

    text_a = _decode_blob(blob_store.get_text(blob_a_sha))
    sources.append(f"blob_store:{blob_a_sha[:16]}")
    text_b = ""
    if blob_store.has(blob_b_sha):
        text_b = _decode_blob(blob_store.get_text(blob_b_sha))
        # Inspected only to compute treatment-specific ban list; never emitted.
        sources.append("blob_store:contrast_inspected_not_emitted")

    banned = treatment_specific_strings(text_a, text_b, anchor)
    banned.add(instruction_path)
    # Also ban github URLs / repo names from rater text.
    repo_url = row.get("repo_url", "")
    if repo_url:
        banned.add(repo_url)
        base = _repo_basename(repo_url)
        if base:
            banned.add(base)

    sentences = extract_instruction_sentences(text_a, anchor)
    if not sentences:
        return PacketBuildResult(
            eligibility=EligibilityRow(
                neutral_id=neutral_id,
                case_id=case_id,
                eligibility_status="insufficient_pre_treatment_context",
                reason_code="anchor_not_in_instruction_blob",
                explanation="Could not locate the anchor citation inside the sanitized instruction source text.",
                sources_inspected=";".join(sources),
            )
        )

    sanitized_sentences = [sanitize_text(s, banned) for s in sentences]
    # If sanitization failed to remove anchor, refuse.
    for s in sanitized_sentences:
        if anchor and anchor in s:
            return PacketBuildResult(
                eligibility=EligibilityRow(
                    neutral_id=neutral_id,
                    case_id=case_id,
                    eligibility_status="condition_leakage_risk",
                    reason_code="anchor_path_not_fully_redacted",
                    explanation="Anchor path remained visible after sanitization; packet generation refused.",
                    sources_inspected=";".join(sources),
                )
            )

    # Generic task prompt alone is not a separable task oracle.
    task_prompt = row.get("task_prompt", "")
    if "described in the project instruction file" in task_prompt.lower():
        # Still allowed if we supply a neutral brief + citation context; flag for review.
        needs_manual = True
    else:
        needs_manual = False

    brief = neutral_task_brief(row.get("test_command", ""), task_prompt)
    role = artifact_role_description(row.get("anchor_reference_type", ""), sanitized_sentences)

    tree_note = (
        "A full repository tree excerpt is not included in this offline packet build. "
        "Judge from the task brief and the instruction citation context only."
    )

    packet_json: dict[str, Any] = {
        "neutral_id": neutral_id,
        "anonymous_snapshot_id": anonymous_snapshot_id(
            row.get("repo_id", ""), row.get("task_commit_sha", ""), seed=seed
        ),
        "protocol_version": PROTOCOL_VERSION,
        "task_brief": brief,
        "reference_type": row.get("anchor_reference_type", ""),
        "referenced_artifact_alias": ARTIFACT_ALIAS,
        "artifact_role_description": role,
        "instruction_citation_excerpts": sanitized_sentences,
        "repository_tree_excerpt": tree_note,
        "path_policy": (
            "Manipulated and experimental path strings are withheld. "
            "Citations use [[REF]] / Referenced artifact R1 so treatment assignment cannot be read from path identity."
        ),
    }

    packet_md = _render_packet_md(packet_json)
    combined = packet_md + "\n" + json.dumps(packet_json, sort_keys=True)
    hits = leakage_hits(combined, extra_banned=banned - {anchor, instruction_path})
    # Anchor/instruction_path must not appear; check explicitly.
    if anchor and anchor in combined:
        hits.append("raw_anchor_present")
    if instruction_path and instruction_path in combined:
        hits.append("instruction_path_present")

    if hits:
        return PacketBuildResult(
            eligibility=EligibilityRow(
                neutral_id=neutral_id,
                case_id=case_id,
                eligibility_status="condition_leakage_risk",
                reason_code="leakage_scan_failed",
                explanation=f"Refused to emit packet; leakage scan hits: {', '.join(hits[:12])}",
                sources_inspected=";".join(sources),
            )
        )

    status = "eligible"
    reason = "pre_treatment_packet_built"
    explanation = "Sanitized pre-treatment packet generated from instruction blob and manifest metadata."
    if needs_manual:
        status = "requires_manual_packet_review"
        reason = "generic_task_prompt_coupled_to_instruction_file"
        explanation = (
            "Packet was built, but the experimental task prompt is generic and couples the task "
            "to the instruction file; human QA should confirm the brief is sufficient before rater distribution."
        )

    packet_hash = sha256_text(packet_md)
    provenance = {
        "neutral_id": neutral_id,
        "protocol_version": PROTOCOL_VERSION,
        "seed": seed,
        "sources": sources,
        "excerpts": [
            {
                "field": "instruction_citation_excerpts",
                "source_kind": "instruction_blob_pre_treatment",
                "sanitized": True,
                "note": "Path tokens replaced with [[REF]]; contrast blob inspected only for ban-list.",
            }
        ],
        "packet_sha256": packet_hash,
        "blinding": {
            "paths_redacted": True,
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
            eligibility_status=status,
            reason_code=reason,
            explanation=explanation,
            sources_inspected=";".join(sources),
            packet_hash=packet_hash,
        ),
        packet_md=packet_md,
        packet_json=packet_json,
        provenance=provenance,
    )


def _render_packet_md(packet: dict[str, Any]) -> str:
    lines = [
        f"# Annotation packet `{packet['neutral_id']}`",
        "",
        f"Protocol: `{packet['protocol_version']}`",
        "",
        "Judge only with the materials below. Do not seek external experimental results.",
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
        lines.append(f"{i}. `{excerpt}`")
        lines.append("")
    lines.extend(
        [
            "## Repository tree excerpt",
            "",
            packet["repository_tree_excerpt"],
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(
    results: list[PacketBuildResult],
    *,
    output_dir: Path,
    seed: int,
) -> dict[str, Any]:
    packets_dir = output_dir / "packets"
    private_dir = output_dir / "private"
    packets_dir.mkdir(parents=True, exist_ok=True)
    private_dir.mkdir(parents=True, exist_ok=True)

    id_map = {
        "access_model": "access_separated_not_cryptographically_sealed",
        "warning": "Never share this file with raters.",
        "protocol_version": PROTOCOL_VERSION,
        "seed": seed,
        "entries": [],
    }
    public_eligibility: list[dict[str, str]] = []
    private_eligibility: list[dict[str, str]] = []

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

        if result.packet_md and result.packet_json and result.provenance:
            if el.eligibility_status in {"eligible", "requires_manual_packet_review"}:
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
    if not template_path.exists():
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
        "eligibility_counts": counts,
        "output_dir": str(output_dir),
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
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    rows = load_manifest(manifest_path)
    candidates = load_candidate_index(candidates_path)
    blob_store = BlobStore(blobs_dir)
    results: list[PacketBuildResult] = []
    for row in rows:
        key = (row["repo_id"], row["instruction_path"], row["anchor_reference"])
        results.append(
            build_packet_for_case(
                row,
                seed=seed,
                blob_store=blob_store,
                candidate=candidates.get(key),
            )
        )
    summary = write_outputs(results, output_dir=output_dir, seed=seed)
    write_readme(output_dir, summary=summary, seed=seed)
    return summary


def write_readme(output_dir: Path, *, summary: dict[str, Any], seed: int) -> None:
    text = f"""# RQ5 v1 blind load-bearing annotation packets

## Purpose

Prepare **outcome-blind**, **condition-blind** annotation packets so human raters can
judge whether a referenced artifact is **materially necessary** for the intended task
**before** any runtime evidence is considered.

Authoritative rater protocol:

- `docs/RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md`
- Commit reference: `e41902c`

## Packet eligibility vs scientific Ambiguous

| Concept | Meaning |
|---------|---------|
| **Eligibility** (`eligibility.csv`) | Data-preparation decision: can we emit a safe pre-treatment packet? |
| **Ambiguous** (rater label) | Scientific judgment: materials are insufficient for confident necessity |

Never map ineligible packets to the annotator label `Ambiguous`.

## Source boundaries (allowed)

- `exports/rq5_agent_impact/rq5_case_manifest.csv`
- Instruction bytes from `data/blobs/` using the **sanitized source blob** only
  (manifest field used internally for retrieval; never named as a condition to raters)
- Optional join to `exports/truth_decay_pilot/rq5_candidate_dataset.csv` for
  pre-treatment metadata (not emitted raw when leaky)
- Protocol document above

## Source boundaries (forbidden)

- Agent traces, success/failure, A/B/C outcomes
- Mediation / uptake / causal-role exports
- Existing load-bearing stratum labels
- Rater exposure to private ID maps

## Blinding guarantees (implemented)

- Opaque `neutral_id` (seed={seed})
- No `case_id`, repo URL, or raw experimental paths in rater packets
- Citations use `[[REF]]` / `Referenced artifact R1`
- Contrast instruction bytes may be inspected only to build a ban-list; never emitted
- Leakage scan before emit; refuse on hit (`condition_leakage_risk`)

## Access model for ID map

`private/id_map.sealed.json` is **access-separated**, not cryptographically sealed.
Do not share `private/` with raters.

## Authoritative final classification rule

Derived from rater fields (not entered manually):

```
if relevance == ambiguous -> ambiguous
elif necessity == ambiguous -> ambiguous
elif relevance == directly_relevant and necessity == materially_necessary -> load_bearing
elif relevance in {{irrelevant, contextually_relevant}} -> non_load_bearing
elif necessity in {{not_necessary, helpful_but_substitutable}} -> non_load_bearing
else -> ambiguous
```

`contextually_relevant + materially_necessary` is **non_load_bearing** (with consistency warning).

Implementation: `artifact_lab/experiments/truth_decay/rq5_experiment/blind_lb_derive.py`

## Generation command

```bash
cd /home/cesar/papers/artifact-lifecycle-lab/artifact-lifecycle-lab
.venv/bin/python -m artifact_lab.experiments.truth_decay.rq5_experiment.blind_lb_packet \\
  --manifest exports/rq5_agent_impact/rq5_case_manifest.csv \\
  --output-dir exports/rq5_lb_blind_annotation \\
  --seed {seed}
```

Or: `make rq5-v1-blind-lb-packets`

Human Annotation Kit (distribute to raters):

```bash
make rq5-v1-blind-lb-annotation-kit
```

Coordinator workflow: `COORDINATOR_GUIDE.md` (not part of the rater ZIP).

## Directory structure

```
exports/rq5_lb_blind_annotation/
├── README.md
├── COORDINATOR_GUIDE.md     # coordinator only
├── eligibility.csv          # rater-safe (no case_id)
├── rater_sheet_template.csv
├── human_annotation_kit/    # DISTRIBUTE THIS DIRECTORY / ZIP
├── packets/<neutral_id>/    # internal generator output
│   ├── packet.md
│   ├── packet.json
│   └── provenance.json
└── private/                 # NEVER give to raters
    ├── id_map.sealed.json
    ├── eligibility_internal.csv
    └── README.md
```

## What raters receive

- The full `human_annotation_kit/` directory (or ZIP)
- Instructions, codebook, forms, `PACKETS/`, `HASHES/`

## What raters must never receive

- `private/`
- Any RQ5 results, traces, mediation exports
- Manuscript sections discussing outcomes

## Known limitations

- Offline build omits full repository tree excerpts (noted in packet).
- Generic experimental task prompts couple the task to the instruction file;
  many packets are marked `requires_manual_packet_review` for human QA before distribution.
- Path redaction prevents showing the literal referenced path; raters judge from role + citation context.

## Last generation summary

- Manifest cases: {summary.get("n_manifest")}
- Packets emitted: {summary.get("n_packets_emitted")}
- Eligibility counts: {json.dumps(summary.get("eligibility_counts", {}), sort_keys=True)}
"""
    (output_dir / "README.md").write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate RQ5 v1 blind LB annotation packets")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--blobs-dir", type=Path, default=DEFAULT_BLOBS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args(argv)
    summary = generate_packets(
        manifest_path=args.manifest,
        candidates_path=args.candidates,
        output_dir=args.output_dir,
        blobs_dir=args.blobs_dir,
        seed=args.seed,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
