# Phase 0 Trace Quality Report

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

## M1→M2→M3→M4 funnel

| Stage | Count | Share |
| --- | --- | --- |
| instruction_read | 24 | 100.0% |
| M1 anchor_attempted | 24 | 100.0% |
| M2 bind_failure | 0 | 0.0% |
| M3 grounding_action | 0 | 0.0% |
| M4 repair_success | 0 | 0.0% |

- **instruction_self_repair** (runs): 2 (8.3%)

## Path confusion table (sequential trace flags)

| Path | Runs |
| --- | --- |
| read→M1 | 24 |
