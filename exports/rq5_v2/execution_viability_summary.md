# Execution Viability Preflight Summary

**Purpose:** mandatory gate before task calibration. No agent execution.

---
## Reproducibility

- **Generated at (UTC):** 2026-07-03T22:32:30.816635+00:00
- **Git commit:** `f86eb9cd46e671624b614bcfb03543b80cea0069`
- **Manifest SHA-256:** `0925645ed19a0646675cd20d7e9d2cfe3547b0fa6628df477180d0ec2750c84e`
- **Python:** 3.12.13
- **Platform:** Linux-6.8.0-124-generic-x86_64-with-glibc2.35

**Analysis script hashes (SHA-256):**

- `execution_viability.py`: `8a215b219e529f4b2a27bf2eb7eb4aed41dd385dcae009927a7d57c2f104f510`
- `execution_viability_checks.py`: `91beed4be836e0a9e51dd0c0e95ca4507d9221631330a884f12d068511cb78f1`

---

## Cohort classification

- Candidates scored: **1524**
- **READY**: 9 (0.6%)
- **MINOR_SETUP**: 227 (14.9%)
- **REQUIRES_MANUAL_FIX**: 0 (0.0%)
- **DROP**: 1288 (84.5%)

## Expected infrastructure-failure reduction

- Observed Phase 0 environment/toolchain failure rate (executed sample): **100.0%**
- Candidates passing READY or MINOR_SETUP gate: **236** (15.5% of pool)

If calibration and factorial selection draw only from **READY ∪ MINOR_SETUP**:

- **Estimated reduction** in infrastructure-class failures: **100% → ~30%** (conservative; assumes MINOR_SETUP fixes succeed)

- Phase 0 repos with toolchain failures not marked READY: **7**

> This is an execution-environment projection, not a scientific success-rate claim.

## Diagnosis (Phase 0 cross-check)

- `fixmyberlin/tilda-geo`: phase0 env failure rate **100%** → viability **DROP**
- `agentwrapper/agent-orchestrator`: phase0 env failure rate **100%** → viability **MINOR_SETUP**
- `vercel/next.js`: phase0 env failure rate **100%** → viability **DROP**
- `alphabitcore/nexus-gateway`: phase0 env failure rate **100%** → viability **MINOR_SETUP**
- `microsoft/vscode`: phase0 env failure rate **100%** → viability **DROP**
- `myriad-dreamin/tinymist`: phase0 env failure rate **100%** → viability **MINOR_SETUP**
- `astral-sh/ruff`: phase0 env failure rate **100%** → viability **MINOR_SETUP**

## Recommended pipeline insertion

```
truth-decay-rq5-v2-candidates
  ↓
rq5-v2-execution-viability   ← this gate
  ↓
task-calibration (READY + MINOR_SETUP only)
  ↓
rq5-v2-factorial-plan
```

## Top failure modes

- **baseline_tests_execute**: 1515
