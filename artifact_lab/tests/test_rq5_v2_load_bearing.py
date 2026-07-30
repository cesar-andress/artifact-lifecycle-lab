"""Unit tests for RQ5 v2 load-bearing candidate identification."""

from __future__ import annotations

from artifact_lab.experiments.truth_decay.rq5_v2.load_bearing import (
    LoadBearingRole,
    classify_reference_load_bearing,
    estimate_difficulty,
    estimate_success_rate,
    synthesize_task,
)


def test_edit_reference_is_load_bearing():
    text = "Before submitting, edit `src/core.py` and run pytest."
    result = classify_reference_load_bearing(
        reference="src/core.py",
        reference_type="path",
        instruction_text=text,
    )
    assert result.is_load_bearing
    assert result.role == LoadBearingRole.EDIT
    assert "edit" in result.why_load_bearing


def test_execute_script_is_load_bearing():
    text = "Run `./scripts/setup.sh` once, then implement the feature."
    result = classify_reference_load_bearing(
        reference="./scripts/setup.sh",
        reference_type="path",
        instruction_text=text,
    )
    assert result.is_load_bearing
    assert result.role == LoadBearingRole.EXECUTE


def test_inspect_test_file_is_load_bearing():
    text = "Read tests/test_api.py to understand expected behavior before changing handlers."
    result = classify_reference_load_bearing(
        reference="tests/test_api.py",
        reference_type="path",
        instruction_text=text,
    )
    assert result.is_load_bearing
    assert result.role == LoadBearingRole.INSPECT


def test_contextual_see_also_rejected():
    text = (
        "## Related files\n"
        "- README.md\n"
        "- docs/architecture.md\n"
        "See also `CONTRIBUTING.md` for background."
    )
    result = classify_reference_load_bearing(
        reference="CONTRIBUTING.md",
        reference_type="path",
        instruction_text=text,
    )
    assert not result.is_load_bearing
    assert result.contextual_only


def test_passive_mention_rejected():
    text = "This project is similar to other tools; you may also refer to docs/guide.md for inspiration."
    result = classify_reference_load_bearing(
        reference="docs/guide.md",
        reference_type="path",
        instruction_text=text,
    )
    assert not result.is_load_bearing


def test_imperative_list_item_edit():
    text = "- Update `config.toml` with your API key\n- Run tests"
    result = classify_reference_load_bearing(
        reference="config.toml",
        reference_type="path",
        instruction_text=text,
    )
    assert result.is_load_bearing
    assert result.role == LoadBearingRole.EDIT


def test_difficulty_and_success_rate():
    assert estimate_difficulty(reference="tests/test_x.py", reference_type="path", instruction_text="") == "easy"
    assert estimate_difficulty(reference="src/deep/nested/module.py", reference_type="path", instruction_text="") in {
        "medium",
        "hard",
    }
    rate = estimate_success_rate(
        difficulty="medium",
        role=LoadBearingRole.EDIT,
        reference_type="path",
        has_test_command=True,
    )
    assert 0.28 <= rate <= 0.72


def test_synthesize_task_includes_reference():
    task = synthesize_task(
        role=LoadBearingRole.EDIT,
        reference="src/foo.py",
        instruction_path="AGENTS.md",
        test_command="pytest",
    )
    assert "src/foo.py" in task
    assert "AGENTS.md" in task
    assert "pytest" in task
