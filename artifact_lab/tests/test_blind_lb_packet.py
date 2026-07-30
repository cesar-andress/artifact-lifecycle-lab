"""Tests for RQ5 v1 blind load-bearing packet infrastructure."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from artifact_lab.experiments.truth_decay.rq5_experiment.blind_lb_derive import (
    derive_final_classification,
)
from artifact_lab.experiments.truth_decay.rq5_experiment.blind_lb_packet import (
    PROTOCOL_VERSION,
    build_packet_for_case,
    generate_packets,
    leakage_hits,
    sanitize_text,
    stable_neutral_id,
    treatment_specific_strings,
)
from artifact_lab.store.blobs import BlobStore

SCHEMA_PATH = Path(
    "artifact_lab/experiments/truth_decay/rq5_experiment/blind_lb_form_schema.json"
)


def test_derive_load_bearing_only_when_directly_relevant_and_material():
    out = derive_final_classification("directly_relevant", "materially_necessary")
    assert out["final_classification"] == "load_bearing"
    assert out["consistency_warning"] is False


def test_derive_contextual_plus_material_is_non_load_bearing_with_warning():
    """Authoritative protocol: NOT the earlier draft rule."""
    out = derive_final_classification("contextually_relevant", "materially_necessary")
    assert out["final_classification"] == "non_load_bearing"
    assert out["consistency_warning"] is True
    assert out["warning_code"] == "contextual_but_materially_necessary"


def test_derive_irrelevant_material_warns():
    out = derive_final_classification("irrelevant", "materially_necessary")
    assert out["final_classification"] == "non_load_bearing"
    assert out["consistency_warning"] is True
    assert out["warning_code"] == "irrelevant_but_materially_necessary"


def test_derive_directly_relevant_not_necessary_warns():
    out = derive_final_classification("directly_relevant", "not_necessary")
    assert out["final_classification"] == "non_load_bearing"
    assert out["consistency_warning"] is True


def test_derive_ambiguous_short_circuits():
    assert derive_final_classification("ambiguous", "materially_necessary")["final_classification"] == "ambiguous"
    assert derive_final_classification("directly_relevant", "ambiguous")["final_classification"] == "ambiguous"


def test_form_schema_valid_and_omits_final_label_enum_for_raters():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert "reference_relevance" in schema["properties"]
    assert "material_necessity" in schema["properties"]
    assert "final_classification" not in schema["properties"]
    assert schema["properties"]["protocol_version"]["const"] == PROTOCOL_VERSION


def test_neutral_ids_deterministic():
    a = stable_neutral_id("caseAAA", seed=42)
    b = stable_neutral_id("caseAAA", seed=42)
    c = stable_neutral_id("caseAAA", seed=7)
    d = stable_neutral_id("caseBBB", seed=42)
    assert a == b
    assert a != c
    assert a != d


def test_sanitize_and_treatment_ban_list():
    text_a = "See docs/config.toml for settings.\n"
    text_b = "See docs/config.toml and missing/false_path.yaml for settings.\n"
    banned = treatment_specific_strings(text_a, text_b, "docs/config.toml")
    assert "missing/false_path.yaml" in banned
    assert "docs/config.toml" in banned
    sanitized = sanitize_text(text_b, banned)
    assert "missing/false_path.yaml" not in sanitized
    assert "docs/config.toml" not in sanitized
    assert "[[REF]]" in sanitized


def _store_with(blobs: Path, content_a: str, content_b: str) -> tuple[BlobStore, str, str]:
    store = BlobStore(blobs)
    sha_a = store.put_text(content_a.encode("utf-8"))
    sha_b = store.put_text(content_b.encode("utf-8"))
    return store, sha_a, sha_b


def test_packet_build_redacts_paths_and_omits_case_id(tmp_path: Path):
    store, sha_a, sha_b = _store_with(
        tmp_path / "blobs",
        "# Guide\nOpen `src/app.py` before testing.\n",
        "# Guide\nOpen `src/app.py` or `ghost/missing.py` before testing.\n",
    )
    row = {
        "case_id": "deadbeefcafebabe",
        "repo_id": "abc123",
        "repo_url": "https://github.com/example/demo",
        "instruction_path": "AGENTS.md",
        "task_commit_sha": "1" * 40,
        "anchor_reference": "src/app.py",
        "anchor_reference_type": "path",
        "condition_a_blob_sha": sha_a,
        "condition_b_blob_sha": sha_b,
        "task_prompt": "Complete the bounded coding task described in the project instruction file.",
        "test_command": "pytest",
    }
    result = build_packet_for_case(row, seed=42, blob_store=store, candidate=None)
    assert result.packet_md is not None
    assert result.eligibility.eligibility_status in {"eligible", "requires_manual_packet_review"}
    assert "deadbeefcafebabe" not in result.packet_md
    assert "src/app.py" not in result.packet_md
    assert "ghost/missing.py" not in result.packet_md
    assert "condition_a" not in result.packet_md.lower()
    assert "born_stale" not in result.packet_md.lower()
    assert "[[REF]]" in result.packet_md
    assert "case_id" not in (result.packet_json or {})


def test_missing_blob_is_source_unavailable(tmp_path: Path):
    store = BlobStore(tmp_path / "blobs")
    row = {
        "case_id": "missingblob0001",
        "repo_id": "abc",
        "repo_url": "https://github.com/example/x",
        "instruction_path": "AGENTS.md",
        "task_commit_sha": "1" * 40,
        "anchor_reference": "a.py",
        "anchor_reference_type": "path",
        "condition_a_blob_sha": "0" * 64,
        "condition_b_blob_sha": "1" * 64,
        "task_prompt": "Do the task.",
        "test_command": "pytest",
    }
    result = build_packet_for_case(row, seed=42, blob_store=store, candidate=None)
    assert result.packet_md is None
    assert result.eligibility.eligibility_status == "source_unavailable"


def test_generate_packets_separates_private_map(tmp_path: Path):
    store, sha_a, sha_b = _store_with(
        tmp_path / "blobs",
        "Use `lib/util.py` in tests.\n",
        "Use `lib/util.py` in tests.\n",
    )
    manifest = tmp_path / "manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "case_id",
                "spec_id",
                "repo_id",
                "repo_url",
                "instruction_path",
                "task_commit_sha",
                "anchor_reference",
                "anchor_reference_type",
                "condition_a_blob_sha",
                "condition_b_blob_sha",
                "born_stale_commit_sha",
                "truthful_commit_sha",
                "task_prompt",
                "test_command",
                "selection_reason",
                "confirmed_false",
                "p1_sample",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "case_id": "caseid0000000001",
                "spec_id": "spec1",
                "repo_id": "repoid1",
                "repo_url": "https://github.com/example/proj",
                "instruction_path": "AGENTS.md",
                "task_commit_sha": "a" * 40,
                "anchor_reference": "lib/util.py",
                "anchor_reference_type": "path",
                "condition_a_blob_sha": sha_a,
                "condition_b_blob_sha": sha_b,
                "born_stale_commit_sha": "b" * 40,
                "truthful_commit_sha": "a" * 40,
                "task_prompt": "Complete the bounded coding task described in the project instruction file.",
                "test_command": "pytest",
                "selection_reason": "born_stale_confirmed_false_with_truthful_pair",
                "confirmed_false": "True",
                "p1_sample": "True",
            }
        )

    out = tmp_path / "out"
    summary = generate_packets(
        manifest_path=manifest,
        candidates_path=tmp_path / "missing_candidates.csv",
        output_dir=out,
        blobs_dir=tmp_path / "blobs",
        seed=42,
    )
    assert summary["n_manifest"] == 1
    assert (out / "private" / "id_map.sealed.json").exists()
    id_map = json.loads((out / "private" / "id_map.sealed.json").read_text(encoding="utf-8"))
    assert id_map["entries"][0]["case_id"] == "caseid0000000001"
    # Public eligibility must not include case_id
    with (out / "eligibility.csv").open(encoding="utf-8") as handle:
        public_rows = list(csv.DictReader(handle))
    assert "case_id" not in public_rows[0]
    # Packets dir must not contain sealed map
    packet_dirs = list((out / "packets").glob("*"))
    assert packet_dirs
    for pdir in packet_dirs:
        blob = (pdir / "packet.md").read_text(encoding="utf-8")
        assert "caseid0000000001" not in blob
        assert "born_stale" not in blob.lower()
        assert "confirmed_false" not in blob.lower()
        assert leakage_hits(blob) == []


def test_regeneration_deterministic(tmp_path: Path):
    store, sha_a, sha_b = _store_with(
        tmp_path / "blobs",
        "See `pkg/main.rs`.\n",
        "See `pkg/main.rs`.\n",
    )
    manifest = tmp_path / "manifest.csv"
    fields = [
        "case_id",
        "spec_id",
        "repo_id",
        "repo_url",
        "instruction_path",
        "task_commit_sha",
        "anchor_reference",
        "anchor_reference_type",
        "condition_a_blob_sha",
        "condition_b_blob_sha",
        "born_stale_commit_sha",
        "truthful_commit_sha",
        "task_prompt",
        "test_command",
        "selection_reason",
        "confirmed_false",
        "p1_sample",
    ]
    with manifest.open("w", newline="", encoding="utf-8") as handle:
        w = csv.DictWriter(handle, fieldnames=fields)
        w.writeheader()
        w.writerow(
            {
                "case_id": "zzzzzzzzzzzzzzzz",
                "spec_id": "s",
                "repo_id": "r",
                "repo_url": "https://github.com/ex/y",
                "instruction_path": "CLAUDE.md",
                "task_commit_sha": "c" * 40,
                "anchor_reference": "pkg/main.rs",
                "anchor_reference_type": "path",
                "condition_a_blob_sha": sha_a,
                "condition_b_blob_sha": sha_b,
                "born_stale_commit_sha": "d" * 40,
                "truthful_commit_sha": "c" * 40,
                "task_prompt": "Complete the bounded coding task described in the project instruction file.",
                "test_command": "cargo test",
                "selection_reason": "x",
                "confirmed_false": "True",
                "p1_sample": "False",
            }
        )
    out1 = tmp_path / "o1"
    out2 = tmp_path / "o2"
    generate_packets(
        manifest_path=manifest,
        candidates_path=tmp_path / "no.csv",
        output_dir=out1,
        blobs_dir=tmp_path / "blobs",
        seed=42,
    )
    generate_packets(
        manifest_path=manifest,
        candidates_path=tmp_path / "no.csv",
        output_dir=out2,
        blobs_dir=tmp_path / "blobs",
        seed=42,
    )
    p1 = next((out1 / "packets").glob("*/packet.md"))
    p2 = out2 / "packets" / p1.parent.name / "packet.md"
    assert p1.read_text(encoding="utf-8") == p2.read_text(encoding="utf-8")
