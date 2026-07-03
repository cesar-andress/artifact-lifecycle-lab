# Phase 0 Execution Viability Preflight

**Scope:** mandatory gate before Phase 0/Phase 1 agent runs. Smoke tests only — no agents.

---
## Reproducibility

- **Generated at (UTC):** 2026-07-03T23:10:56.187724+00:00
- **Git commit:** `eb7a06fceac661d2d438fe104853f766daa54a02`
- **Manifest SHA-256:** `0925645ed19a0646675cd20d7e9d2cfe3547b0fa6628df477180d0ec2750c84e`
- **Python:** 3.12.13
- **Platform:** Linux-6.8.0-124-generic-x86_64-with-glibc2.35

**Analysis script hashes (SHA-256):**

- `execution_preflight.py`: `ab134a5f197902b976bf66dbb8313346ecca131449a7cb0874ee910234c73553`
- `phase0_execution_viability.py`: `0869ee8605f09aa2bd8166070510730b0beda3930def0e22ccf4f427c7aeb141`

---

## Classification summary

- Cases evaluated: **21**
- **READY**: 7 (33.3%)
- **MINOR_SETUP**: 13 (61.9%)
- **REQUIRES_MANUAL_FIX**: 0 (0.0%)
- **DROP**: 1 (4.8%)

## Manifest repair

- Original manifest cases: **20**
- Repaired manifest cases: **20** (READY ∪ MINOR_SETUP)
- Replacement candidates added: **1**

## Expected infrastructure-failure reduction

Phase 0 observed failure mix (prior runs): wrong cwd ~60%, missing runner ~20%, invalid command ~10%, timeout ~10%, task/agent ~0%.

- Repaired cohort preflight-valid toolchain: **20/20** cases

If Phase 0/1 draw only from the repaired manifest with normalized commands and `execution_cwd`:

- **Estimated reduction** in environment-class failures: **~90% → ~10–20%** (remaining MINOR_SETUP cases need install/setup steps)

> Projection based on smoke preflight, not agent outcomes.

## Repaired manifest audit (preflight)

- `09be5687edfd` **automattic/wp-calypso** — `PYTHONNOUSERSITE=1 python -m pytest --confcutdir=. --rootdir=.` — **yes** (valid toolchain)
- `150fbfaadda2` **azure/oav** — `npm test` — **yes** (valid toolchain)
- `1bf1e91d4777` **astral-sh/ruff** — `cargo test` — **yes** (valid toolchain)
- `1e1131e99f59` **vercel/next.js** — `PYTHONNOUSERSITE=1 python -m pytest --confcutdir=. --rootdir=.` — **yes** (valid toolchain)
- `1f69fffb4fb4` **azure/oav** — `npm test` — **yes** (valid toolchain)
- `3ff980d65c78` **agentwrapper/agent-orchestrator** — `go test ./...` — **yes** (valid toolchain)
- `4f7981489a81` **agentwrapper/agent-orchestrator** — `go test ./...` — **yes** (valid toolchain)
- `5c319b363687` **datadog/dd-trace-js** — `yarn test` — **yes** (valid toolchain)
- `67c22d7f97cd` **microsoft/vscode** — `PYTHONNOUSERSITE=1 python -m pytest --confcutdir=. --rootdir=.` — **yes** (valid toolchain)
- `6aab689b93e8` **vercel/next.js** — `PYTHONNOUSERSITE=1 python -m pytest --confcutdir=. --rootdir=.` — **yes** (valid toolchain)
- `8921c9d4e98f` **alphabitcore/nexus-gateway** — `go test ./...` — **yes** (valid toolchain)
- `abced8248ab9` **fixmyberlin/tilda-geo** — `npm test` — **yes** (valid toolchain)
- `b929f379e955` **alphabitcore/nexus-gateway** — `npm test` — **yes** (valid toolchain)
- `ba9ebf91f505` **langgenius/dify** — `PYTHONNOUSERSITE=1 python -m pytest --confcutdir=. --rootdir=.` — **yes** (valid toolchain)
- `c2e719f54871` **goldenpotato137/potatovn** — `PYTHONNOUSERSITE=1 python -m pytest --confcutdir=. --rootdir=.` — **yes** (valid toolchain)
- `d2578b858cfe` **fixmyberlin/tilda-geo** — `npm test` — **yes** (valid toolchain)
- `d5303ea5b426` **agentwrapper/agent-orchestrator** — `go test ./...` — **yes** (valid toolchain)
- `e6e06694f4d1` **automattic/wp-calypso** — `npm test` — **yes** (valid toolchain)
- `ea5545b3e36e` **alphabitcore/nexus-gateway** — `go test ./...` — **yes** (valid toolchain)
- `fa545f0a92aa` **microsoft/vscode** — `PYTHONNOUSERSITE=1 python -m pytest --confcutdir=. --rootdir=.` — **yes** (valid toolchain)

## Top preflight failure classes

- **missing dependency**: 13
- **invalid test command**: 1

## Pipeline insertion

```
rq5-v2-factorial-plan
  ↓
rq5-v2-phase0-execution-viability   ← this gate
  ↓
run-phase0 (phase0_manifest_repaired.json only)
```
