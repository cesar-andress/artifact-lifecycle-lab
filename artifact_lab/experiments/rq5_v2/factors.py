"""Factor encoding for the RQ5 v2 2×2×2 + absent factorial design."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CellCode(str, Enum):
    """Five within-case cells (four present + one absent)."""

    T_L = "T+L"  # truthful, load-bearing, instruction present
    F_L = "F+L"  # false, load-bearing, instruction present
    T_P = "T+P"  # truthful, peripheral, instruction present
    F_P = "F+P"  # false, peripheral, instruction present
    N = "N"  # instruction absent (presence control)


PRESENT_CELLS: tuple[CellCode, ...] = (
    CellCode.T_L,
    CellCode.F_L,
    CellCode.T_P,
    CellCode.F_P,
)
ALL_CELLS: tuple[CellCode, ...] = PRESENT_CELLS + (CellCode.N,)


@dataclass(frozen=True)
class FactorLevels:
    """Factor A × B × C levels for one experimental cell."""

    instruction_present: bool
    reference_truthful: bool | None
    load_bearing: bool | None

    @property
    def factor_a(self) -> str:
        return "present" if self.instruction_present else "absent"

    @property
    def factor_b(self) -> str:
        if not self.instruction_present:
            return "na"
        return "truthful" if self.reference_truthful else "false"

    @property
    def factor_c(self) -> str:
        if not self.instruction_present:
            return "na"
        return "yes" if self.load_bearing else "no"


def levels_for_cell(cell: CellCode | str) -> FactorLevels:
    code = CellCode(cell)
    if code == CellCode.N:
        return FactorLevels(instruction_present=False, reference_truthful=None, load_bearing=None)
    if code == CellCode.T_L:
        return FactorLevels(instruction_present=True, reference_truthful=True, load_bearing=True)
    if code == CellCode.F_L:
        return FactorLevels(instruction_present=True, reference_truthful=False, load_bearing=True)
    if code == CellCode.T_P:
        return FactorLevels(instruction_present=True, reference_truthful=True, load_bearing=False)
    if code == CellCode.F_P:
        return FactorLevels(instruction_present=True, reference_truthful=False, load_bearing=False)
    raise ValueError(f"unknown cell: {cell}")


def cell_from_factors(
    *,
    instruction_present: bool,
    reference_truthful: bool,
    load_bearing: bool,
) -> CellCode:
    if not instruction_present:
        return CellCode.N
    if reference_truthful and load_bearing:
        return CellCode.T_L
    if not reference_truthful and load_bearing:
        return CellCode.F_L
    if reference_truthful and not load_bearing:
        return CellCode.T_P
    return CellCode.F_P


def truth_x_load_bearing(levels: FactorLevels) -> int | None:
    """Interaction indicator for H4 (1 only when both B and C apply)."""
    if not levels.instruction_present:
        return None
    t = 1 if levels.reference_truthful else 0
    lb = 1 if levels.load_bearing else 0
    return t * lb


def false_load_bearing_cell(levels: FactorLevels) -> bool:
    """H3 mediation domain: false reference on load-bearing path."""
    return (
        levels.instruction_present
        and levels.reference_truthful is False
        and levels.load_bearing is True
    )
