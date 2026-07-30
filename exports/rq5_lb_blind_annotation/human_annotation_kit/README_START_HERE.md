# Start here — RQ5 v1 Human Annotation Kit

## Purpose

You will judge, for each case packet, whether a **referenced project artifact** is
**materially necessary** for completing a stated software-engineering task in a
frozen repository snapshot.

You are **not** reviewing a paper, scoring an AI agent, or guessing experimental
outcomes. You only use the materials in this kit.

Protocol version: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`

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
