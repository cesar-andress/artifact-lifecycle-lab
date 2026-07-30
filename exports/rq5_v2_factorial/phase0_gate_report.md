# Phase 0 Gate Report

**Overall verdict:** **FAIL**

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

| Gate | Target | Observed | Status |
| --- | --- | --- | --- |
| Run completion | 60/60 | 24/60 | FAIL |
| Calibration success (T+L) | 0.45–0.75 | 0.125 | FAIL |
| Instruction read (present) | >0.90 | 1.000 | PASS |
| Anchor attempt (M1) | >0.60 | 1.000 | PASS |
| Timeout rate | ≤0.15 | 0.000 | PASS |
| Median files modified | ≤10 | 2.0 | PASS |
| Mechanical truth (design) | 100% | 100.0% | PASS |
| Per-case anchor attempt | ≥0.60 each case | 100.0% cases pass | PASS |
| No dry-run contamination | 0 dry runs | 0 | PASS |
