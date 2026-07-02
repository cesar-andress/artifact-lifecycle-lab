# Gate P4 — Agent Attribution Precision Audit

## Scope
- Total non-human flagged commits (P2): **2816**
- Human-review worksheet sample: **200**

## Auto-classification summary

Categories separated for precision audit. **Dependabot/Renovate/security bots do NOT count as agent maintenance.**

| signature_category | count | agent maintenance? |
|--------------------|------:|:------------------:|
| claude_signature | 23 | yes |
| co_authored_by_claude | 21 | yes |
| co_authored_by_copilot | 19 | yes |
| cursor_signature | 15 | yes |
| co_authored_by_other | 15 | yes |
| security_dependency_bot | 15 | no |
| copilot_signature | 14 | yes |
| generic_bot_author | 14 | no |
| openai_signature | 14 | yes |
| co_authored_by_cursor | 14 | yes |
| co_authored_by_devin | 12 | yes |
| dependabot | 9 | no |
| other_tool_signature | 8 | yes |
| co_authored_by_openai | 7 | yes |

## Breakdown
- **Claude/Cursor/Copilot signatures:** 106
- **Co-Authored-By trailers:** 88
- **Generic bot authors (excl. dependency bots):** 14
- **Dependabot/Renovate/security bots (excluded):** 24

## Agent maintenance vs excluded bots (worksheet sample)
- Counts as agent maintenance (auto): **162**
- Excluded dependency/security bots (auto): **38**

## Precision gate
- **Human labels required** — fill `human_label` in `agent_attribution_gold_worksheet.csv`
  (`agent` / `human` / `ambiguous`).
- Kill criterion: precision < **80%** on agent-maintenance subset.
- Precision = (human_label=agent among counts_as_agent_maintenance=yes) / reviewed agent-maintenance rows.

## Gate status
**PENDING HUMAN REVIEW** — worksheet exported; auto-summary complete.
