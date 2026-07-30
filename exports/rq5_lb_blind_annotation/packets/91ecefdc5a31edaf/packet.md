# Annotation packet `91ecefdc5a31edaf`

Protocol: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`
Packet spec: `rq5_v1_blind_packet_spec_v2`

Judge only with the materials below. Do not seek external repositories or experimental results.

## Annotator question

Is Referenced artifact R1 materially necessary for completing THIS software engineering task in THIS repository snapshot?

## Anonymous snapshot

- Snapshot ID: `fe32b1344d01de1b`
- Reference type: `path`
- Artifact alias: **Referenced artifact R1**

## Task brief

Engineering task (derived only from the pinned instruction text and snapshot signals):

Document title: Testing Utilities. Instruction overview: Test helpers and fixtures shipped with the Prefect SDK for testing flows against a real local server.

While performing this work, the instruction cites Referenced artifact R1. Your annotation question is whether that cited artifact is materially necessary for completing this task in the provided snapshot.

Verification command observed in the pinned repository manifests: `pytest`. Use this only as a snapshot signal of how the project checks work; do not assume other commands.

## Artifact role

Referenced artifact R1 is a repository artifact cited by the project instruction text (reference kind: path). Its literal path string is withheld and shown as [[REF]] so treatment assignment cannot be inferred from path identity. Use the citation excerpts, task brief, and snapshot context below to judge relevance and necessity.

## Path policy

Path identity for the cited artifact and for contrast-only manipulated paths is replaced by [[REF]] using semantic whole-path tokenization (not substring replacement). Other snapshot paths may appear when they do not reveal treatment assignment. Do not infer experimental treatment from path placeholders.

## Instruction citation excerpts

### Excerpt 1

```
Provides the `prefect_test_harness` context manager and assertion helpers consumed by both the Prefect test suite and downstream user code. Does **not** own pytest fixtures (those live in `tests/`) or integration-test infrastructure.

## Entry Points & Contracts

- **`prefect_test_harness()`** (`utilities.py`) — Context manager that spins up a temporary SQLite-backed `SubprocessASGIServer` and overrides `PREFECT_API_URL` for the duration of the block. Safe to nest; restores prior state on exit.
- **`assert_does_not_warn()`** — Converts warnings to errors inside the block. Accepts an `ignore_warnings` list for expected categories.
- **`assert_blocks_equal()`** / **`assert_uses_result_serializer()`** / **`assert_uses_result_storage()`** — Deep-equality helpers for blocks and result metadata.
- **`[[REF]]`** — Pytest fixtures for WebSocket servers, events clients (`AssertingEventsClient`, `AssertingPassthroughEventsClient`), and CSRF/ephemeral-mode overrides. Imported in `tests/conftest.py`.
- **`standard_test_suites/`** — Reusable test suite classes (e.g., `BlockStandardTestSuite`) for testing block implementations.

## Invariants

- **`prefect_test_harness` registers the test server under `SubprocessASGIServer._instances[None]`.** `SubprocessASGIServer` is a port-keyed singleton. The harness creates a server with an explicit port (keyed by that port), then also registers it under the `None` key. This ensures that internal `SubprocessASGIServer()` calls during flow execution return the *same* managed instance rather than spawning a second unmanaged subprocess. On exit the prior `None`-keyed entry is restored (or removed if there was none). Violating this invariant causes a leaked server process that keeps pytest hanging after test completion — see issue #21544.
- **`p
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
src/prefect/testing/__init__.py
src/prefect/testing/cli.py
src/prefect/testing/docker.py
src/prefect/testing/fixtures.py
src/prefect/testing/utilities.py
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
.github/workflows/agents-md-update.yml
```

## Pinned snapshot file excerpts

### snapshot_file_1

```
# Testing Utilities

Test helpers and fixtures shipped with the Prefect SDK for testing flows against a real local server.

## Purpose & Scope

Provides the `prefect_test_harness` context manager and assertion helpers consumed by both the Prefect test suite and downstream user code. Does **not** own pytest fixtures (those live in `tests/`) or integration-test infrastructure.

## Entry Points & Contracts

- **`prefect_test_harness()`** (`utilities.py`) — Context manager that spins up a temporary SQLite-backed `SubprocessASGIServer` and overrides `PREFECT_API_URL` for the duration of the block. Safe to nest; restores prior state on exit.
- **`assert_does_not_warn()`** — Converts warnings to errors inside the block. Accepts an `ignore_warnings` list for expected categories.
- **`assert_blocks_equal()`** / **`assert_uses_result_serializer()`** / **`assert_uses_result_storage()`** — Deep-equality helpers for blocks and result metadata.
- **`[[REF]]`** — Pytest fixtures for WebSocket servers, events clients (`AssertingEventsClient`, `AssertingPassthroughEventsClient`), and CSRF/ephemeral-mode overrides. Imported in `tests/conftest.py`.
- **`standard_test_suites/`** — Reusable test suite classes (e.g., `BlockStandardTestSuite`) for testing block implementations.

## Invariants

- **`prefect_test_harness` registers the test server under `SubprocessASGIServer._instances[None]`.** `SubprocessASGIServer` is a port-keyed singleton. The harness creates a server with an explicit port (keyed by that port), then also registers it under the `None` key. This ensures that internal `SubprocessASGIServer()` calls during flow execution return the *same* managed instance rather than spawning a second unmanaged subprocess. On exit the prior `None`-keyed entry is restored (or removed if there was none). Violating this invariant causes a leaked server process that keeps pytest hanging after test completion — see issue #21544.
- **`prefect_test_harness` drains `APILogWorker` and `EventsWo
```

### snapshot_file_2

```

```

### snapshot_file_3

```
from __future__ import annotations

import contextlib
import getpass
import io
import os
import re
import sys
import textwrap
import warnings
from typing import Iterable

import readchar
from rich.console import Console

# Regex pattern to match ANSI escape codes
_ANSI_ESCAPE_PATTERN = re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi_codes(text: str) -> str:
    """Remove ANSI escape codes from text.

    This is necessary because Typer/Rich may output ANSI codes in CI environments
    (e.g., GitHub Actions) even when Click's CliRunner has color=False, due to
    Typer's terminal detection logic.
    """
    return _ANSI_ESCAPE_PATTERN.sub("", text)


class _TTYStringIO(io.StringIO):
    """A StringIO that reports isatty()=True.

    Rich's Console.is_interactive checks file.isatty() to decide whether to
    show prompts.  By emulating a TTY, any Console created while sys.stdout
    points to this buffer will behave interactively — matching real terminal
    behavior and allowing Confirm.ask / Prompt.ask to work correctly.
    """

    def isatty(self) -> bool:
        return True


class CycloptsResult:
    """Result of a cyclopts CLI invocation.

    Compatible with typer's Result so existing invoke_and_assert callers
    can work with either runner without changes.
    """

    def __init__(
        self,
        stdout: str,
        stderr: str,
        exit_code: int,
        exception: BaseException | None,
    ):
        self.stdout = stdout
        self.stderr = stderr
        # Click's CliRunner merges stdout and stderr into one stream.
        # Match that behavior so `result.output` always contains both.
        self.output: str = stdout + stderr
        self.exit_code = exit_code
        self.exception = exception


class CycloptsCliRunner:
    """In-process test runner for the cyclopts CLI.

    Analogous to Click's CliRunner: captures stdout/stderr, simulates stdin,
    emulates a TTY for Rich Console interactive mode, and isolates global
    state betw
```

### snapshot_file_4

```
from contextlib import contextmanager
from typing import Any, Generator
from unittest import mock

from prefect.utilities.dockerutils import ImageBuilder


@contextmanager
def capture_builders() -> Generator[list[ImageBuilder], None, None]:
    """Captures any instances of ImageBuilder created while this context is active"""
    builders: list[ImageBuilder] = []

    original_init = ImageBuilder.__init__

    def capture(self: ImageBuilder, *args: Any, **kwargs: Any):
        builders.append(self)
        original_init(self, *args, **kwargs)

    with mock.patch.object(ImageBuilder, "__init__", capture):
        yield builders

```

### snapshot_file_5

```
import asyncio
import json
import os
import signal
import socket
import subprocess
import sys
from contextlib import contextmanager
from typing import Any, AsyncGenerator, Callable, Generator, List, Optional, Union
from unittest import mock
from unittest.mock import AsyncMock
from uuid import UUID

import anyio
import httpx
import pytest
from starlette.status import WS_1008_POLICY_VIOLATION
from websockets.asyncio.server import (
    Server,
    ServerConnection,
    serve,
)
from websockets.exceptions import ConnectionClosed

from prefect._internal.compatibility.async_dispatch import async_dispatch
from prefect.events import Event
from prefect.events.clients import (
    AssertingEventsClient,
    AssertingPassthroughEventsClient,
)
from prefect.events.filters import EventFilter
from prefect.events.worker import EventsWorker
from prefect.server.api.server import SubprocessASGIServer
from prefect.server.events.pipeline import EventsPipeline
from prefect.settings import (
    PREFECT_API_URL,
    PREFECT_SERVER_ALLOW_EPHEMERAL_MODE,
    PREFECT_SERVER_CSRF_PROTECTION_ENABLED,
    get_current_settings,
    temporary_settings,
)
from prefect.types._datetime import DateTime, now
from prefect.utilities.asyncutils import run_coro_as_sync
from prefect.utilities.processutils import open_process


@pytest.fixture(autouse=True)
def add_prefect_loggers_to_caplog(
    caplog: pytest.LogCaptureFixture,
) -> Generator[None, None, None]:
    import logging

    logger = logging.getLogger("prefect")
    logger.propagate = True

    try:
        yield
    finally:
        logger.propagate = False


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


@pytest.fixture(scope="session")
async def hosted_api_server(
    unused_tcp_port_factory: Callable[[], int],
    test_database_connection_url: Optional[str],
) -> AsyncGenerator[str, None]:
    """
    Runs an instance of the Pref
```

### snapshot_file_6

```
"""
Internal utilities for tests.
"""

from __future__ import annotations

import atexit
import inspect
import shutil
import socket
import warnings
from contextlib import ExitStack, contextmanager
from pathlib import Path
from pprint import pprint
from tempfile import mkdtemp
from typing import TYPE_CHECKING, Any, Generator

import prefect.context
import prefect.settings
from prefect.blocks.core import Block
from prefect.client.orchestration import get_client
from prefect.client.schemas import sorting
from prefect.client.schemas.filters import FlowFilter, FlowFilterName
from prefect.client.utilities import inject_client
from prefect.events.worker import EventsWorker
from prefect.logging.handlers import APILogWorker
from prefect.results import (
    ResultRecord,
    ResultRecordMetadata,
    ResultStore,
    get_default_result_storage,
)
from prefect.serializers import Serializer
from prefect.server.api.server import SubprocessASGIServer
from prefect.states import State
from prefect.utilities.asyncutils import run_coro_as_sync

if TYPE_CHECKING:
    from prefect.client.orchestration import PrefectClient
    from prefect.client.schemas.objects import FlowRun
    from prefect.filesystems import ReadableFileSystem


def exceptions_equal(a: Exception, b: Exception) -> bool:
    """
    Exceptions cannot be compared by `==`. They can be compared using `is` but this
    will fail if the exception is serialized/deserialized so this utility does its
    best to assert equality using the type and args used to initialize the exception
    """
    if a == b:
        return True
    return type(a) is type(b) and getattr(a, "args", None) == getattr(b, "args", None)


def _find_available_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def kubernetes_environments_equal(
    actual: list[dict[str, str]],
    expected: list[dict[str, str]] | dict[str, str],
) -> bool:
 
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
