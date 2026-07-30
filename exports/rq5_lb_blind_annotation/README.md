# RQ5 v1 blind load-bearing annotation packets

## Purpose

Prepare **outcome-blind**, **condition-blind** annotation packets so human raters can
judge whether a referenced artifact is **materially necessary** for the intended task
**before** any runtime evidence is considered.

Authoritative rater protocol:

- `docs/RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md`
- Commit reference: `e41902c`

## Packet eligibility vs scientific Ambiguous

| Concept | Meaning |
|---------|---------|
| **Eligibility** (`eligibility.csv`) | Data-preparation decision: can we emit a safe pre-treatment packet? |
| **Ambiguous** (rater label) | Scientific judgment: materials are insufficient for confident necessity |

Never map ineligible packets to the annotator label `Ambiguous`.

## Source boundaries (allowed)

- `exports/rq5_agent_impact/rq5_case_manifest.csv`
- Instruction bytes from `data/blobs/` using the **sanitized source blob** only
  (manifest field used internally for retrieval; never named as a condition to raters)
- Optional join to `exports/truth_decay_pilot/rq5_candidate_dataset.csv` for
  pre-treatment metadata (not emitted raw when leaky)
- Protocol document above

## Source boundaries (forbidden)

- Agent traces, success/failure, A/B/C outcomes
- Mediation / uptake / causal-role exports
- Existing load-bearing stratum labels
- Rater exposure to private ID maps

## Blinding guarantees (implemented)

- Opaque `neutral_id` (seed=42)
- No `case_id`, repo URL, or raw experimental paths in rater packets
- Citations use `[[REF]]` / `Referenced artifact R1`
- Contrast instruction bytes may be inspected only to build a ban-list; never emitted
- Leakage scan before emit; refuse on hit (`condition_leakage_risk`)

## Access model for ID map

`private/id_map.sealed.json` is **access-separated**, not cryptographically sealed.
Do not share `private/` with raters.

## Authoritative final classification rule

Derived from rater fields (not entered manually):

```
if relevance == ambiguous -> ambiguous
elif necessity == ambiguous -> ambiguous
elif relevance == directly_relevant and necessity == materially_necessary -> load_bearing
elif relevance in {irrelevant, contextually_relevant} -> non_load_bearing
elif necessity in {not_necessary, helpful_but_substitutable} -> non_load_bearing
else -> ambiguous
```

`contextually_relevant + materially_necessary` is **non_load_bearing** (with consistency warning).

Implementation: `artifact_lab/experiments/truth_decay/rq5_experiment/blind_lb_derive.py`

## Generation command

```bash
cd /home/cesar/papers/artifact-lifecycle-lab/artifact-lifecycle-lab
.venv/bin/python -m artifact_lab.experiments.truth_decay.rq5_experiment.blind_lb_packet \
  --manifest exports/rq5_agent_impact/rq5_case_manifest.csv \
  --output-dir exports/rq5_lb_blind_annotation \
  --seed 42
```

Or: `make rq5-v1-blind-lb-packets`

Human Annotation Kit (what to send to raters):

```bash
make rq5-v1-blind-lb-annotation-kit
# or
.venv/bin/python -m artifact_lab.experiments.truth_decay.rq5_experiment.blind_lb_annotation_kit
```

Coordinator workflow: `COORDINATOR_GUIDE.md` (not part of the rater ZIP).

## Directory structure

```
exports/rq5_lb_blind_annotation/
├── README.md
├── COORDINATOR_GUIDE.md     # coordinator only
├── eligibility.csv          # rater-safe (no case_id)
├── rater_sheet_template.csv
├── human_annotation_kit/    # DISTRIBUTE THIS DIRECTORY / ZIP
│   ├── README_START_HERE.md
│   ├── ANNOTATOR_INSTRUCTIONS.md
│   ├── CODEBOOK.md
│   ├── PACKETS/
│   ├── ANNOTATION_FORM.csv
│   ├── ANNOTATION_FORM.xlsx
│   ├── HASHES/
│   └── ...
├── packets/<neutral_id>/    # internal generator output
│   ├── packet.md
│   ├── packet.json
│   └── provenance.json
└── private/                 # NEVER give to raters
    ├── id_map.sealed.json
    ├── eligibility_internal.csv
    └── README.md
```

## What raters receive

- The full `human_annotation_kit/` directory (or ZIP), including instructions,
  codebook, forms, `PACKETS/`, and `HASHES/`

## What raters must never receive

- `private/`
- Any RQ5 results, traces, mediation exports
- Manuscript sections discussing outcomes

## Known limitations

- Offline build omits full repository tree excerpts (noted in packet).
- Generic experimental task prompts couple the task to the instruction file;
  many packets are marked `requires_manual_packet_review` for human QA before distribution.
- Path redaction prevents showing the literal referenced path; raters judge from role + citation context.

## Last generation summary

- Manifest cases: 35
- Packets emitted: 31
- Eligibility counts: {"insufficient_pre_treatment_context": 4, "requires_manual_packet_review": 31}
