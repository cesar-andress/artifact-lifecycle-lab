# Annotation packet `3700df2d7790d1ff`

Protocol: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`
Packet spec: `rq5_v1_blind_packet_spec_v2`

Judge only with the materials below. Do not seek external repositories or experimental results.

## Annotator question

Is Referenced artifact R1 materially necessary for completing THIS software engineering task in THIS repository snapshot?

## Anonymous snapshot

- Snapshot ID: `16ebbcd434a230b1`
- Reference type: `path`
- Artifact alias: **Referenced artifact R1**

## Task brief

Engineering task (derived only from the pinned instruction text and snapshot signals):

Document title: E2E. Instruction overview: This package contains the repository-level end-to-end tests for Dify. Key instruction points: - backend API started from source - frontend served from the production artifact - middleware services started from Docker - if `web/.next/BUILD_ID` exists, E2E reuses the existing build by default - if you set `E2E_FORCE_WEB_BUILD=1`, E2E rebuilds the frontend before starting it - `scripts/setup.ts` is the single environment entrypoint for reset, middleware, backend, and frontend startup - `run-cucumber.ts` orchestrates the E2E run and Cucumber invocation - `support/web-server.ts` manages frontend reuse, startup, readiness, and shutdown

While performing this work, the instruction cites Referenced artifact R1. Your annotation question is whether that cited artifact is materially necessary for completing this task in the provided snapshot.

Verification command observed in the pinned repository manifests: `make test`. Use this only as a snapshot signal of how the project checks work; do not assume other commands.

## Artifact role

Referenced artifact R1 is a repository artifact cited by the project instruction text (reference kind: path). Its literal path string is withheld and shown as [[REF]] so treatment assignment cannot be inferred from path identity. Use the citation excerpts, task brief, and snapshot context below to judge relevance and necessity.

## Path policy

Path identity for the cited artifact and for contrast-only manipulated paths is replaced by [[REF]] using semantic whole-path tokenization (not substring replacement). Other snapshot paths may appear when they do not reveal treatment assignment. Do not infer experimental treatment from path placeholders.

## Instruction citation excerpts

### Excerpt 1

```
pnpm e2e:middleware:down
'''

Artifacts and diagnostics:

- `cucumber-report/report.html`: HTML report
- `cucumber-report/report.json`: JSON report
- `cucumber-report/artifacts/`: failure screenshots and HTML captures
- `[[REF]]`: backend startup log
- `.logs/cucumber-web.log`: frontend startup log

Open the HTML report locally with:

'''bash
open cucumber-report/report.html
'''
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
.agents/skills/frontend-code-review/SKILL.md
.agents/skills/frontend-code-review/references/business-logic.md
.agents/skills/frontend-code-review/references/code-quality.md
.agents/skills/frontend-code-review/references/performance.md
.agents/skills/frontend-query-mutation/SKILL.md
.agents/skills/frontend-query-mutation/agents/openai.yaml
.agents/skills/frontend-query-mutation/references/contract-patterns.md
.agents/skills/frontend-query-mutation/references/runtime-rules.md
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
.claude/settings.json
.claude/skills/backend-code-review
.claude/skills/component-refactoring
.claude/skills/frontend-code-review
.claude/skills/frontend-query-mutation
.claude/skills/frontend-testing
.coveragerc
.devcontainer/Dockerfile
.devcontainer/README.md
.devcontainer/devcontainer.json
.devcontainer/noop.txt
.devcontainer/post_create_command.sh
.devcontainer/post_start_command.sh
.devcontainer/troubleshooting.png
.editorconfig
.gemini/config.yaml
.gitattributes
.github/CODEOWNERS
.github/CODE_OF_CONDUCT.md
.github/DISCUSSION_TEMPLATE/general.yml
.github/DISCUSSION_TEMPLATE/help.yml
.github/DISCUSSION_TEMPLATE/suggestion.yml
.github/ISSUE_TEMPLATE/bug_report.yml
.github/ISSUE_TEMPLATE/config.yml
.github/ISSUE_TEMPLATE/feature_request.yml
.github/ISSUE_TEMPLATE/refactor.yml
.github/actions/setup-web/action.yml
.github/dependabot.yml
.github/labeler.yml
.github/linters/.hadolint.yaml
.github/linters/.isort.cfg
.github/linters/.yaml-lint.yml
.github/linters/editorconfig-checker.json
```

## Neighbouring paths

```
e2e/.gitignore
e2e/README.md
e2e/cucumber.config.ts
e2e/package.json
e2e/test-env.ts
e2e/tsconfig.json
e2e/vite.config.ts
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
api/core/rag/datasource/vdb/clickzetta/README.md
```

## Nearby configuration paths

```
.agents/skills/frontend-query-mutation/agents/openai.yaml
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
# E2E

This package contains the repository-level end-to-end tests for Dify.

This file is the canonical package guide for `e2e/`. Keep detailed workflow, architecture, debugging, and reporting documentation here. Keep `README.md` as a minimal pointer to this file so the two documents do not drift.

The suite uses Cucumber for scenario definitions and Playwright as the browser execution layer.

It tests:

- backend API started from source
- frontend served from the production artifact
- middleware services started from Docker

## Prerequisites

- Node.js `^22.22.1`
- `pnpm`
- `uv`
- Docker

Run the following commands from the repository root.

Install Playwright browsers once:

'''bash
pnpm install
pnpm -C e2e e2e:install
pnpm -C e2e check
'''

`pnpm install` is resolved through the repository workspace and uses the shared root lockfile plus `pnpm-workspace.yaml`.

Use `pnpm check` as the default local verification step after editing E2E TypeScript, Cucumber support code, or feature glue. It runs formatting, linting, and type checks for this package.

Common commands:

'''bash
# authenticated-only regression (default excludes @fresh)
# expects backend API, frontend artifact, and middleware stack to already be running
pnpm -C e2e e2e

# full reset + fresh install + authenticated scenarios
# starts required middleware/dependencies for you
pnpm -C e2e e2e:full

# run a tagged subset
pnpm -C e2e e2e -- --tags @smoke

# headed browser
pnpm -C e2e e2e:headed -- --tags @smoke

# slow down browser actions for local debugging
E2E_SLOW_MO=500 pnpm -C e2e e2e:headed -- --tags @smoke
'''

Frontend artifact behavior:

- if `web/.next/BUILD_ID` exists, E2E reuses the existing build by default
- if you set `E2E_FORCE_WEB_BUILD=1`, E2E rebuilds the frontend before starting it

## Lifecycle

'''mermaid
flowchart TD
  A["Start E2E run"] --> B["run-cucumber.ts orchestrates setup/API/frontend"]
  B --> C["support/web-server.ts starts or reuses frontend directly"]
  C --> D["Cucumber lo
```

### snapshot_file_2

```
node_modules/
.auth/
playwright-report/
test-results/
cucumber-report/
.logs/

```

### snapshot_file_3

```
# E2E

Canonical documentation for this package lives in [[[INSTRUCTION]]](./[[INSTRUCTION]]).

```

### snapshot_file_4

```
import type { IConfiguration } from '@cucumber/cucumber'

const config = {
  format: [
    'progress-bar',
    'summary',
    'html:./cucumber-report/report.html',
    'json:./cucumber-report/report.json',
  ],
  import: ['features/**/*.ts'],
  parallel: 1,
  paths: ['features/**/*.feature'],
  tags: process.env.E2E_CUCUMBER_TAGS || 'not @fresh and not @skip',
  timeout: 60_000,
} satisfies Partial<IConfiguration> & {
  timeout: number
}

export default config

```

### snapshot_file_5

```
{
  "name": "dify-e2e",
  "private": true,
  "type": "module",
  "scripts": {
    "check": "vp check --fix",
    "e2e": "tsx ./scripts/run-cucumber.ts",
    "e2e:full": "tsx ./scripts/run-cucumber.ts --full",
    "e2e:full:headed": "tsx ./scripts/run-cucumber.ts --full --headed",
    "e2e:headed": "tsx ./scripts/run-cucumber.ts --headed",
    "e2e:install": "playwright install --with-deps chromium",
    "e2e:middleware:down": "tsx ./scripts/setup.ts middleware-down",
    "e2e:middleware:up": "tsx ./scripts/setup.ts middleware-up",
    "e2e:reset": "tsx ./scripts/setup.ts reset"
  },
  "devDependencies": {
    "@cucumber/cucumber": "catalog:",
    "@playwright/test": "catalog:",
    "@types/node": "catalog:",
    "tsx": "catalog:",
    "typescript": "catalog:",
    "vite-plus": "catalog:"
  }
}

```

### snapshot_file_6

```
export const defaultBaseURL = 'http://127.0.0.1:3000'
export const defaultApiURL = 'http://127.0.0.1:5001'
export const defaultLocale = 'en-US'

export const baseURL = process.env.E2E_BASE_URL || defaultBaseURL
export const apiURL = process.env.E2E_API_URL || defaultApiURL

export const cucumberHeadless = process.env.CUCUMBER_HEADLESS !== '0'
export const cucumberSlowMo = Number(process.env.E2E_SLOW_MO || 0)
export const reuseExistingWebServer = process.env.E2E_REUSE_WEB_SERVER
  ? process.env.E2E_REUSE_WEB_SERVER !== '0'
  : !process.env.CI

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
- **TypeScript**: Use the strict config, rely on ESLint (`pnpm lint:fix` preferred) plus `pnpm type-check:tsgo`, and avoid `any` types.

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
  display_name: "Frontend Query & Mutation"
  short_description: "Dify TanStack Query and oRPC patterns"
  default_prompt: "Use this skill when implementing or reviewing Dify frontend contracts, query and mutation call sites, conditional queries, invalidation, or legacy query/mutation migrations."

```
