# RQ5 v1 Blind Load-Bearing Annotation Protocol (Reviewer Version)

You are acting as an independent scientific annotator.

This is **not** a review of the paper.

This is **not** an evaluation of agent performance.

Your only task is to determine whether the referenced artifact is **materially necessary** for the intended software engineering task.

You must ignore any intuition about what probably happened during execution.

You will **never** see:

* agent traces,
* success or failure,
* A/B/C condition,
* experimental results,
* mediation analyses,
* previous labels,
* statistics,
* manuscript text.

You are judging only the task and the repository state before any experiment.

---

# Scientific goal

We want to characterize whether the referenced artifact is intrinsically load-bearing for the task.

This is **not** asking:

* whether the agent actually opened it,
* whether the agent followed it,
* whether the experiment succeeded,
* whether the reference was false,
* whether the manipulation changed outcomes.

Those questions belong to the experiment and are intentionally hidden.

---

# Definitions

## Reference relevance

The referenced artifact is related to the task.

Examples:

* configuration used by the task
* build script
* testing instructions
* repository conventions
* deployment instructions
* architecture notes
* coding standards

Possible labels:

* Irrelevant
* Contextually relevant
* Directly relevant
* Ambiguous

---

## Material necessity

Assume a competent engineer is performing the task.

Ask:

> Would completing the task normally require the information uniquely or materially supplied by this referenced artifact?

Not:

> Would it be helpful?

Not:

> Would I personally read it?

Not:

> Could another engineer solve the task differently?

Possible labels:

* Not necessary
* Helpful but substitutable
* Materially necessary
* Ambiguous

---

## Load-bearing

A reference is load-bearing **only if**

its information is materially necessary for completing the intended task in the pinned repository state.

A reference is **not** load-bearing merely because it:

* looks important,
* is mentioned,
* provides useful context,
* is likely to be read,
* improves understanding,
* reduces effort.

If reasonable engineers could complete the task without that artifact because equivalent information exists elsewhere, classify it as **Helpful but substitutable**, not load-bearing.

---

# Decision process

For every case follow exactly this order.

Step 1

Read the task.

Step 2

Inspect only the provided repository snapshot.

Step 3

Determine reference relevance.

Step 4

Determine material necessity.

Step 5

Assign the final label.

Never reason from hypothetical execution.

Never speculate about agent behaviour.

Never infer whether the manipulation probably mattered.

---

# Final labels

## Load-bearing

Use only when:

* the reference is directly relevant, and
* the task would ordinarily require that information.

---

## Non-load-bearing

Use when:

* the reference is irrelevant,
* or only contextual,
* or useful but substitutable.

---

## Ambiguous

Use whenever the provided material is insufficient for a confident judgment.

Do **not** force a binary decision.

Ambiguous is an acceptable scientific outcome.

---

# Required justification

Provide 2–5 sentences explaining:

* what information the artifact contributes,
* why that information is or is not materially necessary,
* which evidence from the supplied materials supports your judgment.

Do not mention:

* agents,
* traces,
* success,
* failures,
* experimental conditions,
* expected outcomes.

---

# Confidence

Select one:

* High
* Medium
* Low

Low confidence is acceptable.

---

# Independence

Complete every case independently.

Do not compare cases.

Do not revise previous annotations after seeing later cases.

Do not discuss any case with another annotator until both annotation sheets have been submitted.

---

# Output template

For each case report:

Case ID:

Reference relevance:

* Irrelevant
* Contextually relevant
* Directly relevant
* Ambiguous

Material necessity:

* Not necessary
* Helpful but substitutable
* Materially necessary
* Ambiguous

Final classification:

* Load-bearing
* Non-load-bearing
* Ambiguous

Confidence:

* High
* Medium
* Low

Justification:

(2–5 sentences)

---

# Important

This annotation is intended to characterize the intrinsic role of the referenced artifact **before** any runtime evidence is considered.

Do not attempt to infer what happened during the experiment.

If you cannot confidently determine material necessity from the supplied information, select **Ambiguous**.
