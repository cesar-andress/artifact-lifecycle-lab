"""Versioned core dataset path conventions."""

from __future__ import annotations

from pathlib import Path

L1_DATASET_NAME = "file_event_log"
L1_DATASET_VERSION = "v1"

L2_DATASET_NAME = "file_state_panel"
L2_DATASET_VERSION = "v1"


def l1_dataset_dir(data_root: Path = Path("data")) -> Path:
    return data_root / "l1" / L1_DATASET_NAME / L1_DATASET_VERSION


def l2_dataset_dir(data_root: Path = Path("data")) -> Path:
    return data_root / "derived" / L2_DATASET_NAME / L2_DATASET_VERSION
