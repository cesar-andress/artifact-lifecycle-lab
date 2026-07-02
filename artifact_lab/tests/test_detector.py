"""Detector matching and exclusion tests."""

from artifact_lab.protocol.detector import is_excluded, is_matched_path, match_pattern_id


FAMILY = "ai_conventions_v1"


def test_agents_md_matches():
    assert match_pattern_id("AGENTS.md", FAMILY) == "agents_md"
    assert match_pattern_id("docs/AGENTS.md", FAMILY) == "agents_md"


def test_claude_and_cursorrules():
    assert match_pattern_id("CLAUDE.md", FAMILY) == "claude_md"
    assert match_pattern_id(".cursorrules", FAMILY) == "cursorrules"


def test_cursor_rules_glob():
    assert match_pattern_id(".cursor/rules/python.mdc", FAMILY) == "cursor_rules"


def test_copilot_and_github_instructions():
    assert match_pattern_id(".github/copilot-instructions.md", FAMILY) == "copilot_instructions"
    assert match_pattern_id(".github/instructions/foo.md", FAMILY) == "github_instructions"


def test_windsurf_skill_prompts():
    assert match_pattern_id(".windsurf/rules/foo.md", FAMILY) == "windsurf_rules"
    assert match_pattern_id("SKILL.md", FAMILY) == "skill_md"
    assert match_pattern_id("prompts/system.yaml", FAMILY) == "prompts"


def test_exclusions():
    assert not is_matched_path("node_modules/foo/AGENTS.md", FAMILY)
    assert not is_matched_path("vendor/AGENTS.md", FAMILY)
    assert not is_matched_path("README.md", FAMILY)
    assert is_excluded("build/output/AGENTS.md", FAMILY)
