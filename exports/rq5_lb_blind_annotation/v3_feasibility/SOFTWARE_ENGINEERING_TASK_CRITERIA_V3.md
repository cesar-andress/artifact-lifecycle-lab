# Software Engineering Task Criteria (Annotation Instrument v3)

Purpose: decide whether a candidate task oracle defines a **genuine software
engineering task** for RQ5 v1 blind load-bearing annotation.

This document does **not** broaden the construct to retain sample size.

---

## Inclusion rules

A task qualifies **only if** all of the following hold:

1. **Independent oracle.** The task text comes from a source other than the
   treated instruction artifact (issue, PR, failing test, benchmark spec,
   independently stored bug report / user request / task definition, commit
   message paired with a concrete change, test target with expected behavior).
2. **Software-system object.** The work targets source code, build/test/deploy
   configuration, runtime behavior of software, or analysis of a software system
   in a repository snapshot.
3. **Concrete engineering action.** The task asks for at least one of:
   - implementation of functionality;
   - bug diagnosis or debugging;
   - fixing a failing test or build;
   - configuration / infrastructure-as-code change affecting the system;
   - testing / verification action with an engineering success criterion;
   - build or deployment pipeline action on the software;
   - refactoring or maintenance of software artifacts;
   - other concrete modification or analysis of the software system.

---

## Exclusion rules

Exclude when the primary objective is:

- marketing content creation;
- social media planning / calendars;
- commission or earnings calculation as a business workflow;
- content atomization / repurposing for platforms;
- generic research without a software deliverable;
- copywriting;
- affiliate campaign management;
- operating a prompt/content skill **without** modifying or analysing software.

Also exclude when:

- the only “task” is “follow / execute this instruction or skill”;
- the only success signal is unspecified “complete the instruction file”;
- candidate `task_availability` / `issue_availability` flags are heuristic
  proxies over the instruction text (these are **not** inclusion evidence).

---

## Edge cases

| Situation | Decision |
|-----------|----------|
| Docs-only change that alters generated API docs as part of a release pipeline | Include if oracle is independent and success is engineering-defined |
| “Update AGENTS.md wording” as the sole task | Exclude (meta-instruction editing without independent SE oracle) |
| Affiliate skill repo that also contains `package.json` tests | Exclude unless independent SE oracle exists; repo type alone is insufficient |
| “Make pytest pass” with no failing test / no expected change | Exclude (underspecified; not an oracle) |
| Security hardening / dependency bump with CVE issue link | Include if issue/PR is the oracle |

---

## Examples from the current RQ5 v1 dataset

### Exclude (observed)

- Generic manifest prompt: *“Complete the bounded coding task described in the
  project instruction file…”* for all 35 cases — **not independent**, not a
  concrete SE change.
- Affiliate skill purposes (commission calculator, social media calendar,
  content atomizer) — **non-SE primary objective**, even if `npm run test` exists.
- Candidate `issue_availability=True` because the instruction mentions “bug”
  language or stale refs — **not** a stored GitHub issue oracle.

### Include (hypothetical; none present in v1 data)

- Linked issue: “`GET /v1/flows` returns 500 when name contains spaces; add
  regression test.”
- PR description with failing CI log and expected green `make test`.
- Benchmark task JSON with input repo state and FAIL_TO_PASS tests.

---

## Deterministic decision procedure

```
Input: task_oracle_source, task_oracle_text, repository_type

1. If task_oracle_source ∈ {
     none, instruction_file, instruction_derived_summary,
     generic_instruction_coupled_prompt
   }:
     → NOT SE-eligible (fail independence precondition)

2. If repository_type == content_skill_pack AND task text lacks SE action cues
   (implement/fix/test/build/debug/refactor/configure/deploy/migrate):
     → NOT SE-eligible

3. If task text primary objective matches exclusion keywords
   (affiliate, social media calendar, commission workflow, atomize, copywriting)
   AND lacks SE action cues:
     → NOT SE-eligible

4. If task text contains an SE action cue AND targets a software system:
     → SE-eligible

5. Else:
     → NOT SE-eligible
```

Record the failing step as the machine reason. Do not “rescue” with generated prose.
