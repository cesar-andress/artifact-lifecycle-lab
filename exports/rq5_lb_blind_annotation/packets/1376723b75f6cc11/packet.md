# Annotation packet `1376723b75f6cc11`

Protocol: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`
Packet spec: `rq5_v1_blind_packet_spec_v2`

Judge only with the materials below. Do not seek external repositories or experimental results.

## Annotator question

Is Referenced artifact R1 materially necessary for completing THIS software engineering task in THIS repository snapshot?

## Anonymous snapshot

- Snapshot ID: `3132bc9a6468c825`
- Reference type: `path`
- Artifact alias: **Referenced artifact R1**

## Task brief

Engineering task (derived only from the pinned instruction text and snapshot signals):

Document title: Prefect Documentation. Instruction overview: Structural context for any agent working in `docs/`. For the full writing guide (page types, components, code testing, style), use the `/write-docs` skill.

While performing this work, the instruction cites Referenced artifact R1. Your annotation question is whether that cited artifact is materially necessary for completing this task in the provided snapshot.

Verification command observed in the pinned repository manifests: `pytest`. Use this only as a snapshot signal of how the project checks work; do not assume other commands.

## Artifact role

Referenced artifact R1 is a repository artifact cited by the project instruction text (reference kind: path). Its literal path string is withheld and shown as [[REF]] so treatment assignment cannot be inferred from path identity. Use the citation excerpts, task brief, and snapshot context below to judge relevance and necessity.

## Path policy

Path identity for the cited artifact and for contrast-only manipulated paths is replaced by [[REF]] using semantic whole-path tokenization (not substring replacement). Other snapshot paths may appear when they do not reveal treatment assignment. Do not infer experimental treatment from path placeholders.

## Instruction citation excerpts

### Excerpt 1

```
All pages must be registered in `docs/docs.json` under `navigation.tabs`. When adding a page, add its path (without `.mdx` extension) to the appropriate group.

## Links

Use absolute paths from the docs root without `.mdx`:

'''mdx
See the [flows documentation]([[REF]]) for details.
'''

Do not use relative paths or include `.mdx` in links.

## Redirects

When renaming or moving a page, add a redirect in `docs/docs.json` `redirects` array so existing links continue to work. Never remove existing redirects unless you are certain the old URL has no inbound traffic. Paths should not include `.mdx`.
```

### Excerpt 2

```
1. **Do not edit auto-generated files.** Pages under `v3/examples/`, `v3/api-ref/python/`, `v3/api-ref/cli/`, `v3/api-ref/rest-api/`, and `integrations/<name>/api-ref/` are generated from source code. The exception is `v3/api-ref/events/`, which is hand-authored and should be edited when event schemas change.
2. **Register new pages in `docs/docs.json`.** An unregistered page won't appear in navigation. Exception: pages with `hidden: true` are unlisted and do not require navigation registration.
3. **Use `.mdx` extension** for all new documentation files.
4. **Use Mintlify components** (`<Note>`, `<Tabs>`, `<Steps>`, etc.) rather than Markdown-native admonition syntax.
5. **Keep code examples working.** They are tested in CI via `pytest-markdown-docs`. Two skip mechanisms exist:
   - Per-block: add `{/* pmd-metadata: notest */}` above the fenced code block when a single example can't run in isolation.
   - Per-file: add the path to `SKIP_FILES` in `docs/conftest.py` when an entire page requires real external infrastructure (a live database, a dbt project and profiles, real API credentials). Integration pages almost always fall into this category.
6. **Use absolute link paths** without file extensions (e.g., `[[REF]]`).
7. **Check for existing snippets** in `snippets/` before duplicating content.
8. **Start body content at `##`.** The frontmatter `title` renders as H1; do not add another H1 in the body.
```

## Repository tree excerpt (pinned snapshot)

```
.claude/commands/repro.md
.claude/hooks/symlink-agents-to-claude.sh
.claude/settings.json
.claude/skills/agents-md-sync/SKILL.md
.claude/skills/backlog-management/SKILL.md
.claude/skills/document-changes/SKILL.md
.claude/skills/write-docs/SKILL.md
.claude/skills/write-docs/template-concept.mdx
.claude/skills/write-docs/template-howto.mdx
.dockerignore
.github/CODEOWNERS
.github/CONTRIBUTING.md
.github/ISSUE_TEMPLATE/1_bug_report.yaml
.github/ISSUE_TEMPLATE/2_feature_enhancement.yaml
.github/ISSUE_TEMPLATE/config.yml
.github/codeql-config.yml
.github/dependabot.yml
.github/docker/old-sqlite.Dockerfile
.github/labeler.yml
.github/pull_request_template.md
.github/pyrightconfig-ci.json
.github/release.yml
.github/workflows/agents-md-update.yml
.github/workflows/api-compatibility-tests.yaml
.github/workflows/benchmarks.yaml
.github/workflows/claude.yml
.github/workflows/codeql-analysis.yml
.github/workflows/codspeed-benchmarks.yaml
.github/workflows/copy-linked-issue-labels.yml
.github/workflows/dbt-benchmarks.yaml
.github/workflows/devin-fix-flaky-tests.yaml
.github/workflows/docker-images.yaml
.github/workflows/docs-broken-links.yaml
.github/workflows/docs-update.yml
.github/workflows/helm-chart-release.yaml
.github/workflows/integration-package-release.yaml
.github/workflows/integration-package-tests.yaml
.github/workflows/integration-tests.yaml
.github/workflows/k8s-integration-tests.yaml
.github/workflows/kickoff-release.yaml
.github/workflows/labeler.yml
.github/workflows/markdown-tests.yaml
.github/workflows/nightly-release.yaml
.github/workflows/npm_update_latest_prefect.yaml
.github/workflows/prefect-aws-docker-images.yaml
.github/workflows/prefect-aws-docker-test.yaml
.github/workflows/prefect-azure-docker-images.yaml
.github/workflows/prefect-azure-docker-test.yaml
.github/workflows/prefect-client-publish.yaml
.github/workflows/prefect-client.yaml
.github/workflows/prefect-gcp-docker-images.yaml
.github/workflows/prefect-gcp-docker-test.yaml
.github/workflows/proxy-test.yaml
.github/workflows/python-package.yaml
.github/workflows/python-tests.yaml
.github/workflows/sqlite-builder.yaml
.github/workflows/stale.yml
.github/workflows/static-analysis.yaml
.github/workflows/time-docker-build.yaml
.github/workflows/ui-tests.yml
```

## Neighbouring paths

```
docs/.mintignore
docs/.vale.ini
docs/conftest.py
docs/docs.json
docs/justfile
docs/script.js
docs/styles.css
```

## Nearby documentation paths

```
.github/CONTRIBUTING.md
[[INSTRUCTION]]
README.md
benches/README.md
client/[[INSTRUCTION]]
client/README.md
client/pyproject.toml
[[REF]]
integration-tests/[[INSTRUCTION]]
load_testing/README.md
```

## Nearby configuration paths

```
.claude/settings.json
.github/ISSUE_TEMPLATE/1_bug_report.yaml
.github/ISSUE_TEMPLATE/2_feature_enhancement.yaml
.github/ISSUE_TEMPLATE/config.yml
.github/codeql-config.yml
.github/dependabot.yml
.github/labeler.yml
.github/pyrightconfig-ci.json
.github/release.yml
.github/workflows/agents-md-update.yml
```

## Pinned snapshot file excerpts

### snapshot_file_1

```
# Prefect Documentation

Structural context for any agent working in `docs/`. For the full writing guide (page types, components, code testing, style), use the `/write-docs` skill.

## Platform

[Mintlify](https://mintlify.com/) docs published to [docs.prefect.io](https://docs.prefect.io). All files use `.mdx` (Markdown + JSX). Site config lives in `docs/docs.json`.

## Directory structure

'''
docs/
  v3/                     # Primary docs for Prefect 3.x
    get-started/          # Installation, quickstart
    concepts/             # Core concepts (flows, tasks, states, deployments, etc.)
    how-to-guides/        # Practical guides organized by category
    advanced/             # Advanced topics
    examples/             # Auto-generated from examples/ Python files — do NOT edit directly
    api-ref/              # API reference — mix of auto-generated and hand-authored
      python/             # SDK reference (auto-generated — do NOT edit directly)
      cli/                # CLI command reference (auto-generated — do NOT edit directly)
      rest-api/           # REST API docs (server/ and cloud/) (auto-generated — do NOT edit directly)
      events/             # Events reference catalog — hand-authored, editable
    release-notes/        # Version release notes
    img/                  # Images organized by section
  integrations/           # Integration-specific docs (prefect-aws, prefect-gcp, etc.)
  contribute/             # Contributor guides
  snippets/               # Reusable MDX snippets imported across pages
  images/                 # Legacy images
  logos/                  # Brand assets
  styles/                 # Vale linting styles
  resources/              # Unlisted pages (hidden: true) outside the v3/ versioning tree
'''

## Auto-generated content — do not edit

- `v3/examples/` — generated from top-level `examples/` Python files by `generate_example_pages.py`
- `v3/api-ref/python/`, `v3/api-ref/cli/`, `v3/api-ref/rest-api/` — generated AP
```

### snapshot_file_2

```
[[INSTRUCTION]]
styles/
```

### snapshot_file_3

```
StylesPath = styles

MinAlertLevel = warning

Packages = Google

[*]
BasedOnStyles = Vale, Google, CustomStyles

Vale.Spelling = NO
Google.Will = NO
Google.Quotes = NO
Google.OptionalPlurals = NO

# All of the following would be helpful in some cases but get really noisy
Google.Exclamation = NO
Google.Headings = NO
Google.We = NO

[formats]
mdx = md

# Tell vale to ignore MDX's JSX-specific syntax
# None of the following seems to matter, appears to be a bug with mdx and vale
# See https://github.com/errata-ai/vale/issues/858

# IgnoredScopes = code, tt, img, url, a
# SkippedScopes = script, style, pre, figure, code
# Ignore code surrounded by backticks or plus sign, parameters defaults, URLs, and angle brackets.
# TokenIgnores = (<\/?[A-Z].+>), (\x60[^\n\x60]+\x60), ([^\n]+=[^\n]*), (\+[^\n]+\+), (http[^\n]+\[)

# To execute vale on the command line, use the following command:
# vale --glob='!{*.mdx,*.js,*.json,*.png,*.jpg,*.css,*.yml,*.svg,3.0/api-ref/*.md}' ./3.0

```

### snapshot_file_4

```
import glob
import os
from typing import Union
from unittest import mock

import pytest

from prefect.server.database.orm_models import Mapped, Run, mapped_column, sa

SKIP_FILES = {
    "docs/v3/concepts/deployments.mdx": "Needs database fixtures",
    "docs/v3/how-to-guides/deployment_infra/run-flows-in-local-processes.mdx": "Needs blocks setup",
    "docs/v3/develop/blocks.mdx": "Block subclasses defined in docs cannot be properly registered due to test environment limitations",
    "docs/v3/develop/manage-states.mdx": "Needs some extra import help",
    "docs/v3/concepts/results.mdx": "Needs block cleanup handling",
    "docs/v3/how-to-guides/workflows/cache-workflow-steps.mdx": "Tasks defined in docs cannot be properly inspected due to test environment limitations",
    "docs/v3/how-to-guides/workflows/tag-based-concurrency-limits.mdx": "Await outside of async function",
    "docs/v3/how-to-guides/workflows/global-concurrency-limits.mdx": "Await outside of async function",
    "docs/v3/concepts/task-runners.mdx": "Tasks defined in docs cannot be properly inspected due to test environment limitations",
    "docs/v3/how-to-guides/workflows/write-and-run.mdx": "Tasks defined in docs cannot be properly inspected due to test environment limitations",
    "docs/v3/develop/interact-with-api.mdx": "Async function outside of async context",
    "docs/v3/develop/big-data.mdx": "Needs block cleanup handling",
    "docs/contribute/dev-contribute.mdx": "SQLAlchemy model modifications can't be safely tested without affecting the global database schema",
    "docs/integrations/prefect-azure/index.mdx": "Makes live network calls which should be mocked",
    "docs/integrations/prefect-bitbucket/index.mdx": "Needs block cleanup handling",
    "docs/integrations/prefect-dask/index.mdx": "Needs a `dask_cloudprovider` harness",
    "docs/integrations/prefect-dask/usage_guide.mdx": "Attempts to start a dask cluster",
    "docs/integrations/prefect-databricks/index.mdx": "Pydantic fa
```

### snapshot_file_5

```
{
  "$schema": "https://mintlify.com/docs.json",
  "api": {
    "playground": {
      "display": "simple"
    }
  },
  "appearance": {
    "default": "light",
    "strict": false
  },
  "colors": {
    "dark": "#2D6DF6",
    "light": "#5F92FF",
    "primary": "#2D6DF6"
  },
  "errors": {
    "404": {
      "redirect": true
    }
  },
  "favicon": "/logos/favicon.svg",
  "footer": {
    "socials": {
      "github": "https://github.com/PrefectHQ/prefect",
      "linkedin": "https://www.linkedin.com/company/prefect/mycompany/",
      "slack": "https://prefect.io/slack",
      "twitter": "https://x.com/prefectio",
      "youtube": "https://www.youtube.com/c/PrefectIO"
    }
  },
  "integrations": {
    "ga4": {
      "measurementId": "G-8GR5P04T5Y"
    },
    "gtm": {
      "tagId": "GTM-WKTHW8MK"
    }
  },
  "logo": {
    "dark": "/logos/logo-wordmark-light.svg",
    "href": "https://docs.prefect.io",
    "light": "/logos/logo-wordmark-dark.svg"
  },
  "name": "Prefect",
  "navbar": {
    "primary": {
      "href": "https://github.com/PrefectHQ/Prefect",
      "type": "github"
    }
  },
  "navigation": {
    "tabs": [
      {
        "groups": [
          {
            "group": "Get started",
            "pages": [
              "v3/get-started/index",
              "v3/get-started/install",
              "v3/get-started/quickstart"
            ]
          }
        ],
        "tab": "Getting Started"
      },
      {
        "pages": [
          "v3/concepts/index",
          {
            "group": "Workflows",
            "pages": [
              "[[REF]]",
              "v3/concepts/tasks",
              "v3/concepts/assets",
              "v3/concepts/caching",
              "v3/concepts/states",
              "v3/concepts/runtime-context",
              "v3/concepts/artifacts",
              "v3/concepts/task-runners",
              "v3/concepts/global-concurrency-limits",
              "v3/concepts/tag-based-concurrency-limits"
            ]
         
```

### snapshot_file_6

```
# Build and serve documentation
docs:
    npx mint@latest dev

# Check for broken links
links:
    npx mint@latest broken-links

# Lint using Vale
lint:
    vale --glob='**/*.{md,mdx}' .

```

### snapshot_file_7

```
# Contributing

Thanks for considering contributing to Prefect!

To navigate our codebase with confidence, see our [contribution guidelines](https://docs.prefect.io/contribute/).
```

### snapshot_file_8

```
Prefect is a workflow orchestration platform that coordinates and observes data pipelines. It provides a Python SDK for building workflows, a server backend for orchestration, and a web-based UI for managing and monitoring workflows.

# Guiding Principles

Your primary responsibility is to the project and its users. Every change should serve the broader user base — not just the immediate request. Be a quality gate: prefer correct, minimal, well-tested changes over fast ones.

# Directory Structure

'''
prefect/
├── benches/                         # Benchmarks (CLI, flows, tasks, imports)
├── client/                          # prefect-client build: subset of src/prefect/ published as a separate PyPI package
├── compat-tests/                    # Tests for REST API compatibility with Prefect Cloud
├── Dockerfile                       # Production container image
├── docs/                            # Mintlify documentation (see [[REF]])
├── examples/                        # Example flows (auto-published to docs)
├── integration-tests/               # End-to-end integration tests (require running server)
├── justfile                         # Task runner (just <command>)
├── load_testing/                    # Load/performance testing
├── plans/                           # Design/implementation plan documents
├── pyproject.toml                   # Root package config
├── schemas/                         # JSON schemas (prefect.yaml, settings)
├── scripts/                         # Code generation and release scripts
├── src/
│   ├── integrations/                # External service integrations (see src/integrations/[[INSTRUCTION]])
│   └── prefect/                     # Core package: SDK, server, CLI (see src/prefect/[[INSTRUCTION]])
├── tests/                           # Test suite, mirrors src/prefect/ (see tests/[[INSTRUCTION]])
├── tools/                           # Build tools
├── ui/                              # Vue UI (legacy, will be replaced by ui-v2)
├── ui-v2/       
```

### snapshot_file_9

```
<p align="center"><img src="https://github.com/PrefectHQ/prefect/assets/3407835/c654cbc6-63e8-4ada-a92a-efd2f8f24b85" width=1000></p>

<p align="center">
    <a href="https://pypi.org/project/prefect/" alt="PyPI version">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/prefect?color=0052FF&labelColor=090422" />
    </a>
    <a href="https://pypi.org/project/prefect/" alt="PyPI downloads/month">
        <img alt="Downloads" src="https://img.shields.io/pypi/dm/prefect?color=0052FF&labelColor=090422" />
    </a>
    <a href="[repository]/" alt="Stars">
        <img src="https://img.shields.io/github/stars/prefecthq/prefect?color=0052FF&labelColor=090422" />
    </a>
    <a href="[repository]/pulse" alt="Activity">
        <img src="https://img.shields.io/github/commit-activity/m/prefecthq/prefect?color=0052FF&labelColor=090422" />
    </a>
    <br>
    <a href="https://prefect.io/slack" alt="Slack">
        <img src="https://img.shields.io/badge/slack-join_community-red.svg?color=0052FF&labelColor=090422&logo=slack" />
    </a>
    <a href="https://www.youtube.com/c/PrefectIO/" alt="YouTube">
        <img src="https://img.shields.io/badge/youtube-watch_videos-red.svg?color=0052FF&labelColor=090422&logo=youtube" />
    </a>
</p>


<p align="center">
    <a href="https://docs.prefect.io/v3/get-started/index?utm_source=oss&utm_medium=oss&utm_campaign=oss_gh_repo&utm_term=none&utm_content=none">
        Installation
    </a>
    ·
    <a href="https://docs.prefect.io/v3/get-started/quickstart?utm_source=oss&utm_medium=oss&utm_campaign=oss_gh_repo&utm_term=none&utm_content=none">
        Quickstart
    </a>
    ·
    <a href="https://docs.prefect.io/v3/how-to-guides/workflows/write-and-run?utm_source=oss&utm_medium=oss&utm_campaign=oss_gh_repo&utm_term=none&utm_content=none">
        Build workflows
    </a>
    ·
    <a href="https://docs.prefect.io/v3/concepts/deployments?utm_source=oss&utm_medium=oss&utm_campaign
```

### snapshot_file_10

```
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/symlink-agents-to-claude.sh"
          }
        ]
      }
    ]
  }
}

```
