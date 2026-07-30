# Checklist — before submission

- [ ] Every `neutral_id` in `PACKET_INDEX.csv` has exactly one form row.
- [ ] No blank `reference_relevance`, `material_necessity`, or `confidence`.
- [ ] No blank `justification` (minimum ~2 sentences).
- [ ] Values use allowed snake_case enums only.
- [ ] Justification does **not** mention: agent, trace, condition, success, failure,
      runtime, experiment (as study arm / outcome).
- [ ] I consulted **no** external resources beyond this kit.
- [ ] I did **not** discuss cases with the other annotator.
- [ ] I did **not** modify files under `PACKETS/`.
- [ ] I am returning **only** `ANNOTATION_FORM.csv` (optional personal notes kept private).
- [ ] My filename makes the annotator ID clear if the coordinator asked
      (e.g. `ANNOTATION_FORM_annotator_A.csv`) — only if instructed; otherwise keep
      the default name and identify yourself in the submission message.
