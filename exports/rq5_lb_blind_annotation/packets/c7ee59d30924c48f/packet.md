# Annotation packet `c7ee59d30924c48f`

Protocol: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`
Packet spec: `rq5_v1_blind_packet_spec_v2`

Judge only with the materials below. Do not seek external repositories or experimental results.

## Annotator question

Is Referenced artifact R1 materially necessary for completing THIS software engineering task in THIS repository snapshot?

## Anonymous snapshot

- Snapshot ID: `95dd2caab4d57ca2`
- Reference type: `path`
- Artifact alias: **Referenced artifact R1**

## Task brief

Engineering task (derived only from the pinned instruction text and snapshot signals):

Document title: Coding Agent (bash-first). Skill/module name: coding-agent. Stated purpose: Run Codex CLI, Claude Code, OpenCode, or Pi Coding Agent via background process for programmatic control. Instruction overview: Use **bash** (with optional background mode) for all coding agent work. Simple and effective.

While performing this work, the instruction cites Referenced artifact R1. Your annotation question is whether that cited artifact is materially necessary for completing this task in the provided snapshot.

Verification command observed in the pinned repository manifests: `npm run test`. Use this only as a snapshot signal of how the project checks work; do not assume other commands.

## Artifact role

Referenced artifact R1 is a repository artifact cited by the project instruction text (reference kind: path). Its literal path string is withheld and shown as [[REF]] so treatment assignment cannot be inferred from path identity. Use the citation excerpts, task brief, and snapshot context below to judge relevance and necessity.

## Path policy

Path identity for the cited artifact and for contrast-only manipulated paths is replaced by [[REF]] using semantic whole-path tokenization (not substring replacement). Other snapshot paths may appear when they do not reveal treatment assignment. Do not infer experimental treatment from path placeholders.

## Instruction citation excerpts

### Excerpt 1

```
'''

**Why workdir matters:** Agent wakes up in a focused directory, doesn't wander off reading unrelated files (like your soul.md 😅).

---

## Codex CLI

**Model:** `gpt-5.2-codex` is the default (set in ~[[REF]])

### Flags

| Flag            | Effect                                             |
| --------------- | -------------------------------------------------- |
| `exec "prompt"` | One-shot execution, exits when done                |
| `--full-auto`   | Sandboxed but auto-approves in workspace           |
| `--yolo`        | NO sandbox, NO approvals (fastest, most dangerous) |
```

## Repository tree excerpt (pinned snapshot)

```
.detect-secrets.cfg
.dockerignore
.env.example
.gitattributes
.github/workflows/ci.yml
.github/workflows/orchestrator-release.yml
.gitignore
.markdownlint-cli2.jsonc
.npmrc
[[REF]]
```

## Neighbouring paths

_None listed in the minimal context window._

## Nearby documentation paths

```
AGENTS.md
CONTRIBUTING.md
README.md
benchmarks/biomemeval/README.md
benchmarks/dream-ablation/README.md
benchmarks/longmemeval/README.md
deploy/bootnode/README.md
desktop/README.md
desktop/package.json
desktop/src-tauri/Cargo.toml
```

## Nearby configuration paths

```
.detect-secrets.cfg
.github/workflows/ci.yml
.github/workflows/orchestrator-release.yml
.oxlintrc.json
.pre-commit-config.yaml
.swiftlint.yml
Dockerfile
benchmarks/biomemeval/results/biomemeval-report.json
benchmarks/biomemeval/results/vitest-results.json
benchmarks/longmemeval/data/longmemeval_oracle.json
```

## Pinned snapshot file excerpts

### snapshot_file_1

```
---
name: coding-agent
description: Run Codex CLI, Claude Code, OpenCode, or Pi Coding Agent via background process for programmatic control.
metadata:
  {
    "bitterbot":
      { "emoji": "🧩", "requires": { "anyBins": ["claude", "codex", "opencode", "pi"] } },
  }
---

# Coding Agent (bash-first)

Use **bash** (with optional background mode) for all coding agent work. Simple and effective.

## ⚠️ PTY Mode Required!

Coding agents (Codex, Claude Code, Pi) are **interactive terminal applications** that need a pseudo-terminal (PTY) to work correctly. Without PTY, you'll get broken output, missing colors, or the agent may hang.

**Always use `pty:true`** when running coding agents:

'''bash
# ✅ Correct - with PTY
bash pty:true command:"codex exec 'Your prompt'"

# ❌ Wrong - no PTY, agent may break
bash command:"codex exec 'Your prompt'"
'''

### Bash Tool Parameters

| Parameter    | Type    | Description                                                                 |
| ------------ | ------- | --------------------------------------------------------------------------- |
| `command`    | string  | The shell command to run                                                    |
| `pty`        | boolean | **Use for coding agents!** Allocates a pseudo-terminal for interactive CLIs |
| `workdir`    | string  | Working directory (agent sees only this folder's context)                   |
| `background` | boolean | Run in background, returns sessionId for monitoring                         |
| `timeout`    | number  | Timeout in seconds (kills process on expiry)                                |
| `elevated`   | boolean | Run on host instead of sandbox (if allowed)                                 |

### Process Tool Actions (for background sessions)

| Action      | Description                                          |
| ----------- | ---------------------------------------------------- |
| `list`      | List all running/recent sessions                     |
| `poll`      | 
```

### snapshot_file_2

```
# Bitterbot — Repository Guidelines

## What is Bitterbot?

A self-hosted AI agent gateway with a biological memory system that dreams, gets curious, and evolves a personality. Bitterbot connects to your chat apps (WhatsApp, Telegram, Discord, Signal, Slack, and more) and runs AI agents that actually _remember_ — with a dream engine that consolidates knowledge while idle, a curiosity function that drives self-directed learning, a hormonal system that shapes personality in real-time, and an economic layer that lets agents transact. Agents share skills through a P2P marketplace, earn reputation, and develop persistent identities across sessions.

## What Makes Bitterbot Different

### 1. Memory System (`src/memory/`)

A consciousness-inspired memory pipeline with no equivalent in any other agent framework:

- **Knowledge Crystals**: Atomic memory units with embeddings, semantic types (fact, preference, skill, episode, insight, goal, relationship, task_pattern), importance scores, and a full lifecycle (generated → activated → consolidated → archived → expired). Skills are `frozen` (immune to decay).
- **Consolidation Pipeline**: Runs every 30 minutes — hormonal decay, Ebbinghaus importance recalculation, chunk merging (cosine ≥ 0.92), low-importance forgetting, governance TTL enforcement, stalled goal detection.
- **Session Transcript Indexing**: Conversations are automatically chunked, embedded, and made searchable. The agent can recall prior exchanges semantically.
- **Governance**: Sensitivity tagging (normal/personal/confidential), TTL enforcement, audit trails on all memory operations. Anti-catastrophic forgetting safeguards.
- **User Profile**: Automatically learned preferences (directive, world_fact, mental_model, experience types) persisted across sessions.

### 2. Dream Engine (`src/memory/dream-engine.ts`)

The agent thinks while it sleeps. Every 2 hours, the dream engine runs autonomous cycles with 7 modes:

- **Replay**: Re-process recent high-importance me
```

### snapshot_file_3

```
# Contributing to Bitterbot

Thanks for wanting to contribute! Bitterbot is an open-source project and we welcome PRs from humans and AI alike.

## Quick Start

'''bash
git clone https://github.com/Bitterbot-AI/bitterbot-desktop.git && cd bitterbot-desktop
cp .env.example .env   # Add your API keys
pnpm install && pnpm build
'''

**Runtime:** Node ≥ 22. **Package manager:** pnpm.

### Development Mode

The fastest way to get both the gateway and the Control UI running:

'''bash
pnpm dev:all
'''

This spawns the gateway and the Vite dev server in one terminal with color-tagged output. Ctrl+C stops both. The gateway auto-rebuilds on TypeScript changes.

If you prefer separate terminals (useful when debugging one process in isolation):

'''bash
# Terminal 1 — Gateway with auto-reload on TS changes
pnpm gateway:watch

# Terminal 2 — Control UI (Vite, hot reload)
cd desktop && pnpm dev
'''

Open `http://localhost:5173` for the Control UI. It connects to the gateway on port 19001 automatically.

> **Note:** `pnpm gateway:watch` auto-rebuilds on TS changes (use this for dev). `pnpm start gateway` is one-shot with no file watching (production). The orchestrator (P2P sidecar) is spawned automatically by the gateway.

**Control UI auth:** the onboarding wizard (`pnpm bitterbot onboard`) auto-generates `desktop/.env` with the gateway token. If you skipped the wizard, copy `desktop/.env.example` to `desktop/.env` and paste your token from `~/.bitterbot/bitterbot.json → gateway.auth.token`.

## Project Structure

| Directory       | What's In There                                                              |
| --------------- | ---------------------------------------------------------------------------- |
| `src/agents/`   | Agent runtime, tools, system prompt, identity, endocrine state               |
| `src/memory/`   | Memory system: dream engine, curiosity/GCCRF, crystals, hormones, governance |
| `src/gateway/`  | Gateway server, RPC methods, A2A protocol, routing        
```

### snapshot_file_4

```
<p align="center">
  <img src="docs/public/Bitterbot_logo.svg" alt="Bitterbot logo" width="72">
</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/public/bitterbot-title-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="docs/public/bitterbot-title-light.svg">
    <img src="docs/public/bitterbot-title-light.svg" alt="bitterbot" height="48">
  </picture>
</p>

<p align="center">
  <strong>A local-first personal AI with biological memory, a dream engine, and a P2P skills economy.</strong>
</p>

<p align="center">
  <a href="https://github.com/Bitterbot-AI/bitterbot-desktop/releases"><img src="https://img.shields.io/badge/version-2026.2.15--beta-7c3aed?style=flat-square" alt="Version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-a855f7?style=flat-square" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/node-%E2%89%A5%2022-c084fc?style=flat-square&logo=node.js&logoColor=white" alt="Node >= 22">
  <img src="https://img.shields.io/badge/platform-macOS%20%C2%B7%20Linux%20%C2%B7%20Windows-9333ea?style=flat-square" alt="Platform">
  <a href="https://x.com/Bitterbot_AI"><img src="https://img.shields.io/badge/@Bitterbot__AI-000000?style=flat-square&logo=x&logoColor=white" alt="X / Twitter"></a>
</p>

Most AI agents are stateless wrappers around an LLM API. Close the terminal, and they forget you exist.

**Bitterbot is different.** It's a personal AI that lives on your devices, remembers your life, and actually _does_ things, browses the web, runs code, talks to you on WhatsApp. While you sleep, it dreams: consolidating knowledge, discovering new skills, and evolving a persistent personality. It packages those learned skills and trades them with other agents on a P2P marketplace for USDC.

[About](https://about.bitterbot.ai) · [Docs](docs/) · [Getting Started](docs/start/getting-started.md)

---

## Quick Start

**Runtime: Node ≥ 22** · **Package manager: pnpm**

'''b
```

### snapshot_file_5

```
# detect-secrets exclusion patterns (regex)
#
# Note: detect-secrets does not read this file by default. If you want these
# applied, wire them into your scan command (e.g. translate to --exclude-files
# / --exclude-lines) or into a baseline's filters_used.

[exclude-files]
# pnpm lockfiles contain lots of high-entropy package integrity blobs.
pattern = (^|/)pnpm-lock\.yaml$
# Generated output and vendored assets.
pattern = (^|/)(dist|vendor)/
# Local config file with allowlist patterns.
pattern = (^|/)\.detect-secrets\.cfg$

[exclude-lines]
# Fastlane checks for private key marker; not a real key.
pattern = key_content\.include\?\("BEGIN PRIVATE KEY"\)
# UI label string for Anthropic auth mode.
pattern = case \.apiKeyEnv: "API key \(env var\)"
# CodingKeys mapping uses apiKey literal.
pattern = case apikey = "apiKey"
# Schema labels referencing password fields (not actual secrets).
pattern = "gateway\.remote\.password"
pattern = "gateway\.auth\.password"
# Schema label for talk API key (label text only).
pattern = "talk\.apiKey"
# checking for typeof is not something we care about.
pattern = === "string"
# specific optional-chaining password check that didn't match the line above.
pattern = typeof remote\?\.password === "string"

```

### snapshot_file_6

```
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build:
    name: Build & Test
    runs-on: ubuntu-latest
    timeout-minutes: 15

    strategy:
      matrix:
        node-version: [22]

    steps:
      - uses: actions/checkout@v4

      - uses: pnpm/action-setup@v4

      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: pnpm

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Type check
        run: npx tsc --noEmit

      - name: Build
        run: pnpm build

      - name: Unit tests
        run: pnpm test:fast

  lint:
    name: Lint
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - uses: pnpm/action-setup@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: pnpm

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Lint
        run: pnpm lint

      - name: Format check
        run: pnpm format:check

```

### snapshot_file_7

```
name: Orchestrator Release

# Tag-triggered build + publish of prebuilt bitterbot-orchestrator binaries
# for the 5 supported platforms. Bump orchestrator/Cargo.toml version, commit,
# and push a matching `orchestrator-v<version>` tag to run this workflow.

on:
  push:
    tags:
      - "orchestrator-v*"
  workflow_dispatch:
    inputs:
      tag:
        description: "Tag to build (e.g. orchestrator-v0.1.0). Must already exist."
        required: true
        type: string

concurrency:
  group: orchestrator-release-${{ github.ref }}
  cancel-in-progress: false

permissions:
  contents: write # required by softprops/action-gh-release to publish

jobs:
  build:
    name: Build ${{ matrix.target }}
    runs-on: ${{ matrix.os }}
    timeout-minutes: 45

    strategy:
      fail-fast: false
      matrix:
        include:
          - target: linux-x64
            os: ubuntu-latest
            rust-target: x86_64-unknown-linux-gnu
            bin: bitterbot-orchestrator
            asset: bitterbot-orchestrator-linux-x64
          - target: linux-arm64
            os: ubuntu-22.04-arm
            rust-target: aarch64-unknown-linux-gnu
            bin: bitterbot-orchestrator
            asset: bitterbot-orchestrator-linux-arm64
          - target: darwin-x64
            os: macos-14
            rust-target: x86_64-apple-darwin
            bin: bitterbot-orchestrator
            asset: bitterbot-orchestrator-darwin-x64
          - target: darwin-arm64
            os: macos-14
            rust-target: aarch64-apple-darwin
            bin: bitterbot-orchestrator
            asset: bitterbot-orchestrator-darwin-arm64
          - target: win32-x64
            os: windows-latest
            rust-target: x86_64-pc-windows-msvc
            bin: bitterbot-orchestrator.exe
            asset: bitterbot-orchestrator-win32-x64.exe

    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ inputs.tag || github.ref }}

      - name: Install Rust toolchain
        uses
```
