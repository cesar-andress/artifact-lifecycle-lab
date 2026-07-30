"""RQ5 v2 load-bearing candidate identification from instruction text + references."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from artifact_lab.experiments.truth_pilots.gates_common import VERIFIABLE_REFERENCE_TYPES

# Section headers / phrases that mark contextual (non-actionable) mentions.
CONTEXTUAL_SECTION_RE = re.compile(
    r"(?i)(^|\n)\s*(#{1,6}\s*)?"
    r"(related files?|see also|background|optional|further reading|references|"
    r"for context|inspiration|similar projects?|learn more|appendix)\b"
)

CONTEXTUAL_PHRASE_RE = re.compile(
    r"(?i)\b("
    r"similar to|inspired by|based on|for more (?:info|information|details)|"
    r"optional reading|may (?:also )?refer to|can (?:also )?refer to|"
    r"unrelated to|not (?:required|needed)|for context only|"
    r"background (?:material|reading)"
    r")\b"
)

EDIT_VERB_RE = re.compile(
    r"(?i)\b("
    r"edit|modify|update|change|fix|patch|implement|add|refactor|extend|"
    r"create|write|adjust|correct|amend|insert|remove|delete|rename"
    r")\b"
)

EXECUTE_VERB_RE = re.compile(
    r"(?i)\b("
    r"run|execute|invoke|call|launch|start|trigger|use|install|build|compile|test"
    r")\b"
)

INSPECT_VERB_RE = re.compile(
    r"(?i)\b("
    r"read|review|check|consult|examine|inspect|understand|analyze|analyse|"
    r"refer to|look at|see|study|locate|find|identify|verify|validate"
    r")\b"
)

IMPERATIVE_LINE_RE = re.compile(
    r"(?i)^\s*(?:[-*+]|\d+[.)])\s+.*\b("
    r"edit|modify|update|change|fix|run|execute|read|review|check|implement|add"
    r")\b"
)

TEST_PATH_RE = re.compile(
    r"(?i)(?:^|[/\\])(?:tests?|__tests__|spec|test_[^/\\]+|[^/\\]+_test\.(?:py|rs|go|ts|js|tsx|jsx))",
)

SOURCE_EXT_RE = re.compile(
    r"\.(?:py|rs|go|ts|tsx|js|jsx|java|kt|cs|cpp|c|h|rb|php|swift|vue|svelte)$",
    re.I,
)

SCRIPT_EXT_RE = re.compile(r"\.(?:sh|bash|zsh|ps1|bat|cmd)$", re.I)

CONFIG_NAMES = frozenset(
    {
        "package.json",
        "pyproject.toml",
        "setup.py",
        "cargo.toml",
        "go.mod",
        "makefile",
        "dockerfile",
        "pytest.ini",
        "tox.ini",
        "vitest.config.ts",
        "jest.config.js",
    }
)

PERIPHERAL_PATH_HINTS = (
    "readme",
    "contributing",
    "changelog",
    "license",
    "code_of_conduct",
    "security.md",
    "authors",
)


class LoadBearingRole(str, Enum):
    EDIT = "edit"
    EXECUTE = "execute"
    INSPECT = "inspect"
    CONTEXTUAL = "contextual"


@dataclass(frozen=True)
class LoadBearingClassification:
    role: LoadBearingRole
    why_load_bearing: str
    is_load_bearing: bool
    confidence: float
    contextual_only: bool


@dataclass(frozen=True)
class LoadBearingCandidate:
    repository: str
    task: str
    reference: str
    why_load_bearing: str
    difficulty: str
    estimated_success_rate: float
    repo_id: str
    repo_url: str
    instruction_path: str
    commit_sha: str
    reference_type: str
    role: str
    confidence: float
    context_snippet: str


def _normalize_ref(reference: str) -> str:
    return reference.strip().strip("`\"'")


def _line_for_reference(text: str, reference: str) -> str:
    """Return the line containing the reference, or empty."""
    ref = _normalize_ref(reference)
    base = ref.rstrip("/").split("/")[-1]
    for line in text.splitlines():
        if ref in line or (base and len(base) > 2 and base in line):
            return line.strip()
    return ""


def _section_is_contextual(text: str, reference: str) -> bool:
    """True if reference appears only under a contextual section header."""
    ref = _normalize_ref(reference)
    idx = text.find(ref)
    if idx < 0:
        base = ref.rstrip("/").split("/")[-1]
        idx = text.find(base) if base else -1
    if idx < 0:
        return False
    prefix = text[:idx]
    # Last heading before reference
    headings = list(re.finditer(r"(?m)^#{1,6}\s+(.+)$", prefix))
    if headings:
        heading = headings[-1].group(1).strip().lower()
        if any(
            kw in heading
            for kw in (
                "related",
                "see also",
                "background",
                "optional",
                "reference",
                "appendix",
                "further",
                "context",
                "inspiration",
            )
        ):
            return True
    return bool(CONTEXTUAL_SECTION_RE.search(prefix[-400:]))


def _proximity(pattern: re.Pattern[str], text: str, reference: str, *, window: int = 120) -> bool:
    ref = _normalize_ref(reference)
    base = ref.rstrip("/").split("/")[-1]
    for term in (ref, base):
        if not term or len(term) < 2:
            continue
        idx = text.find(term)
        while idx >= 0:
            start = max(0, idx - window)
            end = min(len(text), idx + len(term) + window)
            chunk = text[start:end]
            if pattern.search(chunk):
                return True
            idx = text.find(term, idx + 1)
    return False


def _reference_positions(text: str, reference: str) -> list[int]:
    ref = _normalize_ref(reference)
    base = ref.rstrip("/").split("/")[-1]
    positions: list[int] = []
    for term in (ref, base):
        if not term or len(term) < 2:
            continue
        start = 0
        while True:
            idx = text.find(term, start)
            if idx < 0:
                break
            positions.append(idx)
            start = idx + 1
    return positions or [0]


def _closest_role(
    text: str,
    reference: str,
    *,
    has_edit: bool,
    has_execute: bool,
    has_inspect: bool,
    reference_type: str,
) -> LoadBearingRole | None:
    """Pick edit/execute/inspect by minimum character distance from reference."""
    positions = _reference_positions(text, reference)
    ref_center = positions[0] + len(_normalize_ref(reference)) // 2

    candidates: list[tuple[int, LoadBearingRole]] = []
    if has_edit:
        for match in EDIT_VERB_RE.finditer(text):
            candidates.append((abs(match.start() - ref_center), LoadBearingRole.EDIT))
    if has_execute:
        for match in EXECUTE_VERB_RE.finditer(text):
            candidates.append((abs(match.start() - ref_center), LoadBearingRole.EXECUTE))
    if has_inspect:
        for match in INSPECT_VERB_RE.finditer(text):
            candidates.append((abs(match.start() - ref_center), LoadBearingRole.INSPECT))

    if not candidates:
        if has_execute and (
            bool(SCRIPT_EXT_RE.search(reference)) or _normalize_ref(reference).startswith("./")
        ):
            return LoadBearingRole.EXECUTE
        if has_edit:
            return LoadBearingRole.EDIT
        if has_inspect:
            return LoadBearingRole.INSPECT
        return None

    candidates.sort(key=lambda item: item[0])
    best_dist, best_role = candidates[0]
    if (
        best_role == LoadBearingRole.EDIT
        and has_execute
        and (SCRIPT_EXT_RE.search(reference) or reference_type == "script_name")
    ):
        execute_distances = [
            abs(m.start() - ref_center) for m in EXECUTE_VERB_RE.finditer(text)
        ]
        if execute_distances and min(execute_distances) <= best_dist + 20:
            return LoadBearingRole.EXECUTE
    return best_role


def classify_reference_load_bearing(
    *,
    reference: str,
    reference_type: str,
    instruction_text: str,
    context_snippet: str = "",
) -> LoadBearingClassification:
    """
    Classify whether a reference is load-bearing (edit, execute, inspect) or contextual.

    Returns contextual-only references with is_load_bearing=False (caller should reject).
    """
    ref = _normalize_ref(reference)
    text = instruction_text or ""
    snippet = context_snippet or text
    line = _line_for_reference(text, ref)
    ref_lower = ref.lower()

    if any(h in ref_lower for h in PERIPHERAL_PATH_HINTS):
        if not (EDIT_VERB_RE.search(line) or EXECUTE_VERB_RE.search(line)):
            return LoadBearingClassification(
                role=LoadBearingRole.CONTEXTUAL,
                why_load_bearing="contextual:peripheral_documentation_path",
                is_load_bearing=False,
                confidence=0.85,
                contextual_only=True,
            )

    contextual_phrase = bool(CONTEXTUAL_PHRASE_RE.search(snippet))
    section_contextual = _section_is_contextual(text, ref)

    has_edit = (
        _proximity(EDIT_VERB_RE, snippet, ref)
        or bool(EDIT_VERB_RE.search(line))
        or (f"`{ref}`" in text and IMPERATIVE_LINE_RE.search(line))
    )
    has_execute = (
        _proximity(EXECUTE_VERB_RE, snippet, ref)
        or bool(EXECUTE_VERB_RE.search(line))
        or ref_lower.startswith("./")
        or bool(SCRIPT_EXT_RE.search(ref))
        or reference_type == "script_name"
    )
    has_inspect = _proximity(INSPECT_VERB_RE, snippet, ref) or bool(INSPECT_VERB_RE.search(line))

    if section_contextual and not (has_edit or has_execute):
        return LoadBearingClassification(
            role=LoadBearingRole.CONTEXTUAL,
            why_load_bearing="contextual:reference_in_non_actionable_section",
            is_load_bearing=False,
            confidence=0.8,
            contextual_only=True,
        )

    if contextual_phrase and not (has_edit or has_execute):
        return LoadBearingClassification(
            role=LoadBearingRole.CONTEXTUAL,
            why_load_bearing="contextual:passive_mention_phrase",
            is_load_bearing=False,
            confidence=0.75,
            contextual_only=True,
        )

    if reference_type == "directory" and not (has_edit or has_execute):
        if not (has_inspect and TEST_PATH_RE.search(ref)):
            return LoadBearingClassification(
                role=LoadBearingRole.CONTEXTUAL,
                why_load_bearing="contextual:directory_without_action_verb",
                is_load_bearing=False,
                confidence=0.7,
                contextual_only=True,
            )

    reasons: list[str] = []
    role = LoadBearingRole.CONTEXTUAL
    confidence = 0.5

    chosen = _closest_role(
        snippet,
        ref,
        has_edit=has_edit,
        has_execute=has_execute,
        has_inspect=has_inspect,
        reference_type=reference_type,
    )

    if chosen == LoadBearingRole.EXECUTE:
        role = LoadBearingRole.EXECUTE
        reasons.append("instruction_requires_execution_of_reference")
        confidence = 0.82
    elif chosen == LoadBearingRole.EDIT:
        role = LoadBearingRole.EDIT
        reasons.append("instruction_requires_edit_of_reference")
        confidence = 0.85
    elif chosen == LoadBearingRole.INSPECT:
        task_coupled = (
            TEST_PATH_RE.search(ref)
            or SOURCE_EXT_RE.search(ref)
            or ref.rstrip("/").split("/")[-1].lower() in CONFIG_NAMES
            or _proximity(
                re.compile(r"(?i)\b(before|then|after|must|should|need to)\b"),
                snippet,
                ref,
                window=80,
            )
        )
        if task_coupled:
            role = LoadBearingRole.INSPECT
            reasons.append("instruction_requires_inspection_to_complete_task")
            confidence = 0.72
        else:
            return LoadBearingClassification(
                role=LoadBearingRole.CONTEXTUAL,
                why_load_bearing="contextual:inspect_without_task_coupling",
                is_load_bearing=False,
                confidence=0.65,
                contextual_only=True,
            )
    else:
        if f"`{ref}`" in text and IMPERATIVE_LINE_RE.search(line):
            role = LoadBearingRole.EDIT
            reasons.append("imperative_list_item_targets_reference")
            confidence = 0.68
        else:
            return LoadBearingClassification(
                role=LoadBearingRole.CONTEXTUAL,
                why_load_bearing="contextual:no_edit_execute_or_inspect_signal",
                is_load_bearing=False,
                confidence=0.6,
                contextual_only=True,
            )

    if section_contextual and role != LoadBearingRole.CONTEXTUAL:
        confidence *= 0.85
        reasons.append("note:mentioned_in_context_section_but_actionable")

    why = f"{role.value}:" + "+".join(reasons)
    return LoadBearingClassification(
        role=role,
        why_load_bearing=why,
        is_load_bearing=True,
        confidence=round(confidence, 3),
        contextual_only=False,
    )


def estimate_difficulty(
    *,
    reference: str,
    reference_type: str,
    instruction_text: str,
) -> str:
    ref = _normalize_ref(reference)
    depth = len([p for p in ref.split("/") if p and p not in (".", "..")])
    base = ref.rstrip("/").split("/")[-1].lower()

    if reference_type == "directory":
        return "hard"
    if base in CONFIG_NAMES or reference_type == "dependency":
        return "hard"
    if TEST_PATH_RE.search(ref) or depth <= 3:
        return "easy"
    if depth <= 5 and SOURCE_EXT_RE.search(ref):
        return "medium"
    if depth > 6:
        return "hard"
    return "medium"


def estimate_success_rate(
    *,
    difficulty: str,
    role: LoadBearingRole,
    reference_type: str,
    has_test_command: bool,
) -> float:
    base = {"easy": 0.62, "medium": 0.52, "hard": 0.42}.get(difficulty, 0.50)
    if role == LoadBearingRole.EDIT:
        base += 0.05
    elif role == LoadBearingRole.EXECUTE:
        base += 0.03
    elif role == LoadBearingRole.INSPECT:
        base -= 0.06
    if reference_type == "script_name":
        base += 0.02
    if reference_type == "dependency":
        base -= 0.08
    if has_test_command:
        base += 0.02
    return round(max(0.28, min(0.72, base)), 3)


def synthesize_task(
    *,
    role: LoadBearingRole,
    reference: str,
    instruction_path: str,
    test_command: str,
) -> str:
    ref = _normalize_ref(reference)
    test_hint = f" Run `{test_command}` before finishing." if test_command else " Run project tests before finishing."
    if role == LoadBearingRole.EDIT:
        return (
            f"Modify `{ref}` following the workflow in `{instruction_path}`. "
            f"The cited file must be edited to complete the task.{test_hint}"
        )
    if role == LoadBearingRole.EXECUTE:
        return (
            f"Execute `{ref}` as directed in `{instruction_path}`, then complete the "
            f"bounded change validated by the project test suite.{test_hint}"
        )
    return (
        f"Inspect `{ref}` to determine the required change described in `{instruction_path}`, "
        f"implement that change in the repository, and validate with tests.{test_hint}"
    )


def _detect_test_command(instruction_text: str) -> str:
    from artifact_lab.experiments.truth_decay.rq5_availability import TEST_COMMAND_PATTERNS

    for pattern in TEST_COMMAND_PATTERNS:
        match = pattern.search(instruction_text)
        if match:
            return match.group(0).strip()
    if "pytest" in instruction_text.lower():
        return "pytest"
    return "pytest"


def _repo_display_name(repo_url: str, repo_id: str) -> str:
    if repo_url and "github.com/" in repo_url:
        parts = repo_url.rstrip("/").split("github.com/")[-1].split("/")
        if len(parts) >= 2:
            return f"{parts[0]}/{parts[1]}"
    return repo_id


def build_load_bearing_candidates(
    *,
    rows: list[dict],
    repo_urls: dict[str, str],
    blob_index: dict[tuple[str, str, str], str],
    blob_store,
    min_candidates: int = 100,
) -> list[LoadBearingCandidate]:
    """
    Scan longitudinal panel for VERIFIED references with load-bearing instruction coupling.

    Rejects contextual-only mentions. Returns candidates sorted by confidence descending.
    """
    from collections import defaultdict

    from artifact_lab.experiments.truth_decay.born_stale_context import extract_snippet
    from artifact_lab.experiments.truth_decay.rq5_candidates import (
        _counts,
        build_commit_spec_states,
        _verified_refs,
    )

    by_spec = build_commit_spec_states(rows)
    spec_rows: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        if row.get("reference_removed"):
            continue
        spec_rows[(row["repo_id"], row["instruction_path"])].append(row)

    text_cache: dict[str, str] = {}
    candidates: list[LoadBearingCandidate] = []
    seen: set[tuple[str, str, str]] = set()

    for (repo_id, instruction_path), states in sorted(by_spec.items()):
        if not states:
            continue
        # Prefer commit with highest verified ratio (same as truthful snapshot selection)
        best_state = None
        best_ratio = -1.0
        for state in states:
            counts = _counts(state)
            if counts["n_verifiable"] == 0:
                continue
            ratio = counts["n_verified_verifiable"] / counts["n_verifiable"]
            if ratio > best_ratio:
                best_ratio = ratio
                best_state = state
        if best_state is None or best_ratio <= 0:
            continue

        commit = best_state.commit
        blob_sha = blob_index.get((repo_id, instruction_path, commit), "")
        if not blob_sha:
            continue
        if blob_sha not in text_cache:
            try:
                text_cache[blob_sha] = blob_store.get_text(blob_sha).decode("utf-8", errors="replace")
            except OSError:
                text_cache[blob_sha] = ""
        instruction_text = text_cache[blob_sha]
        if not instruction_text.strip():
            continue

        test_command = _detect_test_command(instruction_text)
        repo_url = repo_urls.get(repo_id, "")
        repository = _repo_display_name(repo_url, repo_id)

        for ref in _verified_refs(best_state):
            ref_type = "path"
            for (t, r), st in best_state.references.items():
                if r == ref and st == "VERIFIED":
                    ref_type = t
                    break
            if ref_type not in VERIFIABLE_REFERENCE_TYPES:
                continue

            dedupe_key = (repo_id, instruction_path, ref)
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            snippet = extract_snippet(instruction_text, ref)
            classification = classify_reference_load_bearing(
                reference=ref,
                reference_type=ref_type,
                instruction_text=instruction_text,
                context_snippet=snippet,
            )
            if not classification.is_load_bearing:
                continue

            difficulty = estimate_difficulty(
                reference=ref,
                reference_type=ref_type,
                instruction_text=instruction_text,
            )
            success_rate = estimate_success_rate(
                difficulty=difficulty,
                role=classification.role,
                reference_type=ref_type,
                has_test_command=bool(test_command),
            )
            task = synthesize_task(
                role=classification.role,
                reference=ref,
                instruction_path=instruction_path,
                test_command=test_command,
            )

            candidates.append(
                LoadBearingCandidate(
                    repository=repository,
                    task=task,
                    reference=ref,
                    why_load_bearing=classification.why_load_bearing,
                    difficulty=difficulty,
                    estimated_success_rate=success_rate,
                    repo_id=repo_id,
                    repo_url=repo_url,
                    instruction_path=instruction_path,
                    commit_sha=commit,
                    reference_type=ref_type,
                    role=classification.role.value,
                    confidence=classification.confidence,
                    context_snippet=snippet[:300],
                )
            )

    candidates.sort(key=lambda c: (-c.confidence, -c.estimated_success_rate, c.repository, c.reference))

    if len(candidates) < min_candidates:
        # Second pass: relax to VERIFIED refs at any commit with ratio >= 0.05
        for (repo_id, instruction_path), states in sorted(by_spec.items()):
            if len(candidates) >= min_candidates:
                break
            for state in states:
                if len(candidates) >= min_candidates:
                    break
                counts = _counts(state)
                if counts["n_verifiable"] == 0:
                    continue
                ratio = counts["n_verified_verifiable"] / counts["n_verifiable"]
                if ratio < 0.05:
                    continue
                commit = state.commit
                blob_sha = blob_index.get((repo_id, instruction_path, commit), "")
                if not blob_sha:
                    continue
                if blob_sha not in text_cache:
                    try:
                        text_cache[blob_sha] = blob_store.get_text(blob_sha).decode("utf-8", errors="replace")
                    except OSError:
                        text_cache[blob_sha] = ""
                instruction_text = text_cache[blob_sha]
                if not instruction_text.strip():
                    continue
                test_command = _detect_test_command(instruction_text)
                repo_url = repo_urls.get(repo_id, "")
                repository = _repo_display_name(repo_url, repo_id)

                for ref in _verified_refs(state):
                    dedupe_key = (repo_id, instruction_path, ref)
                    if dedupe_key in seen:
                        continue
                    ref_type = "path"
                    for (t, r), st in state.references.items():
                        if r == ref and st == "VERIFIED":
                            ref_type = t
                            break
                    if ref_type not in VERIFIABLE_REFERENCE_TYPES:
                        continue
                    snippet = extract_snippet(instruction_text, ref)
                    classification = classify_reference_load_bearing(
                        reference=ref,
                        reference_type=ref_type,
                        instruction_text=instruction_text,
                        context_snippet=snippet,
                    )
                    if not classification.is_load_bearing:
                        continue
                    seen.add(dedupe_key)
                    difficulty = estimate_difficulty(
                        reference=ref, reference_type=ref_type, instruction_text=instruction_text
                    )
                    success_rate = estimate_success_rate(
                        difficulty=difficulty,
                        role=classification.role,
                        reference_type=ref_type,
                        has_test_command=bool(test_command),
                    )
                    candidates.append(
                        LoadBearingCandidate(
                            repository=repository,
                            task=synthesize_task(
                                role=classification.role,
                                reference=ref,
                                instruction_path=instruction_path,
                                test_command=test_command,
                            ),
                            reference=ref,
                            why_load_bearing=classification.why_load_bearing,
                            difficulty=difficulty,
                            estimated_success_rate=success_rate,
                            repo_id=repo_id,
                            repo_url=repo_url,
                            instruction_path=instruction_path,
                            commit_sha=commit,
                            reference_type=ref_type,
                            role=classification.role.value,
                            confidence=classification.confidence,
                            context_snippet=snippet[:300],
                        )
                    )

        candidates.sort(key=lambda c: (-c.confidence, -c.estimated_success_rate, c.repository, c.reference))

    return candidates
