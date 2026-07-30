# P2 — Agent Attribution Pilot

## Scope
- Instruction files in sample: **100**
- Commits scanned (history for sampled paths): **327**
- Commits with agent signal: **92**

## Attribution classes

| class | count |
|-------|------:|
| agent_coauthored | 58 |
| agent_signature_in_message | 32 |
| bot_author | 2 |
| human | 235 |

## Signal types detected
- `agent_coauthored` — Co-Authored-By trailer matching agent/bot patterns
- `bot_author` — author name/email matching known bot accounts
- `agent_signature_in_message` — Claude/Cursor/Copilot/OpenAI-style message signatures
- `human` — no agent signal in pilot heuristics

## Interpretation
This pilot validates whether **agent attribution signals exist** in commits touching instruction files.
It does not estimate population prevalence — sample only.
