# Codebook — authoritative definitions

Source of truth: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`

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
elif relevance in {irrelevant, contextually_relevant} -> non_load_bearing
elif necessity in {not_necessary, helpful_but_substitutable} -> non_load_bearing
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
