# Re-identification Test Protocol (Annotation Instrument v3)

Automated leak scanners are **necessary but not sufficient**.

Blinding fails if a competent reviewer can identify or confidently search for the
original repository from the packet alone.

---

## Identifier classes

For each token that would appear in a proposed packet, classify:

| Class | Meaning |
|-------|---------|
| `generic_and_safe` | Common token; does not identify a project |
| `aliasable_without_semantic_loss` | Can be replaced by a neutral alias |
| `necessary_but_identifying` | Semantically needed but identifies the project |
| `non_redactable` | Cannot be removed/aliased without destroying judgment |
| `uncertain` | Needs human adversarial review |

A case may proceed only if **no** `necessary_but_identifying` or
`non_redactable` identifier remains in the rater-facing packet, and residual
`uncertain` items are cleared by the adversarial test below.

---

## Checklist of channels

Test all of:

- repository / owner / organisation names
- domains and hosts
- package and application names
- distinctive directories and skill names
- URLs, badges, copyright lines
- documentation branding
- ecosystem names (VS Code, Calypso, Dify, Prefect, Next.js, Automattic, …)
- unusual tree shapes
- external service names

---

## Adversarial manual test (required)

For each candidate packet:

1. Give the packet to a technically competent reviewer who does **not** know the
   case mapping.
2. Ask:

   > Given only this packet, can you identify or plausibly search for the
   > original repository within 10 minutes?

3. Allowed tools: web search, GitHub search, package registries.
4. Disallowed: private id maps, experimental exports, asking the coordinator.
5. Outcomes:
   - `identified` → fail (non-anonymizable)
   - `plausible_shortlist≤3` → fail unless aliases remove the shortlist
   - `not_identified` → pass this test (still subject to other v3 gates)

Do not ship any packet that fails this test.

---

## Relation to v3 eligibility

In the current RQ5 v1 audit, **no case reaches** the anonymization gate because
all 35 fail `no_independent_task_oracle` first. Re-identification classifications
are still recorded for completeness in `reidentification_risk_v3.csv`.
