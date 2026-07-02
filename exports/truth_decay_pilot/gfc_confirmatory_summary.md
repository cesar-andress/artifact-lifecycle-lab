# Born-Stale Confirmatory Audit — `genuine_false_claim`

## Purpose

Second-pass validation of **1,405** references previously labeled `genuine_false_claim`
in the born-stale autopsy. Determines how many are **confirmed false path claims**
versus measurement artifacts (template, anchor, extraction, normative).

## Cohort

- Prior `genuine_false_claim` references audited: **1405**
- LLM dual-judge enabled: **yes**
- References sent to LLM judges: **0**
- Judge disagreements (unresolved): **0**

## Confirmed-false rate

- **Confirmed false (A):** 1200 (85.4%)
- Wilson 95% CI: **83.5%–87.2%**
- Adjusted born-stale false-claim rate (17,747 cohort): **6.76%**

## Confirmatory taxonomy

| Letter | Category | Count | % |
|--------|----------|------:|--:|
| A | `confirmed_false` | 1200 | 85.4% |
| B | `artifact` | 4 | 0.3% |
| C | `normative` | 51 | 3.6% |
| D | `anchor_issue` | 0 | 0.0% |
| E | `template` | 150 | 10.7% |
| F | `ambiguous` | 0 | 0.0% |

## Protocol

1. Deterministic confirmatory heuristics override prior LLM `genuine_false_claim` when
   template/glob, command-like, anchor, normative, or extraction signals fire.
2. Dual LLM judges (`deepseek-coder-v2:lite`, `devstral:latest`) only for
   `ambiguous` cases.
3. Disagreements remain `ambiguous`; never silently merged.

## Implications

- The raw born-stale `genuine_false_claim` rate (7.9%) is an **upper bound**.
- Reviewer-facing false-claim construct should use **confirmed_false** with CI.

## Outputs

- `gfc_confirmatory_audit.csv`
- `gfc_confirmatory_examples.csv`
- `gfc_confirmatory_disagreements.csv`
- `figure_gfc_confirmatory.pdf`
