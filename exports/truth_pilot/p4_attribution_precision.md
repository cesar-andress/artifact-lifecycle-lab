# Gate P4 — Agent Attribution Precision Audit

## Scope
- Total non-human flagged commits (P2): **2816**
- Human-review worksheet sample: **200**

## Category separation (reviewer objection closure)

Dependabot/Renovate/security bots **do not** count as agent maintenance.

| signature_category | count | agent maintenance? |
|--------------------|------:|:------------------:|
| co_authored_by_trailer | 30 | yes |
| claude_signature | 30 | yes |
| cursor_signature | 28 | yes |
| copilot_signature | 28 | yes |
| bot_author | 28 | no |
| generic_automation | 28 | yes |
| dependabot_renovate_security_bot | 28 | no |

## Breakdown
- **Claude/Cursor/Copilot signatures:** 86
- **Co-Authored-By trailers:** 30
- **Bot authors:** 28
- **Generic automation:** 28
- **Dependabot/Renovate/security bots (excluded):** 28

## Agent maintenance vs excluded bots (worksheet sample)
- Counts as agent maintenance (auto): **144**
- Excluded dependency/security bots (auto): **56**

## Precision gate
- **Human labels required** — fill `human_label` in `agent_attribution_gold_worksheet.csv`
  (`agent` / `human` / `ambiguous`).
- Kill criterion: precision < **80%** on agent-maintenance subset.
- Precision = (human_label=agent among counts_as_agent_maintenance=yes) / reviewed agent-maintenance rows.

## Gate status
**PENDING HUMAN REVIEW** — worksheet exported; auto-summary complete.
