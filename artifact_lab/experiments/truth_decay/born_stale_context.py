"""Load instruction-file context snippets for born-stale adjudication."""

from __future__ import annotations

import re
from pathlib import Path

import pyarrow.parquet as pq

from artifact_lab.experiments.truth_decay.longitudinal import load_instruction_file_events
from artifact_lab.store.blobs import BlobStore


def build_blob_index(
    l1_paths: list[Path],
    *,
    family: str = "ai_conventions_v1",
) -> dict[tuple[str, str, str], str]:
    """Map (repo_id, instruction_path, commit_sha) -> blob_sha."""
    grouped = load_instruction_file_events(l1_paths, family=family)
    index: dict[tuple[str, str, str], str] = {}
    for (repo_id, instruction_path), events in grouped.items():
        for ev in events:
            sha = (ev.get("blob_sha") or "").strip()
            commit = (ev.get("commit_sha") or ev.get("commit") or "").strip()
            if sha and commit:
                index[(repo_id, instruction_path, commit)] = sha
    return index


def extract_snippet(text: str, reference: str, *, window: int = 240) -> str:
    """Return local context around first occurrence of reference in instruction text."""
    if not text or not reference:
        return ""
    idx = text.find(reference)
    if idx < 0:
        # Try basename for path-like refs
        base = reference.rstrip("/").split("/")[-1]
        if base and base != reference:
            idx = text.find(base)
    if idx < 0:
        return text[: window * 2].strip()
    start = max(0, idx - window)
    end = min(len(text), idx + len(reference) + window)
    snippet = text[start:end].replace("\n", " ").strip()
    snippet = re.sub(r"\s+", " ", snippet)
    return snippet[:500]


def load_snippet_for_trajectory(
    *,
    repo_id: str,
    instruction_path: str,
    commit: str,
    reference: str,
    blob_index: dict[tuple[str, str, str], str],
    blob_store: BlobStore,
) -> tuple[str, bool]:
    sha = blob_index.get((repo_id, instruction_path, commit), "")
    if not sha:
        return "", False
    try:
        text = blob_store.get_text(sha).decode("utf-8", errors="replace")
    except OSError:
        return "", False
    return extract_snippet(text, reference), True
