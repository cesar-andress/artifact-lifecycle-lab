# P1 — Reference Density Pilot

## Scope
- Instruction files sampled: **400**
- Stratified across: AGENTS.md, CLAUDE.md, Cursor rules, Copilot, GitHub instructions, Skills, prompts
- Extraction failures (missing blob): **0**

## Density
- Files with ≥1 verifiable reference: **288** (72.0%)
- Median references per file: **4.0**
- Median verifiable references per file: **3.0**

## Sampled files by family group

| family group | count |
|--------------|------:|
| AGENTS.md | 69 |
| CLAUDE.md | 57 |
| Copilot instructions | 25 |
| Cursor rules | 59 |
| GitHub instructions | 40 |
| Skills | 65 |
| prompt files | 85 |

## Verification outcomes

| status | count |
|--------|------:|
| missing | 2533 |
| unverifiable | 3743 |
| verified | 829 |

**Path/directory/script/dependency precision proxy** (verified / (verified + missing)): **24.7%**

## References by type

| type | count |
|------|------:|
| command | 3837 |
| dependency | 14 |
| directory | 755 |
| path | 2228 |
| script_name | 271 |

## Interpretation
- Verifiable types: path, directory, script_name, dependency.
- Commands are extracted but typically `ambiguous` (unverifiable) in this pilot.
- `false` (missing) references are candidates for truth-decay measurement at scale.
