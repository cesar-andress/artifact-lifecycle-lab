# Annotator instructions (plain language)

Protocol reference: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`

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
