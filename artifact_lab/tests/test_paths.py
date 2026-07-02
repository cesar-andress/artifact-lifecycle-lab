"""Canonical path constants."""

from artifact_lab.contracts.paths import EXTRACTION_QUEUE_PATH


def test_extraction_queue_path():
    assert EXTRACTION_QUEUE_PATH == __import__("pathlib").Path("data/state/extraction_jobs.db")
