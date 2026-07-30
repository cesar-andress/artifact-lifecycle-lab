# Coordinator guide — RQ5 v1 blind LB annotation

## DISTRIBUTION STATUS: BLOCKED

**Do not distribute the v2 human annotation kit.**

Read first:

- `DO_NOT_DISTRIBUTE_V2.md`
- `v3_feasibility/RQ5_V1_V3_FEASIBILITY_REPORT.md`

The v2 kit failed construct-validity and blinding review. The v3 feasibility audit
found **0 / 35** RQ5 v1 cases with an independent task oracle.

Until a new prospectively sampled case set exists, there is **no** annotator ZIP
to send.

Historical v2 paths (`human_annotation_kit/`, `packets/`) are retained for
provenance only and are **non-distributable**.

---

## What coordinators may do now

1. Run the v3 feasibility audit (does not build a kit):

```bash
.venv/bin/python -m artifact_lab.experiments.truth_decay.rq5_experiment.blind_lb_v3_feasibility
```

2. Review CSVs under `v3_feasibility/`.
3. Do **not** run `make rq5-v1-blind-lb-annotation-kit` for human delivery.
4. Do **not** compute agreement on v2 annotations (none should be collected).

## Obsolete sections

Previous instructions in this file about zipping `human_annotation_kit/`,
assigning annotator IDs for v2 packets, and collecting `ANNOTATION_FORM.csv` for
the v2 kit are **withdrawn**.

Protocol reference (for future redesign): `docs/RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md` @ `e41902c`.
