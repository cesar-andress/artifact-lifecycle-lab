"""Instruction variant synthesis for factorial cells."""

from __future__ import annotations

import hashlib

from artifact_lab.experiments.rq5_v2.factors import CellCode, levels_for_cell
from artifact_lab.experiments.rq5_v2.models import FactorialCell
from artifact_lab.store.blobs import BlobStore

RELATED_SECTION = "\n\n## Related files\n\n"
LB_TASK_TEMPLATE = (
    "Complete the bounded coding task described in the project instruction file. "
    "Treat the instruction file as authoritative project context. "
    "You must modify `{target}` to satisfy the required change. "
    "Use only the repository state at the pinned commit. "
    "Run `{test_command}` before finishing."
)
PB_TASK_TEMPLATE = (
    "Complete the bounded coding task described in the project instruction file. "
    "Modify `{decoy}` only to satisfy the required change. "
    "Do not edit other files unless required by tests. "
    "Use only the repository state at the pinned commit. "
    "Run `{test_command}` before finishing."
)
ABSENT_TASK_TEMPLATE = (
    "Complete the bounded coding task using only the repository at the pinned commit. "
    "Modify `{decoy}` with a small, bounded change verifiable by tests. "
    "Run `{test_command}` before finishing. "
    "No project instruction file is provided for this run."
)


def derive_false_path(true_path: str) -> str:
    """Deterministic false anchor (typo suffix) for false cells."""
    path = true_path.strip().strip("`")
    if path.startswith("@"):
        return f"{path}-missing"
    if "/" in path:
        parent, name = path.rsplit("/", 1)
        return f"{parent}/_{name}.missing"
    return f"_{path}.missing"


def derive_decoy_path(true_path: str, instruction_path: str) -> str:
    """Peripheral-task decoy: sibling README or tests stub."""
    if true_path.endswith(".md"):
        return "README.md"
    if "test" in true_path.lower():
        base = true_path.rsplit("/", 1)[0] if "/" in true_path else "."
        return f"{base}/README.md" if base != "." else "README.md"
    parts = true_path.split("/")
    if len(parts) > 1:
        return "/".join(parts[:-1] + ["README.md"])
    return "README.md"


def _inject_lb_section(text: str, anchor: str, *, test_command: str) -> str:
    block = (
        f"\n\n## Task requirement (load-bearing)\n\n"
        f"To complete this task, modify `{anchor}` with a minimal bounded change. "
        f"Run `{test_command}` before finishing.\n"
    )
    return text.rstrip() + block


def _inject_pb_section(text: str, anchor: str, decoy: str) -> str:
    if RELATED_SECTION.strip() in text:
        return text.replace(
            RELATED_SECTION.strip(),
            f"{RELATED_SECTION}{anchor}\n",
            1,
        )
    return text.rstrip() + f"{RELATED_SECTION}- `{anchor}` (context only; do not edit)\n"


def _swap_anchor(text: str, true_path: str, cited: str) -> str:
    if true_path == cited:
        return text
    return text.replace(true_path, cited).replace(f"`{true_path}`", f"`{cited}`")


def build_cell_instruction_text(
    *,
    base_text: str,
    cell_code: CellCode | str,
    anchor_true: str,
    anchor_false: str,
    decoy_path: str,
    test_command: str,
) -> tuple[str, str, bool]:
    """
    Return (instruction_text, cited_anchor, mechanical_truth) for a cell.

    mechanical_truth: cited path should exist at commit (verifier gate).
    """
    code = CellCode(cell_code)
    levels = levels_for_cell(code)
    text = base_text

    if code == CellCode.N:
        return "", "", True

    cited = anchor_true if levels.reference_truthful else anchor_false
    mechanical = bool(levels.reference_truthful)

    if levels.load_bearing:
        text = _inject_lb_section(text, cited, test_command=test_command)
    else:
        text = _inject_pb_section(text, anchor_true, decoy=decoy_path)
        if not levels.reference_truthful:
            text = _swap_anchor(text, anchor_true, cited)

    if not levels.reference_truthful and levels.load_bearing:
        text = _swap_anchor(text, anchor_true, cited)

    return text, cited, mechanical


def build_task_prompt(
    *,
    cell_code: CellCode | str,
    anchor_true: str,
    decoy_path: str,
    test_command: str,
    cited_anchor: str,
    load_bearing: bool,
) -> str:
    code = CellCode(cell_code)
    if code == CellCode.N:
        return ABSENT_TASK_TEMPLATE.format(decoy=decoy_path, test_command=test_command)
    if load_bearing:
        return LB_TASK_TEMPLATE.format(target=cited_anchor, test_command=test_command)
    return PB_TASK_TEMPLATE.format(decoy=decoy_path, test_command=test_command)


def build_factorial_cells(
    *,
    base_instruction_text: str,
    anchor_true: str,
    test_command: str,
    blob_store: BlobStore,
    anchor_false: str | None = None,
    decoy_path: str | None = None,
) -> dict[str, FactorialCell]:
    """Materialize all five cell variants into the blob store."""
    false_path = anchor_false or derive_false_path(anchor_true)
    decoy = decoy_path or derive_decoy_path(anchor_true, "")

    cells: dict[str, FactorialCell] = {}
    for code in CellCode:
        if code == CellCode.N:
            cells[code.value] = FactorialCell(
                cell_code=code.value,
                instruction_blob_sha="",
                cited_anchor=anchor_true,
                mechanical_truth=True,
                task_prompt=build_task_prompt(
                    cell_code=code,
                    anchor_true=anchor_true,
                    decoy_path=decoy,
                    test_command=test_command,
                    cited_anchor=anchor_true,
                    load_bearing=False,
                ),
                load_bearing=False,
            )
            continue

        levels = levels_for_cell(code)
        text, cited, mechanical = build_cell_instruction_text(
            base_text=base_instruction_text,
            cell_code=code,
            anchor_true=anchor_true,
            anchor_false=false_path,
            decoy_path=decoy,
            test_command=test_command,
        )
        blob_sha = blob_store.put_text(text.encode("utf-8"))
        cells[code.value] = FactorialCell(
            cell_code=code.value,
            instruction_blob_sha=blob_sha,
            cited_anchor=cited,
            mechanical_truth=mechanical,
            task_prompt=build_task_prompt(
                cell_code=code,
                anchor_true=anchor_true,
                decoy_path=decoy,
                test_command=test_command,
                cited_anchor=cited,
                load_bearing=bool(levels.load_bearing),
            ),
            load_bearing=bool(levels.load_bearing),
        )
    return cells


def case_id_from_candidate(candidate_id: str, commit_sha: str) -> str:
    digest = hashlib.sha256(f"{candidate_id}:{commit_sha}".encode()).hexdigest()
    return digest[:16]
