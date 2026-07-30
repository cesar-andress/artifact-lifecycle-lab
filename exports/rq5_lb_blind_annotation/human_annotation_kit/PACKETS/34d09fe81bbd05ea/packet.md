# Annotation packet `34d09fe81bbd05ea`

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

Document title: Events (Client-Side). Instruction overview: Client-side event system for emitting, subscribing to, and defining automations on Prefect events.

While performing this work, the instruction cites Referenced artifact R1. Your annotation question is whether that cited artifact is materially necessary for completing this task in the provided snapshot.

Verification command observed in the pinned repository manifests: `pytest`. Use this only as a snapshot signal of how the project checks work; do not assume other commands.

## Artifact role

Referenced artifact R1 is a repository artifact cited by the project instruction text (reference kind: path). Its literal path string is withheld and shown as [[REF]] so treatment assignment cannot be inferred from path identity. Use the citation excerpts, task brief, and snapshot context below to judge relevance and necessity.

## Path policy

Path identity for the cited artifact and for contrast-only manipulated paths is replaced by [[REF]] using semantic whole-path tokenization (not substring replacement). Other snapshot paths may appear when they do not reveal treatment assignment. Do not infer experimental treatment from path placeholders.

## Instruction citation excerpts

### Excerpt 1

```
- Automations combine triggers (event, metric, compound, sequence) with actions.
- `DeploymentTriggerTypes` are the subset of triggers usable in `prefect.yaml` deployment definitions.

## Structure

- `schemas/` — Pydantic models: `Event`, `Resource`, `RelatedResource`, `Automation`, triggers, deployment triggers
- `clients.py` — Event emission client (sends events to server/Cloud)
- `subscribers.py` — WebSocket subscribers for real-time event streams
- `[[REF]]` — Automation action types (`RunDeployment`, `PauseDeployment`, `SendNotification`, etc.)
- `worker.py` — Background event emission worker
- `filters.py` — Event query filters
- `related.py` — Related resource resolution

## Client vs Server

| Concern | Client (`events/`) | Server (`server/events/`) |
|---------|-------------------|--------------------------|
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
src/prefect/events/__init__.py
src/prefect/events/actions.py
src/prefect/events/clients.py
src/prefect/events/filters.py
src/prefect/events/related.py
src/prefect/events/subscribers.py
src/prefect/events/utilities.py
src/prefect/events/worker.py
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
.github/workflows/api-compatibility-tests.yaml
```

## Pinned snapshot file excerpts

### snapshot_file_1

```
# Events (Client-Side)

Client-side event system for emitting, subscribing to, and defining automations on Prefect events.

## Key Contracts

- **Event schemas are defined here, not on the server.** The server imports schemas from this module.
- Events follow the CloudEvents-inspired schema: `Event` with `Resource` and `RelatedResource`.
- Automations combine triggers (event, metric, compound, sequence) with actions.
- `DeploymentTriggerTypes` are the subset of triggers usable in `prefect.yaml` deployment definitions.

## Structure

- `schemas/` — Pydantic models: `Event`, `Resource`, `RelatedResource`, `Automation`, triggers, deployment triggers
- `clients.py` — Event emission client (sends events to server/Cloud)
- `subscribers.py` — WebSocket subscribers for real-time event streams
- `[[REF]]` — Automation action types (`RunDeployment`, `PauseDeployment`, `SendNotification`, etc.)
- `worker.py` — Background event emission worker
- `filters.py` — Event query filters
- `related.py` — Related resource resolution

## Client vs Server

| Concern | Client (`events/`) | Server (`server/events/`) |
|---------|-------------------|--------------------------|
| Event schemas | Defined here | Imported from client |
| Emission | `clients.py` | Receives via API |
| Subscriptions | `subscribers.py` | `stream.py`, `messaging.py` |
| Trigger evaluation | Definition only | Evaluation and firing |
| Actions | Type definitions | Execution |

## Related

- `server/events/` → Server-side event processing
- `client/schemas/events.py` → Client-side event schema re-exports

```

### snapshot_file_2

```
from .schemas.events import Event, ReceivedEvent
from .schemas.events import Resource, RelatedResource, ResourceSpecification
from .schemas.automations import (
    Automation,
    AutomationCore,
    Posture,
    TriggerTypes,
    Trigger,
    ResourceTrigger,
    EventTrigger,
    MetricTrigger,
    MetricTriggerOperator,
    MetricTriggerQuery,
    CompositeTrigger,
    CompoundTrigger,
    SequenceTrigger,
)
from .schemas.deployment_triggers import (
    DeploymentTriggerTypes,
    DeploymentEventTrigger,
    DeploymentMetricTrigger,
    DeploymentCompoundTrigger,
    DeploymentSequenceTrigger,
)
from .actions import (
    ActionTypes,
    Action,
    DoNothing,
    RunDeployment,
    PauseDeployment,
    ResumeDeployment,
    ChangeFlowRunState,
    CancelFlowRun,
    SuspendFlowRun,
    CallWebhook,
    SendNotification,
    PauseWorkPool,
    ResumeWorkPool,
    PauseWorkQueue,
    ResumeWorkQueue,
    PauseAutomation,
    ResumeAutomation,
    DeclareIncident,
)
from .clients import get_events_client, get_events_subscriber
from .subscribers import FlowRunSubscriber
from .utilities import emit_event

__all__ = [
    "Event",
    "ReceivedEvent",
    "Resource",
    "RelatedResource",
    "ResourceSpecification",
    "Automation",
    "AutomationCore",
    "Posture",
    "TriggerTypes",
    "Trigger",
    "ResourceTrigger",
    "EventTrigger",
    "MetricTrigger",
    "MetricTriggerOperator",
    "MetricTriggerQuery",
    "CompositeTrigger",
    "CompoundTrigger",
    "SequenceTrigger",
    "DeploymentTriggerTypes",
    "DeploymentEventTrigger",
    "DeploymentMetricTrigger",
    "DeploymentCompoundTrigger",
    "DeploymentSequenceTrigger",
    "ActionTypes",
    "Action",
    "DoNothing",
    "RunDeployment",
    "PauseDeployment",
    "ResumeDeployment",
    "ChangeFlowRunState",
    "CancelFlowRun",
    "SuspendFlowRun",
    "CallWebhook",
    "SendNotification",
    "PauseWorkPool",
    "ResumeWorkPool",
    "PauseWorkQueue",
    "ResumeWorkQueue",
    "Pa
```

### snapshot_file_3

```
import abc
from datetime import timedelta
from typing import Any, Dict, Optional, Union
from uuid import UUID

from pydantic import Field, model_validator
from typing_extensions import Literal, Self, TypeAlias

from prefect._internal.schemas.bases import PrefectBaseModel
from prefect.client.schemas.objects import StateType
from prefect.types import NonNegativeTimeDelta


class Action(PrefectBaseModel, abc.ABC):
    """An Action that may be performed when an Automation is triggered"""

    type: str

    def describe_for_cli(self) -> str:
        """A human-readable description of the action"""
        return self.type.replace("-", " ").capitalize()


class DoNothing(Action):
    """Do nothing when an Automation is triggered"""

    type: Literal["do-nothing"] = "do-nothing"


class DeploymentAction(Action):
    """Base class for Actions that operate on Deployments and need to infer them from
    events"""

    source: Literal["selected", "inferred"] = Field(
        "selected",
        description=(
            "Whether this Action applies to a specific selected "
            "deployment (given by `deployment_id`), or to a deployment that is "
            "inferred from the triggering event.  If the source is 'inferred', "
            "the `deployment_id` may not be set.  If the source is 'selected', the "
            "`deployment_id` must be set."
        ),
    )
    deployment_id: Optional[UUID] = Field(
        None, description="The identifier of the deployment"
    )

    @model_validator(mode="after")
    def selected_deployment_requires_id(self):
        wants_selected_deployment = self.source == "selected"
        has_deployment_id = bool(self.deployment_id)
        if wants_selected_deployment != has_deployment_id:
            raise ValueError(
                "deployment_id is "
                + ("not allowed" if has_deployment_id else "required")
            )
        return self


class RunDeployment(DeploymentAction):
    """Runs the given deployment 
```

### snapshot_file_4

```
import abc
import asyncio
from datetime import timedelta
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    List,
    MutableMapping,
    Optional,
    Tuple,
    Type,
    cast,
)
from uuid import UUID

import orjson
from cachetools import TTLCache
from prometheus_client import Counter
from typing_extensions import Self
from websockets import Subprotocol
from websockets.asyncio.client import ClientConnection
from websockets.exceptions import (
    ConnectionClosed,
    ConnectionClosedError,
    ConnectionClosedOK,
)

import prefect.types._datetime
from prefect._internal.websockets import websocket_connect
from prefect.events import Event
from prefect.logging import get_logger
from prefect.settings import (
    PREFECT_API_KEY,
    PREFECT_API_URL,
    PREFECT_CLOUD_API_URL,
    PREFECT_DEBUG_MODE,
    PREFECT_SERVER_ALLOW_EPHEMERAL_MODE,
    get_current_settings,
)

if TYPE_CHECKING:
    from prefect.events.filters import EventFilter

EVENTS_EMITTED = Counter(
    "prefect_events_emitted",
    "The number of events emitted by Prefect event clients",
    labelnames=["client"],
)
EVENTS_OBSERVED = Counter(
    "prefect_events_observed",
    "The number of events observed by Prefect event subscribers",
    labelnames=["client"],
)
EVENT_WEBSOCKET_CONNECTIONS = Counter(
    "prefect_event_websocket_connections",
    (
        "The number of times Prefect event clients have connected to an event stream, "
        "broken down by direction (in/out) and connection (initial/reconnect)"
    ),
    labelnames=["client", "direction", "connection"],
)
EVENT_WEBSOCKET_CHECKPOINTS = Counter(
    "prefect_event_websocket_checkpoints",
    "The number of checkpoints performed by Prefect event clients",
    labelnames=["client"],
)

if TYPE_CHECKING:
    import logging

logger: "logging.Logger" = get_logger(__name__)

# Exceptions that indicate transient network issues and should trigger retries.
# These are used consistent
```

### snapshot_file_5

```
from __future__ import annotations

import datetime
from typing import Optional, Union
from uuid import UUID

from pydantic import Field

import prefect.types._datetime
from prefect._internal.schemas.bases import PrefectBaseModel
from prefect.types import DateTime
from prefect.utilities.collections import AutoEnum

from .schemas.events import Event, Resource, ResourceSpecification


class AutomationFilterCreated(PrefectBaseModel):
    """Filter by `Automation.created`."""

    before_: Optional[DateTime] = Field(
        default=None,
        description="Only include automations created before this datetime",
    )


class AutomationFilterName(PrefectBaseModel):
    """Filter by `Automation.created`."""

    any_: Optional[list[str]] = Field(
        default=None,
        description="Only include automations with names that match any of these strings",
    )


class AutomationFilter(PrefectBaseModel):
    name: Optional[AutomationFilterName] = Field(
        default=None, description="Filter criteria for `Automation.name`"
    )
    created: Optional[AutomationFilterCreated] = Field(
        default=None, description="Filter criteria for `Automation.created`"
    )


class EventDataFilter(PrefectBaseModel, extra="forbid"):  # type: ignore[call-arg]
    """A base class for filtering event data."""

    def get_filters(self) -> list["EventDataFilter"]:
        filters: list[EventDataFilter] = []
        for filter in [
            getattr(self, name) for name in self.__class__.model_fields.keys()
        ]:
            # Any embedded list of filters are flattened and thus ANDed together
            subfilters: list[EventDataFilter] = (
                filter if isinstance(filter, list) else [filter]
            )

            for subfilter in subfilters:
                if not isinstance(subfilter, EventDataFilter):
                    continue

                filters.append(subfilter)

        return filters

    def includes(self, event: Event) -> bool:
        "
```

### snapshot_file_6

```
import asyncio
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)
from uuid import UUID

import prefect.types._datetime

from .schemas.events import RelatedResource

if TYPE_CHECKING:
    from prefect._internal.schemas.bases import ObjectBaseModel
    from prefect.client.orchestration import PrefectClient

ResourceCacheEntry = Dict[str, Union[str, "ObjectBaseModel", None]]
RelatedResourceCache = Dict[
    str, Tuple[ResourceCacheEntry, prefect.types._datetime.DateTime]
]

MAX_CACHE_SIZE = 100
RESOURCE_CACHE: RelatedResourceCache = {}


def tags_as_related_resources(tags: Iterable[str]) -> List[RelatedResource]:
    return [
        RelatedResource(
            {
                "prefect.resource.id": f"prefect.tag.{tag}",
                "prefect.resource.role": "tag",
            }
        )
        for tag in sorted(tags)
    ]


def object_as_related_resource(kind: str, role: str, object: Any) -> RelatedResource:
    if as_related_resource := getattr(object, "as_related_resource", None):
        return as_related_resource(role=role)

    resource_id = f"prefect.{kind}.{object.id}"
    return RelatedResource(
        {
            "prefect.resource.id": resource_id,
            "prefect.resource.role": role,
            "prefect.resource.name": object.name,
        }
    )


async def related_resources_from_run_context(
    client: "PrefectClient",
    exclude: Optional[Set[str]] = None,
) -> List[RelatedResource]:
    from prefect.client.schemas.objects import FlowRun
    from prefect.context import FlowRunContext, TaskRunContext

    if exclude is None:
        exclude = set()

    flow_run_context = FlowRunContext.get()
    task_run_context = TaskRunContext.get()

    if not flow_run_context and not task_run_context:
        return []

    flow_run_id: Optional[UUID] = getattr(
        getattr(flow_run_context, "flow_run", None), "id", None
    ) or getat
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
