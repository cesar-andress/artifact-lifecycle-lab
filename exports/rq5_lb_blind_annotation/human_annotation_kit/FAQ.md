# FAQ

Protocol: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`

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
