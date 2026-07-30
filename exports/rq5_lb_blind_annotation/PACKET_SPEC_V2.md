# RQ5 v1 Blind Packet Specification v2

`packet_spec_version`: `rq5_v1_blind_packet_spec_v2`  
Protocol: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`

## Annotator question (only)

> Is Referenced artifact R1 materially necessary for completing THIS software
> engineering task in THIS repository snapshot?

## Required rater-facing fields

| Field | Type | Requirement |
|-------|------|-------------|
| `neutral_id` | string | Opaque ID |
| `anonymous_snapshot_id` | string | Opaque snapshot ID |
| `protocol_version` | string | Protocol pin |
| `packet_spec_version` | string | `rq5_v1_blind_packet_spec_v2` |
| `annotator_question` | string | Fixed question above |
| `task_brief` | string | Concrete task derived from pinned instruction + snapshot verification signal |
| `task_brief_source` | string | Provenance tags for brief extraction |
| `verification_command_observed` | string | Empty if unidentified; never invented |
| `verification_evidence` | string | Why that command was inferred |
| `reference_type` | string | path / directory / … |
| `referenced_artifact_alias` | string | Always `Referenced artifact R1` |
| `artifact_role_description` | string | Neutral role text |
| `instruction_citation_excerpts` | string[] | Rich windows around citation; paths semantically redacted |
| `instruction_language_original` | string | `en` / `zh` / `ru` / … |
| `instruction_provided_in` | string | Always `en` for raters |
| `repository_tree_excerpt` | string[] | Minimal pinned paths |
| `neighbor_paths` | string[] | Neighbours of focus |
| `nearby_documentation_paths` | string[] | Docs near focus |
| `nearby_configuration_paths` | string[] | Configs near focus |
| `snapshot_file_excerpts` | object[] | `{file_alias, role, content}` |
| `path_policy` | string | Redaction policy |

## Forbidden content

- Experimental case IDs, conditions, outcomes, traces, mediation labels
- Literal treated/false path identity for the citation
- Absence claims about `[[REF]]` / R1
- Generic “make pytest pass” briefs unrelated to the repository
- Substring-corrupted `[[REF]]` artifacts (`80/[[REF]]0`, etc.)

## Eligibility statuses

| Status | Emit packet? | Meaning |
|--------|--------------|---------|
| `eligible` | yes | Construct-valid instrument unit |
| `not_safe_for_blinding` | no | Cannot sanitize without treatment leakage |
| `task_not_separable` | no | No concrete task extractable |
| `degenerate_packet` | no | Too little information after enrichment |
| `non_software_repository` | no | Not an SE repository under protocol framing |
| `insufficient_pre_treatment_context` | no | Anchor not in instruction source |
| `source_unavailable` | no | Blob/tree unavailable |
| `condition_leakage_risk` | no | Leakage scan failed |

Scientific label `Ambiguous` is **not** an eligibility status.

## Redaction rule

Replace **complete path spans** matching banned anchors using semantic tokenization.
Short/numeric anchors (`1/`, `2/`) require exact span match only.

## Generation

```bash
make rq5-v1-blind-lb-packets
make rq5-v1-blind-lb-annotation-kit
```

Requires network for bare clones into `scratch/rq5_blind_trees/`.
