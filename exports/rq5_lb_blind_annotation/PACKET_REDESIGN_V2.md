# RQ5 v1 Blind Annotation Packet Redesign (v2)

Protocol unchanged: `docs/RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md` @ `e41902c`.

This document justifies the **instrument** redesign. The protocol’s construct is
accepted; the previous packet kit did not measure it.

Packet spec version: `rq5_v1_blind_packet_spec_v2`

---

## Scientific objective

Annotators must answer only:

> Is the referenced artifact materially necessary for completing **this** software
> engineering task in **this** repository snapshot?

An instrument that forces guessing, invents `pytest` for JS/Swift/C++ repos, corrupts
citations, or hides the repository cannot support that judgment.

---

## Decision table

| Old design | Problem | New design | Threat mitigated |
|------------|---------|------------|------------------|
| Generic brief: “make `pytest` pass” for all cases | Wrong verification signal; task not the repository’s task; destroys construct validity | Task brief derived from pinned instruction purpose/sections; verification command inferred only from pinned manifests (`package.json`, Makefile, `go.mod`, etc.) or explicitly stated as unidentified | Construct under-representation; false necessity cues from wrong toolchain |
| No repository tree (“offline packet omits tree”) | Cannot judge substitutability / equivalent information elsewhere | Minimal pinned tree excerpt + neighbours + nearby docs/config + small file excerpts via bare clone @ `task_commit_sha` | Missing context → forced Ambiguous or invented knowledge |
| Substring `str.replace` redaction (`1/` → all `1`) | Corrupted text (`80/[[REF]]0`, `[[REF]].0.0`); unreadable; path still sometimes recoverable from damage patterns | Semantic whole-path tokenization; short/numeric anchors require exact path-span match only | Instrumentation artifact; leakage via corruption; invalid judgments |
| Statements implying absence (“no [[REF]] directory”) | Reveals treatment when false paths are the manipulation | Absence language banned; if safe wording impossible → `not_safe_for_blinding` exclude | Condition leakage via existence |
| Thin one-line excerpts | Cannot distinguish irrelevant / contextual / directly relevant / necessary | Enrich ±8 line windows; attach snapshot file excerpts; exclude if still degenerate | Degenerate instrument |
| Non-English packets without translation | English annotators cannot read materials | Script detection + professional translation cache; missing cache → exclude | Language barrier confounding |
| Skill/content packs silently included | Not software-engineering repositories under the protocol’s SE task framing | Software-repo detector (source/manifest signals); `non_software_repository` exclude | Domain mismatch |
| `requires_manual_packet_review` used as soft pass for all | Distributed unusable packets | Emit only `eligible`; all other statuses listed in `exclusions.csv` | Premature distribution |

---

## Redesign decisions (detail)

### 1. Real task briefs

**Decision:** Parse instruction frontmatter (`name`, `description`) and sections
(Purpose / When to Use / workflow / rules). Combine with a verification command
**observed in the pinned tree**, never the broken manifest default `pytest`.

**Non-decision:** We do not invent “implement endpoint X” unless the instruction
states that work. If purpose cannot be extracted → `task_not_separable`.

### 2. Minimal repository context

**Decision:** Bare partial clone cache (`scratch/rq5_blind_trees/`), `ls-tree` at
`task_commit_sha`, focus neighborhood around instruction path and resolved reference
aliases, plus small file excerpts.

**Blinding:** Reference path strings and contrast-only paths are semantically
redacted to `[[REF]]`. We never claim a path is missing.

### 3. Semantic redaction

**Decision:** Match path spans (backticks and multi-segment tokens). Short anchors
(`1/`, `2/`) redact only exact spans. Corruption markers fail closed.

### 4. Absence

**Decision:** Regex gate on absence phrasing in emitted text. Fail →
`not_safe_for_blinding`.

### 5. Language

**Decision:** Detect CJK/Cyrillic/etc. Apply cached professional English translation
keyed by SHA-256 of source bytes.

### 6. Degenerate packets

**Decision:** Automatic enrichment; if still too thin → `degenerate_packet` exclude.

### 7. Non-software

**Decision:** Require source/manifest signals; else `non_software_repository`.

---

## What raters receive (eligible only)

- Concrete English task brief
- Instruction citation excerpts (redacted)
- Tree / neighbours / docs / configs
- Snapshot file excerpts (aliased)
- Path policy + single annotator question

They never receive: case IDs, conditions, outcomes, traces, mediation labels, private maps.

---

## Residual risks (honest)

- Some instructions describe broad skills; necessity may still be hard — **Ambiguous**
  remains valid scientifically.
- Tree excerpts are minimal, not full checkouts in the ZIP.
- Path redaction removes literal names; raters judge from role + local structure.
- Clone failures exclude cases (`source_unavailable`) rather than shipping empty trees.

If eligible packets still cannot support independent necessity judgments, the kit must
not be declared ready.

---

## Excluded packets (this generation)

| neutral_id | status | reason_code | explanation |
|---|---|---|---|
| `edc493748044c205` | `not_safe_for_blinding` | `leakage_or_absence_risk` | Refused emit; scan hits: banned_path:@automattic/grid, raw_anchor_present |
| `4b9a3c6654895937` | `not_safe_for_blinding` | `leakage_or_absence_risk` | Refused emit; scan hits: banned_path:/route.ts, raw_anchor_present |
| `930e6bd912075b0c` | `not_safe_for_blinding` | `leakage_or_absence_risk` | Refused emit; scan hits: banned_path:@copilotkit/react, raw_anchor_present |
| `091eb6d22fc90585` | `task_not_separable` | `could_not_extract_task_purpose` | Could not derive a concrete engineering task brief from the pinned instruction. |
| `faa505ff151a1867` | `non_software_repository` | `not_software_repository` | Pinned tree lacks sufficient source/manifest signals of a software repository; signals=['manifest_or_doc:agents.md', 'manifest_or_doc:readme.md', 'manifest_or_doc:claude.md', 'mark |
| `cbea9e122bb3ae2f` | `not_safe_for_blinding` | `unsafe_path_residual` | Could not fully redact path identity without leakage: ['vs/sessions', 'vs/sessions'] |
| `f3100b00298d1424` | `insufficient_pre_treatment_context` | `anchor_not_in_instruction_blob` | Anchor citation not found in the sanitized instruction source. |
| `80994240f7b369b7` | `not_safe_for_blinding` | `unsafe_path_residual` | Could not fully redact path identity without leakage: ['/__init__.py', '/__init__.py'] |
| `51fc8d1a5d5767b4` | `insufficient_pre_treatment_context` | `anchor_not_in_instruction_blob` | Anchor citation not found in the sanitized instruction source. |
| `fa72bc285f4b7183` | `not_safe_for_blinding` | `leakage_or_absence_risk` | Refused emit; scan hits: banned_path:api/ |
| `fc56ab50ea68a616` | `task_not_separable` | `could_not_extract_task_purpose` | Could not derive a concrete engineering task brief from the pinned instruction. |

**Eligible emitted:** 24 / 35 manifest cases.
