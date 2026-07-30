# Annotation packet `477af6ec413b58de`

Protocol: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`
Packet spec: `rq5_v1_blind_packet_spec_v2`

Judge only with the materials below. Do not seek external repositories or experimental results.

## Annotator question

Is Referenced artifact R1 materially necessary for completing THIS software engineering task in THIS repository snapshot?

## Anonymous snapshot

- Snapshot ID: `35a7a6d33a9dc047`
- Reference type: `path`
- Artifact alias: **Referenced artifact R1**

## Task brief

Engineering task (derived only from the pinned instruction text and snapshot signals):

Document title: next-dev-loop. Skill/module name: next-dev-loop. Stated purpose: Verify Next.js runtime behavior after editing app code. Use this skill to confirm a change actually works in a running app — not just that it compiles or type-checks. Combines [[REF]] (Next.js's view) with agent-browser (the browser's view). Requires a running `next dev`. Instruction overview: The edit/verify rhythm during `next dev` — make a change, then confirm it actually works at runtime, not only that the types or the build are happy.

While performing this work, the instruction cites Referenced artifact R1. Your annotation question is whether that cited artifact is materially necessary for completing this task in the provided snapshot.

Verification command observed in the pinned repository manifests: `npm run test`. Use this only as a snapshot signal of how the project checks work; do not assume other commands.

## Artifact role

Referenced artifact R1 is a repository artifact cited by the project instruction text (reference kind: path). Its literal path string is withheld and shown as [[REF]] so treatment assignment cannot be inferred from path identity. Use the citation excerpts, task brief, and snapshot context below to judge relevance and necessity.

## Path policy

Path identity for the cited artifact and for contrast-only manipulated paths is replaced by [[REF]] using semantic whole-path tokenization (not substring replacement). Other snapshot paths may appear when they do not reveal treatment assignment. Do not infer experimental treatment from path placeholders.

## Instruction citation excerpts

### Excerpt 1

```
---
name: next-dev-loop
description: >
  Verify Next.js runtime behavior after editing app code. Use this
  skill to confirm a change actually works in a running app — not
  just that it compiles or type-checks. Combines [[REF]]
  (Next.js's view) with agent-browser (the browser's view).
  Requires a running `next dev`.
---

# next-dev-loop

The edit/verify rhythm during `next dev` — make a change, then
confirm it actually works at runtime, not only that the types or
```

### Excerpt 2

```
# next-dev-loop

The edit/verify rhythm during `next dev` — make a change, then
confirm it actually works at runtime, not only that the types or
the build are happy.

You verify through two views of the same running app:

- **`[[REF]]`** — an HTTP endpoint Next.js exposes about itself.
  Knows framework-specific things: routes, segments, RSC, server
  actions, server logs, and errors as Next.js saw them. Call
  `tools/list` for the current surface.
- **`agent-browser`** — a CLI that drives a real Chrome. Knows
  framework-agnostic browser things: DOM, console, network, React
  fiber, vitals. Run `agent-browser --help` for the current surface.

The two views cross-check each other.
```

### Excerpt 3

```
- **`agent-browser`** — a CLI that drives a real Chrome. Knows
  framework-agnostic browser things: DOM, console, network, React
  fiber, vitals. Run `agent-browser --help` for the current surface.

The two views cross-check each other.

## requires

- Next.js **16.3+** with **Turbopack** — `[[REF]]` plus the
  proactive compile check via `get_compilation_issues`.
- `agent-browser` **>= 0.27.0** — when React introspection landed.

These are hard floors, not soft preferences. If anything is missing,
tell the user how to upgrade and stop. Don't fall back to grepping
source or to a weaker probe — this skill assumes both views are live
at the versions above.
```

### Excerpt 4

```
browser is the user's, not yours; `agent-browser open` is
   headless by default, so `--headed` is required. If the page is
   behind login, gated by a feature flag, or needs specific state,
   the user drives that — log in, set state, navigate. Continue
   only after they confirm. Session state is sticky per session:
   you can't add `--enable react-devtools` after the session is
   open, and `cookies set` on a not-yet-opened session creates a
   sessionless cookie that silently fails to apply.
2. POST `tools/list` to `[[REF]]`. Send
   `Accept: application/json, text/event-stream`; responses are
   SSE-framed, strip the `data: ` prefix before parsing JSON.
   - Unreachable → either `next dev` isn't running, or Next.js is
     below 16.3. Check `package.json` to disambiguate, then refuse.
   - `get_compilation_issues` not in the list → Next.js below 16.3.
     Refuse and tell the user to upgrade.
3. `mcp get_compilation_issues` doubles as a Turbopack probe.
   An error response of `"Turbopack project is not available..."`
```

### Excerpt 5

```
An error response of `"Turbopack project is not available..."`
   means the user is on webpack. Refuse — Turbopack is required.
4. `mcp get_routes` → your route map for the rest of the session.

## loop

### before the edit — narrow the scope

Ask the running app, not the codebase. `[[REF]]` knows which
files rendered the current route; use those as your search scope.
Runtime introspection stays cheap as the codebase grows; agentic
search doesn't.

### after the edit — verify

Four failure modes. Check each:
```

## Repository tree excerpt (pinned snapshot)

```
"test/e2e/image-optimizer/app/public/\303\244\303\266\303\274\305\241\304\215\305\231\303\255.png"
"test/e2e/next-image-legacy/unicode/public/\303\244\303\266\303\274\305\241\304\215\305\231\303\255.png"
"test/e2e/next-image-new/unicode/public/\303\244\303\266\303\274\305\241\304\215\305\231\303\255.png"
.agents/skills/README.md
.agents/skills/authoring-skills/[[INSTRUCTION]]
.agents/skills/backport-pr/[[INSTRUCTION]]
.agents/skills/create-pr/[[INSTRUCTION]]
.agents/skills/dce-edge/[[INSTRUCTION]]
.agents/skills/flags/[[INSTRUCTION]]
.agents/skills/gh-stack/[[INSTRUCTION]]
.agents/skills/pr-status-triage/[[INSTRUCTION]]
.agents/skills/pr-status-triage/local-repro.md
.agents/skills/pr-status-triage/workflow.md
.agents/skills/react-vendoring/[[INSTRUCTION]]
.agents/skills/router-act/[[INSTRUCTION]]
.agents/skills/runtime-debug/[[INSTRUCTION]]
.agents/skills/update-docs/[[INSTRUCTION]]
.agents/skills/update-docs/references/CODE-TO-DOCS-MAPPING.md
.agents/skills/update-docs/references/DOC-CONVENTIONS.md
.agents/skills/v8-jit/[[INSTRUCTION]]
.agents/skills/write-api-reference/[[INSTRUCTION]]
.agents/skills/write-guide/[[INSTRUCTION]]
.alexignore
.alexrc
.cargo/.vercel.approvers
.cargo/config.toml
.claude-plugin/marketplace.json
.claude-plugin/plugins/README.md
.claude-plugin/plugins/cache-components/.claude-plugin/plugin.json
.claude-plugin/plugins/cache-components/README.md
.claude-plugin/plugins/cache-components/skills/cache-components/PATTERNS.md
.claude-plugin/plugins/cache-components/skills/cache-components/REFERENCE.md
.claude-plugin/plugins/cache-components/skills/cache-components/[[INSTRUCTION]]
.claude-plugin/plugins/cache-components/skills/cache-components/TROUBLESHOOTING.md
.claude/skills
.conductor/README.md
.conductor/scripts/run.sh
.conductor/scripts/setup.sh
[[REF]]
```

## Neighbouring paths

_None listed in the minimal context window._

## Nearby documentation paths

```
.agents/skills/README.md
.claude-plugin/plugins/README.md
.claude-plugin/plugins/cache-components/README.md
.conductor/README.md
.github/actions/needs-triage/package.json
.github/actions/next-integration-stat/package.json
.github/actions/next-repo-actions/package.json
.github/actions/next-stats-action/README.md
.github/actions/next-stats-action/package.json
.github/actions/pr-auto-label/README.md
```

## Nearby configuration paths

```
.cargo/config.toml
.claude-plugin/marketplace.json
.claude-plugin/plugins/cache-components/.claude-plugin/plugin.json
.config/ast-grep/rule-tests/__snapshots__/no-context-format-snapshot.yml
.config/ast-grep/rule-tests/__snapshots__/no-context-snapshot.yml
.config/ast-grep/rule-tests/__snapshots__/no-context-turbofmt-snapshot.yml
.config/ast-grep/rule-tests/__snapshots__/no-err-anyhow-snapshot.yml
.config/ast-grep/rule-tests/__snapshots__/no-map-async-cell-snapshot.yml
.config/ast-grep/rule-tests/__snapshots__/resolved-vc-in-return-type-snapshot.yml
.config/ast-grep/rule-tests/__snapshots__/resolved-vc-in-trait-arguments-snapshot.yml
```

## Pinned snapshot file excerpts

### snapshot_file_1

```
---
name: next-dev-loop
description: >
  Verify Next.js runtime behavior after editing app code. Use this
  skill to confirm a change actually works in a running app — not
  just that it compiles or type-checks. Combines [[REF]]
  (Next.js's view) with agent-browser (the browser's view).
  Requires a running `next dev`.
---

# next-dev-loop

The edit/verify rhythm during `next dev` — make a change, then
confirm it actually works at runtime, not only that the types or
the build are happy.

You verify through two views of the same running app:

- **`[[REF]]`** — an HTTP endpoint Next.js exposes about itself.
  Knows framework-specific things: routes, segments, RSC, server
  actions, server logs, and errors as Next.js saw them. Call
  `tools/list` for the current surface.
- **`agent-browser`** — a CLI that drives a real Chrome. Knows
  framework-agnostic browser things: DOM, console, network, React
  fiber, vitals. Run `agent-browser --help` for the current surface.

The two views cross-check each other.

## requires

- Next.js **16.3+** with **Turbopack** — `[[REF]]` plus the
  proactive compile check via `get_compilation_issues`.
- `agent-browser` **>= 0.27.0** — when React introspection landed.

These are hard floors, not soft preferences. If anything is missing,
tell the user how to upgrade and stop. Don't fall back to grepping
source or to a weaker probe — this skill assumes both views are live
at the versions above.

- Upgrade Next.js: `pnpm next upgrade` (or `npx next upgrade`).
  Docs: https://nextjs.org/docs/app/getting-started/upgrading
  (version-16 guide:
  https://nextjs.org/docs/app/guides/upgrading/version-16)
- Upgrade `agent-browser`: `npm i -g agent-browser@latest`.

## preflight

Once per session, confirm both views are live.

1. **Open the user's `agent-browser` session at the target URL
   with `--headed` and react-devtools enabled, then pause.** The
   browser is the user's, not yours; `agent-browser open` is
   headless by default, so `-
```

### snapshot_file_2

```
# Skills Authoring Guide

Skills are on-demand context files that Claude loads when relevant. They extend `AGENTS.md` with deep-dive workflows, code templates, and verification steps.

## When to Create a Skill

Create a skill when content is:
- **Too detailed for AGENTS.md** (code templates, multi-step workflows, diagnostic procedures)
- **Only relevant for specific tasks** (not every session needs it)
- **Self-contained enough to load independently**

Do NOT create a skill for:
- One-liner rules or guardrails (keep those in AGENTS.md)
- Content every agent session needs (that's what AGENTS.md is for)
- Simple facts without actionable steps

## File Structure

'''
.agents/skills/
├── my-skill/
│   └── [[INSTRUCTION]]          # Required: frontmatter + content
│   └── workflow.md        # Optional: supplementary files
│   └── examples.md        # Optional: referenced from [[INSTRUCTION]]
└── README.md              # This file
'''

## [[INSTRUCTION]] Format

'''yaml
---
name: my-skill
description: >
  What this skill covers and when to use it. Include key file names,
  concepts, and trigger phrases so Claude can match user intent to this
  skill. This is the primary field Claude uses for auto-activation.
---
'''

### Supported Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Skill name, used for `$name` references and `/name` slash commands |
| `description` | Yes | What the skill does and when to use it. **This is how Claude decides to auto-load the skill.** Include file names, concepts, and keywords. |
| `argument-hint` | No | Hint for expected arguments in autocomplete |
| `user-invocable` | No | Set to `false` to hide from `/` slash command menu |
| `disable-model-invocation` | No | Set to `true` to prevent Claude from auto-triggering this skill |
| `allowed-tools` | No | Tools Claude can use without permission when this skill is active |
| `model` | No | Model override for this skill |
| `context` | No | Set to `fork` for iso
```

### snapshot_file_3

```
# Next.js Claude Code Plugins

This directory contains Claude Code plugins for Next.js development.

## Using the Next.js Plugin Marketplace

The Next.js repository serves as a Claude Code plugin marketplace. Team members and contributors can install plugins directly from this repo.

### Quick Start

'''bash
# Add the Next.js marketplace
/plugin marketplace add vercel/next.js

# List available plugins
/plugin list

# Install a plugin
/plugin install cache-components@nextjs
'''

### Available Plugins

| Plugin | Description |
|--------|-------------|
| `cache-components` | Expert guidance for Cache Components and PPR |

## For Team Members

To auto-enable plugins for everyone working in a Next.js project, add to `.claude/settings.json`:

'''json
{
  "extraKnownMarketplaces": {
    "nextjs": {
      "source": {
        "source": "github",
        "repo": "vercel/next.js"
      }
    }
  },
  "enabledPlugins": {
    "cache-components@nextjs": true
  }
}
'''

## Creating New Plugins

To add a new plugin to the marketplace:

### 1. Create Plugin Directory

'''bash
mkdir -p .claude-plugin/plugins/my-plugin/.claude-plugin
mkdir -p .claude-plugin/plugins/my-plugin/skills/my-skill
'''

### 2. Create Plugin Manifest

**File**: `.claude-plugin/plugins/my-plugin/.claude-plugin/plugin.json`

'''json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "What the plugin does",
  "author": {
    "name": "Next.js Team"
  }
}
'''

### 3. Create Skill

**File**: `.claude-plugin/plugins/my-plugin/skills/my-skill/[[INSTRUCTION]]`

'''yaml
---
name: my-skill
description: When to use this skill
---

# My Skill

Instructions for Claude...
'''

### 4. Register in Marketplace

Add to `.claude-plugin/marketplace.json`:

'''json
{
  "plugins": [
    {
      "name": "my-plugin",
      "source": "./plugins/my-plugin",
      "description": "What it does"
    }
  ]
}
'''

### 5. Test Locally

'''bash
claude --plugin-dir .claude-plugin/plugins/my-plugin
'''

## Plugin Structure

'''
.claude-plu
```

### snapshot_file_4

```
# Cache Components Plugin for Claude Code

Expert guidance for Next.js Cache Components and Partial Prerendering (PPR).

## Features

This plugin provides a comprehensive skill that:

- **Proactively activates** in projects with `cacheComponents: true`
- Teaches the `'use cache'` directive, `cacheLife()`, `cacheTag()`, and invalidation APIs
- Explains **parameter permutation rendering** and subshell generation
- Covers migration from deprecated `revalidate`/`dynamic` segment configs
- Provides build-time error solutions and debugging guidance

## Installation

### Step 1: Add the Next.js Marketplace

'''
/plugin marketplace add vercel/next.js
'''

### Step 2: Install the Plugin

'''
/plugin install cache-components@nextjs
'''

Or install via CLI:

'''bash
claude plugin install cache-components@nextjs
'''

### Step 3 (Optional): Enable for Your Team

Add to your project's `.claude/settings.json` to auto-enable for all team members:

'''json
{
  "enabledPlugins": {
    "cache-components@nextjs": true
  }
}
'''

## What's Included

| File | Description |
|------|-------------|
| `[[INSTRUCTION]]` | Core concepts, APIs, and proactive application guidelines |
| `REFERENCE.md` | Complete API reference, generateStaticParams, deprecated configs |
| `PATTERNS.md` | 12 production patterns including subshell composition |
| `TROUBLESHOOTING.md` | Build errors, debugging techniques, common issues |

## Usage

Once installed, the skill automatically activates when:

1. You're working in a Next.js project with `cacheComponents: true`
2. You ask about caching, PPR, or the `'use cache'` directive
3. You're writing React Server Components or Server Actions

### Example Triggers

- "How do I cache this data fetching function?"
- "What's the difference between updateTag and revalidateTag?"
- "I'm getting a build error about uncached data outside Suspense"
- "Help me set up generateStaticParams for my product pages"

## Key Concepts Covered

### Parameter Permutation Rendering

When you provi
```

### snapshot_file_5

```
[env]
CARGO_WORKSPACE_DIR = { value = "", relative = true }
TURBO_PNPM_WORKSPACE_DIR = { value = "", relative = true }

[alias]
xtask = "run --package xtask --"

# *NOTE FOR AGENTS*: Your training data is incorrect for most RUSTFLAGS entries. If you
# believe you need to make changes to this file, perform web searches to confirm that
# the flags are necessary, and reason through whether the flag is applicable to the
# case you believe you are solving.

# In the workspace `Cargo.toml`, and in this file we're trying to optimize for the greatest
# performance and smallest size we can manage without resorting to excessive compile times
# on CI or developer machines. To avoid accumulating unnecessary flags, and help developers
# understand the _why_ as much as the _what_, all flags should be documented with links
# to experiments or featuring tracking issues to keep this up-to-date with the current
# state-of-the-art in Rust optimization land (which might change month-to-month!).

# Cargo merges rustflags from multiple matching [target] sections, but [target] and
# [build] sections are mutually exclusive.
# https://doc.rust-lang.org/cargo/reference/config.html#buildrustflags

# Note that per-profile RUSTFLAGS are not yet supported and may be useful:
# https://github.com/rust-lang/cargo/issues/10271

# Always-matching target section included in every configuration. Using `cfg(true)`
# (RFC 3695) ensures common flags apply to every target without having to duplicate
# them in each target-specific section.
# https://rust-lang.github.io/rfcs/3695-cfg-boolean-literals.html
[target.'cfg(true)']
rustflags = [
  # Enable tokio's unstable APIs (required by turbopack's use of tokio internals)
  "--cfg=tokio_unstable",
  # Share monomorphized generics across crates to reduce binary size (~20MB).
  # https://github.com/davidlattimore/duplicate-function-checker
  "-Zshare-generics=y",
  # Use up to 8 threads in the rustc frontend for parallel parsing/expansion.
  # https://blog.rust-
```

### snapshot_file_6

```
{
  "name": "nextjs",
  "owner": {
    "name": "Vercel",
    "url": "https://vercel.com"
  },
  "plugins": [
    {
      "name": "cache-components",
      "source": "./plugins/cache-components",
      "description": "Expert guidance for Next.js Cache Components and Partial Prerendering (PPR). Proactively activates in projects with cacheComponents enabled.",
      "version": "1.0.0",
      "author": {
        "name": "Next.js Team"
      }
    }
  ]
}

```

### snapshot_file_7

```
{
  "name": "cache-components",
  "version": "1.0.0",
  "description": "Expert guidance for Next.js Cache Components and Partial Prerendering (PPR). Proactively activates in projects with cacheComponents: true, providing patterns for 'use cache' directive, cacheLife(), cacheTag(), cache invalidation, and parameter permutation rendering.",
  "author": {
    "name": "Next.js Team",
    "url": "https://nextjs.org"
  },
  "homepage": "https://nextjs.org/docs/app/building-your-application/caching",
  "repository": "[repository]",
  "license": "MIT",
  "keywords": [
    "nextjs",
    "cache",
    "ppr",
    "partial-prerendering",
    "react-server-components",
    "use-cache"
  ]
}

```
