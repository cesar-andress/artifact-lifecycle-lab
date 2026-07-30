# DO NOT DISTRIBUTE — RQ5 v1 blind annotation kit v2

**Status: SUPERSEDED / NON-DISTRIBUTABLE**

The v2 human annotation kit under

`exports/rq5_lb_blind_annotation/human_annotation_kit/`

and the v2 packet tree under

`exports/rq5_lb_blind_annotation/packets/`

**must not be sent to annotators.**

## Why

An adversarial instrument review found critical construct-validity and blinding
failures, including:

- task briefs derived from the same instruction that cites R1 (circularity);
- non–software-engineering “tasks” (e.g. affiliate/content skills) framed as SE;
- repository re-identification via distinctive paths, hosts, and ecosystem names;
- protocol/form contradictions and treatment-demand language.

See:

- `v3_feasibility/RQ5_V1_V3_FEASIBILITY_REPORT.md`
- prior audit conclusions recorded in project history

## What to do instead

1. Do **not** run `make rq5-v1-blind-lb-annotation-kit` for distribution.
2. Do **not** zip or email `human_annotation_kit/`.
3. Follow the v3 feasibility audit. No distributable v3 kit exists until a
   construct-valid case set with independent task oracles is available.

Coordinator guides that still describe v2 distribution are obsolete; distribution
is **blocked** until explicitly re-authorized after a passing v3 gate.
