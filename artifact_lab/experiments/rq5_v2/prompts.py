"""Agent prompts for factorial cells."""

from __future__ import annotations

from artifact_lab.experiments.rq5_v2.factors import CellCode, levels_for_cell
from artifact_lab.experiments.rq5_v2.models import FactorialCase


def build_factorial_prompt(case: FactorialCase, *, cell_code: str) -> str:
    """Vendor-neutral task prompt for one cell."""
    cell = case.get_cell(cell_code)
    levels = levels_for_cell(cell_code)

    lines = [cell.task_prompt, ""]

    if levels.instruction_present:
        lines.extend(
            [
                f"Instruction file (authoritative when present): `{case.instruction_path}`",
                f"Cited anchor in instruction: `{cell.cited_anchor}`",
            ]
        )
    else:
        lines.append("No project instruction file is provided for this run.")

    lines.extend(
        [
            f"Test command: `{case.test_command}`",
            "",
            "Constraints:",
            "- Use only files in this repository snapshot.",
            "- Do not fetch new commits or use network except running tests.",
            "- Make a small, bounded change verifiable by the test command.",
        ]
    )

    if cell_code in (CellCode.T_P.value, CellCode.F_P.value):
        lines.append(f"- Required edit target (peripheral task): `{case.decoy_path}` only.")

    return "\n".join(lines)
