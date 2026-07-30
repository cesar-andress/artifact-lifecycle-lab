# Annotation packet `1e39c3352c8e8e69`

Protocol: `RQ5_V1_BLIND_LB_ANNOTATION_PROTOCOL.md@e41902c`
Packet spec: `rq5_v1_blind_packet_spec_v2`

Judge only with the materials below. Do not seek external repositories or experimental results.

## Annotator question

Is Referenced artifact R1 materially necessary for completing THIS software engineering task in THIS repository snapshot?

## Anonymous snapshot

- Snapshot ID: `3c40f96b963174ed`
- Reference type: `path`
- Artifact alias: **Referenced artifact R1**

## Task brief

Engineering task (derived only from the pinned instruction text and snapshot signals):

Instruction overview: ## Directory purpose `app/ui/graph/library_pages/entity_placement/`: split implementation of the entity-placement page (`EntityPlacementWidget`), factored by responsibility into mixins and utility modules (UI assembly / page protocol / list construction / level entities / instance operations / decoration merge) to reduce single-file complexity and improve reuse and testing.

While performing this work, the instruction cites Referenced artifact R1. Your annotation question is whether that cited artifact is materially necessary for completing this task in the provided snapshot.

Verification command observed in the pinned repository manifests: `pytest`. Use this only as a snapshot signal of how the project checks work; do not assume other commands.

## Artifact role

Referenced artifact R1 is a repository artifact cited by the project instruction text (reference kind: path). Its literal path string is withheld and shown as [[REF]] so treatment assignment cannot be inferred from path identity. Use the citation excerpts, task brief, and snapshot context below to judge relevance and necessity.

## Path policy

Path identity for the cited artifact and for contrast-only manipulated paths is replaced by [[REF]] using semantic whole-path tokenization (not substring replacement). Other snapshot paths may appear when they do not reveal treatment assignment. Do not infer experimental treatment from path placeholders.

## Instruction citation excerpts

### Excerpt 1

```
## Directory purpose
`app/ui/graph/library_pages/entity_placement/`: split implementation of the entity-placement page (`EntityPlacementWidget`), factored by responsibility into mixins and utility modules (UI assembly / page protocol / list construction / level entities / instance operations / decoration merge) to reduce single-file complexity and improve reuse and testing.

## Current status
- **Entry class**: `app/ui/graph/library_pages/entity_placement_widget.py` keeps only the `EntityPlacementWidget` shell and signal definitions, and provides full behavior by composing mixins.
- **Centralized constants**: page-related item roles, category keys, dialog sizes, vector ranges, and formatting parameters are consolidated in `[[REF]]` to avoid scattered magic numbers.
- **Implementation split**: each mixin owns one concern (for example shortcuts/context menus, list refresh and selection restore, level-entity logic, decoration-merge workflow); persistence/index moves still delegate to upper components such as `ResourceManager` / `PackageIndexManager`.
- **Module layout**: `ui_mixin.py` (UI/shortcuts/menus), `protocol_mixin.py` (page protocol/selection linkage), `instance_list_mixin.py` (list construction and shared badges), `level_entity_mixin.py` (level entities), `instance_ops_mixin.py` (add/remove/edit/move operations), `merge_decorations_mixin.py` (decoration merge workflow).

## Notes
- Mixins must not silently degrade or swallow errors with bare try/except; errors should be raised explicitly or surfaced through the existing UI notification path.
- List rebuilds must reuse `rebuild_list_with_preserved_selection` so the “signal blocking + selection restore” semantics stay stable and the right-hand panel does not flicker.
- Resource ownership move/delete semantics m
```

## Repository tree excerpt (pinned snapshot)

```
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\345\244\215\345\220\210\350\212\202\347\202\271\345\272\223/claude.md"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\345\244\215\345\220\210\350\212\202\347\202\271\345\272\223/composite_\345\206\267\345\215\264_\346\243\200\346\237\245\345\271\266\346\233\264\346\226\260\346\227\266\351\227\264\346\210\263.py"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\345\244\215\345\220\210\350\212\202\347\202\271\345\272\223/composite_\345\256\236\344\275\223\345\210\227\350\241\250_\346\214\211\350\257\204\345\210\206\345\217\226TopK.py"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\345\244\215\345\220\210\350\212\202\347\202\271\345\272\223/composite_\345\256\236\344\275\223\345\210\227\350\241\250_\346\235\203\351\207\215\351\232\217\346\234\272\351\200\211\346\213\251\345\256\236\344\275\223.py"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\345\244\215\345\220\210\350\212\202\347\202\271\345\272\223/composite_\345\256\236\344\275\223\345\210\227\350\241\250_\346\237\245\346\211\276\351\246\226\346\254\241\345\207\272\347\216\260\345\272\217\345\217\267.py"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\345\244\215\345\220\210\350\212\202\347\202\271\345\272\223/composite_\345\256\236\344\275\223\345\210\227\350\241\250_\350\277\207\346\273\244_\346\214\211\345\270\203\345\260\224\345\200\274\345\210\227\350\241\250.py"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\345\244\215\345\220\210\350\212\202\347\202\271\345\272\223/composite_\345\270\203\345\260\224\345\200\274\345\210\227\350\241\250_\344\273\273\346\204\217\344\270\272\347\234\237.py"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\345\244\215\345\220\210\350\212\202\347\202\271\345\272\223/composite_\345\270\203\345\260\224\345\200\274\345\210\227\350\241\250_\345\205\250\351\203\250\344\270\272\347\234\237.py"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\345\244\215\345\220\210\350\212\202\347\202\271\345\272\223/composite_\346\225\264\346\225\260\345\210\227\350\241\250_\345\210\207\347\211\207.py"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\345\244\215\345\220\210\350\212\202\347\202\271\345\272\223/composite_\346\225\264\346\225\260\345\210\227\350\241\250_\346\214\211\346\225\264\346\225\260\351\224\256\345\210\206\347\273\204.py"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\345\244\215\345\220\210\350\212\202\347\202\271\345\272\223/composite_\346\225\264\346\225\260\345\210\227\350\241\250_\346\237\245\346\211\276\351\246\226\346\254\241\345\207\272\347\216\260\345\272\217\345\217\267.py"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\345\244\215\345\220\210\350\212\202\347\202\271\345\272\223/composite_\346\225\264\346\225\260\345\210\227\350\241\250_\346\261\202\345\222\214.py"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\345\244\215\345\220\210\350\212\202\347\202\271\345\272\223/composite_\346\225\264\346\225\260\345\210\227\350\241\250_\350\277\207\346\273\244_\346\214\211\345\270\203\345\260\224\345\200\274\345\210\227\350\241\250.py"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\345\244\215\345\220\210\350\212\202\347\202\271\345\272\223/composite_\346\225\264\346\225\260\345\210\227\350\241\250_\351\242\221\346\254\241\347\273\237\350\256\241.py"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\345\244\215\345\220\210\350\212\202\347\202\271\345\272\223/composite_\346\225\264\346\225\260_\346\255\243\346\250\241\350\277\220\347\256\227.py"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\345\244\215\345\220\210\350\212\202\347\202\271\345\272\223/composite_\346\235\241\344\273\266\351\200\211\346\213\251_\346\225\264\346\225\260.py"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\345\244\215\345\220\210\350\212\202\347\202\271\345\272\223/composite_\346\235\241\344\273\266\351\200\211\346\213\251_\346\265\256\347\202\271\346\225\260.py"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\345\244\215\345\220\210\350\212\202\347\202\271\345\272\223/composite_\346\265\256\347\202\271\346\225\260\345\210\227\350\241\250_\346\235\203\351\207\215\351\232\217\346\234\272\351\200\211\346\213\251\345\272\217\345\217\267.py"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\346\226\207\346\241\243/claude.md"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\347\256\241\347\220\206\351\205\215\347\275\256/UI\346\272\220\347\240\201/claude.md"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\347\256\241\347\220\206\351\205\215\347\275\256/\344\277\241\345\217\267/claude.md"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\347\256\241\347\220\206\351\205\215\347\275\256/\347\273\223\346\236\204\344\275\223\345\256\232\344\271\211/\345\237\272\347\241\200\347\273\223\346\236\204\344\275\223/\345\205\250\347\261\273\345\236\213\347\273\223\346\236\204\344\275\223\347\244\272\344\276\213.py"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\347\256\241\347\220\206\351\205\215\347\275\256/\347\273\223\346\236\204\344\275\223\345\256\232\344\271\211/\345\237\272\347\241\200\347\273\223\346\236\204\344\275\223/claude.md"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\347\256\241\347\220\206\351\205\215\347\275\256/claude.md"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\350\212\202\347\202\271\345\233\276/claude.md"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\350\212\202\347\202\271\345\233\276/client/\345\270\203\345\260\224\350\277\207\346\273\244\345\231\250\350\212\202\347\202\271\345\233\276/claude.md"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\350\212\202\347\202\271\345\233\276/client/\346\212\200\350\203\275\350\212\202\347\202\271\345\233\276/claude.md"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\350\212\202\347\202\271\345\233\276/client/\346\225\264\346\225\260\350\277\207\346\273\244\345\231\250\350\212\202\347\202\271\345\233\276/claude.md"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\350\212\202\347\202\271\345\233\276/client/claude.md"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\350\212\202\347\202\271\345\233\276/server/\345\256\236\344\275\223\350\212\202\347\202\271\345\233\276/\346\250\241\346\235\277\347\244\272\344\276\213/\346\250\241\346\235\277\347\244\272\344\276\213_\345\205\261\344\272\253\345\244\215\345\220\210\350\212\202\347\202\271\346\211\251\345\261\225\350\257\255\346\263\225\347\263\226.py"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\350\212\202\347\202\271\345\233\276/server/\345\256\236\344\275\223\350\212\202\347\202\271\345\233\276/\346\250\241\346\235\277\347\244\272\344\276\213/\346\250\241\346\235\277\347\244\272\344\276\213_\345\205\261\344\272\253\345\244\215\345\220\210\350\212\202\347\202\271\350\260\203\347\224\250.py"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\350\212\202\347\202\271\345\233\276/server/\345\256\236\344\275\223\350\212\202\347\202\271\345\233\276/\346\250\241\346\235\277\347\244\272\344\276\213/claude.md"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\350\212\202\347\202\271\345\233\276/server/\345\256\236\344\275\223\350\212\202\347\202\271\345\233\276/claude.md"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\350\212\202\347\202\271\345\233\276/server/\347\212\266\346\200\201\350\212\202\347\202\271\345\233\276/claude.md"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\350\212\202\347\202\271\345\233\276/server/\350\201\214\344\270\232\350\212\202\347\202\271\345\233\276/claude.md"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\350\212\202\347\202\271\345\233\276/server/\351\201\223\345\205\267\350\212\202\347\202\271\345\233\276/claude.md"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/\350\212\202\347\202\271\345\233\276/server/claude.md"
"assets/\350\265\204\346\272\220\345\272\223/\345\205\261\344\272\253/claude.md"
"assets/\350\265\204\346\272\220\345\272\223/\351\241\271\347\233\256\345\255\230\346\241\243/\346\265\213\350\257\225\351\241\271\347\233\256/[[INSTRUCTION]]"
"assets/\350\265\204\346\272\220\345\272\223/\351\241\271\347\233\256\345\255\230\346\241\243/\346\265\213\350\257\225\351\241\271\347\233\256/\345\244\215\345\220\210\350\212\202\347\202\271\345\272\223/[[INSTRUCTION]]"
"assets/\350\265\204\346\272\220\345\272\223/\351\241\271\347\233\256\345\255\230\346\241\243/\346\265\213\350\257\225\351\241\271\347\233\256/\345\244\215\345\220\210\350\212\202\347\202\271\345\272\223/composite_TS_\345\205\250\347\261\273\345\236\213\345\206\231\345\205\245_v1.py"
"assets/\350\265\204\346\272\220\345\272\223/\351\241\271\347\233\256\345\255\230\346\241\243/\346\265\213\350\257\225\351\241\271\347\233\256/\345\244\215\345\220\210\350\212\202\347\202\271\345\272\223/composite_TS_\345\210\227\350\241\250\345\255\227\345\205\270\345\206\231\345\205\245_v1.py"
"assets/\350\265\204\346\272\220\345\272\223/\351\241\271\347\233\256\345\255\230\346\241\243/\346\265\213\350\257\225\351\241\271\347\233\256/\345\244\215\345\220\210\350\212\202\347\202\271\345\272\223/composite_TS_\345\220\210\345\271\266\345\274\225\350\204\232_\346\211\207\345\207\272_v1.py"
"assets/\350\265\204\346\272\220\345\272\223/\351\241\271\347\233\256\345\255\230\346\241\243/\346\265\213\350\257\225\351\241\271\347\233\256/\345\244\215\345\220\210\350\212\202\347\202\271\345\272\223/composite_TS_\345\244\215\345\220\210\345\206\205\345\217\221\351\200\201\344\277\241\345\217\267_v1.py"
"assets/\350\265\204\346\272\220\345\272\223/\351\241\271\347\233\256\345\255\230\346\241\243/\346\265\213\350\257\225\351\241\271\347\233\256/\345\244\215\345\220\210\350\212\202\347\202\271\345\272\223/composite_TS_\345\265\214\345\245\227\345\244\215\345\220\210_\347\273\204\345\220\210_v1.py"
"assets/\350\265\204\346\272\220\345\272\223/\351\241\271\347\233\256\345\255\230\346\241\243/\346\265\213\350\257\225\351\241\271\347\233\256/\345\244\215\345\220\210\350\212\202\347\202\271\345\272\223/composite_TS_\346\234\200\345\260\217\345\270\203\345\260\224\345\244\215\345\220\210_v1.py"
"assets/\350\265\204\346\272\220\345\272\223/\351\241\271\347\233\256\345\255\230\346\241\243/\346\265\213\350\257\225\351\241\271\347\233\256/\346\210\230\346\226\227\351\242\204\350\256\276/[[INSTRUCTION]]"
"assets/\350\265\204\346\272\220\345\272\223/\351\241\271\347\233\256\345\255\230\346\241\243/\346\265\213\350\257\225\351\241\271\347\233\256/\346\210\230\346\226\227\351\242\204\350\256\276/\347\216\251\345\256\266\346\250\241\346\235\277/[[INSTRUCTION]]"
"assets/\350\265\204\346\272\220\345\272\223/\351\241\271\347\233\256\345\255\230\346\241\243/\346\265\213\350\257\225\351\241\271\347\233\256/\346\210\230\346\226\227\351\242\204\350\256\276/\347\216\251\345\256\266\346\250\241\346\235\277/\346\265\213\350\257\225_\345\217\230\351\207\217\346\270\205\345\215\225_\347\216\251\345\256\266\346\250\241\346\235\277.json"
"assets/\350\265\204\346\272\220\345\272\223/\351\241\271\347\233\256\345\255\230\346\241\243/\346\265\213\350\257\225\351\241\271\347\233\256/\347\256\241\347\220\206\351\205\215\347\275\256/[[INSTRUCTION]]"
"assets/\350\265\204\346\272\220\345\272\223/\351\241\271\347\233\256\345\255\230\346\241\243/\346\265\213\350\257\225\351\241\271\347\233\256/\347\256\241\347\220\206\351\205\215\347\275\256/UI\346\272\220\347\240\201/[[INSTRUCTION]]"
"assets/\350\265\204\346\272\220\345\272\223/\351\241\271\347\233\256\345\255\230\346\241\243/\346\265\213\350\257\225\351\241\271\347\233\256/\347\256\241\347\220\206\351\205\215\347\275\256/UI\346\272\220\347\240\201/__hook_tests__/bad_empty_placeholder.html"
"assets/\350\265\204\346\272\220\345\272\223/\351\241\271\347\233\256\345\255\230\346\241\243/\346\265\213\350\257\225\351\241\271\347\233\256/\347\256\241\347\220\206\351\205\215\347\275\256/UI\346\272\220\347\240\201/__hook_tests__/bad_progress_dict_path.html"
"assets/\350\265\204\346\272\220\345\272\223/\351\241\271\347\233\256\345\255\230\346\241\243/\346\265\213\350\257\225\351\241\271\347\233\256/\347\256\241\347\220\206\351\205\215\347\275\256/UI\346\272\220\347\240\201/__hook_tests__/bad_progress_empty_binding.html"
"assets/\350\265\204\346\272\220\345\272\223/\351\241\271\347\233\256\345\255\230\346\241\243/\346\265\213\350\257\225\351\241\271\347\233\256/\347\256\241\347\220\206\351\205\215\347\275\256/UI\346\272\220\347\240\201/__hook_tests__/bad_space_in_expr.html"
"assets/\350\265\204\346\272\220\345\272\223/\351\241\271\347\233\256\345\255\230\346\241\243/\346\265\213\350\257\225\351\241\271\347\233\256/\347\256\241\347\220\206\351\205\215\347\275\256/UI\346\272\220\347\240\201/__hook_tests__/bad_unknown_scope.html"
"assets/\350\265\204\346\272\220\345\272\223/\351\241\271\347\233\256\345\255\230\346\241\243/\346\265\213\350\257\225\351\241\271\347\233\256/\347\256\241\347\220\206\351\205\215\347\275\256/UI\346\272\220\347\240\201/__hook_tests__/claude.md"
"assets/\350\265\204\346\272\220\345\272\223/\351\241\271\347\233\256\345\255\230\346\241\243/\346\265\213\350\257\225\351\241\271\347\233\256/\347\256\241\347\220\206\351\205\215\347\275\256/UI\346\272\220\347\240\201/__hook_tests__/ok_progress_numbers.html"
"assets/\350\265\204\346\272\220\345\272\223/\351\241\271\347\233\256\345\255\230\346\241\243/\346\265\213\350\257\225\351\241\271\347\233\256/\347\256\241\347\220\206\351\205\215\347\275\256/UI\346\272\220\347\240\201/__hook_tests__/ok_simple.html"
"assets/\350\265\204\346\272\220\345\272\223/\351\241\271\347\233\256\345\255\230\346\241\243/\346\265\213\350\257\225\351\241\271\347\233\256/\347\256\241\347\220\206\351\205\215\347\275\256/UI\346\272\220\347\240\201/__workbench_out__/claude.md"
```

## Neighbouring paths

```
app/ui/graph/library_pages/entity_placement/__init__.py
app/ui/graph/library_pages/entity_placement/constants.py
app/ui/graph/library_pages/entity_placement/instance_list_mixin.py
app/ui/graph/library_pages/entity_placement/instance_ops_mixin.py
app/ui/graph/library_pages/entity_placement/level_entity_mixin.py
app/ui/graph/library_pages/entity_placement/merge_decorations_mixin.py
app/ui/graph/library_pages/entity_placement/protocol_mixin.py
app/ui/graph/library_pages/entity_placement/ui_mixin.py
```

## Nearby documentation paths

```
.github/claude.md
.github/workflows/claude.md
CONTRIBUTING.md
LICENSES/claude.md
README.md
app/automation/_static_checks/claude.md
app/automation/capture/claude.md
app/automation/claude.md
app/automation/config/claude.md
app/automation/editor/claude.md
```

## Nearby configuration paths

```
.github/workflows/ci.yml
app/runtime/package_state.json
private_extensions/shape-editor/perfectPixel/pyproject.toml
private_extensions/ugc_file_tools/builtin_resources/bootstrap_min_sections/min_ui_node9.json
private_extensions/ugc_file_tools/builtin_resources/dtype/dtype.json
private_extensions/ugc_file_tools/gia_export/builtin_component_template_base_field_map.json
private_extensions/ugc_file_tools/graph_ir/node_type_semantic_map.json
private_extensions/ugc_file_tools/node_data/index.json
pyrightconfig.json
pytest.ini
```

## Pinned snapshot file excerpts

### snapshot_file_1

```
## 目录用途
`app/ui/graph/library_pages/entity_placement/`：实体摆放页面（`EntityPlacementWidget`）的拆分实现，按“UI装配/页面协议/列表构建/关卡实体/实例操作/装饰物合并”等职责拆成多个 mixin 与工具模块，降低单文件复杂度并便于复用与测试。

## 当前状态
- **入口类**：`app/ui/graph/library_pages/entity_placement_widget.py` 仅保留 `EntityPlacementWidget` 壳与信号定义，并通过组合 mixin 提供完整能力。
- **常量集中**：页面相关的 item role、分类 key、对话框尺寸、向量范围与格式化参数统一收敛到 `[[REF]]`，避免散落魔法数字。
- **实现拆分**：各 mixin 只负责自身职责（例如快捷键/上下文菜单、列表刷新与选中恢复、关卡实体专用逻辑、装饰物合并工作流），写盘/索引移动仍委托 `ResourceManager`/`PackageIndexManager` 等上层组件。
- **模块划分**：`ui_mixin.py`（UI/快捷键/菜单）、`protocol_mixin.py`（页面协议/选中联动）、`instance_list_mixin.py`（列表构建与共享徽章）、`level_entity_mixin.py`（关卡实体）、`instance_ops_mixin.py`（增删改移动等操作）、`merge_decorations_mixin.py`（装饰物合并工作流）。

## 注意事项
- mixin 内不做静默降级或 try/except 吞错；错误应显式抛出或通过既有 UI 提示链路暴露。
- 列表重建必须复用 `rebuild_list_with_preserved_selection` 以保证“信号阻塞 + 选中恢复”语义稳定，避免右侧面板联动抖动。
- 涉及资源归属移动/删除的语义需继续区分 `PackageView` 与 `GlobalResourceView`，不要在页面层直接散落文件 I/O。


```

### snapshot_file_2

```
"""实体摆放页面的拆分实现子包。"""


```

### snapshot_file_3

```
"""实体摆放页面常量。"""

from __future__ import annotations

from PyQt6 import QtCore

# QListWidget item roles -------------------------------------------------------

INSTANCE_ID_ROLE = QtCore.Qt.ItemDataRole.UserRole
ENTITY_TYPE_ROLE = QtCore.Qt.ItemDataRole.UserRole + 1
SEARCH_TEXT_ROLE = QtCore.Qt.ItemDataRole.UserRole + 2
IS_SHARED_INSTANCE_ROLE = QtCore.Qt.ItemDataRole.UserRole + 3

# Category keys ----------------------------------------------------------------

CATEGORY_ALL = "all"
CATEGORY_LEVEL_ENTITY = "level_entity"

# Level entity visual semantics -------------------------------------------------

LEVEL_ENTITY_ICON = "📍"
LEVEL_ENTITY_LABEL_TEXT = "关卡实体"

# Form dialog / editor ranges ---------------------------------------------------

NEW_INSTANCE_DIALOG_SIZE = (520, 640)
POSITION_EDITOR_MIN = -10000
POSITION_EDITOR_MAX = 10000
ROTATION_EDITOR_MIN = -360
ROTATION_EDITOR_MAX = 360

# Display formatting ------------------------------------------------------------

VECTOR_DISPLAY_DECIMALS = 1
DEFAULT_VECTOR3 = (0.0, 0.0, 0.0)

# Formatting helpers -----------------------------------------------------------


def format_vector3(vector: list[float] | tuple[float, ...], *, decimals: int = VECTOR_DISPLAY_DECIMALS) -> str:
    """将三维向量格式化为 (x, y, z) 文本。"""
    x, y, z = vector
    fmt = "{:." + str(int(decimals)) + "f}"
    return f"({fmt.format(float(x))}, {fmt.format(float(y))}, {fmt.format(float(z))})"

# Decorations merge -------------------------------------------------------------

MERGE_TARGET_NEW_INSTANCE_ID = "__new__"
MERGE_CARRIER_TEMPLATE_ID_PREFIX = "shape_editor_empty__"


```

### snapshot_file_4

```
"""实体摆放页面的实例列表构建与刷新逻辑。"""

from __future__ import annotations

import functools
from pathlib import Path
from typing import Any, Optional

from PyQt6 import QtWidgets

from app.ui.foundation.shared_resource_badge_delegate import SHARED_RESOURCE_BADGE_ROLE
from app.ui.graph.library_mixins import rebuild_list_with_preserved_selection
from app.ui.graph.library_pages.entity_placement.constants import (
    CATEGORY_ALL,
    CATEGORY_LEVEL_ENTITY,
    ENTITY_TYPE_ROLE,
    INSTANCE_ID_ROLE,
    IS_SHARED_INSTANCE_ROLE,
    SEARCH_TEXT_ROLE,
    VECTOR_DISPLAY_DECIMALS,
    format_vector3,
)
from engine.configs.resource_types import ResourceType
from engine.graph.models.entity_templates import (
    get_entity_type_info,
    get_template_library_entity_types,
)
from engine.graph.models.package_model import InstanceConfig, TemplateConfig
from engine.resources.resource_manager import ResourceManager
from engine.utils.resource_library_layout import get_shared_root_dir


_SPECIAL_TEMPLATE_CATEGORIES = {"元件组", "掉落物"}


class EntityPlacementInstanceListMixin:
    """实体摆放页面实例列表 mixin。"""

    def _rebuild_instances(self) -> None:
        """根据当前分类重建右侧实体列表。"""
        previously_selected_id = self._current_instance_id()
        if not self.current_package:
            self.entity_list.clear()
            return

        effective_category = self.current_category or CATEGORY_ALL
        if effective_category == CATEGORY_LEVEL_ENTITY:
            self.entity_list.clear()
            self._rebuild_level_entity_view(previously_selected_id)
            return

        allowed_types = set(get_template_library_entity_types())
        shared_instance_ids = self._collect_shared_instance_ids()
        build_items = functools.partial(
            self._build_instance_items,
            effective_category=effective_category,
            allowed_types=allowed_types,
            shared_instance_ids=shared_instance_ids,
        )
        on_cleared = functools.partial(
            self._emit_em
```

### snapshot_file_5

```
"""实体摆放页面的实例操作逻辑。"""

from __future__ import annotations

import copy
import types
from typing import Optional

from PyQt6 import QtCore, QtWidgets

from app.ui.foundation import input_dialogs
from app.ui.foundation.id_generator import generate_prefixed_id
from app.ui.foundation.toast_notification import ToastNotification
from app.ui.forms.schema_dialog import FormDialogBuilder
from app.ui.graph.library_pages.entity_placement.constants import (
    CATEGORY_LEVEL_ENTITY,
    DEFAULT_VECTOR3,
    INSTANCE_ID_ROLE,
    IS_SHARED_INSTANCE_ROLE,
    NEW_INSTANCE_DIALOG_SIZE,
    POSITION_EDITOR_MAX,
    POSITION_EDITOR_MIN,
    ROTATION_EDITOR_MAX,
    ROTATION_EDITOR_MIN,
)
from app.ui.graph.library_pages.library_scaffold import LibraryChangeEvent
from app.ui.graph.library_pages.library_view_scope import describe_resource_view_scope
from engine.configs.resource_types import ResourceType
from engine.graph.models.entity_templates import get_template_library_entity_types
from engine.graph.models.package_model import InstanceConfig, TemplateConfig
from engine.resources.global_resource_view import GlobalResourceView
from engine.resources.package_index_manager import PackageIndexManager
from engine.resources.package_view import PackageView
from engine.resources.resource_manager import ResourceManager


class EntityPlacementInstanceOpsMixin:
    """实体摆放页面实例操作 mixin。"""

    def _current_instance_id(self) -> Optional[str]:
        """返回当前列表选中的实例 ID。"""
        current_item = self.entity_list.currentItem()
        if current_item is None:
            return None
        instance_id = current_item.data(INSTANCE_ID_ROLE)
        return instance_id if isinstance(instance_id, str) else None

    def select_instance(self, instance_id: str) -> None:
        """在列表中选中并滚动到指定实例。"""
        for row in range(self.entity_list.count()):
            item = self.entity_list.item(row)
            if item and item.data(INSTANCE_ID_ROLE) == instance_id:
                self.entity_list.setCurren
```

### snapshot_file_6

```
"""实体摆放页面的关卡实体逻辑。"""

from __future__ import annotations

from typing import Optional

from PyQt6 import QtWidgets

from app.ui.foundation.id_generator import generate_prefixed_id
from app.ui.graph.library_pages.entity_placement.constants import (
    DEFAULT_VECTOR3,
    ENTITY_TYPE_ROLE,
    INSTANCE_ID_ROLE,
    LEVEL_ENTITY_ICON,
    SEARCH_TEXT_ROLE,
    VECTOR_DISPLAY_DECIMALS,
    format_vector3,
)
from engine.graph.models.package_model import InstanceConfig
from engine.resources.global_resource_view import GlobalResourceView
from engine.resources.package_view import PackageView


class EntityPlacementLevelEntityMixin:
    """实体摆放页面关卡实体 mixin。"""

    def _is_level_entity_instance_id(self, instance_id: str) -> bool:
        """判断给定 instance_id 是否为当前视图的关卡实体。"""
        if not self.current_package:
            return False
        level_entity = getattr(self.current_package, "level_entity", None)
        if not level_entity:
            return False
        level_instance_id = getattr(level_entity, "instance_id", "")
        return isinstance(level_instance_id, str) and level_instance_id == instance_id

    def _rebuild_level_entity_view(self, previously_selected_id: Optional[str]) -> None:
        """在关卡实体分类下重建右侧列表。"""
        _ = previously_selected_id
        level_entity = getattr(self.current_package, "level_entity", None) if self.current_package else None
        if not level_entity:
            return

        level_entity_item = self._create_level_entity_item(level_entity)
        self.entity_list.addItem(level_entity_item)
        self.entity_list.setCurrentRow(0)
        self._emit_current_selection_or_clear()

    def _append_level_entity_in_all_category(self, displayed_instance_ids: set[str]) -> None:
        """在全部实体分类下追加关卡实体条目。"""
        if not self.current_package:
            return

        level_entity = getattr(self.current_package, "level_entity", None)
        if not level_entity:
            return

        if not isinstance(level_entity.
```

### snapshot_file_7

```
# .github 目录

## 目录用途
- 存放 GitHub 平台相关的仓库元数据：CI 工作流、Issue/PR 模板、自动化策略等。
- 目标：让仓库在 GitHub 上“可验证、可协作、可维护”，但不引入任何运行期依赖或业务逻辑。

## 当前状态
- `workflows/`：仅包含最小 CI（Windows + pytest），用于保护引擎/工具链的基础回归。

## 注意事项
- 不在此目录存放任何私密信息（密钥/Token/账号等）；CI 侧需要的敏感信息必须通过 GitHub Secrets 注入。
- 展示型发布策略：`docs/` 不随仓库分发；CI 只依赖仓库中公开的测试与示例资源。

---
注意：本文件不记录任何修改历史，仅描述 `.github` 目录的用途、当前状态与使用注意事项。



```

### snapshot_file_8

```
# GitHub Actions 工作流目录（.github/workflows）

## 目录用途
存放 CI 工作流定义，用于在 PR/Push 时强制执行仓库护栏与回归测试，确保“节点库（SoT）变更”必须显式可见并可机器判定 breaking。

## 当前状态
- `ci.yml`：Windows（PowerShell）流水线，按顺序执行：
  - 自动化静态扫描护栏：`app.automation._static_checks.*`
  - UI 静态护栏：`app.ui._static_checks.check_large_files --fail --max-lines 1500`
  - 节点图/复合节点全量校验（CI gate：仅 error 阻断，warning 仅记录到 JSON 报告）：`app.cli.graph_tools validate-graphs --all --json` + `tools/validate_graphs_ci_gate.py`
  - 单测：`pytest`

## 注意事项
- PowerShell 不使用 `&&`；命令以逐行方式执行。
- 如需恢复“节点库 manifest 快照卡点 / 派生文档一致性检查”，请先将对应工具链模块纳入仓库版本管理，再在 CI 中启用（避免引用不存在的 `tools.*` 模块）。


```

### snapshot_file_9

```
# 贡献指南

本仓库是面向原神“千星奇域”的离线沙箱编辑器与 Graph Code 工具链。

对大多数使用者来说：**只需要编写节点图 Graph Code，不要修改引擎（engine/）/工具链代码**（见 `docs/用户必读.md`）。  
如果你发现了引擎 BUG，推荐先通过 Issue/群反馈给作者并提供最小可复现；如确需提交代码改动，请先开 Issue 与作者对齐方向。

## 你可以贡献什么
- 反馈问题并提供**最小可复现**（优先：报错输出 + 单文件复现）
- 为重要规则补充回归测试（优先）
- 改进用户文档（例如 `README.md`、`docs/用户必读.md`、各公开目录的 `claude.md`）
- 在 Issue 讨论达成一致后，提交引擎/工具链的 bug 修复或改进

## 你不应该提交什么
- 任何私密资源、账号信息、Token、截图、个人工程存档
- 不应公开的资源库内容（例如本地私有 `assets/资源库/` 资源、OCR 模板、个人项目存档等）
- 运行期缓存与本地状态（见根目录 `.gitignore`）

## 开发环境
- Windows 10/11
- Python 3.10 - 3.12（推荐 3.10.x，不支持 3.13）
- 依赖安装（PowerShell，逐行执行）：

'''powershell
pip install -r requirements-dev.txt -c constraints.txt
'''

## 运行测试

'''powershell
python -X utf8 -m pytest
'''

## 节点库变更（重要：SoT + 可回归）

当你修改以下目录时，视为“节点库变更”（端口/类型/约束/语义/兼容性都会影响历史资产）：
- `plugins/nodes/**`（基础节点：`@node_spec(...)` 为单一事实源）
- `assets/资源库/共享/复合节点库/**` 与 `assets/资源库/项目存档/<项目存档名>/复合节点库/**`（复合节点：同属节点库的一部分）

### 必跑护栏（推荐用一键入口）

'''powershell
# 运行回归测试
python -X utf8 -m pytest

# 校验（单文件调试，开发期推荐）
python -X utf8 -m app.cli.graph_tools validate-file <对应文件路径>

# 校验（节点图/复合节点 + 项目存档，全量扫描）
python -X utf8 -m app.cli.graph_tools validate-graphs --all
python -X utf8 -m app.cli.graph_tools validate-project
'''

说明：
- `tests/snapshots/node_library_manifest.json` 为节点库 manifest baseline（不建议手工编辑；如需变更请走维护流程）。
- `docs/generated/node_library/` 为自动生成参考文档（端口/类型/约束等接口真相），禁止手工编辑。

### 兼容性约定（避免 breaki
```

### snapshot_file_10

```
name: CI

on:
  push:
  pull_request:

jobs:
  windows:
    runs-on: windows-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        shell: pwsh
        run: |
          python -m pip install --upgrade pip
          python -m pip install -r requirements-dev.txt -c constraints.txt

      - name: Static checks (automation)
        shell: pwsh
        env:
          PYTHONUTF8: "1"
        run: |
          python -X utf8 -m app.automation._static_checks.no_direct_vision_bridge_import
          python -X utf8 -m app.automation._static_checks.no_custom_chinese_regex_or_similarity
          python -X utf8 -m app.automation._static_checks.check_executor_protocol

      - name: Static checks (ui)
        shell: pwsh
        env:
          PYTHONUTF8: "1"
        run: |
          python -X utf8 -m app.ui._static_checks.check_large_files --fail --max-lines 1500

      - name: Validate graphs (all)
        shell: pwsh
        env:
          PYTHONUTF8: "1"
        run: |
          New-Item -ItemType Directory -Force tmp\artifacts | Out-Null
          python -X utf8 -m app.cli.graph_tools validate-graphs --all --json | Set-Content -Encoding utf8 tmp\artifacts\validate_graphs_ci_report.json
          python -X utf8 tools\validate_graphs_ci_gate.py tmp\artifacts\validate_graphs_ci_report.json

      - name: Pytest
        shell: pwsh
        env:
          PYTHONUTF8: "1"
        run: |
          python -X utf8 -m pytest -q



```
