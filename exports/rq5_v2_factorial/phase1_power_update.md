# Phase 1 Power Update (observed Phase 0 variance)

All estimates use **observed** Phase 0 data only.

## Observed variance

- Runs (Phase 0): **24**
- Observed success rate: **0.125**
- Per-run variance (Bernoulli sample): **0.1094**
- Per-case variance (mean of 3 replicates): **0.1094**
- Cases with data: **8**

## Required runs for T+L success-rate precision (Wilson-normal approx.)

| Target half-width (95%) | Required runs (p̂=0.125) |
|---|---|
| ±0.05 | 169 |
| ±0.08 | 66 |
| ±0.10 | 43 |

## Phase 1a (40 cases × 5 cells × 3 replicates = 600 runs planned)

- With **observed per-case variance** and **N=40 cases**, expected 95% CI half-width on case-mean success: **±0.102**.
- To tighten half-width to ±0.10 at same variance: need **~43 cases** (+3 vs plan).

## Phase 1b (120 cases × 5 cells × 3 replicates = 1,800 runs planned)

- Expected 95% CI half-width on case-mean success at N=120: **±0.059**.

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
