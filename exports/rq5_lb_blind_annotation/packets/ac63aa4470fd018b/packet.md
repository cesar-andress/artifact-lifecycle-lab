# Annotation packet `ac63aa4470fd018b`

Protocol: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`
Packet spec: `rq5_v1_blind_packet_spec_v2`

Judge only with the materials below. Do not seek external repositories or experimental results.

## Annotator question

Is Referenced artifact R1 materially necessary for completing THIS software engineering task in THIS repository snapshot?

## Anonymous snapshot

- Snapshot ID: `cc4cbff7634be23f`
- Reference type: `directory`
- Artifact alias: **Referenced artifact R1**

## Task brief

Engineering task (derived only from the pinned instruction text and snapshot signals):

Document title: Social Media Scheduler. Skill/module name: social-media-scheduler. Stated purpose: Create a 30-day social media content calendar for affiliate marketing. Triggers on: "create a social media calendar", "30-day content plan", "social media schedule", "content calendar for [product]", "plan my social posts", "social media strategy", "schedule my affiliate posts", "content plan for LinkedIn", "30 days of content", "social posting schedule", "what should I post this month", "write my social content", "create posts for LinkedIn X Facebook", "affiliate content calendar", "social media plan for my affiliate program". When To Use: - User wants a content plan for promoting an affiliate product over 30 days - User asks for a social media calendar, posting schedule, or content strategy - User wants platform-specific posts (LinkedIn professional angle, X casual, Reddit community-first) - User has an audience on one or more social platforms and wants consistent posting - Chaining from S1 (product research) — user found a product and now wants a social plan Instruction overview: Generate a complete 30-day social media content calendar with post copy, hashtags, and scheduling times for LinkedIn, X (Twitter), Facebook, and Reddit. Follows the 80/20 rule: 80% value and engagement content, 20% affiliate promotions. Every post is ready to copy-paste or load into a scheduling tool.

While performing this work, the instruction cites Referenced artifact R1. Your annotation question is whether that cited artifact is materially necessary for completing this task in the provided snapshot.

Verification command observed in the pinned repository manifests: `npm run test`. Use this only as a snapshot signal of how the project checks work; do not assume other commands.

## Artifact role

Referenced artifact R1 is a repository artifact cited by the project instruction text (reference kind: directory). Its literal path string is withheld and shown as [[REF]] so treatment assignment cannot be inferred from path identity. Use the citation excerpts, task brief, and snapshot context below to judge relevance and necessity.

## Path policy

Path identity for the cited artifact and for contrast-only manipulated paths is replaced by [[REF]] using semantic whole-path tokenization (not substring replacement). Other snapshot paths may appear when they do not reveal treatment assignment. Do not infer experimental treatment from path placeholders.

## Instruction citation excerpts

### Excerpt 1

```
metadata:
  author: affitor
  version: "1.0"
  stage: S5-Distribution
---

# Social Media Scheduler

Generate a complete 30-day social media content calendar with post copy, hashtags, and scheduling times for LinkedIn, X (Twitter), Facebook, and Reddit. Follows the 80/20 rule: 80% value and engagement content, 20% affiliate promotions. Every post is ready to copy-paste or load into a scheduling tool.

## Stage

S5: Distribution — Social media is the top free traffic channel for affiliate marketers. This skill eliminates "what do I post today?" paralysis by giving you 30 days of content in one shot, optimized for each platform's algorithm and audience behavior.

## When to Use

- User wants a content plan for promoting an affiliate product over 30 days
```

### Excerpt 2

```
# Default: "educational"
  personal_story: string    # OPTIONAL — brief personal experience with the product

platforms:
  - string                  # REQUIRED — list of platforms: "linkedin" | "x" | "facebook" | "reddit"
                            # Default: ["linkedin", "x"]

calendar:
  start_date: string        # OPTIONAL — ISO date (e.g., "2026-04-01"). Default: next Monday.
  posts_per_week: number    # OPTIONAL — 3-7. Default: 5 (weekdays only)
  promotion_ratio: number   # OPTIONAL — % of posts that are affiliate promo. Default: 20
'''

**Chaining context**: If S1 (product research) was run, auto-fill `product.name`, `product.affiliate_url`, `product.key_benefits`. If S3 (blog post) was run, include 2 posts linking to the blog post. If S4 (landing page) was run, include posts driving to the landing page.

## Workflow
```

### Excerpt 3

```
platforms:
  - string                  # REQUIRED — list of platforms: "linkedin" | "x" | "facebook" | "reddit"
                            # Default: ["linkedin", "x"]

calendar:
  start_date: string        # OPTIONAL — ISO date (e.g., "2026-04-01"). Default: next Monday.
  posts_per_week: number    # OPTIONAL — 3-7. Default: 5 (weekdays only)
  promotion_ratio: number   # OPTIONAL — % of posts that are affiliate promo. Default: 20
'''

**Chaining context**: If S1 (product research) was run, auto-fill `product.name`, `product.affiliate_url`, `product.key_benefits`. If S3 (blog post) was run, include 2 posts linking to the blog post. If S4 (landing page) was run, include posts driving to the landing page.

## Workflow

### Step 1: Gather Inputs
```

### Excerpt 4

```
# Default: ["linkedin", "x"]

calendar:
  start_date: string        # OPTIONAL — ISO date (e.g., "2026-04-01"). Default: next Monday.
  posts_per_week: number    # OPTIONAL — 3-7. Default: 5 (weekdays only)
  promotion_ratio: number   # OPTIONAL — % of posts that are affiliate promo. Default: 20
'''

**Chaining context**: If S1 (product research) was run, auto-fill `product.name`, `product.affiliate_url`, `product.key_benefits`. If S3 (blog post) was run, include 2 posts linking to the blog post. If S4 (landing page) was run, include posts driving to the landing page.

## Workflow

### Step 1: Gather Inputs

Collect required fields. If product details are available from S1, use them. Otherwise ask:
- "What product are you promoting and what's your affiliate link?"
- "What's your content niche and who's your target audience?"
```

### Excerpt 5

```
### Step 1: Gather Inputs

Collect required fields. If product details are available from S1, use them. Otherwise ask:
- "What product are you promoting and what's your affiliate link?"
- "What's your content niche and who's your target audience?"
- "Which platforms: LinkedIn, X, Facebook, Reddit? (pick 1-4)"

### Step 2: Plan the 30-Day Arc

Divide the month into 4 weeks with a strategic arc:

| Week | Theme | Promo Ratio |
|------|-------|-------------|
| Week 1 | Education + awareness — establish authority, zero sell | 0% |
| Week 2 | Problem agitation — surface pain points the product solves | 10% |
| Week 3 | Solution introduction — introduce product, soft sell | 30% |
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
skills/distribution/social-media-scheduler/LICENSE.txt
[[REF]]
```

## Neighbouring paths

```
skills/distribution/social-media-scheduler/LICENSE.txt
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
name: social-media-scheduler
description: >
  Create a 30-day social media content calendar for affiliate marketing. Triggers on:
  "create a social media calendar", "30-day content plan", "social media schedule",
  "content calendar for [product]", "plan my social posts", "social media strategy",
  "schedule my affiliate posts", "content plan for LinkedIn", "30 days of content",
  "social posting schedule", "what should I post this month", "write my social content",
  "create posts for LinkedIn X Facebook", "affiliate content calendar",
  "social media plan for my affiliate program".
license: MIT
version: "1.0.0"
tags: ["affiliate-marketing", "distribution", "deployment", "email-marketing", "scheduling", "content-calendar"]
compatibility: "Claude Code, ChatGPT, Gemini CLI, Cursor, Windsurf, OpenClaw, any AI agent"
metadata:
  author: affitor
  version: "1.0"
  stage: S5-Distribution
---

# Social Media Scheduler

Generate a complete 30-day social media content calendar with post copy, hashtags, and scheduling times for LinkedIn, X (Twitter), Facebook, and Reddit. Follows the 80/20 rule: 80% value and engagement content, 20% affiliate promotions. Every post is ready to copy-paste or load into a scheduling tool.

## Stage

S5: Distribution — Social media is the top free traffic channel for affiliate marketers. This skill eliminates "what do I post today?" paralysis by giving you 30 days of content in one shot, optimized for each platform's algorithm and audience behavior.

## When to Use

- User wants a content plan for promoting an affiliate product over 30 days
- User asks for a social media calendar, posting schedule, or content strategy
- User wants platform-specific posts (LinkedIn professional angle, X casual, Reddit community-first)
- User has an audience on one or more social platforms and wants consistent posting
- Chaining from S1 (product research) — user found a product and now wants a social plan

## Input Schema

'''yaml
product:
  name: string     
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
