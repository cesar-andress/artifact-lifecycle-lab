# Phase 0 Toolchain Failure Audit

**Scope:** execution-environment audit only — not a scientific reinterpretation of success.

---
## Reproducibility

- **Generated at (UTC):** 2026-07-03T22:24:16.961390+00:00
- **Git commit:** `f86eb9cd46e671624b614bcfb03543b80cea0069`
- **Manifest SHA-256:** `0925645ed19a0646675cd20d7e9d2cfe3547b0fa6628df477180d0ec2750c84e`
- **Python:** 3.12.13
- **Platform:** Linux-6.8.0-124-generic-x86_64-with-glibc2.35

**Analysis script hashes (SHA-256):**

- `phase0_toolchain_audit.py`: `6b0bddf09cb767916d58ec678c7f9291d2c415f2503b09929acca16b0e479fa0`

---

## Executive summary

- Runs audited: **33**
- Successes: **3** (9.1%)
- Failed runs: **30**
- Environment/toolchain-class failures: **30** (100.0% of failures)
- Task/agent-class failures: **0** (0.0% of failures)

> **Diagnosis:** low success rate is **primarily driven by broken or mis-specified execution environments**, not task difficulty.

## Failure class distribution

- **missing test runner**: 6 (20.0%)
- **wrong working directory**: 18 (60.0%)
- **invalid test command**: 3 (10.0%)
- **timeout**: 3 (10.0%)

## Revised Phase 0 case-quality report

### Cases with valid toolchain (1)

- `150fbfaadda2` **azure/oav** — `npm test` (3/3 ok; n/a) — keep

### Cases with invalid toolchain (9)

- `1e1131e99f59` **vercel/next.js** — `pytest` (0/3 ok; wrong working directory) — fix test_command before drop: pytest picked up lab root pyproject.toml; constrain cwd to case repo submodule with tests
- `3ff980d65c78` **agentwrapper/agent-orchestrator** — `go test` (0/3 ok; wrong working directory) — fix test_command before drop: run `go test` from Go module root (backend/ or subdir), not repo root
- `67c22d7f97cd` **microsoft/vscode** — `pytest` (0/3 ok; wrong working directory) — fix test_command before drop: pytest picked up lab root pyproject.toml; constrain cwd to case repo submodule with tests
- `6aab689b93e8` **vercel/next.js** — `pytest` (0/3 ok; wrong working directory) — fix test_command before drop: pytest picked up lab root pyproject.toml; constrain cwd to case repo submodule with tests
- `9040e7f7272a` **myriad-dreamin/tinymist** — `yarn test` (0/3 ok; invalid test command) — fix test_command before drop: package.json lacks test script; pick valid script from repo or drop case; was `yarn test`
- `abced8248ab9` **fixmyberlin/tilda-geo** — `Vitest` (0/3 ok; missing test runner) — replace bare runner with ecosystem entrypoint (e.g. npm test / npx vitest); was `Vitest`
- `d2578b858cfe` **fixmyberlin/tilda-geo** — `Vitest` (0/3 ok; missing test runner) — replace bare runner with ecosystem entrypoint (e.g. npm test / npx vitest); was `Vitest`
- `d5303ea5b426` **agentwrapper/agent-orchestrator** — `go test` (0/3 ok; wrong working directory) — fix test_command before drop: run `go test` from Go module root (backend/ or subdir), not repo root
- `ea5545b3e36e` **alphabitcore/nexus-gateway** — `go test` (0/3 ok; wrong working directory) — fix test_command before drop: run `go test` from Go module root (backend/ or subdir), not repo root

### Cases requiring setup command (1)

- `1bf1e91d4777` **astral-sh/ruff** — `cargo test` (0/3 ok; timeout) — add compile/install preflight or longer timeout

### Cases requiring different test command (9)

- `1e1131e99f59` **vercel/next.js** — `pytest` (0/3 ok; wrong working directory) — fix test_command before drop: pytest picked up lab root pyproject.toml; constrain cwd to case repo submodule with tests
- `3ff980d65c78` **agentwrapper/agent-orchestrator** — `go test` (0/3 ok; wrong working directory) — fix test_command before drop: run `go test` from Go module root (backend/ or subdir), not repo root
- `67c22d7f97cd` **microsoft/vscode** — `pytest` (0/3 ok; wrong working directory) — fix test_command before drop: pytest picked up lab root pyproject.toml; constrain cwd to case repo submodule with tests
- `6aab689b93e8` **vercel/next.js** — `pytest` (0/3 ok; wrong working directory) — fix test_command before drop: pytest picked up lab root pyproject.toml; constrain cwd to case repo submodule with tests
- `9040e7f7272a` **myriad-dreamin/tinymist** — `yarn test` (0/3 ok; invalid test command) — fix test_command before drop: package.json lacks test script; pick valid script from repo or drop case; was `yarn test`
- `abced8248ab9` **fixmyberlin/tilda-geo** — `Vitest` (0/3 ok; missing test runner) — replace bare runner with ecosystem entrypoint (e.g. npm test / npx vitest); was `Vitest`
- `d2578b858cfe` **fixmyberlin/tilda-geo** — `Vitest` (0/3 ok; missing test runner) — replace bare runner with ecosystem entrypoint (e.g. npm test / npx vitest); was `Vitest`
- `d5303ea5b426` **agentwrapper/agent-orchestrator** — `go test` (0/3 ok; wrong working directory) — fix test_command before drop: run `go test` from Go module root (backend/ or subdir), not repo root
- `ea5545b3e36e` **alphabitcore/nexus-gateway** — `go test` (0/3 ok; wrong working directory) — fix test_command before drop: run `go test` from Go module root (backend/ or subdir), not repo root

### Cases to drop (0)

- *(none in current sample)*

### Cases to keep (1)

- `150fbfaadda2` **azure/oav** — `npm test` (3/3 ok; n/a) — keep

### Cases pending execution (9)

- 9 manifest cases have no completed runs in the ledger yet.


## Per-case detail

| case_id | repository | test_command | ok/runs | valid | dominant failure |
| --- | --- | --- | --- | --- | --- |
| 150fbfaadda2 | azure/oav | npm test | 3/3 | yes | — |
| 1bf1e91d4777 | astral-sh/ruff | cargo test | 0/3 | partial | timeout |
| 1e1131e99f59 | vercel/next.js | pytest | 0/3 | no | wrong working directory |
| 3ff980d65c78 | agentwrapper/agent-orchestra | go test | 0/3 | no | wrong working directory |
| 67c22d7f97cd | microsoft/vscode | pytest | 0/3 | no | wrong working directory |
| 6aab689b93e8 | vercel/next.js | pytest | 0/3 | no | wrong working directory |
| 9040e7f7272a | myriad-dreamin/tinymist | yarn test | 0/3 | no | invalid test command |
| abced8248ab9 | fixmyberlin/tilda-geo | Vitest | 0/3 | no | missing test runner |
| d2578b858cfe | fixmyberlin/tilda-geo | Vitest | 0/3 | no | missing test runner |
| d5303ea5b426 | agentwrapper/agent-orchestra | go test | 0/3 | no | wrong working directory |
| ea5545b3e36e | alphabitcore/nexus-gateway | go test | 0/3 | no | wrong working directory |
