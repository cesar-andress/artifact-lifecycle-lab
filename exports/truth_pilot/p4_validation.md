# P4 — Human Gold Validation Report

## Summary

- **Gold source (archival):** `exports/truth_pilot/agent_attribution_gold_worksheet.csv` (frozen worksheet; original local annotation file not redistributed)
- **Reviewed rows:** 200
- **Gate threshold:** precision ≥ **80%** (agent-maintenance positive class)
- **Gate result:** **PASS** (precision = 0.958)

## Methodology

Pure validation step — **no relabeling, no retraining, no algorithm changes**.

The existing P4 heuristic (`categorize_signature` / `counts_as_agent_maintenance`) is evaluated
against independent human labels on the stratified 200-commit worksheet exported by Gate P4.

**Positive class (gold):** `human_label = true_agent_maintenance`

**Negative class (gold):** `human_label ∈ {human_only, generic_bot}`

**Classifier prediction:** frozen worksheet column `counts_as_agent_maintenance` (`yes`/`no`),
produced at worksheet export time by the current P4 rules.

Metrics are computed on the **full reviewed sample** (N=200). Cohen's κ is reported for
binary agent-maintenance agreement (appropriate for two nominal raters on yes/no).

## Gold protocol

1. Stratified sample of 200 non-human flagged commits from `agent_commit_candidates.csv`
   (seed=42, exported as `agent_attribution_gold_worksheet.csv`).
2. Human reviewer assigned `human_label` per commit:
   - `true_agent_maintenance` — commit reflects genuine agent-assisted instruction maintenance
   - `human_only` — automation signal present but human-maintained / not agent maintenance
   - `generic_bot` — infrastructure or CI bot (Dependabot, github-actions, release automation)
3. Classifier labels were **not** edited during review.

## Annotation assumptions

- **Agent maintenance** requires evidence that an coding agent (Claude, Cursor, Copilot, etc.)
  materially contributed to the instruction-file commit, not merely a mention in prose.
- **Co-Authored-By** trailers naming known agent identities count as agent maintenance;
  human-only or unknown co-authors may be labeled `human_only`.
- **Bot authors** (Dependabot, github-actions, azure-sdk-automation) default to `generic_bot`
  even when agent co-trailers appear — human judgment resolved mixed-signal cases.
- **Tool-pattern signatures** (`tool_pattern:phrase:…`) require contextual review;
  boilerplate automation text may be `human_only`.

## Global metrics

| Metric | Value |
|--------|------:|
| Precision | 0.9583 |
| Recall | 0.9650 |
| F1 | 0.9617 |
| Accuracy | 0.9450 |
| Cohen's κ | 0.8643 |

### Confusion matrix (rows = gold, columns = classifier)

| Gold \ Predicted | yes | no |
|------------------|----:|---:|
| true_agent_maintenance | 138 | 5 |
| not_agent_maintenance | 6 | 51 |

Human label distribution: {'true_agent_maintenance': 143, 'generic_bot': 48, 'human_only': 9}

## Precision by attribution signal

Stratified metrics within each `signature_category` group. Precision is conditional on
classifier predicting `yes` within the stratum.

| Signal | N | Pred yes | TP | FP | FN | Precision | Recall |
|--------|--:|---------:|---:|---:|---:|----------:|-------:|
| Co-Authored-By | 30 | 30 | 27 | 3 | 0 | 0.900 | 1.000 |
| Claude signatures | 30 | 30 | 30 | 0 | 0 | 1.000 | 1.000 |
| Cursor signatures | 28 | 28 | 28 | 0 | 0 | 1.000 | 1.000 |
| Copilot signatures | 28 | 28 | 28 | 0 | 0 | 1.000 | 1.000 |
| generic bots | 56 | 0 | 0 | 0 | 5 | — | 0.000 |
| generic automation (OpenAI/Devin/etc.) | 28 | 28 | 25 | 3 | 0 | 0.893 | 1.000 |

## Disagreement analysis

- **False positives (classifier yes, human no):** 6
- **False negatives (classifier no, human yes):** 5

### False positives

- **#73** `co_authored_by_trailer` → human=`human_only` — 3f33ab9828ac52ad/client/dashboard/sites/CLAUDE.md @ `f1f128fe`
- **#82** `generic_automation` → human=`human_only` — 4801516ff573cf43/python_modules/dagster/dagster_tests/declarative_automation_tests/automation_condition_tests/builtins/CLAUDE.md @ `3c8d5c85`
- **#117** `co_authored_by_trailer` → human=`generic_bot` — 79e5b3dcaadc644e/.claude/skills/document-changes/SKILL.md @ `7f18c0c9`
- **#137** `generic_automation` → human=`human_only` — 956a087a689baeee/.agents/skills/update-sdk/references/docker-image-locations.md @ `75c9f6e5`
- **#141** `co_authored_by_trailer` → human=`human_only` — 97dcab4759c83fdb/.agents/skills/frontend-testing/SKILL.md @ `e8397ae7`
- **#187** `generic_automation` → human=`human_only` — e916d975160d16b9/.github/workflows/shared/prompts/pydantic-ai-pr-review.md @ `16305ef0`

### False negatives

Dominant pattern: commits classified as `dependabot_renovate_security_bot` because `github-actions[bot]` appears in evidence, but human reviewers labeled agent maintenance due to **Claude Co-Authored-By** trailers in the same commit.

- **#95** `dependabot_renovate_security_bot` → human=`true_agent_maintenance` — 709dc9caa5f1ae36/AGENTS.md @ `59820516`
- **#97** `dependabot_renovate_security_bot` → human=`true_agent_maintenance` — 709dc9caa5f1ae36/AGENTS.md @ `dd3faa73`
- **#150** `dependabot_renovate_security_bot` → human=`true_agent_maintenance` — ab3194c6a08d7bdc/.github/prompts/reviewer-context.md @ `824c3828`
- **#152** `dependabot_renovate_security_bot` → human=`true_agent_maintenance` — ab3194c6a08d7bdc/.github/prompts/reviewer-context.md @ `9e58c2e6`
- **#153** `dependabot_renovate_security_bot` → human=`true_agent_maintenance` — ab3194c6a08d7bdc/CLAUDE.md @ `a29bcb97`

## Gate assessment

| Criterion | Required | Observed | Result |
|-----------|----------|----------|--------|
| Precision (agent maintenance) | ≥ 80% | 95.8% | **PASS** |

## Interpretation

The predefined P4 precision gate **passes**. The current classifier is sufficiently accurate for downstream observational use (RQ3 maintenance regimes) without algorithm changes. Residual errors concentrate in (1) mixed human/agent Co-Authored-By trailers and (2) github-actions bot commits that also carry Claude agent trailers — a recall issue, not a precision failure.

## Limitations

- Single human review pass; no adjudication of ambiguous cases.
- Worksheet is a pilot sample (N=200), not exhaustive over all flagged commits.
- κ reflects binary collapse of three-level human taxonomy.
