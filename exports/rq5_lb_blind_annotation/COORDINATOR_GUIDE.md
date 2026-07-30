# Coordinator guide — RQ5 v1 blind LB annotation

This file is **not** part of the annotator distribution.
Distribute only `human_annotation_kit/` (or a ZIP of that directory).

Protocol: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`  
Packet spec: `rq5_v1_blind_packet_spec_v2` (see `PACKET_SPEC_V2.md`, `PACKET_REDESIGN_V2.md`)

Distribute **only eligible packets** already placed in the kit (`PACKETS/`).
Excluded cases are listed in `exclusions.csv` and must not be annotated under this wave.

## Distribute

1. Build/regenerate packets, then the kit (see commands below).
2. Verify `QA/packet_qa.csv` has `qa_ok=True` for all rows.
3. Review `PACKET_INDEX.csv` notes — all current packets may be
   `requires_manual_packet_review` (generic task brief). Spot-check a sample of
   `PACKETS/*/packet.md` before release.
4. Zip `human_annotation_kit/` identically for both annotators.
5. Send the same ZIP to both; record the `HASHES/manifest.sha256` fingerprint.

Do **not** send `exports/rq5_lb_blind_annotation/private/`.

## Assign annotator IDs

Use opaque IDs such as `annotator_A` and `annotator_B`. Put the ID in the submission
email / filename, not inside packets.

## Collect responses

Expect only `ANNOTATION_FORM.csv` per annotator.
Rename on receipt to `ANNOTATION_FORM__<annotator_id>__<date>.csv`.
Store raw files immutable under an archive folder.

## Verify hashes

On the coordinator machine:

```bash
cd human_annotation_kit
sha256sum -c HASHES/manifest.sha256
```

Both annotators’ kits must match the same manifest.

## Merge responses

Join on `neutral_id`. Keep separate columns per annotator for:

- reference_relevance
- material_necessity
- confidence
- justification

Derive finals with
`artifact_lab.experiments.truth_decay.rq5_experiment.blind_lb_derive.derive_final_classification`
for each annotator independently.

## Calculate agreement (workflow only — do not run here)

1. Derive final label per annotator per case.
2. Compute pairwise agreement / Cohen’s κ on the final label and optionally on each
   dimension.
3. List disagreements for adjudication.

## Prepare adjudication

For disagreements, create a third packet-identical review set without showing either
annotator’s labels. Document adjudication rules before opening disagreements.

## Archive

Keep forever:

- kit `VERSION.txt` + `HASHES/manifest.sha256`
- raw returned CSVs
- merge table
- adjudication log

Never mix private `id_map.sealed.json` into annotator archives.

## Regeneration commands

```bash
make rq5-v1-blind-lb-packets
.venv/bin/python -m artifact_lab.experiments.truth_decay.rq5_experiment.blind_lb_annotation_kit
```
