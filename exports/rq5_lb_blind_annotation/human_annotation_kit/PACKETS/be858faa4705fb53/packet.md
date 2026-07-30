# Annotation packet `be858faa4705fb53`

Protocol: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`
Packet spec: `rq5_v1_blind_packet_spec_v2`

Judge only with the materials below. Do not seek external repositories or experimental results.

## Annotator question

Is Referenced artifact R1 materially necessary for completing THIS software engineering task in THIS repository snapshot?

## Anonymous snapshot

- Snapshot ID: `8009e5cc2e2ab4cd`
- Reference type: `directory`
- Artifact alias: **Referenced artifact R1**

## Task brief

Engineering task (derived only from the pinned instruction text and snapshot signals):

Document title: Content Pillar Atomizer. Skill/module name: content-pillar-atomizer. Stated purpose: Take 1 blog post or article and generate 15-30 platform-native micro-content pieces. Not reformatting — re-contextualizing for each platform's culture. Triggers on: "atomize this content", "repurpose my blog post", "turn this into social posts", "content atomizer", "pillar content", "one to many content", "repurpose content", "multiply my content", "content explosion", "turn article into posts", "break down this article", "micro content from blog", "content pillar strategy", "10x my content", "platform-native content", "atomize", "content multiplication". When To Use: - User has a blog post, article, or long-form content and wants to maximize its reach - User asks to "repurpose" or "atomize" content - User says "turn this into social posts", "content multiplication", "pillar content" - After `affiliate-blog-builder` (S3) produces an article — atomize it into social - User wants to maintain consistent content output without creating from scratch daily Instruction overview: S2: Content Creation — This IS content creation, just at 10x scale. One piece of deep work becomes a month of social content.

While performing this work, the instruction cites Referenced artifact R1. Your annotation question is whether that cited artifact is materially necessary for completing this task in the provided snapshot.

Verification command observed in the pinned repository manifests: `npm run test`. Use this only as a snapshot signal of how the project checks work; do not assume other commands.

## Artifact role

Referenced artifact R1 is a repository artifact cited by the project instruction text (reference kind: directory). Its literal path string is withheld and shown as [[REF]] so treatment assignment cannot be inferred from path identity. Use the citation excerpts, task brief, and snapshot context below to judge relevance and necessity.

## Path policy

Path identity for the cited artifact and for contrast-only manipulated paths is replaced by [[REF]] using semantic whole-path tokenization (not substring replacement). Other snapshot paths may appear when they do not reveal treatment assignment. Do not infer experimental treatment from path placeholders.

## Instruction citation excerpts

### Excerpt 1

```
---
name: content-pillar-atomizer
description: >
  Take 1 blog post or article and generate 15-30 platform-native micro-content pieces.
  Not reformatting — re-contextualizing for each platform's culture.
  Triggers on: "atomize this content", "repurpose my blog post", "turn this into social posts",
  "content atomizer", "pillar content", "one to many content", "repurpose content",
  "multiply my content", "content explosion", "turn article into posts",
  "break down this article", "micro content from blog", "content pillar strategy",
  "10x my content", "platform-native content", "atomize", "content multiplication".
license: MIT
version: "1.0.0"
```

### Excerpt 2

```
name: content-pillar-atomizer
description: >
  Take 1 blog post or article and generate 15-30 platform-native micro-content pieces.
  Not reformatting — re-contextualizing for each platform's culture.
  Triggers on: "atomize this content", "repurpose my blog post", "turn this into social posts",
  "content atomizer", "pillar content", "one to many content", "repurpose content",
  "multiply my content", "content explosion", "turn article into posts",
  "break down this article", "micro content from blog", "content pillar strategy",
  "10x my content", "platform-native content", "atomize", "content multiplication".
license: MIT
version: "1.0.0"
tags: ["affiliate-marketing", "content-creation", "social-media", "copywriting", "content-strategy", "repurposing"]
compatibility: "Claude Code, ChatGPT, Gemini CLI, Cursor, Windsurf, OpenClaw, any AI agent"
metadata:
  author: affitor
  version: "1.0"
  stage: S2-Content
```

### Excerpt 3

```
Take 1 blog post or article and generate 15-30 platform-native micro-content pieces.
  Not reformatting — re-contextualizing for each platform's culture.
  Triggers on: "atomize this content", "repurpose my blog post", "turn this into social posts",
  "content atomizer", "pillar content", "one to many content", "repurpose content",
  "multiply my content", "content explosion", "turn article into posts",
  "break down this article", "micro content from blog", "content pillar strategy",
  "10x my content", "platform-native content", "atomize", "content multiplication".
license: MIT
version: "1.0.0"
tags: ["affiliate-marketing", "content-creation", "social-media", "copywriting", "content-strategy", "repurposing"]
compatibility: "Claude Code, ChatGPT, Gemini CLI, Cursor, Windsurf, OpenClaw, any AI agent"
metadata:
  author: affitor
  version: "1.0"
  stage: S2-Content
---
```

### Excerpt 4

```
"break down this article", "micro content from blog", "content pillar strategy",
  "10x my content", "platform-native content", "atomize", "content multiplication".
license: MIT
version: "1.0.0"
tags: ["affiliate-marketing", "content-creation", "social-media", "copywriting", "content-strategy", "repurposing"]
compatibility: "Claude Code, ChatGPT, Gemini CLI, Cursor, Windsurf, OpenClaw, any AI agent"
metadata:
  author: affitor
  version: "1.0"
  stage: S2-Content
---

# Content Pillar Atomizer

Take 1 blog post or article and generate 15-30 platform-native micro-content pieces. This is NOT reformatting — it's re-contextualizing each piece for the platform's culture, format, and audience expectations. A LinkedIn post reads nothing like a Reddit comment, even if they carry the same insight.

## Stage
```

### Excerpt 5

```
metadata:
  author: affitor
  version: "1.0"
  stage: S2-Content
---

# Content Pillar Atomizer

Take 1 blog post or article and generate 15-30 platform-native micro-content pieces. This is NOT reformatting — it's re-contextualizing each piece for the platform's culture, format, and audience expectations. A LinkedIn post reads nothing like a Reddit comment, even if they carry the same insight.

## Stage

S2: Content Creation — This IS content creation, just at 10x scale. One piece of deep work becomes a month of social content.

## When to Use

- User has a blog post, article, or long-form content and wants to maximize its reach
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
CHANGELOG.md
CLAUDE.md
[[REF]]
```

## Neighbouring paths

_None listed in the minimal context window._

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
name: content-pillar-atomizer
description: >
  Take 1 blog post or article and generate 15-30 platform-native micro-content pieces.
  Not reformatting — re-contextualizing for each platform's culture.
  Triggers on: "atomize this content", "repurpose my blog post", "turn this into social posts",
  "content atomizer", "pillar content", "one to many content", "repurpose content",
  "multiply my content", "content explosion", "turn article into posts",
  "break down this article", "micro content from blog", "content pillar strategy",
  "10x my content", "platform-native content", "atomize", "content multiplication".
license: MIT
version: "1.0.0"
tags: ["affiliate-marketing", "content-creation", "social-media", "copywriting", "content-strategy", "repurposing"]
compatibility: "Claude Code, ChatGPT, Gemini CLI, Cursor, Windsurf, OpenClaw, any AI agent"
metadata:
  author: affitor
  version: "1.0"
  stage: S2-Content
---

# Content Pillar Atomizer

Take 1 blog post or article and generate 15-30 platform-native micro-content pieces. This is NOT reformatting — it's re-contextualizing each piece for the platform's culture, format, and audience expectations. A LinkedIn post reads nothing like a Reddit comment, even if they carry the same insight.

## Stage

S2: Content Creation — This IS content creation, just at 10x scale. One piece of deep work becomes a month of social content.

## When to Use

- User has a blog post, article, or long-form content and wants to maximize its reach
- User asks to "repurpose" or "atomize" content
- User says "turn this into social posts", "content multiplication", "pillar content"
- After `affiliate-blog-builder` (S3) produces an article — atomize it into social
- User wants to maintain consistent content output without creating from scratch daily

## Input Schema

'''yaml
pillar_content: string        # REQUIRED — the full blog post/article text, or URL to fetch

platforms: string[]           # OPTIONAL — target platforms
                 
```

### snapshot_file_2

```
# Affiliate Skills by Affitor

50 AI-powered skills for affiliate marketers. Full flywheel across 8 stages: Research (9), Content (7), Blog & SEO (7), Offers & Landing (8), Distribution (4), Analytics (5), Automation (5), Meta (5).

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

### snapshot_file_3

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

### snapshot_file_4

```
# affiliate-skills

**Turn any AI into your affiliate marketing team.**

50 AI-powered skills across 8 stages with a closed-loop flywheel. Research programs, scout trending content, write data-backed posts, generate infographics, build pages, deploy, track, optimize, scale — with any AI agent.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-50-brightgreen)](skills/)
[![Standard](https://img.shields.io/badge/standard-agentskills.io-purple)](https://agentskills.io)

Works with: **Claude Code** · **Pi** · **ChatGPT** · **Gemini CLI** · **Cursor** · **Windsurf** · **OpenClaw** · **any AI that reads text**

### Install

'''bash
# Claude Code / Pi (recommended)
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
- You write content from gut feeling with no idea what format actually performs
- You have no data on what's trending, what hooks work, or what gaps exist
- You spend 4 hours on a landing page that converts at 0.2%
- You pick programs by vibes instead of data

### With affiliate-skills

| Skill | Mode | What it does |
|-------|------|--------------|
| Program Search | Data analyst | Live program data from list.affitor.com — commissions, cookies, comparisons. |
| Trending Scout
```

### snapshot_file_5

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

### snapshot_file_6

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

### snapshot_file_7

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
