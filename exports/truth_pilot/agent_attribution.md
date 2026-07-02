# P2 — Agent Attribution Pilot

## Scope
- Commits scanned (from L1 instruction-file events): **11187**
- Instruction files touched: **3253**
- Files with ≥1 agent signal: **989** (30.4%)

## Candidate counts
- Candidate agent-authored commits: **1210**
- Candidate agent-co-authored commits: **1606**
- Combined agent signal rate: **25.2%**

## Attribution classes

| class | count |
|-------|------:|
| agent_coauthored | 1606 |
| agent_signature_in_message | 1042 |
| bot_author | 168 |
| human | 8371 |

## Signature types

| signature_type | count |
|----------------|------:|
| bot_account | 168 |
| co_authored_by | 1606 |
| message_signature | 1034 |
| tool_pattern | 8 |

## Example candidates

- `127cfbdb` .claude/skills/docs-style/SKILL.md — **agent_signature_in_message** (message_signature): message_signature:claude:claude
- `a93d3b6f` .continue/prompts/sub-agent-foreground.md — **agent_coauthored** (co_authored_by): co_authored_by:unknown:cubic-dev-ai[bot] <191113872+cubic-dev-ai[bot]@users.noreply.github.com>
- `abb1fc04` extensions/cli/AGENTS.md — **agent_coauthored** (co_authored_by): co_authored_by:claude:Claude Opus 4.6 <noreply@anthropic.com>; co_authored_by:claude:Claude Opus 4.6
- `34910325` skills/cn-check/SKILL.md — **agent_coauthored** (co_authored_by): co_authored_by:claude:Claude Opus 4.5 <noreply@anthropic.com>
- `46b04cad` skills/cn-check/SKILL.md — **agent_coauthored** (co_authored_by): co_authored_by:claude:Claude Opus 4.5 <noreply@anthropic.com>
- `ddaba21e` AGENTS.md — **agent_signature_in_message** (message_signature): message_signature:copilot:copilot
- `b4d87c70` AGENTS.md — **agent_signature_in_message** (message_signature): message_signature:copilot:copilot
- `6f3169eb` AGENTS.md — **agent_signature_in_message** (message_signature): message_signature:copilot:copilot

## Interpretation
- Deterministic heuristics only (Co-Authored-By, bot accounts, tool strings).
- L1 supplies commit SHAs; git supplies messages and author emails.
- Signal strength is a pilot estimate, not population prevalence.
