# Annotation packet `8bec66320d554a6d`

Protocol: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`

Judge only with the materials below. Do not seek external experimental results.

## Anonymous snapshot

- Snapshot ID: `49d0202578f7eb0d`
- Reference type: `directory`
- Artifact alias: **Referenced artifact R1**

## Task brief

Complete a small, bounded change in the pinned repository snapshot so that the project test command `pytest` passes. Use only files present in the snapshot. Judge whether Referenced artifact R1 is materially necessary for that task.

## Artifact role

Referenced artifact R1 denotes a directory path cited by the project instruction text. Its identity is withheld as a path string so treatment assignment cannot be inferred. The instruction context around the citation is provided below with the path replaced by [[REF]].

## Path policy

Manipulated and experimental path strings are withheld. Citations use [[REF]] / Referenced artifact R1 so treatment assignment cannot be read from path identity.

## Instruction citation excerpts

1. `- `repos/plugins/<name>/`, `repos/themes/<name>/` - Standalone/local plugin and theme checkouts that live outside the monorepo (e.g. private or customer-specific plugins, `newspack-manager`, licensed WooCommerce extensions). The `repos/plugins` and `repos/themes` directories are tracked (`.gitkeep`); anything you drop inside them is gitignored. Mounted at `[[REF]]` and symlinked into the active site (`wp-content/plugins/`, `wp-content/themes/`) by `bin/link-repos.sh`. **Any directory works with no registration** - `n` commands (`n build`, `n composer`, `n watch`, cwd-detection) discover `repos/` checkouts by path, so there's no need to edit `bin/repos.sh`. If a name also exists in the monorepo `plugins/`/`themes/`, the **tracked copy wins** and the `repos/` duplicate is skipped. Workflow: drop a real checkout in (clone/unzip directly, or `git worktree add`), build it, then `n restart`/`n start` to pick it up. A symlink *inside* `repos/` pointing outside the workspace will dangle in the container - use a real directory.`

## Repository tree excerpt

A full repository tree excerpt is not included in this offline packet build. Judge from the task brief and the instruction citation context only.
