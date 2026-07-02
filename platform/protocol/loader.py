"""Load YAML protocol families."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

FAMILIES_DIR = Path(__file__).resolve().parent / "families"


@lru_cache(maxsize=16)
def load_family(name: str) -> dict:
    path = FAMILIES_DIR / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"protocol family not found: {name} ({path})")
    with path.open(encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    if cfg.get("family") != name:
        raise ValueError(f"protocol family mismatch: expected {name}, got {cfg.get('family')}")
    return cfg


def family_version(name: str) -> str:
    return str(load_family(name).get("version", "0.0.0"))
