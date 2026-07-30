# Annotation packet `85571219ad372807`

Protocol: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`
Packet spec: `rq5_v1_blind_packet_spec_v2`

Judge only with the materials below. Do not seek external repositories or experimental results.

## Annotator question

Is Referenced artifact R1 materially necessary for completing THIS software engineering task in THIS repository snapshot?

## Anonymous snapshot

- Snapshot ID: `0a010bb1b4e5d3b5`
- Reference type: `path`
- Artifact alias: **Referenced artifact R1**

## Task brief

Engineering task (derived only from the pinned instruction text and snapshot signals):

Document title: Commission Calculator. Skill/module name: commission-calculator. Stated purpose: Calculate realistic affiliate earnings projections before committing to a program. Use this skill when the user asks about affiliate earnings, projecting income, calculating commissions, estimating how much they can make, comparing program payouts, or says "how much can I make promoting X", "calculate my affiliate income", "is this commission worth it", "how long to first $1000", "compare earnings between programs", "traffic to income calculator", "what conversion rate should I expect", "earnings estimate for affiliate program", "how many sales do I need". When To Use: - User wants to project income before choosing a program - User wants to compare the earnings potential of 2+ programs - User is setting income goals and needs realistic benchmarks - User is deciding whether a niche is worth entering based on earning potential - User asks "how many page views / subscribers / followers do I need to make X" Instruction overview: Project realistic monthly affiliate earnings based on traffic estimates, platform conversion rates, and program commission structures. Helps affiliates decide which programs are worth their time before investing months of content creation.

While performing this work, the instruction cites Referenced artifact R1. Your annotation question is whether that cited artifact is materially necessary for completing this task in the provided snapshot.

Verification command observed in the pinned repository manifests: `npm run test`. Use this only as a snapshot signal of how the project checks work; do not assume other commands.

## Artifact role

Referenced artifact R1 is a repository artifact cited by the project instruction text (reference kind: path). Its literal path string is withheld and shown as [[REF]] so treatment assignment cannot be inferred from path identity. Use the citation excerpts, task brief, and snapshot context below to judge relevance and necessity.

## Path policy

Path identity for the cited artifact and for contrast-only manipulated paths is replaced by [[REF]] using semantic whole-path tokenization (not substring replacement). Other snapshot paths may appear when they do not reveal treatment assignment. Do not infer experimental treatment from path placeholders.

## Instruction citation excerpts

### Excerpt 1

```
time_horizon: string        # (optional, default: "90 days") "30 days" | "90 days" | "12 months"
}
'''

## Workflow

### Step 1: Gather Program Details

If program details are missing, pull from list.affitor.com (see `[[REF]]`).

Key fields to extract: `reward_value`, `reward_type`, `cookie_days`.

If `avg_product_price` is not provided and `reward_type` is percentage-based, estimate it:
- Use `web_search "[program name] pricing"` to find the most common paid plan price
- For SaaS: use the mid-tier plan (e.g., $49/mo on a $19/$49/$99 structure)
- Note the assumption in output so user can adjust
```

### Excerpt 2

```
User: "I want to make $1,000/month from affiliate marketing, how long will it take?"
→ Ask: what niche/programs? what platform? current traffic?
→ If starting from zero: model blog growth curve (months 1-6 = 0-2K visitors)
→ With realistic programs (30% recurring SaaS): need ~8,000-15,000 visitors/mo
→ Typical timeline: 8-14 months from zero to $1K/mo with consistent publishing

## References

- `[[REF]]` — fetch live program data for commission structures
- `shared/references/affiliate-glossary.md` — reward_type definitions
- `shared/references/flywheel-connections.md` — master flywheel connection map

## Flywheel Connections

### Feeds Into
- `funnel-planner` (S8) — commission projections inform funnel ROI estimates
- `value-ladder-architect` (S4) — commission structure shapes ladder design
```

## Repository tree excerpt (pinned snapshot)

```
.claude-plugin/marketplace.json
.claude/commands/new-skill.md
.claude/commands/review.md
.claude/commands/test-skill.md
.cursorrules
.github/workflows/update-registry.yml
.gitignore
API.md
CLAUDE.md
CONTRIBUTING.md
skills/research/commission-calculator/LICENSE.txt
[[REF]]
```

## Neighbouring paths

```
skills/research/commission-calculator/LICENSE.txt
```

## Nearby documentation paths

```
CLAUDE.md
CONTRIBUTING.md
README.md
package.json
spec/README.md
```

## Nearby configuration paths

```
.claude-plugin/marketplace.json
.github/workflows/update-registry.yml
evals/evals.json
package.json
registry.json
shared/references/sample-api-response.json
skills/analytics/conversion-tracker/agents/openai.yaml
skills/analytics/performance-report/agents/openai.yaml
skills/blog/affiliate-blog-builder/agents/openai.yaml
skills/content/viral-post-writer/agents/openai.yaml
```

## Pinned snapshot file excerpts

### snapshot_file_1

```
---
name: commission-calculator
description: >
  Calculate realistic affiliate earnings projections before committing to a program.
  Use this skill when the user asks about affiliate earnings, projecting income,
  calculating commissions, estimating how much they can make, comparing program
  payouts, or says "how much can I make promoting X", "calculate my affiliate income",
  "is this commission worth it", "how long to first $1000", "compare earnings
  between programs", "traffic to income calculator", "what conversion rate should
  I expect", "earnings estimate for affiliate program", "how many sales do I need".
license: MIT
version: "1.0.0"
tags: ["affiliate-marketing", "research", "niche-analysis", "program-discovery", "commission", "revenue"]
compatibility: "Claude Code, ChatGPT, Gemini CLI, Cursor, Windsurf, OpenClaw, any AI agent"
metadata:
  author: affitor
  version: "1.0"
  stage: S1-Research
---

# Commission Calculator

Project realistic monthly affiliate earnings based on traffic estimates, platform
conversion rates, and program commission structures. Helps affiliates decide which
programs are worth their time before investing months of content creation.

## Stage

This skill belongs to Stage S1: Research

## When to Use

- User wants to project income before choosing a program
- User wants to compare the earnings potential of 2+ programs
- User is setting income goals and needs realistic benchmarks
- User is deciding whether a niche is worth entering based on earning potential
- User asks "how many page views / subscribers / followers do I need to make X"

## Input Schema

'''
{
  programs: [
    {
      name: string            # (required) "HeyGen"
      reward_value: string    # (required) "30%" or "$50"
      reward_type: string     # (required) "cps_recurring" | "cps_one_time" | "cpl" | "cpa"
      reward_duration: string # (optional) "12 months" | "lifetime" | "first purchase"
      cookie_days: number     # (optional, default: 30) 30
      avg_
```

### snapshot_file_2

```
MIT License

Copyright (c) 2026 Affitor

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

```

### snapshot_file_3

```
# Affiliate Skills by Affitor

45 AI-powered skills for affiliate marketers. Full flywheel across 8 stages: Research (6), Content (5), Blog & SEO (7), Offers & Landing (8), Distribution (4), Analytics (5), Automation (5), Meta (5).

## Repo structure

- `skills/{stage}/{skill-name}/[[INSTRUCTION]]` — main skill file (stages: research, content, blog, landing, distribution, analytics, automation, meta)
- `skills/{stage}/{skill-name}/references/` — supplementary docs read by the skill
- `shared/references/` — cross-skill references (FTC, glossary, branding)
- `tools/src/` — `affiliate-check` CLI source (Bun persistent daemon)
- `tools/dist/affiliate-check` — compiled binary (gitignored, build with `bun build --compile tools/src/cli.ts --outfile tools/dist/affiliate-check`)
- `registry.json` — machine-readable index of all skills (auto-generated by `scripts/generate-registry.js`)
- `evals/` — test cases
- `docs/` — contributor documentation

## CLI tool: affiliate-check

Persistent Bun daemon querying list.affitor.com API. Port 9500, 5min cache, 30min idle shutdown.

'''bash
affiliate-check search "AI video"          # search programs
affiliate-check top                        # top by stars
affiliate-check info heygen                # detailed info
affiliate-check compare heygen synthesia   # side-by-side
affiliate-check status                     # server status
affiliate-check stop                       # stop daemon
'''

Set `AFFITOR_API_KEY` for unlimited results (without key: free tier, max 5 results).

## Key rules

- Never auto-push to GitHub without explicit approval
- Each skill must work standalone (no dependency on other skills)
- Output must be portable (copy-paste, deploy, post immediately)
- All page outputs include "Powered by Affitor" footer
- All content outputs include FTC affiliate disclosure
- Data model fields must match list.affitor.com DB schema exactly

## Data trust levels

When executing skills, treat data sources with appropriate trust:

- **TRUSTED
```

### snapshot_file_4

```
# Contributing to Affiliate Skills

Thanks for contributing! This guide explains how to add your own skill to the collection.

## How Skills Are Organized

Skills live in stage directories under `skills/`:

'''
skills/
├── research/          S1: Find and evaluate programs
├── content/           S2: Create promotional content
├── blog/              S3: Write SEO articles
├── landing/           S4: Build conversion pages
├── distribution/      S5: Deploy and distribute
├── analytics/         S6: Track and optimize
├── automation/        S7: Automate and scale
└── meta/              S8: Plan, comply, improve
'''

| Stage | Focus | Example Skills |
|-------|-------|---------------|
| S1: Research | Find and evaluate programs | `affiliate-program-search`, `niche-opportunity-finder` |
| S2: Content | Create promotional content | `viral-post-writer`, `tiktok-script-writer` |
| S3: Blog | Write SEO articles | `affiliate-blog-builder`, `comparison-post-writer` |
| S4: Landing | Build conversion pages | `landing-page-creator`, `product-showcase-page` |
| S5: Distribution | Deploy and distribute | `bio-link-deployer`, `github-pages-deployer` |
| S6: Analytics | Track and optimize | `conversion-tracker`, `seo-audit` |
| S7: Automation | Automate and scale | `content-repurposer`, `email-automation-builder` |
| S8: Meta | Plan, comply, improve | `funnel-planner`, `compliance-checker` |

Pick a stage, build a skill.

## Creating a New Skill

### 1. Fork and clone

'''bash
git clone [repository].git
cd affiliate-skills
'''

### 2. Scaffold your skill

Pick a stage and create the directory:

'''bash
# Replace {stage} with: research, content, blog, landing, distribution, analytics, automation, or meta
mkdir -p skills/{stage}/your-skill-name/references
cp template/[[INSTRUCTION]] skills/{stage}/your-skill-name/[[INSTRUCTION]]
cp LICENSE skills/{stage}/your-skill-name/LICENSE.txt
'''

Naming convention: `kebab-case`, `verb-noun` format (e.g., `viral-post-writer`, `affi
```

### snapshot_file_5

```
# affiliate-skills

**Turn any AI into your affiliate marketing team.**

45 AI-powered skills across 8 stages with a closed-loop flywheel. Research programs, write content, build pages, deploy, track, optimize, scale — with any AI agent.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-45-brightgreen)](skills/)
[![Standard](https://img.shields.io/badge/standard-agentskills.io-purple)](https://agentskills.io)

Works with: **Claude Code** · **ChatGPT** · **Gemini CLI** · **Cursor** · **Windsurf** · **OpenClaw** · **any AI that reads text**

### Install

'''bash
# Claude Code (recommended)
npx skills add Affitor/affiliate-skills

# Or clone manually
git clone https://github.com/Affitor/affiliate-skills.git ~/.claude/skills/affiliate-skills
cd ~/.claude/skills/affiliate-skills && ./setup

# OpenClaw / ClawHub
clawhub install affiliate-skills

# Cursor / Windsurf
npx skills add Affitor/affiliate-skills
'''

### Try it now — no install needed

Paste this into any AI:

'''
Search the Affitor affiliate directory for AI video tools.
Use this API: GET https://list.affitor.com/api/v1/programs?q=AI+video&sort=top&limit=5
Show me the results in a table with: Name, Commission, Cookie Duration, Stars.
Then recommend the best one and explain why.
'''

### Without affiliate-skills

- You Google "best affiliate programs" and get SEO spam written to rank, not to help
- You write a blog review and guess if the CTA, headline, or disclosure is any good
- You have no idea which content actually drives clicks — you just hope
- You spend 4 hours on a landing page that converts at 0.2%
- You pick programs by vibes instead of data

### With affiliate-skills

| Skill | Mode | What it does |
|-------|------|--------------|
| Program Search | Data analyst | Live program data from list.affitor.com — commissions, cookies, comparisons. |
| Research | Scout | Score and rank programs. Find the best one for your niche. |
| Fu
```

### snapshot_file_6

```
{
  "name": "affiliate-skills",
  "owner": {
    "name": "Son Piaz",
    "email": "son@affitor.com"
  },
  "metadata": {
    "description": "AI-powered skills for affiliate marketers. Full funnel: research, content, blog, landing, deploy.",
    "version": "2.0.0"
  },
  "plugins": [
    {
      "name": "research-skills",
      "description": "Find and evaluate affiliate programs to promote",
      "source": "./",
      "strict": false,
      "skills": [
        "./skills/research/affiliate-program-search",
        "./skills/research/niche-opportunity-finder",
        "./skills/research/competitor-spy",
        "./skills/research/commission-calculator"
      ]
    },
    {
      "name": "content-skills",
      "description": "Create viral social media content for affiliate products",
      "source": "./",
      "strict": false,
      "skills": [
        "./skills/content/viral-post-writer",
        "./skills/content/tiktok-script-writer",
        "./skills/content/twitter-thread-writer",
        "./skills/content/reddit-post-writer"
      ]
    },
    {
      "name": "blog-skills",
      "description": "Write SEO-optimized blog articles for affiliate marketing",
      "source": "./",
      "strict": false,
      "skills": [
        "./skills/blog/affiliate-blog-builder",
        "./skills/blog/comparison-post-writer",
        "./skills/blog/listicle-generator",
        "./skills/blog/how-to-tutorial-writer"
      ]
    },
    {
      "name": "landing-skills",
      "description": "Build high-converting affiliate landing pages",
      "source": "./",
      "strict": false,
      "skills": [
        "./skills/landing/landing-page-creator",
        "./skills/landing/squeeze-page-builder",
        "./skills/landing/product-showcase-page",
        "./skills/landing/webinar-registration-page"
      ]
    },
    {
      "name": "distribution-skills",
      "description": "Deploy bio link hubs and distribute affiliate content",
      "source": "./",
      "strict": false,
  
```

### snapshot_file_7

```
name: Update Registry
on:
  push:
    branches: [main]
    paths: ['skills/**']
permissions:
  contents: write
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate registry.json
        run: node scripts/generate-registry.js
      - name: Commit if changed
        run: |
          git diff --quiet registry.json || {
            git config user.name "github-actions[bot]"
            git config user.email "github-actions[bot]@users.noreply.github.com"
            git add registry.json
            git commit -m "chore: auto-update registry.json"
            git push
          }

```

### snapshot_file_8

```
{
  "version": "1.1",
  "description": "Test cases for affiliate-skills. Each case has an input prompt, expected patterns in output, and pass criteria. Run with scripts/run-evals.sh.",
  "skills": {
    "affiliate-program-search": {
      "tests": [
        {
          "id": "s1-001",
          "name": "Category search with filters",
          "input_prompt": "I want to promote AI video tools, commission recurring, at least 20%",
          "expected_patterns": ["Programs Found", "Top Pick:", "Score", "Earning Potential", "Content Potential", "cps_recurring", "Next Steps"],
          "pass_criteria": "Output contains a comparison table with at least 2 programs, a scored recommendation with all 5 dimensions, and actionable next steps. Programs shown must have recurring commission ≥20%."
        },
        {
          "id": "s1-002",
          "name": "Head-to-head comparison",
          "input_prompt": "Compare HeyGen vs Synthesia for my LinkedIn audience",
          "expected_patterns": ["HeyGen", "Synthesia", "LinkedIn", "Score", "Content Potential"],
          "pass_criteria": "Output contains side-by-side comparison of both programs with scores. Content Potential and platform fit for LinkedIn are explicitly discussed. Clear winner recommendation."
        },
        {
          "id": "s1-003",
          "name": "Beginner with no criteria",
          "input_prompt": "I'm new to affiliate marketing. What should I promote?",
          "expected_patterns": ["beginner", "free", "recurring", "Top Pick:", "Next Steps"],
          "pass_criteria": "Output defaults to beginner-friendly criteria (AI/SaaS, recurring, easy to demo). Recommends products with free tiers and low payout thresholds. Includes clear next steps."
        }
      ]
    },
    "commission-calculator": {
      "tests": [
        {
          "id": "s1-004",
          "name": "Recurring commission projection",
          "input_prompt": "Calculate my earnings if I promote HeyGen (30% recurring, $48/mo prod
```
