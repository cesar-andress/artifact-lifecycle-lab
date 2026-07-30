"""Build the rater-facing RQ5 v1 Human Annotation Kit from generated packets.

Does not classify cases, inspect outcomes, or expose the private ID map.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from artifact_lab.experiments.truth_decay.rq5_experiment.blind_lb_packet import (
    DEFAULT_OUTPUT,
    DEFAULT_SEED,
    leakage_hits,
)

KIT_GENERATOR_VERSION = "1.0.0"
PROTOCOL_VERSION = "RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c"
ALLOWED_PACKET_KEYS = frozenset(
    {
        "anonymous_snapshot_id",
        "artifact_role_description",
        "instruction_citation_excerpts",
        "neutral_id",
        "path_policy",
        "protocol_version",
        "reference_type",
        "referenced_artifact_alias",
        "repository_tree_excerpt",
        "task_brief",
    }
)
FORM_COLUMNS = [
    "neutral_id",
    "reference_relevance",
    "material_necessity",
    "confidence",
    "justification",
    "notes_for_coordinator",
]
RELEVANCE_VALUES = [
    "irrelevant",
    "contextually_relevant",
    "directly_relevant",
    "ambiguous",
]
NECESSITY_VALUES = [
    "not_necessary",
    "helpful_but_substitutable",
    "materially_necessary",
    "ambiguous",
]
CONFIDENCE_VALUES = ["high", "medium", "low"]

# Extra tokens that must never appear in the rater-facing kit.
KIT_FORBIDDEN_EXTRA = (
    "case_id",
    "load_bearing",
    "non_load_bearing",
    "mediation",
    "uptake",
    "born_stale",
    "confirmed_false",
    "condition_a",
    "condition_b",
    "condition_c",
    "task_success",
    "failure_reason",
    "causal_role",
    "id_map",
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _repo_commit(repo_root: Path) -> str:
    head = repo_root / ".git" / "HEAD"
    if not head.exists():
        return "unknown"
    ref = head.read_text(encoding="utf-8").strip()
    if ref.startswith("ref:"):
        ref_path = repo_root / ".git" / ref.split(" ", 1)[1].strip()
        if ref_path.exists():
            return ref_path.read_text(encoding="utf-8").strip()[:40]
    return ref[:40]


def write_docs(kit_dir: Path) -> list[Path]:
    """Write static instruction documents into the kit. Returns written paths."""
    docs: dict[str, str] = {}

    docs["README_START_HERE.md"] = f"""# Start here — RQ5 v1 Human Annotation Kit

## Purpose

You will judge, for each case packet, whether a **referenced project artifact** is
**materially necessary** for completing a stated software-engineering task in a
frozen repository snapshot.

You are **not** reviewing a paper, scoring an AI agent, or guessing experimental
outcomes. You only use the materials in this kit.

Protocol version: `{PROTOCOL_VERSION}`

## Estimated duration

About **1–2 hours** for ~30 cases (roughly 2–4 minutes each). Some cases may take
longer if the materials are thin; **Ambiguous** is an allowed answer.

## Independence (required)

- Work alone.
- Do not discuss cases with the other annotator until both have submitted.
- Do not look up the repositories online or open related project folders.
- Do not compare notes mid-task.

## What you produce

1. Fill **`ANNOTATION_FORM.csv`** (or the Excel twin, then export/save as CSV).
2. Optionally keep private scratch notes — do **not** return packets.

Return **only** your completed `ANNOTATION_FORM.csv` (see return instructions below).

## How to work (order)

1. Read `CHECKLIST_BEFORE_STARTING.md` and tick it mentally.
2. Skim `ANNOTATOR_INSTRUCTIONS.md`, then keep `CODEBOOK.md` open while coding labels.
3. Use `PACKET_INDEX.csv` as your worklist.
4. For each `neutral_id`, open `PACKETS/<neutral_id>/packet.md` (JSON is optional).
5. Enter one row per case in `ANNOTATION_FORM.csv`.
6. Before sending, complete `CHECKLIST_BEFORE_SUBMISSION.md`.

## Submission

Email or upload **only**:

- `ANNOTATION_FORM.csv`

Do not modify or return the `PACKETS/` tree. Do not return this whole kit.

## If something looks broken

Stop on that case. Put `ambiguous` for both relevance and necessity if needed, set
confidence to `low`, and describe the issue in `notes_for_coordinator` (e.g. missing
file, unreadable packet). Contact the study coordinator with the `neutral_id` only —
never invent experimental labels.

FAQ: `FAQ.md`.
"""

    docs["ANNOTATOR_INSTRUCTIONS.md"] = f"""# Annotator instructions (plain language)

Protocol reference: `{PROTOCOL_VERSION}`

You are an experienced software engineer reviewing frozen case packets. You have
never seen this study before — that is intentional.

## What the task is

Each packet describes:

- a **task brief** (what a competent engineer would try to do),
- a **referenced artifact** shown only as an alias such as **Referenced artifact R1**,
- short **instruction-file excerpts** where the real path is replaced by `[[REF]]`,
- a factual note about the artifact’s role.

Your job for every case:

1. Judge **reference relevance** — how the artifact relates to the task.
2. Judge **material necessity** — whether that artifact’s information would normally
   be required to complete the task in the given snapshot.
3. Record **confidence** and a short **justification**.

You do **not** enter a final “load-bearing / not” label. The coordinator derives that
later from your two dimensions using a fixed rule.

## What you should evaluate

Ask yourself:

> For this task, in this snapshot, would a competent engineer ordinarily need the
> information that Referenced artifact R1 uniquely or materially supplies?

Use only:

- the packet text,
- definitions in `CODEBOOK.md`.

## What you must ignore

Do **not** reason about:

- whether any AI agent would open the file,
- whether a run would succeed or fail,
- which study arm a case might belong to,
- “what the experimenters were testing”,
- prior papers, blogs, or GitHub searches about the project.

If a thought like that appears, discard it and return to the packet.

## Uncertainty

If the packet does not give enough pre-task evidence, choose **`ambiguous`** on the
dimension(s) you cannot support. Ambiguous is a valid scientific answer — do not
force a binary guess.

## Confidence

- **high** — clear evidence in the packet for both judgments.
- **medium** — plausible reading, some gaps.
- **low** — thin materials or conflicting cues; often pairs with `ambiguous`.

Low confidence is acceptable.

## Allowed label spellings (use exactly)

**reference_relevance:** `irrelevant` | `contextually_relevant` | `directly_relevant` | `ambiguous`

**material_necessity:** `not_necessary` | `helpful_but_substitutable` | `materially_necessary` | `ambiguous`

**confidence:** `high` | `medium` | `low`

## Good justifications (style)

Good:

> The citation tells the engineer to add configuration to [[REF]]. The task is to
> make pytest pass with a small change. The excerpt does not show that [[REF]] holds
> unique test or build settings; equivalent guidance could live in the test tree.
> I mark contextually relevant and helpful but substitutable.

Good:

> Packet materials are limited to a generic task brief and one redacted citation
> line. I cannot tell whether R1 uniquely supplies required settings. Ambiguous on
> both dimensions; low confidence.

## Bad justifications (avoid)

Bad:

> Agents usually ignore AGENTS.md so this is not load-bearing.

Bad:

> Condition B would break this path so it must matter.

Bad:

> I looked up the repo on GitHub and the file is important.

Bad:

> Success rates in similar papers suggest…

Keep justifications to **2–5 sentences**, grounded only in the packet.

## Practical workflow

1. Open `PACKETS/<id>/packet.md`.
2. Read the task brief once.
3. Read the role note and citation excerpts.
4. Assign relevance, then necessity (in that order).
5. Write the justification.
6. Move to the next row — do not revise earlier rows after seeing later cases.
"""

    docs["CODEBOOK.md"] = f"""# Codebook — authoritative definitions

Source of truth: `{PROTOCOL_VERSION}`

Form fields use **snake_case** values listed below.

---

## Reference relevance

How the referenced artifact relates to the task.

### `irrelevant`

The artifact has no meaningful connection to completing the stated task.

**Positive example:** Task is fix a unit test in `tests/`; R1 is a marketing copy file
never mentioned in build/test flow.

**Negative example (do not use irrelevant here):** Task needs the correct pytest
config and R1 is clearly that config file — that is at least contextual or direct.

### `contextually_relevant`

Related background (conventions, architecture notes, general setup) that helps
understanding but is not the specific information the task hinges on.

**Positive example:** Coding-standards doc cited near the task area; task can still
be done from tests and code without that doc.

### `directly_relevant`

The artifact is specifically about the same concern as the task (e.g. the config,
script, or instructions the task would normally consult).

**Positive example:** Task is “make pytest pass”; R1 is the project’s pytest/config
entry the instruction file tells you to edit.

### `ambiguous` (relevance)

Packet evidence is insufficient to place the artifact on the relevance scale.

---

## Material necessity

Assume a **competent engineer** doing the task. Ask whether completing the task
**normally requires** information uniquely or materially supplied by R1.

Not: “Would it be nice to read?” Not: “Would I personally open it?”

### `not_necessary`

Task can be completed without that artifact’s information.

### `helpful_but_substitutable`

Useful, but equivalent information exists (or would ordinarily be found) elsewhere
in the snapshot / standard engineering practice for this task.

### `materially_necessary`

The task would ordinarily require that information; without it, competent completion
is not expected from the remaining materials alone.

### `ambiguous` (necessity)

Cannot tell from the packet whether the information is required.

---

## Final derivation rule (coordinator only — do not fill this in)

You do **not** enter the final label. For transparency, the rule is:

```
if relevance == ambiguous -> ambiguous
elif necessity == ambiguous -> ambiguous
elif relevance == directly_relevant AND necessity == materially_necessary -> load_bearing
elif relevance in {{irrelevant, contextually_relevant}} -> non_load_bearing
elif necessity in {{not_necessary, helpful_but_substitutable}} -> non_load_bearing
else -> ambiguous
```

Important: **`contextually_relevant` + `materially_necessary` is not load-bearing**
under this protocol; it derives to non-load-bearing (and may be audited).

Load-bearing requires **both** `directly_relevant` and `materially_necessary`.

---

## Decision tree

```
Start
  └─ Enough evidence for relevance?
        ├─ No → relevance = ambiguous → (necessity may also be ambiguous)
        └─ Yes → pick irrelevant / contextually_relevant / directly_relevant
              └─ Enough evidence for necessity?
                    ├─ No → necessity = ambiguous
                    └─ Yes → not_necessary / helpful_but_substitutable / materially_necessary
```

Then stop. Do not compute the final class yourself.

---

## Common mistakes

1. Calling something load-bearing because it “looks important” or is mentioned.
2. Using necessity = materially_necessary when relevance is only contextual
   (allowed as your judgment, but understand it will not become load-bearing).
3. Inferring what an agent did at runtime.
4. Searching the live repository instead of using the packet.
5. Leaving justification blank or one vague sentence.
6. Using display labels with spaces instead of snake_case form values.
"""

    docs["FAQ.md"] = f"""# FAQ

Protocol: `{PROTOCOL_VERSION}`

### What if I cannot decide?

Use `ambiguous` on the dimension(s) you cannot support. Set confidence to `low` or
`medium`. Explain briefly what is missing in the justification.

### What if multiple files seem equivalent?

If R1’s information could equally come from another ordinary source in the project,
prefer `helpful_but_substitutable` rather than `materially_necessary`.

### What if the reference seems useful but optional?

That is usually `helpful_but_substitutable` (and often `contextually_relevant` or
`directly_relevant` depending on how specific it is). Useful ≠ necessary.

### What if I suspect information is missing?

Do not invent contents. Mark `ambiguous` as needed and note the gap in
`notes_for_coordinator`.

### What if I think the packet is malformed?

Finish other cases. For the bad one, use `ambiguous` / `ambiguous` / `low` if you
cannot judge, and describe the defect in `notes_for_coordinator` with the
`neutral_id`. Contact the coordinator.

### What if I recognize the repository?

Do not dig into memory or the internet for extra files. Judge **only** what the
packet shows. If recognition makes you unsure you can stay blind, say so in
`notes_for_coordinator` and prefer `ambiguous` when memory would substitute for
packet evidence.

### What if I accidentally infer the experiment?

Stop that line of thought. Re-read the task brief and excerpts only. Do not write
experimental guesses in the justification. If the inference won’t go away, use
`ambiguous` and tell the coordinator in notes (without spelling out treatment
guesses if you can avoid it).

### Should I fill a final load-bearing column?

No. Only the columns in `ANNOTATION_FORM.csv`.

### Can I edit packet files?

No. Read-only. Return only the form.
"""

    docs["CHECKLIST_BEFORE_STARTING.md"] = """# Checklist — before starting

Confirm each item:

- [ ] I have read `README_START_HERE.md` and `ANNOTATOR_INSTRUCTIONS.md`.
- [ ] I understand `CODEBOOK.md` label spellings (snake_case).
- [ ] I have **not** seen another annotator’s answers for these cases.
- [ ] I will **not** discuss cases until both submissions are in.
- [ ] I understand **Ambiguous** is an acceptable scientific outcome.
- [ ] I will complete every case **independently** and in isolation from runtime results.
- [ ] I will not search the web or open external checkouts for these projects.
- [ ] I will record confidence and a 2–5 sentence justification for every row.
- [ ] I know I must return only `ANNOTATION_FORM.csv`.
"""

    docs["CHECKLIST_BEFORE_SUBMISSION.md"] = """# Checklist — before submission

- [ ] Every `neutral_id` in `PACKET_INDEX.csv` has exactly one form row.
- [ ] No blank `reference_relevance`, `material_necessity`, or `confidence`.
- [ ] No blank `justification` (minimum ~2 sentences).
- [ ] Values use allowed snake_case enums only.
- [ ] Justification does **not** mention: agent, trace, condition, success, failure,
      runtime, experiment (as study arm / outcome).
- [ ] I consulted **no** external resources beyond this kit.
- [ ] I did **not** discuss cases with the other annotator.
- [ ] I did **not** modify files under `PACKETS/`.
- [ ] I am returning **only** `ANNOTATION_FORM.csv` (optional personal notes kept private).
- [ ] My filename makes the annotator ID clear if the coordinator asked
      (e.g. `ANNOTATION_FORM_annotator_A.csv`) — only if instructed; otherwise keep
      the default name and identify yourself in the submission message.
"""

    docs["RETURN_INSTRUCTIONS.md"] = """# What to return

## Required

- `ANNOTATION_FORM.csv` — fully filled, one row per packet.

## Optional

- A short personal notes file **only if the coordinator asks**. Default: do not send.

## Do not return

- The `PACKETS/` directory or any modified packet.
- This entire kit ZIP.
- Screenshots of code search outside the kit.
- Any file from outside `human_annotation_kit/`.

## Integrity

If the coordinator sent `HASHES/manifest.sha256`, you do not need to recompute hashes
unless asked. Do not alter instruction files before reading them.
"""

    written: list[Path] = []
    for name, text in docs.items():
        path = kit_dir / name
        path.write_text(text.strip() + "\n", encoding="utf-8")
        written.append(path)
    return written


def write_annotation_form_csv(path: Path, neutral_ids: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FORM_COLUMNS)
        w.writeheader()
        for nid in neutral_ids:
            w.writerow(
                {
                    "neutral_id": nid,
                    "reference_relevance": "",
                    "material_necessity": "",
                    "confidence": "",
                    "justification": "",
                    "notes_for_coordinator": "",
                }
            )


def write_annotation_form_xlsx(path: Path, neutral_ids: list[str]) -> None:
    """Write a minimal XLSX (Office Open XML) without third-party deps."""

    def col_letter(idx: int) -> str:
        # 1-based index to Excel column letters
        letters = ""
        while idx:
            idx, rem = divmod(idx - 1, 26)
            letters = chr(65 + rem) + letters
        return letters

    def sheet_xml(name: str, rows: list[list[str]]) -> str:
        # Shared-string-free inline strings for simplicity.
        sheet_rows = []
        for r_i, row in enumerate(rows, start=1):
            cells = []
            for c_i, val in enumerate(row, start=1):
                ref = f"{col_letter(c_i)}{r_i}"
                cells.append(
                    f'<c r="{ref}" t="inlineStr"><is><t>{escape(val)}</t></is></c>'
                )
            sheet_rows.append(f'<row r="{r_i}">{"".join(cells)}</row>')
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            f'<sheetData>{"".join(sheet_rows)}</sheetData></worksheet>'
        )

    ann_rows = [FORM_COLUMNS] + [
        [nid, "", "", "", "", ""] for nid in neutral_ids
    ]
    legend_rows = [["field", "allowed_value"]]
    for v in RELEVANCE_VALUES:
        legend_rows.append(["reference_relevance", v])
    for v in NECESSITY_VALUES:
        legend_rows.append(["material_necessity", v])
    for v in CONFIDENCE_VALUES:
        legend_rows.append(["confidence", v])

    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>
"""
    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>
"""
    wb = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="annotations" sheetId="1" r:id="rId1"/>
    <sheet name="allowed_values" sheetId="2" r:id="rId2"/>
  </sheets>
</workbook>
"""
    wb_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>
</Relationships>
"""
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("xl/workbook.xml", wb)
        zf.writestr("xl/_rels/workbook.xml.rels", wb_rels)
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml("annotations", ann_rows))
        zf.writestr("xl/worksheets/sheet2.xml", sheet_xml("allowed_values", legend_rows))


def copy_packets(src_packets: Path, dest_packets: Path) -> list[str]:
    """Copy rater-facing packet files only (no internal provenance metadata)."""
    if dest_packets.exists():
        shutil.rmtree(dest_packets)
    dest_packets.mkdir(parents=True)
    ids: list[str] = []
    for child in sorted(src_packets.iterdir()):
        if not child.is_dir():
            continue
        nid = child.name
        ids.append(nid)
        target = dest_packets / nid
        target.mkdir()
        # Omit provenance.json: internal lineage may mention case_id_* flags.
        for name in ("packet.md", "packet.json"):
            src = child / name
            if src.exists():
                shutil.copy2(src, target / name)
    return ids


def build_packet_index(
    path: Path,
    *,
    neutral_ids: list[str],
    eligibility: dict[str, dict[str, str]],
) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["neutral_id", "packet_filename", "status", "notes"],
        )
        w.writeheader()
        for nid in neutral_ids:
            el = eligibility.get(nid, {})
            status = el.get("eligibility_status", "unknown")
            note = el.get("reason_code", "")
            if status == "requires_manual_packet_review":
                notes = (
                    f"{note}; coordinator flagged for human QA of task-brief sufficiency"
                )
            else:
                notes = note
            w.writerow(
                {
                    "neutral_id": nid,
                    "packet_filename": f"PACKETS/{nid}/packet.md",
                    "status": status,
                    "notes": notes,
                }
            )


def load_eligibility(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as f:
        return {row["neutral_id"]: row for row in csv.DictReader(f)}


def qa_packet(packet_dir: Path, *, generated_at: str) -> dict[str, Any]:
    md = packet_dir / "packet.md"
    js = packet_dir / "packet.json"
    issues: list[str] = []
    if not md.exists():
        issues.append("missing_packet_md")
    if not js.exists():
        issues.append("missing_packet_json")

    schema_valid = False
    forbidden_field_hits: list[str] = []
    text_leak_hits: list[str] = []
    if js.exists():
        packet_obj = json.loads(js.read_text(encoding="utf-8"))
        keys = set(packet_obj.keys())
        if keys <= ALLOWED_PACKET_KEYS and "neutral_id" in keys:
            schema_valid = True
        else:
            issues.append(
                f"unexpected_or_missing_keys:{sorted(keys - ALLOWED_PACKET_KEYS)}"
            )
            if "neutral_id" not in keys:
                issues.append("missing_neutral_id")
        for k in keys:
            kl = k.lower()
            for bad in KIT_FORBIDDEN_EXTRA:
                if bad in kl:
                    forbidden_field_hits.append(k)
        blob = json.dumps(packet_obj, sort_keys=True)
        text_leak_hits.extend(leakage_hits(blob))
        for tok in KIT_FORBIDDEN_EXTRA:
            if tok in blob.lower():
                text_leak_hits.append(tok)

    combined_text = ""
    for p in (md, js):
        if p.exists():
            combined_text += p.read_text(encoding="utf-8", errors="replace") + "\n"
    text_leak_hits.extend(leakage_hits(combined_text))
    if re.search(r"\bcase_id\b", combined_text, flags=re.I):
        text_leak_hits.append("case_id_token")

    text_leak_hits = sorted(set(text_leak_hits))
    file_hash = sha256_file(js) if js.exists() else ""
    size = sum(p.stat().st_size for p in packet_dir.iterdir() if p.is_file())

    ok = (
        not issues
        and schema_valid
        and not forbidden_field_hits
        and not text_leak_hits
        and md.exists()
        and js.exists()
    )
    return {
        "neutral_id": packet_dir.name,
        "packet_exists": md.exists() and js.exists(),
        "schema_valid": schema_valid,
        "forbidden_fields": forbidden_field_hits,
        "leakage_hits": text_leak_hits,
        "issues": issues,
        "sha256_packet_json": file_hash,
        "size_bytes": size,
        "generation_timestamp": generated_at,
        "qa_ok": ok,
    }


def write_hashes(kit_dir: Path, hash_dir: Path) -> Path:
    hash_dir.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for path in sorted(kit_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.is_relative_to(hash_dir):
            continue
        rel = path.relative_to(kit_dir).as_posix()
        lines.append(f"{sha256_file(path)}  {rel}")
    manifest = hash_dir / "manifest.sha256"
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    # Self-hash note
    (hash_dir / "README.md").write_text(
        "SHA256 hashes of all kit files except this HASHES directory.\n"
        "Verify with: `cd human_annotation_kit && sha256sum -c HASHES/manifest.sha256`\n"
        "(paths in the manifest are relative to the kit root.)\n",
        encoding="utf-8",
    )
    return manifest


def final_kit_leak_scan(kit_dir: Path) -> list[dict[str, str]]:
    """Scan all rater-facing text/json/csv/md for forbidden experimental content."""
    problems: list[dict[str, str]] = []
    skip_dirs = {"HASHES"}
    # Coordinator guide must not live inside the kit; if present, flag.
    for path in sorted(kit_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.parts[-2] == "HASHES" or path.parent.name in skip_dirs:
            continue
        if path.suffix.lower() not in {".md", ".json", ".csv", ".txt", ".xlsx"}:
            continue
        # Skip binary xlsx for substring scan of experimental labels in compressed form —
        # still scan CSV twin.
        if path.suffix.lower() == ".xlsx":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        # Do not ban words that appear in instructions explaining what to avoid,
        # but ban structured leakage patterns and condition tokens.
        hits = []
        lower = text.lower()
        for tok in (
            "condition_a",
            "condition_b",
            "condition_c",
            "born_stale",
            "confirmed_false",
            "task_success",
            "failure_reason",
            "causal_role",
            "id_map.sealed",
        ):
            if tok in lower:
                hits.append(tok)
        # case_id as a field exposure (not the English phrase in coordinator docs —
        # annotator kit should not mention mapping to case ids)
        if path.name not in {
            "COORDINATOR_GUIDE.md",
        } and re.search(r"\bcase_id\b", text):
            # Allow FAQ/instructions that say not to use case ids? Prefer zero.
            if "case_id" in lower:
                hits.append("case_id")
        for h in hits:
            problems.append({"path": str(path.relative_to(kit_dir)), "hit": h})
    return problems


def build_kit(
    *,
    packets_root: Path = DEFAULT_OUTPUT,
    kit_dir: Path | None = None,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    packets_src = packets_root / "packets"
    eligibility_path = packets_root / "eligibility.csv"
    if kit_dir is None:
        kit_dir = packets_root / "human_annotation_kit"
    if not packets_src.is_dir():
        raise FileNotFoundError(f"Missing packets at {packets_src}")

    if kit_dir.exists():
        shutil.rmtree(kit_dir)
    kit_dir.mkdir(parents=True)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    repo_root = Path(__file__).resolve().parents[4]
    commit = _repo_commit(repo_root)

    write_docs(kit_dir)
    neutral_ids = copy_packets(packets_src, kit_dir / "PACKETS")
    eligibility = load_eligibility(eligibility_path)
    build_packet_index(
        kit_dir / "PACKET_INDEX.csv",
        neutral_ids=neutral_ids,
        eligibility=eligibility,
    )
    write_annotation_form_csv(kit_dir / "ANNOTATION_FORM.csv", neutral_ids)
    write_annotation_form_xlsx(kit_dir / "ANNOTATION_FORM.xlsx", neutral_ids)

    # Copy protocol for reference (rater-safe)
    protocol_src = repo_root / "docs" / "RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md"
    if protocol_src.exists():
        shutil.copy2(protocol_src, kit_dir / "PROTOCOL.md")

    qa_dir = kit_dir / "QA"
    qa_dir.mkdir()
    qa_rows: list[dict[str, Any]] = []
    for nid in neutral_ids:
        qa_rows.append(qa_packet(kit_dir / "PACKETS" / nid, generated_at=generated_at))
    (qa_dir / "packet_qa.json").write_text(
        json.dumps(qa_rows, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    with (qa_dir / "packet_qa.csv").open("w", encoding="utf-8", newline="") as f:
        fields = [
            "neutral_id",
            "packet_exists",
            "schema_valid",
            "qa_ok",
            "sha256_packet_json",
            "size_bytes",
            "generation_timestamp",
            "leakage_hits",
            "forbidden_fields",
            "issues",
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in qa_rows:
            w.writerow(
                {
                    "neutral_id": row["neutral_id"],
                    "packet_exists": row["packet_exists"],
                    "schema_valid": row["schema_valid"],
                    "qa_ok": row["qa_ok"],
                    "sha256_packet_json": row["sha256_packet_json"],
                    "size_bytes": row["size_bytes"],
                    "generation_timestamp": row["generation_timestamp"],
                    "leakage_hits": ";".join(row["leakage_hits"]),
                    "forbidden_fields": ";".join(row["forbidden_fields"]),
                    "issues": ";".join(row["issues"]),
                }
            )

    version_text = "\n".join(
        [
            f"protocol_version={PROTOCOL_VERSION}",
            f"kit_generator_version={KIT_GENERATOR_VERSION}",
            f"repository_commit={commit}",
            f"generation_timestamp={generated_at}",
            f"packet_seed={seed}",
            f"n_packets={len(neutral_ids)}",
        ]
    ) + "\n"
    (kit_dir / "VERSION.txt").write_text(version_text, encoding="utf-8")

    # Hashes after all files except HASHES itself
    write_hashes(kit_dir, kit_dir / "HASHES")

    leak_problems = final_kit_leak_scan(kit_dir)
    (qa_dir / "kit_leak_scan.json").write_text(
        json.dumps(leak_problems, indent=2) + "\n",
        encoding="utf-8",
    )

    manual = [
        nid
        for nid in neutral_ids
        if eligibility.get(nid, {}).get("eligibility_status")
        == "requires_manual_packet_review"
    ]
    qa_failures = [r["neutral_id"] for r in qa_rows if not r["qa_ok"]]

    summary = {
        "kit_dir": str(kit_dir),
        "n_packets": len(neutral_ids),
        "n_qa_ok": sum(1 for r in qa_rows if r["qa_ok"]),
        "qa_failures": qa_failures,
        "manual_review_packets": len(manual),
        "kit_leak_hits": leak_problems,
        "generated_at": generated_at,
        "commit": commit,
        "seed": seed,
    }
    (qa_dir / "kit_build_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def write_coordinator_guide(path: Path) -> None:
    path.write_text(
        f"""# Coordinator guide — RQ5 v1 blind LB annotation

This file is **not** part of the annotator distribution.
Distribute only `human_annotation_kit/` (or a ZIP of that directory).

Protocol: `{PROTOCOL_VERSION}`

## Distribute

1. Build/regenerate packets, then the kit (see commands below).
2. Verify `QA/packet_qa.csv` has `qa_ok=True` for all rows.
3. Review `PACKET_INDEX.csv` notes — all current packets may be
   `requires_manual_packet_review` (generic task brief). Spot-check a sample of
   `PACKETS/*/packet.md` before release.
4. Zip `human_annotation_kit/` identically for both annotators.
5. Send the same ZIP to both; record the `HASHES/manifest.sha256` fingerprint.

Do **not** send `exports/rq5_lb_blind_annotation/private/`.

## Assign annotator IDs

Use opaque IDs such as `annotator_A` and `annotator_B`. Put the ID in the submission
email / filename, not inside packets.

## Collect responses

Expect only `ANNOTATION_FORM.csv` per annotator.
Rename on receipt to `ANNOTATION_FORM__<annotator_id>__<date>.csv`.
Store raw files immutable under an archive folder.

## Verify hashes

On the coordinator machine:

```bash
cd human_annotation_kit
sha256sum -c HASHES/manifest.sha256
```

Both annotators’ kits must match the same manifest.

## Merge responses

Join on `neutral_id`. Keep separate columns per annotator for:

- reference_relevance
- material_necessity
- confidence
- justification

Derive finals with
`artifact_lab.experiments.truth_decay.rq5_experiment.blind_lb_derive.derive_final_classification`
for each annotator independently.

## Calculate agreement (workflow only — do not run here)

1. Derive final label per annotator per case.
2. Compute pairwise agreement / Cohen’s κ on the final label and optionally on each
   dimension.
3. List disagreements for adjudication.

## Prepare adjudication

For disagreements, create a third packet-identical review set without showing either
annotator’s labels. Document adjudication rules before opening disagreements.

## Archive

Keep forever:

- kit `VERSION.txt` + `HASHES/manifest.sha256`
- raw returned CSVs
- merge table
- adjudication log

Never mix private `id_map.sealed.json` into annotator archives.

## Regeneration commands

```bash
make rq5-v1-blind-lb-packets
.venv/bin/python -m artifact_lab.experiments.truth_decay.rq5_experiment.blind_lb_annotation_kit
```
""",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build RQ5 v1 human annotation kit")
    parser.add_argument("--packets-root", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--kit-dir",
        type=Path,
        default=None,
        help="Default: <packets-root>/human_annotation_kit",
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args(argv)
    summary = build_kit(
        packets_root=args.packets_root,
        kit_dir=args.kit_dir,
        seed=args.seed,
    )
    write_coordinator_guide(args.packets_root / "COORDINATOR_GUIDE.md")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if summary["qa_failures"] or summary["kit_leak_hits"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
