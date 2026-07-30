# P1 — Reference Verification Pilot

## Scope
- Instruction files sampled: **100**
- Mechanically extracted references: **1715**

## Verification outcomes

| status | count |
|--------|------:|
| missing | 588 |
| unverifiable | 1046 |
| verified | 81 |

**Path/directory precision proxy** (verified / (verified + missing)): **12.1%**

## References by type

| type | count |
|------|------:|
| command | 1050 |
| dependency | 3 |
| directory | 88 |
| path | 574 |

## Interpretation
- `verified` / `missing` apply to path, directory, and dependency checks against HEAD.
- `unverifiable` is expected for commands not mapped to filesystem checks in this pilot.
- This pilot validates whether **mechanically verifiable references exist** in instruction files.
