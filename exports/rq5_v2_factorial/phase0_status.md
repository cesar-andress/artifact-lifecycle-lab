# RQ5 v2 Phase 0 — Live Status

**Updated (UTC):** 2026-07-03T22:20:04.977843+00:00

> **Provisional:** fewer than 60 runs complete — do not treat metrics as final calibration.

## Progress

- Completed runs: **32 / 60**
- Completed cases: **11 / 20**

## Current metrics

- Success rate: **0.094**
- Instruction read rate: **1.000**
- Anchor attempt rate: **1.000**
- Timeout rate: **0.000**
- Infrastructure/toolchain failure rate: **0.750**
- Median files modified: **2.0**

## Cost & runtime

- Mean cost per run: **$0.5127**
- Cumulative cost: **$16.4051**
- Estimated remaining cost: **$14.3545**
- Mean runtime: **142.8 s**
- Estimated ETA (UTC): **2026-07-03T23:26:43.339918+00:00**

## Last completed run

- Run ID: `f75cb4311ac21301e554`
- Case ID: `1bf1e91d4777d875`

## Last failure reason

```
Compiling unicode-ident v1.0.24
   Compiling memchr v2.8.1
   Compiling cfg-if v1.0.4
   Compiling itoa v1.0.15
   Compiling smallvec v1.15.1
   Compiling regex-syntax v0.8.11
   Compiling equivalent v1.0.2
   Compiling log v0.4.32
   Compiling foldhash v0.2.0
   Compiling once_cell v1.21.4
   Compi
```

## Warning flags

- WARN: success rate 0.094 outside [0.30, 0.85] (n=32)
- WARN: infrastructure/toolchain failure rate 0.750 > 0.20 (n=32)

## Recent log tail

```
summary_md -> exports/rq5_v2_factorial/phase0_summary.md
trace_audit_csv -> exports/rq5_v2_factorial/phase0_trace_audit.csv
decision_md -> exports/rq5_v2_factorial/phase0_decision.md
run_plan_csv -> exports/rq5_v2_factorial/phase0_run_plan.csv
preflight_json -> exports/rq5_v2_factorial/phase0_preflight.json
```
