# RQ5 v2 — Load-Bearing Candidate Export

Automatic identification of instruction-file references that are **genuinely load-bearing**
(must be edited, executed, or inspected to solve the task). Contextual-only mentions are rejected.

**No agent runs.** Dataset construction only.

- Output CSV: `exports/rq5_v2/load_bearing_candidates.csv`
- Candidate count: **1524**
- Unique repositories: **72**
- Mean estimated success rate: **0.567**

## Load-bearing roles

| Role | Count |
|------|------:|
| edit | 451 |
| execute | 910 |
| inspect | 163 |

## Difficulty

| Difficulty | Count |
|------------|------:|
| easy | 635 |
| medium | 296 |
| hard | 593 |

## Selection rules

1. Reference must be **VERIFIED** at the pinned commit (mechanical panel check).
2. Instruction blob (L1b) must be recoverable.
3. Reference must appear in **actionable** context: edit / execute / inspect verbs near the path.
4. Reject: Related files / See also sections, passive mentions, peripheral docs without imperatives.

## Protocol

See `docs/RQ5_V2_PROTOCOL.md` for the full factorial experiment design.
