# Phase 0 Editorial Decision

## Associate Editor recommendation

**Proceed to Phase 1a?** **No**

### Manipulation validity

- Instruction uptake: **adequate** for present-cell manipulation check.
- Operational load-bearing (M1): **adequate** at pooled level.

### Calibration validity

- T+L success (**0.125**) is **outside** [0.45, 0.75] — calibration not validated.

### Causal validity

- Phase 0 does not estimate H4. Causal identifiability for Phase 1 depends on passing operational LB and instruction-read gates.
- **2 gate(s) FAIL** — causal runway not cleared.

### Statistical validity

- **Incomplete execution** (24/60 runs) — inferential summaries are provisional.

### Protocol deviations

- No major protocol deviations detected in completed runs.

### Risks

- **Toolchain**: 18 failures (86% of failed runs).
- **Success**: 3 failures (14% of failed runs).
- **Tests**: 3 failures (14% of failed runs).

### Required fixes before Phase 1a

- Fix **Run completion** (observed 24/60, target 60/60).
- Fix **Calibration success (T+L)** (observed 0.125, target 0.45–0.75).
---
## Reproducibility

- **Generated at (UTC):** 2026-07-03T21:56:54.041569+00:00
- **Git commit:** `f86eb9cd46e671624b614bcfb03543b80cea0069`
- **Manifest SHA-256:** `0925645ed19a0646675cd20d7e9d2cfe3547b0fa6628df477180d0ec2750c84e`
- **Python:** 3.12.13
- **Platform:** Linux-6.8.0-124-generic-x86_64-with-glibc2.35

**Analysis script hashes (SHA-256):**

- `phase0_analysis.py`: `0fac5990e4166984902cda756bb419fb812af2c19d2e35326052715b37d3ba5d`
- `phase0_figures.py`: `adb4694edfb0df4586bc111b5dce153d73ed14c1b8f080288480f3787fd33779`
- `phase0_provenance.py`: `b8ad62ac93a4ad4cfc3bdac8642271a5542999dba028e218691ef91d836d5d1d`
- `phase0_trace.py`: `83c6c110fc6981bf22ac7a4f748f4f40ef238965b8fee8086f62abc9d6798b5e`

---
