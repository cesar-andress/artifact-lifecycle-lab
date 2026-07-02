"""Artifact lifecycle research platform.

This package name shadows the stdlib ``platform`` module. We re-export the
stdlib API so third-party libraries (pytest, pyarrow, uuid, …) keep working,
while subpackages ``platform.ingest``, ``platform.derive``, etc. remain available.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_PKG_DIR = Path(__file__).resolve().parent
__path__ = [str(_PKG_DIR)]


def _load_stdlib_platform() -> None:
    stdlib_file = (
        Path(sys.base_prefix)
        / "lib"
        / f"python{sys.version_info.major}.{sys.version_info.minor}"
        / "platform.py"
    )
    if not stdlib_file.exists():
        return
    spec = importlib.util.spec_from_file_location("_stdlib_platform", stdlib_file)
    if spec is None or spec.loader is None:
        return
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for name in dir(mod):
        if name.startswith("_"):
            continue
        globals()[name] = getattr(mod, name)


_load_stdlib_platform()

__version__ = "0.1.0"
