# Annotation packet `8222c534ec20c9c2`

Protocol: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`
Packet spec: `rq5_v1_blind_packet_spec_v2`

Judge only with the materials below. Do not seek external repositories or experimental results.

## Annotator question

Is Referenced artifact R1 materially necessary for completing THIS software engineering task in THIS repository snapshot?

## Anonymous snapshot

- Snapshot ID: `73cc5feb8bfb0384`
- Reference type: `path`
- Artifact alias: **Referenced artifact R1**

## Task brief

Engineering task (derived only from the pinned instruction text and snapshot signals):

Document title: CopilotKit Debugging Skill. Skill/module name: copilotkit-debug. Stated purpose: "Use when diagnosing CopilotKit issues -- runtime connectivity failures, agent not responding, streaming errors, tool execution problems, transcription failures, version mismatches, and AG-UI event tracing." When To Use: Invoke this skill when: - The CopilotKit runtime is unreachable or returning errors - Agents fail to connect, respond, or stream events - Frontend tools are not executing or returning results - Transcription (voice) is failing - Version mismatch errors appear between packages - AG-UI SSE events are malformed or missing - CORS errors block browser requests to the runtime Instruction overview: 1. **Package versions** -- Run `npm ls @copilotkit/runtime @copilotkit/react @copilotkit/core @ag-ui/client` (or the v1 equivalents). Version mismatches between runtime and react packages are a common root cause. 2. **Runtime mode** -- Is this SSE mode (`CopilotSseRuntime`) or Intelligence mode (`CopilotIntelligenceRuntime`)? Check the runtime constructor. 3. **Transport configuration** -- What is `runtimeUrl` set to in `CopilotKitProvider`? Does it match the `basePath` in `createCopilotEndpoint`? 4. **Agent type** -- Is the agent a `BuiltInAgent`, `LangGraphAgent`, `A2AAgent`, or custom `AbstractAgent`? 5. **Error messages** -- Collect the exact error from browser console and server logs. C

While performing this work, the instruction cites Referenced artifact R1. Your annotation question is whether that cited artifact is materially necessary for completing this task in the provided snapshot.

Verification command observed in the pinned repository manifests: `npm run test`. Use this only as a snapshot signal of how the project checks work; do not assume other commands.

## Artifact role

Referenced artifact R1 is a repository artifact cited by the project instruction text (reference kind: path). Its literal path string is withheld and shown as [[REF]] so treatment assignment cannot be inferred from path identity. Use the citation excerpts, task brief, and snapshot context below to judge relevance and necessity.

## Path policy

Path identity for the cited artifact and for contrast-only manipulated paths is replaced by [[REF]] using semantic whole-path tokenization (not substring replacement). Other snapshot paths may appear when they do not reveal treatment assignment. Do not infer experimental treatment from path placeholders.

## Instruction citation excerpts

### Excerpt 1

```
## Using mcp-docs for Live Documentation Lookups

During debugging, use the `copilotkit-docs` MCP server to look up the latest CopilotKit documentation. This server provides two tools: `search-docs` (search documentation) and `search-code` (search source code examples).

### MCP Setup

**Claude Code:** The MCP server is auto-configured by the plugin's `.mcp.json` -- no manual setup needed. The agent can call the `search-docs` and `search-code` tools from the `copilotkit-docs` server directly.

**Codex:** Add the following to your `[[REF]]`:

'''toml
[mcp_servers.copilotkit-docs]
type = "http"
url = "https://mcp.copilotkit.ai/mcp"
'''

### Tool Usage
```

## Repository tree excerpt (pinned snapshot)

```
.agents/skills/showcase-demo-debugging/[[INSTRUCTION]]
.agents/skills/showcase-demo-debugging/agents/openai.yaml
.changeset/bump-license-verifier-ent-251.md
.changeset/debug-mode.md
.changeset/empty-mails-applaud.md
.changeset/ent-314-thread-connect-ux.md
.changeset/five-avocados-visit.md
.changeset/fix-thread-switch-state-reset.md
.changeset/little-pears-tell.md
.claude-plugin/marketplace.json
.claude-plugin/plugin.json
.claude/docs/architecture.md
.claude/docs/git.md
.claude/docs/hooks.md
.claude/docs/workflow.md
.claude/skills/copilotkit-demo-parity/[[INSTRUCTION]]
.claude/skills/git-hooks/[[INSTRUCTION]]
.claude/skills/showcase-demo-debugging/[[INSTRUCTION]]
.claude/skills/showcase-demo-debugging/agents/openai.yaml
.cursor/rules/agent-development.mdc
.cursor/rules/copilotkit-architecture.mdc
.cursor/rules/development-workflow.mdc
.cursor/rules/examples-and-demos.mdc
.cursor/rules/frontend-development.mdc
.cursor/rules/quick-reference.mdc
.cursor/rules/suggestions-development.mdc
.cursor/rules/working-with-rules.mdc
.dockerignore
.gitattributes
.github/CODEOWNERS
.github/ISSUE_TEMPLATE/1-bug-report.yml
.github/ISSUE_TEMPLATE/2-feature-request.yml
.github/ISSUE_TEMPLATE/3-documentation.yml
.github/ISSUE_TEMPLATE/config.yml
.github/ISSUE_TEMPLATE/issue_template.md
.github/PULL_REQUEST_TEMPLATE.md
.github/config-allowlist.txt
.github/dependabot.yml
.github/scripts/check-config-allowlist.sh
.github/workflows/auto_merge_showcases.yml
.github/workflows/cleanup_pr-caches.yml
.github/workflows/dependabot-auto-merge.yml
.github/workflows/dependabot-major-analysis.yml
.github/workflows/ghcr_unlinked_packages.yml
.github/workflows/integrations_parity.yml
.github/workflows/plugin-skills-check.yml
.github/workflows/prerelease.yml
.github/workflows/publish-commit.yml
.github/workflows/publish-release.yml
.github/workflows/security_fork-pr-alert.yml
.github/workflows/security_zizmor.yml
.github/workflows/showcase_build.yml
.github/workflows/showcase_build_check.yml
.github/workflows/showcase_capture-previews.yml
.github/workflows/showcase_deploy.yml
.github/workflows/showcase_docs-sync.yml
.github/workflows/showcase_eval-webhook_build.yml
.github/workflows/showcase_eval.yml
.github/workflows/showcase_eval_check.yml
.github/workflows/showcase_keep-alive.yml
```

## Neighbouring paths

```
skills/copilotkit-debug/sources.md
```

## Nearby documentation paths

```
AGENTS.md
CLAUDE.md
CONTRIBUTING.md
README.md
community/content/CONTRIBUTING.md
community/content/README.md
docs/README.md
docs/components/content/landing-pages/README.md
docs/package.json
examples/README.md
```

## Nearby configuration paths

```
.agents/skills/showcase-demo-debugging/agents/openai.yaml
.claude-plugin/marketplace.json
.claude-plugin/plugin.json
.claude/skills/showcase-demo-debugging/agents/openai.yaml
.github/ISSUE_TEMPLATE/1-bug-report.yml
.github/ISSUE_TEMPLATE/2-feature-request.yml
.github/ISSUE_TEMPLATE/3-documentation.yml
.github/ISSUE_TEMPLATE/config.yml
.github/dependabot.yml
.github/workflows/auto_merge_showcases.yml
```

## Pinned snapshot file excerpts

### snapshot_file_1

```
---
name: copilotkit-debug
description: "Use when diagnosing CopilotKit issues -- runtime connectivity failures, agent not responding, streaming errors, tool execution problems, transcription failures, version mismatches, and AG-UI event tracing."
version: 1.0.0
---

# CopilotKit Debugging Skill

## When to Use

Invoke this skill when:

- The CopilotKit runtime is unreachable or returning errors
- Agents fail to connect, respond, or stream events
- Frontend tools are not executing or returning results
- Transcription (voice) is failing
- Version mismatch errors appear between packages
- AG-UI SSE events are malformed or missing
- CORS errors block browser requests to the runtime

## Diagnostic Workflow

### Step 1: Gather Information

Before proposing any fix, collect:

1. **Package versions** -- Run `npm ls @copilotkit/runtime @copilotkit/react @copilotkit/core @ag-ui/client` (or the v1 equivalents). Version mismatches between runtime and react packages are a common root cause.
2. **Runtime mode** -- Is this SSE mode (`CopilotSseRuntime`) or Intelligence mode (`CopilotIntelligenceRuntime`)? Check the runtime constructor.
3. **Transport configuration** -- What is `runtimeUrl` set to in `CopilotKitProvider`? Does it match the `basePath` in `createCopilotEndpoint`?
4. **Agent type** -- Is the agent a `BuiltInAgent`, `LangGraphAgent`, `A2AAgent`, or custom `AbstractAgent`?
5. **Error messages** -- Collect the exact error from browser console and server logs. CopilotKit uses structured error codes (see `references/error-patterns.md`).
6. **Browser network tab** -- Check the `/info` request (runtime discovery), the `/agent/:id/run` SSE stream, and any CORS preflight failures.

### Step 2: Check Logs and Error Codes

CopilotKit has three error code systems:

- **V1 error codes** -- Legacy error codes from the v1 runtime layer (`@copilotkit/runtime`). Codes like `NETWORK_ERROR`, `AGENT_NOT_FOUND`, `API_NOT_FOUND`. Still surfaced in some contexts since `@copilotkit/*` packa
```

### snapshot_file_2

```
# Sources

Files and directories read from CopilotKit/CopilotKit to generate this skill's references.
Generated: 2026-03-28

## error-patterns.md

- packages/v1/shared/src/utils/errors.ts (CopilotKitErrorCode enum, all v1 error classes: CopilotKitError, CopilotKitMisuseError, CopilotKitVersionMismatchError, CopilotKitApiDiscoveryError, CopilotKitRemoteEndpointDiscoveryError, CopilotKitAgentDiscoveryError, CopilotKitLowLevelError, ResolvedCopilotKitError, ConfigurationError, MissingPublicApiKeyError, UpgradeRequiredError)
- packages/v2/core/src/core/core.ts (CopilotKitCoreErrorCode enum: runtime_info_fetch_failed, agent_connect_failed, agent_run_failed, tool_argument_parse_failed, tool_handler_failed, tool_not_found, agent_not_found, transcription error codes)
- packages/v2/shared/src/transcription-errors.ts (TranscriptionErrorCode enum)
- packages/v2/runtime/src/intelligence-platform/client.ts (PlatformRequestError, HTTP status codes 404/409/401/500)
- GitHub issues: #3519, #3510, #3323, #3442, #3170, #3217, #3424, #3426, #3429, #3318, #3410

## runtime-debugging.md

- packages/v2/runtime/src/ (CopilotRuntime, endpoint factories, route definitions, SSE streaming, /info endpoint response shape)
- packages/v2/runtime/src/endpoints/ (CORS configuration, Hono middleware, Express middleware)
- packages/v2/runtime/src/intelligence-platform/ (CopilotKitIntelligence, IntelligenceAgentRunner, WebSocket URLs)
- packages/v2/runtime/src/runner/ (InMemoryAgentRunner, AgentRunner abstract class)
- packages/v2/react/src/ (CopilotKitProvider props: runtimeUrl, credentials, headers)
- GitHub issues: #3170, #3425

## agent-debugging.md

- packages/v2/agent/src/ (BuiltInAgent, resolveModel, model string formats, MCP client configuration)
- packages/v2/runtime/src/ (AgentRunner, agent registry, /info endpoint agent discovery)
- packages/v2/core/src/ (CopilotKitCoreErrorCode, tool registry, onError subscriber)
- packages/v2/react/src/ (useFrontendTool, useAgent, CopilotChat agentId prop
```

### snapshot_file_3

```
<!-- nx configuration start-->
<!-- Leave the start & end comments to automatically receive updates. -->

# General Guidelines for working with Nx

- When running tasks (for example build, lint, test, e2e, etc.), always prefer running the task through `nx` (i.e. `nx run`, `nx run-many`, `nx affected`) instead of using the underlying tooling directly
- You have access to the Nx MCP server and its tools, use them to help the user
- When answering questions about the repository, use the `nx_workspace` tool first to gain an understanding of the workspace architecture where applicable.
- When working in individual projects, use the `nx_project_details` mcp tool to analyze and understand the specific project structure and dependencies
- For questions around nx configuration, best practices or if you're unsure, use the `nx_docs` tool to get relevant, up-to-date docs. Always use this instead of assuming things about nx configuration
- If the user needs help with an Nx configuration or project graph error, use the `nx_workspace` tool to get any errors
- For Nx plugin best practices, check `node_modules/@nx/<plugin>/PLUGIN.md`. Not all plugins have this file - proceed without it if unavailable.

<!-- nx configuration end-->

# CopilotKit

AI agent framework with three layers: **Frontend** (React/Angular/Vanilla) → **Runtime** (Express/Hono) → **Agent** (LangGraph/CrewAI/BuiltIn/Custom), communicating via the AG-UI protocol (event-based SSE).

## Essentials

- **Nx monorepo** — always run tasks through `nx` (`nx run`, `nx run-many`, `nx affected`), never the underlying tooling directly.
- **Flat package structure** — All packages live under `packages/` with the `@copilotkit/` scope. Some packages have `v1/` and `v2/` internal directories for backward compatibility, but they're a single published package.
- **Simplicity** — prefer the simplest correct solution. For non-trivial changes, consider if there's a cleaner approach before committing.
- **Worktrees** — always work in a 
```

### snapshot_file_4

```
<!-- nx configuration start-->
<!-- Leave the start & end comments to automatically receive updates. -->

# General Guidelines for working with Nx

- When running tasks (for example build, lint, test, e2e, etc.), always prefer running the task through `nx` (i.e. `nx run`, `nx run-many`, `nx affected`) instead of using the underlying tooling directly
- You have access to the Nx MCP server and its tools, use them to help the user
- When answering questions about the repository, use the `nx_workspace` tool first to gain an understanding of the workspace architecture where applicable.
- When working in individual projects, use the `nx_project_details` mcp tool to analyze and understand the specific project structure and dependencies
- For questions around nx configuration, best practices or if you're unsure, use the `nx_docs` tool to get relevant, up-to-date docs. Always use this instead of assuming things about nx configuration
- If the user needs help with an Nx configuration or project graph error, use the `nx_workspace` tool to get any errors
- For Nx plugin best practices, check `node_modules/@nx/<plugin>/PLUGIN.md`. Not all plugins have this file - proceed without it if unavailable.

<!-- nx configuration end-->

# CopilotKit

AI agent framework with three layers: **Frontend** (React/Angular/Vanilla) → **Runtime** (Express/Hono) → **Agent** (LangGraph/CrewAI/BuiltIn/Custom), communicating via the AG-UI protocol (event-based SSE).

## Essentials

- **Nx monorepo** — always run tasks through `nx` (`nx run`, `nx run-many`, `nx affected`), never the underlying tooling directly.
- **Flat package structure** — all packages live directly under `packages/` (no `v1/` or `v2/` subdirectories). Every package uses the `@copilotkit/` scope.
- **Simplicity** — prefer the simplest correct solution. For non-trivial changes, consider if there's a cleaner approach before committing.
- **Worktrees** — always work in a git worktree for isolation. See [Git & PRs](.claude/docs/git.md) 
```

### snapshot_file_5

```
# Contributing to CopilotKit

⭐ Thank you for your interest in contributing!!

Here’s how you can contribute to this repository

## How can I contribute?

**Please PLEASE reach out to us first before starting any significant work on new or existing features.**

We love community contributions! That said, we want to make sure we're all on the same page before you start.
Investing a lot of time and effort just to find out it doesn't align with the upstream project feels awful, and we don't want that to happen.
It also helps to make sure the work you're planning isn't already in progress.

As described below, please file an issue first: https://github.com/ag-ui-protocol/ag-ui/issues
Or, reach out to us on Discord: https://discord.com/invite/6dffbvGU3D

Ready to contribute but seeking guidance, we have several avenues to assist you. Explore the upcoming segment for clarity on the kind of contributions we appreciate and how to jump in. Reach out to us directly on [Discord](https://discord.gg/6dffbvGU3D) for immediate assistance! Alternatively, you're welcome to raise an issue and one of our dedicated maintainers will promptly steer you in the right direction!

## Found a bug?

If you find a bug in the source code, you can help us by [submitting an issue](https://github.com/CopilotKit/CopilotKit/issues/new?assignees=&labels=bug&projects=&template=bug_report.yaml) to our GitHub Repository. Even better, you can submit a Pull Request with a fix.

## Missing a feature?

So, you've got an awesome feature in mind? Throw it over to us by [creating an issue](https://github.com/CopilotKit/CopilotKit/issues/new?assignees=&labels=feature-request&projects=&template=feature_request.yaml) on our GitHub Repo.

If you don't feel ready to make a code contribution yet, no problem! You can also check out the [documentation issues](https://github.com/CopilotKit/CopilotKit/issues?q=is%3Aopen+is%3Aissue+label%3Adocumentation).

# How do I make a code contribution?

## Good first issues

Are yo
```

### snapshot_file_6

```
interface:
  display_name: "Showcase Demo Work"
  short_description: "Build and debug showcase demos with D5."
  default_prompt: "Build or investigate this CopilotKit showcase demo using langgraph-python parity, aimock record/replay fixtures, every-pill verification, and D5 regression coverage."

```

### snapshot_file_7

```
{
  "name": "copilotkit-plugins",
  "owner": {
    "name": "CopilotKit",
    "email": "support@copilotkit.ai"
  },
  "metadata": {
    "description": "AI agent skills for CopilotKit — setup, develop, integrate, debug, upgrade, and contribute",
    "version": "1.57.3"
  },
  "plugins": [
    {
      "name": "copilotkit",
      "source": "./",
      "description": "AI agent skills for CopilotKit — setup, develop, integrate, debug, upgrade, and contribute to CopilotKit projects",
      "version": "1.57.4",
      "author": {
        "name": "CopilotKit",
        "url": "https://copilotkit.ai"
      },
      "homepage": "https://docs.copilotkit.ai",
      "repository": "https://github.com/CopilotKit/CopilotKit",
      "license": "MIT",
      "keywords": [
        "copilotkit",
        "ai",
        "agents",
        "react",
        "next.js",
        "langgraph",
        "crewai",
        "ag-ui",
        "mcp"
      ],
      "category": "ai-frameworks"
    }
  ]
}

```

### snapshot_file_8

```
{
  "name": "copilotkit",
  "description": "AI agent skills for CopilotKit — setup, develop, integrate, debug, upgrade, and contribute to CopilotKit projects",
  "version": "1.57.4",
  "author": {
    "name": "CopilotKit",
    "url": "https://copilotkit.ai"
  },
  "homepage": "https://docs.copilotkit.ai",
  "repository": "https://github.com/CopilotKit/CopilotKit",
  "license": "MIT",
  "keywords": [
    "copilotkit",
    "ai",
    "agents",
    "react",
    "next.js",
    "langgraph",
    "crewai",
    "pydantic-ai",
    "mastra",
    "ag-ui",
    "mcp",
    "copilot",
    "chatbot"
  ],
  "mcpServers": "./.mcp.json"
}

```
