# Annotation packet `b6f1d2c6e3328de2`

Protocol: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`
Packet spec: `rq5_v1_blind_packet_spec_v2`

Judge only with the materials below. Do not seek external repositories or experimental results.

## Annotator question

Is Referenced artifact R1 materially necessary for completing THIS software engineering task in THIS repository snapshot?

## Anonymous snapshot

- Snapshot ID: `73cd71803e2ed400`
- Reference type: `path`
- Artifact alias: **Referenced artifact R1**

## Task brief

Engineering task (derived only from the pinned instruction text and snapshot signals):

Document title: [[INSTRUCTION]] — difyctl (TypeScript CLI). Instruction overview: TypeScript port of difyctl. Stack: custom CLI framework (`src/framework/`), Node 22+, ESM, ky for HTTP, vitest, eslint via @antfu/eslint-config.

While performing this work, the instruction cites Referenced artifact R1. Your annotation question is whether that cited artifact is materially necessary for completing this task in the provided snapshot.

Verification command observed in the pinned repository manifests: `npm run lint`. Use this only as a snapshot signal of how the project checks work; do not assume other commands.

## Artifact role

Referenced artifact R1 is a repository artifact cited by the project instruction text (reference kind: path). Its literal path string is withheld and shown as [[REF]] so treatment assignment cannot be inferred from path identity. Use the citation excerpts, task brief, and snapshot context below to judge relevance and necessity.

## Path policy

Path identity for the cited artifact and for contrast-only manipulated paths is replaced by [[REF]] using semantic whole-path tokenization (not substring replacement). Other snapshot paths may appear when they do not reveal treatment assignment. Do not infer experimental treatment from path placeholders.

## Instruction citation excerpts

### Excerpt 1

```
| --------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| commands  | `src/commands/`                  | Command class shells (extend `DifyCommand`). Only place framework imports run.                                                        |
| domain    | `src/run/`, `src/get/`, etc.     | Plain TS modules. Take typed deps via options. Testable without the framework.                                                        |
| api       | `src/api/`                       | One typed client per resource. Each takes `KyInstance`.                                                                               |
| http      | `src/http/`                      | `createClient` + middleware (auth, retry, logging, error mapping). Only place ky runs.                                                |
| io        | `src/io/`                        | Streams + spinner. Fence between data-out and progress UI.                                                                            |
| printers  | `src/printers/`                  | `CompositePrintFlags` + `-o {json,yaml,name,wide,text}` matrix.                                                                       |
| errors    | `src/errors/`                    | `BaseError`, `ErrorCode` enum, `ExitCode` enum, dispatch table, `formatErrorForCli`.                                                  |
| guide     | `[[REF]]` | Per-command agent guide string. Export `agentGuide`, assign `static agentGuide = agentGuide` in command class. Surfaced via `--help`. |
| cache     | `src/cache/`                     | On-disk caches (app-info, etc.).                                                      
```

## Repository tree excerpt (pinned snapshot)

```
.agents/skills/backend-code-review/SKILL.md
.agents/skills/backend-code-review/references/architecture-rule.md
.agents/skills/backend-code-review/references/db-schema-rule.md
.agents/skills/backend-code-review/references/repositories-rule.md
.agents/skills/backend-code-review/references/sqlalchemy-rule.md
.agents/skills/component-refactoring/SKILL.md
.agents/skills/component-refactoring/references/complexity-patterns.md
.agents/skills/component-refactoring/references/component-splitting.md
.agents/skills/component-refactoring/references/hook-extraction.md
.agents/skills/e2e-cucumber-playwright/SKILL.md
.agents/skills/e2e-cucumber-playwright/agents/openai.yaml
.agents/skills/e2e-cucumber-playwright/references/cucumber-best-practices.md
.agents/skills/e2e-cucumber-playwright/references/playwright-best-practices.md
.agents/skills/frontend-code-review/SKILL.md
.agents/skills/frontend-code-review/references/business-logic.md
.agents/skills/frontend-code-review/references/code-quality.md
.agents/skills/frontend-code-review/references/performance.md
.agents/skills/frontend-testing/SKILL.md
.agents/skills/frontend-testing/assets/component-test.template.tsx
.agents/skills/frontend-testing/assets/hook-test.template.ts
.agents/skills/frontend-testing/assets/utility-test.template.ts
.agents/skills/frontend-testing/references/async-testing.md
.agents/skills/frontend-testing/references/checklist.md
.agents/skills/frontend-testing/references/common-patterns.md
.agents/skills/frontend-testing/references/domain-components.md
.agents/skills/frontend-testing/references/mocking.md
.agents/skills/frontend-testing/references/workflow.md
.agents/skills/how-to-write-component/SKILL.md
.claude/settings.json
.claude/skills/backend-code-review
.claude/skills/component-refactoring
.claude/skills/e2e-cucumber-playwright
.claude/skills/frontend-code-review
.claude/skills/frontend-query-mutation
.claude/skills/frontend-testing
.codex
.coveragerc
.devcontainer/Dockerfile
.devcontainer/README.md
.devcontainer/devcontainer.json
.devcontainer/noop.txt
.devcontainer/post_create_command.sh
.devcontainer/post_start_command.sh
.devcontainer/troubleshooting.png
.dockerignore
.editorconfig
.gemini/config.yaml
cli/.gitignore
[[REF]]
cli/ARD.md
cli/README.md
cli/package.json
cli/tsconfig.json
cli/vite.config.ts
```

## Neighbouring paths

```
cli/.gitignore
cli/ARD.md
cli/README.md
cli/package.json
cli/tsconfig.json
cli/vite.config.ts
```

## Nearby documentation paths

```
.devcontainer/README.md
.vscode/README.md
[[INSTRUCTION]]
CLAUDE.md
CONTRIBUTING.md
Makefile
README.md
api/[[INSTRUCTION]]
api/README.md
api/enterprise/telemetry/README.md
```

## Nearby configuration paths

```
.agents/skills/e2e-cucumber-playwright/agents/openai.yaml
.claude/settings.json
.devcontainer/Dockerfile
.devcontainer/devcontainer.json
.gemini/config.yaml
.github/DISCUSSION_TEMPLATE/general.yml
.github/DISCUSSION_TEMPLATE/help.yml
.github/DISCUSSION_TEMPLATE/suggestion.yml
.github/ISSUE_TEMPLATE/bug_report.yml
.github/ISSUE_TEMPLATE/config.yml
```

## Pinned snapshot file excerpts

### snapshot_file_1

```
# [[INSTRUCTION]] — difyctl (TypeScript CLI)

TypeScript port of difyctl. Stack: custom CLI framework (`src/framework/`), Node 22+, ESM, ky for HTTP, vitest, eslint via @antfu/eslint-config.

> Architecture patterns, scaffolding recipe, printer chain, strategy pattern, testing conventions, anti-patterns: see **[`ARD.md`]**.

## Code rules

- **Spaces, not tabs.**
- **Minimum comments.** Code speak for self. Comment only non-obvious WHY — hidden constraints, subtle invariants, bug-workaround notes. Never restate code. Never reference tasks, PRs, current callers.
- **No magic strings or numbers.** Enums or named constants for bounded value sets.
- **No long positional arg lists.** Use options objects.
- **No long if/switch ladders on discriminator.** Polymorphism, dispatch tables, or strategy pattern. Name concept, let implementations plug in.
- **No `any`. No `unknown` outside genuine wire boundaries** (HTTP body parse, env vars). Narrow types everywhere else.
- **Avoid `!` non-null assertions.** Narrow instead.
- **`readonly` on inputs not mutated.**
- **Discriminated unions** for variant data (SSE events, run outputs, error shapes), not optional-field bags.
- **No backwards-compat shims.** No re-exports of old names, no `// removed:` markers, no deprecation notes. Delete, update callers.
- **No new dependencies without explicit approval.**
- **No CLI behavior changes in refactor commit.** Same flags, same output, same exit codes.
- **Every leaf command extends `DifyCommand`.** Add `static agentGuide` string when command benefits from agent workflow docs — see `src/commands/[[INSTRUCTION]]`.

## Layering

| Layer     | Path                             | Role                                                                                                                                  |
| --------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| command
```

### snapshot_file_2

```
dist/
coverage/
node_modules/
*.tsbuildinfo
.vitest-cache/
docs/specs/
context/
```

### snapshot_file_3

```
# ARD — Architecture & Design Reference

Onboarding ref for `dify/cli/` contributors. Cover canonical patterns, layer contracts, scaffolding recipe, dev workflow, anti-patterns. Read before adding command or touching shared infra.

Spec authority: [`docs/specs/`]. Specs own HTTP wire shape + server behavior; this file owns CLI code structure.

---

## Project layout

'''
src/
  commands/          one folder per command leaf
  api/               HTTP client wrappers (one file per resource)
  auth/              hosts.yml read/write
  cache/             app-info cache
  config/            config.yml read/write
  errors/            BaseError, ErrorCode, exit codes
  http/              ky client factory + middleware
  io/                IOStreams, spinner, printer chain
  limit/             --limit flag parsing
  types/             shared TypeScript types
  util/              small pure helpers
  workspace/         workspace ID resolution
'''

---

## New command scaffold

Recipe for adding command leaf. Follow order.

**1. Create folder**

'''
src/commands/<topic>/<verb>/
'''

Examples: `get/app/`, `auth/devices/revoke/`, `describe/app/`.

**2. Mandatory files**

| File       | Responsibility                                                                          |
| ---------- | --------------------------------------------------------------------------------------- |
| `index.ts` | `DifyCommand` subclass. Flag/arg declaration + `run()` wiring only. No business logic.  |
| `run.ts`   | Pure async function. Typed options + deps. Returns string. No `src/framework/` imports. |

**3. Optional files — add as needed**

| File               | Purpose                                             |
| ------------------ | --------------------------------------------------- |
| `handlers.ts`      | Output format handlers (text, table, etc.)          |
| `print-flags.ts`   | `--output` flag → printer resolution                |
| `payload-shape.ts` | Response type narrowing/transfo
```

### snapshot_file_4

```
# difyctl

CLI client for [Dify] platform. Browser device-flow signin, list/inspect apps, run with structured input, parse output as JSON, YAML, or human text.

## Install

Builds are standalone binaries (Bun-compiled) published as **GitHub Actions workflow artifacts** — no npm, no GitHub Release assets. The installer fetches the latest successful `cli-release.yml` run on `main`, verifies sha256, and copies the binary into `$HOME/.local/bin/difyctl`.

'''sh
# GH_TOKEN with `actions:read` scope is required — workflow artifact downloads
# need auth even on public repos.
export GH_TOKEN=<your-pat>
curl -fsSL https://raw.githubusercontent.com/langgenius/dify/main/cli/scripts/install-cli.sh | sh
'''

| Env              | Default           | Purpose                                               |
| ---------------- | ----------------- | ----------------------------------------------------- |
| `GH_TOKEN`       | —                 | GitHub PAT (or `GITHUB_TOKEN`) with `actions:read`.   |
| `DIFYCTL_PREFIX` | `$HOME/.local`    | Install root. Binary lands at `<prefix>/bin/difyctl`. |
| `DIFYCTL_REPO`   | `langgenius/dify` | Source repo.                                          |
| `DIFYCTL_BRANCH` | `main`            | Branch to pick the latest successful run from.        |

Supported targets: `darwin-arm64`, `darwin-x64`, `linux-arm64`, `linux-x64`, `windows-x64.exe`. The shell installer covers Linux + macOS; Windows users can download the `.exe` directly from the same artifact.

## Quickstart

'''sh
difyctl auth login                                       # opens browser; paste the device code shown
difyctl get app                                          # list apps in default workspace
difyctl describe app <app-id>                            # inspect parameters
difyctl run app <app-id> "hello"                         # run, blocking
difyctl run app <app-id> "hello" -o json | jq .answer    # JSON output
difyctl run app <app-id> --input name=world --input topic=cats   # 
```

### snapshot_file_5

```
{
  "name": "@langgenius/difyctl",
  "type": "module",
  "version": "0.1.0-rc.1",
  "description": "Dify command-line interface",
  "difyctl": {
    "channel": "rc",
    "compat": {
      "minDify": "1.14.0",
      "maxDify": "1.15.0"
    }
  },
  "license": "Apache-2.0",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.js"
    }
  },
  "files": [
    "README.md",
    "bin",
    "dist"
  ],
  "engines": {
    "node": "^22.22.1"
  },
  "scripts": {
    "build": "vp pack",
    "dev": "bun bin/dev.js",
    "test": "vp test",
    "test:coverage": "vp test --coverage",
    "lint": "eslint",
    "lint:fix": "eslint --fix",
    "type-check": "tsc",
    "tree:gen": "bun scripts/generate-command-tree.ts",
    "tree:check": "bun scripts/generate-command-tree.ts --check",
    "prebuild": "pnpm tree:gen",
    "predev": "pnpm tree:gen",
    "pretest": "pnpm tree:gen",
    "ci": "pnpm tree:check && pnpm type-check && pnpm lint && pnpm test:coverage && pnpm build",
    "clean": "rm -rf dist node_modules/.cache",
    "version:info": "bun scripts/print-buildinfo.ts",
    "build:bin": "scripts/release-build.sh"
  },
  "dependencies": {
    "@dify/contracts": "workspace:*",
    "@napi-rs/keyring": "catalog:",
    "cli-table3": "catalog:",
    "eventsource-parser": "catalog:",
    "js-yaml": "catalog:",
    "ky": "catalog:",
    "lockfile": "catalog:",
    "open": "catalog:",
    "ora": "catalog:",
    "picocolors": "catalog:",
    "std-semver": "catalog:",
    "zod": "catalog:"
  },
  "devDependencies": {
    "@dify/tsconfig": "workspace:*",
    "@hono/node-server": "catalog:",
    "@types/js-yaml": "catalog:",
    "@types/lockfile": "catalog:",
    "@types/node": "catalog:",
    "@vitest/coverage-v8": "catalog:",
    "eslint": "catalog:",
    "hono": "catalog:",
    "typescript": "catalog:",
    "vite": "catalog:",
    "vite-plus": "catalog:",
    "vitest": "catalog:"
  }
}

```

### snapshot_file_6

```
{
  "extends": "@dify/tsconfig/node.json",
  "compilerOptions": {
    "rootDir": "src",
    "paths": {
      "@/*": [
        "./*"
      ],
      "~@/*": [
        "./*"
      ]
    },
    "types": ["node"],
    "declaration": true,
    "declarationMap": true,
    "noEmit": false,
    "outDir": "dist",
    "sourceMap": true
  },
  "include": ["src/**/*.ts"],
  "exclude": ["node_modules", "**/*.test.ts"]
}

```

### snapshot_file_7

```
# Development with devcontainer

This project includes a devcontainer configuration that allows you to open the project in a container with a fully configured development environment.
Both frontend and backend environments are initialized when the container is started.

## GitHub Codespaces

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/langgenius/dify)

you can simply click the button above to open this project in GitHub Codespaces.

For more info, check out the [GitHub documentation](https://docs.github.com/en/free-pro-team@latest/github/developing-online-with-codespaces/creating-a-codespace#creating-a-codespace).

## VS Code Dev Containers

[![Open in Dev Containers](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=[repository])

if you have VS Code installed, you can click the button above to open this project in VS Code Dev Containers.

You can learn more in the [Dev Containers documentation](https://code.visualstudio.com/docs/devcontainers/containers).

## Pros of Devcontainer

Unified Development Environment: By using devcontainers, you can ensure that all developers are developing in the same environment, reducing the occurrence of "it works on my machine" type of issues.

Quick Start: New developers can set up their development environment in a few simple steps, without spending a lot of time on environment configuration.

Isolation: Devcontainers isolate your project from your host operating system, reducing the chance of OS updates or other application installations impacting the development environment.

## Cons of Devcontainer

Learning Curve: For developers unfamiliar with Docker and VS Code, using devcontainers may be somewhat complex.

Performance Impact: While usually minimal, programs running inside a devcontainer may be slightly sl
```

### snapshot_file_8

```
# Debugging with VS Code

This `launch.json.template` file provides various debug configurations for the Dify project within VS Code / Cursor. To use these configurations, you should copy the contents of this file into a new file named `launch.json` in the same `.vscode` directory.

## How to Use

1. **Create `launch.json`**: If you don't have one, create a file named `launch.json` inside the `.vscode` directory.
1. **Copy Content**: Copy the entire content from `launch.json.template` into your newly created `launch.json` file.
1. **Select Debug Configuration**: Go to the Run and Debug view in VS Code / Cursor (Ctrl+Shift+D or Cmd+Shift+D).
1. **Start Debugging**: Select the desired configuration from the dropdown menu and click the green play button.

## Tips

- If you need to debug with Edge browser instead of Chrome, modify the `serverReadyAction` configuration in the "Next.js: debug full stack" section, change `"debugWithChrome"` to `"debugWithEdge"` to use Microsoft Edge for debugging.

```

### snapshot_file_9

```
# [[INSTRUCTION]]

## Project Overview

Dify is an open-source platform for developing LLM applications with an intuitive interface combining agentic AI workflows, RAG pipelines, agent capabilities, and model management.

The codebase is split into:

- **Backend API** (`/api`): Python Flask application organized with Domain-Driven Design
- **Frontend Web** (`/web`): Next.js application using TypeScript and React
- **Docker deployment** (`/docker`): Containerized deployment configurations
- **Dify Agent Backend** (`/dify-agent`): Backend services for managing and executing agent

## Backend Workflow

- Read `api/[[INSTRUCTION]]` for details
- Run backend CLI commands through `uv run --project api <command>`.
- Integration tests are CI-only and are not expected to run in the local environment.

## Frontend Workflow

- Read `web/[[INSTRUCTION]]` for details

## Testing & Quality Practices

- Follow TDD: red → green → refactor.
- Use `pytest` for backend tests with Arrange-Act-Assert structure.
- Enforce strong typing; avoid `Any` and prefer explicit type annotations.
- Write self-documenting code; only add comments that explain intent.

## Language Style

- **Python**: Keep type hints on functions and attributes, and implement relevant special methods (e.g., `__repr__`, `__str__`). Prefer `TypedDict` over `dict` or `Mapping` for type safety and better code documentation.
- **TypeScript**: Use the strict config, rely on ESLint (`pnpm lint:fix` preferred) plus `pnpm type-check`, and avoid `any` types.

## General Practices

- Prefer editing existing files; add new documentation only when requested.
- Inject dependencies through constructors and preserve clean architecture boundaries.
- Handle errors with domain-specific exceptions at the correct layer.

## Project Conventions

- Backend architecture adheres to DDD and Clean Architecture principles.
- Async work runs through Celery with Redis as the broker.
- Frontend user-facing strings must use `web/i18n/en-US/`; avoid hardcoded text.

```

### snapshot_file_10

```
interface:
  display_name: "E2E Cucumber + Playwright"
  short_description: "Write and review Dify E2E scenarios."
  default_prompt: "Use $e2e-cucumber-playwright to write or review a Dify E2E scenario under e2e/."

```
