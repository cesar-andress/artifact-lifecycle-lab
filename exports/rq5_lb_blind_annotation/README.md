# RQ5 v1 blind load-bearing annotation packets (spec v2)

## Purpose

Construct-valid, outcome-blind packets so raters can answer:

> Is the referenced artifact materially necessary for completing THIS software
> engineering task in THIS repository snapshot?

Protocol: `docs/RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md` @ `e41902c`  
Packet spec: `rq5_v1_blind_packet_spec_v2`  
Redesign rationale: `PACKET_REDESIGN_V2.md`

## What changed vs v1 instrument

- Concrete task briefs derived from pinned instruction text (not generic pytest templates)
- Verification commands inferred from pinned manifests only
- Minimal repository tree + neighbours + docs/config + file excerpts
- Semantic whole-path redaction (no substring `[[REF]]` corruption)
- Absence statements forbidden; unsafe cases excluded as `not_safe_for_blinding`
- Non-English excerpts professionally translated via cache
- Degenerate / non-software packets excluded

## Eligibility vs Ambiguous

Eligibility is a data-preparation decision. Scientific `Ambiguous` remains an annotator label.

## Generation

```bash
make rq5-v1-blind-lb-packets
# requires network for bare clones into scratch/rq5_blind_trees/
```

Seed: 42

## Last generation

- Manifest cases: 35
- Packets emitted: 24
- Excluded: 11
- Counts: {"eligible": 24, "insufficient_pre_treatment_context": 2, "non_software_repository": 1, "not_safe_for_blinding": 6, "task_not_separable": 2}
