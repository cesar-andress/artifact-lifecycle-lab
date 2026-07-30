# Annotation packet `67c2974c57527180`

Protocol: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`
Packet spec: `rq5_v1_blind_packet_spec_v2`

Judge only with the materials below. Do not seek external repositories or experimental results.

## Annotator question

Is Referenced artifact R1 materially necessary for completing THIS software engineering task in THIS repository snapshot?

## Anonymous snapshot

- Snapshot ID: `b8faa07291c6c05b`
- Reference type: `path`
- Artifact alias: **Referenced artifact R1**

## Task brief

Engineering task (derived only from the pinned instruction text and snapshot signals):

Document title: prefect-client Package Build. Instruction overview: Build configuration for `prefect-client`, a lightweight subset of `prefect` published as a separate PyPI package. This directory does **not** contain source code — it selects files from `src/prefect/` and repackages them.

While performing this work, the instruction cites Referenced artifact R1. Your annotation question is whether that cited artifact is materially necessary for completing this task in the provided snapshot.

Verification command observed in the pinned repository manifests: `pytest`. Use this only as a snapshot signal of how the project checks work; do not assume other commands.

## Artifact role

Referenced artifact R1 is a repository artifact cited by the project instruction text (reference kind: path). Its literal path string is withheld and shown as [[REF]] so treatment assignment cannot be inferred from path identity. Use the citation excerpts, task brief, and snapshot context below to judge relevance and necessity.

## Path policy

Path identity for the cited artifact and for contrast-only manipulated paths is replaced by [[REF]] using semantic whole-path tokenization (not substring replacement). Other snapshot paths may appear when they do not reveal treatment assignment. Do not infer experimental treatment from path placeholders.

## Instruction citation excerpts

### Excerpt 1

```
## Key Contracts

- **Dependency changes in root `pyproject.toml` that affect client-side code must be mirrored in `client/pyproject.toml`.** This is the most common source of build failures.
- **New imports in `src/prefect/` can break this build** if they pull in server-only dependencies. The build strips server code, so any import that reaches `server/database`, `server/models`, etc. from client-side code will fail.
- **The build is tested automatically on every PR** via `.github/workflows/prefect-client.yaml`.

## How It Works

`[[REF]]` copies `src/prefect/` into a temp directory, **deletes** server-only and CLI code, then builds with `client/pyproject.toml`. The resulting package has the same version as `prefect` but fewer dependencies.

### What gets removed

- `cli/` — entire CLI
- `server/` — database, models, orchestration, schemas, services, utilities (keeps only `server/api/`)
- `deployments/recipes/` and `deployments/templates/`
- `testing/`
```

### Excerpt 2

```
- `server/` — database, models, orchestration, schemas, services, utilities (keeps only `server/api/`)
- `deployments/recipes/` and `deployments/templates/`
- `testing/`

## Build Triggers

- **PR created** — CI builds and smoke-tests
- **GitHub release published** — CI builds and publishes to PyPI (same version as `prefect`)
- **Manual** — `bash client/build_client.sh`

If the CI build fails, reproduce locally with `bash client/build_client.sh` and run the smoke tests (`client_flow.py`, `client_deploy.py`).

## Related

- `src/prefect/client/` → Actual client SDK source code
- Root `pyproject.toml` → Must stay in sync with `client/pyproject.toml` for shared dependencies
```

### Excerpt 3

```
- `testing/`

## Build Triggers

- **PR created** — CI builds and smoke-tests
- **GitHub release published** — CI builds and publishes to PyPI (same version as `prefect`)
- **Manual** — `bash client/build_client.sh`

If the CI build fails, reproduce locally with `bash client/build_client.sh` and run the smoke tests (`client_flow.py`, `client_deploy.py`).

## Related

- `src/prefect/client/` → Actual client SDK source code
- Root `pyproject.toml` → Must stay in sync with `client/pyproject.toml` for shared dependencies
```

## Repository tree excerpt (pinned snapshot)

```
.claude/commands/repro.md
.claude/hooks/symlink-agents-to-claude.sh
.claude/settings.json
.claude/skills/agents-md-sync/SKILL.md
.claude/skills/backlog-management/SKILL.md
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
.github/workflows/api-compatibility-tests.yaml
.github/workflows/benchmarks.yaml
.github/workflows/claude.yml
.github/workflows/codeql-analysis.yml
.github/workflows/codspeed-benchmarks.yaml
.github/workflows/copy-linked-issue-labels.yml
.github/workflows/dbt-benchmarks.yaml
.github/workflows/devin-fix-flaky-tests.yaml
.github/workflows/docker-images.yaml
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
.github/workflows/ui-v2-checks.yml
.github/workflows/ui-v2-e2e-tests.yml
.github/workflows/validate_worker_metadata.yaml
.github/workflows/windows-tests.yaml
```

## Neighbouring paths

```
client/Dockerfile
client/INFO.md
client/README.md
client/build_client.sh
client/client_deploy.py
client/client_flow.py
client/prefect-cli-stub
client/pyproject.toml
```

## Nearby documentation paths

```
.github/CONTRIBUTING.md
[[INSTRUCTION]]
README.md
benches/README.md
[[REF]]
client/README.md
client/pyproject.toml
docs/[[INSTRUCTION]]
load_testing/README.md
load_testing/local-telemetry/README.md
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
.github/workflows/api-compatibility-tests.yaml
```

## Pinned snapshot file excerpts

### snapshot_file_1

```
# prefect-client Package Build

Build configuration for `prefect-client`, a lightweight subset of `prefect` published as a separate PyPI package. This directory does **not** contain source code — it selects files from `src/prefect/` and repackages them.

## Key Contracts

- **Dependency changes in root `pyproject.toml` that affect client-side code must be mirrored in `client/pyproject.toml`.** This is the most common source of build failures.
- **New imports in `src/prefect/` can break this build** if they pull in server-only dependencies. The build strips server code, so any import that reaches `server/database`, `server/models`, etc. from client-side code will fail.
- **The build is tested automatically on every PR** via `.github/workflows/prefect-client.yaml`.

## How It Works

`[[REF]]` copies `src/prefect/` into a temp directory, **deletes** server-only and CLI code, then builds with `client/pyproject.toml`. The resulting package has the same version as `prefect` but fewer dependencies.

### What gets removed

- `cli/` — entire CLI
- `server/` — database, models, orchestration, schemas, services, utilities (keeps only `server/api/`)
- `deployments/recipes/` and `deployments/templates/`
- `testing/`

## Build Triggers

- **PR created** — CI builds and smoke-tests
- **GitHub release published** — CI builds and publishes to PyPI (same version as `prefect`)
- **Manual** — `bash client/build_client.sh`

If the CI build fails, reproduce locally with `bash client/build_client.sh` and run the smoke tests (`client_flow.py`, `client_deploy.py`).

## Related

- `src/prefect/client/` → Actual client SDK source code
- Root `pyproject.toml` → Must stay in sync with `client/pyproject.toml` for shared dependencies

```

### snapshot_file_2

```
ARG PYTHON_VERSION=3.10
# SQLite version — must match the tag published to prefecthq/prefect-sqlite on DockerHub
# See Dockerfile.sqlite-builder and .github/workflows/sqlite-builder.yaml
ARG SQLITE_VERSION=3.50.4

# Pull pre-compiled SQLite binaries (built by .github/workflows/sqlite-builder.yaml).
# This avoids compiling SQLite from source on every build.
# To publish a new version: bump SQLITE_VERSION and run the sqlite-builder workflow.
FROM prefecthq/prefect-sqlite:${SQLITE_VERSION} AS sqlite-builder

# Build the Python distributable.
# Without this build step, versioningit cannot infer the version without git
FROM python:${PYTHON_VERSION}-slim AS python-builder

WORKDIR /opt/prefect

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    gpg \
    git=1:2.* \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install UV from official image - pin to specific version for build caching
COPY --from=ghcr.io/astral-sh/uv:0.5.30 /uv /bin/uv

# Copy the repository in; requires full git history for versions to generate correctly
COPY . ./

# Create a source distributable archive; ensuring existing dists are removed first
ENV TMPDIR=/tmp/prefect-client-build
RUN mkdir -p $TMPDIR && \
    sh client/build_client.sh && \
    cd $TMPDIR && \
    uv build --sdist --out-dir /opt/prefect/dist
RUN mv "dist/prefect_client-"*".tar.gz" "dist/prefect_client.tar.gz"


FROM python:${PYTHON_VERSION}-slim

# Redeclare ARGs needed in this stage
ARG PYTHON_VERSION
ARG SQLITE_VERSION

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_SYSTEM_PYTHON=1

# Ensure Python uses the upgraded SQLite library
ENV LD_LIBRARY_PATH=/usr/local/lib

LABEL maintainer="help@prefect.io" \
    io.prefect.python-version=${PYTHON_VERSION} \
    io.prefect.sqlite-version=${SQLITE_VERSION} \
    org.label-schema.schema-version="1.0" \
    org.label-schema.name="prefect" \
    org.label-schema.url="https://www.prefect.io/"

WORKDIR /opt/prefect

#
```

### snapshot_file_3

```
# Overview

This directory contains files for building and publishing the `prefect-client` 
library. `prefect-client` is built by removing source code from `prefect` and 
packages its own `requirements.txt` and `setup.py`. This process can happen 
in one of three ways:

- automatically whenever a PR is created (see 
`.github/workflows/prefect-client.yaml`)
- automatically whenever a Github release is published (see 
`.github/workflows/prefect-client-publish.yaml`)
- manually by running the `client/build_client.sh` script locally

Note that whenever a Github release is published the `prefect-client` will 
not only get built but will also be distributed to PyPI. `prefect-client` 
releases will have the same versioning as `prefect` - only the package names 
will be different.

This directory also includes a "minimal" flow that is used for smoke 
tests to ensure that the built `prefect-client` is functional.

In general, these builds, smoke tests, and publish steps should be transparent. 
It these automated steps fail, use the `client/build_client.sh` script to run 
the build and smoke test locally and iterate on a fix. The failures will likely 
be from:

- including a new dependency that is not installed in `prefect-client`
- re-arranging or adding files in such a way that a necessary file is rm'd at 
  build time

```

### snapshot_file_4

```
<p align="center"><img src="https://github.com/PrefectHQ/prefect/assets/3407835/c654cbc6-63e8-4ada-a92a-efd2f8f24b85" width=1000></p>

<p align="center">
    <a href="https://pypi.python.org/pypi/prefect-client/" alt="PyPI version">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/prefect-client?color=0052FF&labelColor=090422"></a>
    <a href="[repository]/" alt="Stars">
        <img src="https://img.shields.io/github/stars/prefecthq/prefect?color=0052FF&labelColor=090422" /></a>
    <a href="https://pepy.tech/badge/prefect-client/" alt="Downloads">
        <img src="https://img.shields.io/pypi/dm/prefect-client?color=0052FF&labelColor=090422" /></a>
    <a href="[repository]/pulse" alt="Activity">
        <img src="https://img.shields.io/github/commit-activity/m/prefecthq/prefect?color=0052FF&labelColor=090422" /></a>
    <br>
    <a href="https://prefect.io/slack" alt="Slack">
        <img src="https://img.shields.io/badge/slack-join_community-red.svg?color=0052FF&labelColor=090422&logo=slack" /></a>
    <a href="https://www.youtube.com/c/PrefectIO/" alt="YouTube">
        <img src="https://img.shields.io/badge/youtube-watch_videos-red.svg?color=0052FF&labelColor=090422&logo=youtube" /></a>
</p>

# prefect-client

The `prefect-client` package is a minimal-installation of `prefect` which is designed for interacting with Prefect Cloud
or remote any `prefect` server. It sheds some functionality and dependencies in exchange for a smaller installation size,
making it ideal for use in lightweight or ephemeral environments. These characteristics make it ideal for use in lambdas
or other resource-constrained environments.


## Getting started

`prefect-client` shares the same installation requirements as prefect. To install, make sure you are on Python 3.10 or
later and run the following command:

'''bash
pip install prefect-client
'''

Next, ensure that your `prefect-client` has access to a remote `prefect` serve
```

### snapshot_file_5

```
#!/bin/bash

CWD=$(pwd)

# if running in GH Actions, this will already be set
if [ -z ${TMPDIR+x} ];
    then
        TMPDIR=$(mktemp -d);
        echo "Using workspace at $TMPDIR";
    else echo "Using workspace at $TMPDIR";
fi

# init the workspace
cp -rf ./ $TMPDIR
cd $TMPDIR/src/prefect

# delete the files we don't need
rm -rf cli/
rm -rf deployments/recipes/
rm -rf deployments/templates
rm -rf server/__init__.py
find ./server \
    -not -path "./server" \
    -not -path "./server/api" \
    -not -path "./server/api/*" \
    -delete
rm -rf server/database
rm -rf server/models
rm -rf server/orchestration
rm -rf server/schemas
rm -rf server/services
rm -rf testing
rm -rf server/utilities

# replace old build files with client build files
cd $TMPDIR
cp client/pyproject.toml .
cp client/README.md .

cd $CWD

```

### snapshot_file_6

```
"""
This PR tests the code path for remote execution works for prefect-client. Because of prefect-client's reduced
dependency set, we need to guard against accidentally adding extraneous dependencies to this code path.
"""

import asyncio
import inspect
from pathlib import Path
from typing import TYPE_CHECKING

from prefect import Flow, get_client
from prefect.client.schemas.actions import WorkPoolCreate
from prefect.exceptions import ObjectNotFound
from prefect.runner.runner import Runner


async def main():
    async with get_client() as client:
        # Check if the smoke-test work pool exists
        try:
            await client.read_work_pool("smoke-test")
        except ObjectNotFound:
            # Create the work pool if it doesn't exist
            await client.create_work_pool(
                WorkPoolCreate(name="smoke-test", type="process")
            )

        # Deploy the flow
        smoke_test_flow = await Flow.afrom_source(
            source=Path(__file__).resolve().parent,
            entrypoint="client_flow.py:smoke_test_flow",
        )

        coro = smoke_test_flow.deploy(
            name="prefect-client-smoke-test",
            work_pool_name="smoke-test",
            print_next_steps=False,
        )
        if TYPE_CHECKING:
            assert inspect.iscoroutine(coro)

        deployment_id = await coro

        # Execute a run via a runner
        flow_run = await client.create_flow_run_from_deployment(
            deployment_id=deployment_id
        )

        await Runner().execute_flow_run(flow_run.id)


if __name__ == "__main__":
    asyncio.run(main())

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
├── docs/                            # Mintlify documentation (see docs/[[INSTRUCTION]])
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
