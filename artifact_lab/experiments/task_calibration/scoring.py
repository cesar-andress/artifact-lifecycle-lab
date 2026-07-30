"""Heuristic difficulty dimension scorers (0 = easy, 1 = hard)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from artifact_lab.experiments.truth_decay.rq5_availability import TEST_COMMAND_PATTERNS

MONOREPO_PREFIXES = ("packages/", "apps/", "modules/", "libs/", "crates/", "services/")
BUILD_LANGUAGE_RE = re.compile(
    r"(?i)\b("
    r"build|compile|webpack|gradle|maven|xcode|docker|cargo build|"
    r"typescript|tsc|lerna|turbo|nx run|pnpm|yarn workspace"
    r")\b"
)
E2E_PATH_RE = re.compile(r"(?i)(?:^|[/\\])(?:e2e|integration|cypress|playwright)(?:[/\\]|$)")
TEST_FILE_RE = re.compile(
    r"(?i)(?:^|[/\\])(?:tests?|__tests__|spec|test_[^/\\]+|[^/\\]+_test\.(?:py|rs|go|ts|js|tsx|jsx))",
)
SCOPED_PKG_RE = re.compile(r"^@[^/]+/")
SOURCE_EXT_RE = re.compile(
    r"\.(?:py|rs|go|ts|tsx|js|jsx|java|kt|cs|cpp|c|h|rb|php|swift|vue|svelte)$",
    re.I,
)

# Ordered by increasing build friction (index / len used as score component).
TEST_COMMAND_TIERS = (
    (re.compile(r"(?i)^pytest\b"), 0.15),
    (re.compile(r"(?i)^tox\b"), 0.25),
    (re.compile(r"(?i)^cargo\s+test\b"), 0.45),
    (re.compile(r"(?i)^go\s+test\b"), 0.40),
    (re.compile(r"(?i)^make\s+test\b"), 0.50),
    (re.compile(r"(?i)^npm\s+(?:run\s+)?test\b"), 0.55),
    (re.compile(r"(?i)^yarn\s+test\b"), 0.55),
    (re.compile(r"(?i)^vitest\b"), 0.50),
    (re.compile(r"(?i)^jest\b"), 0.50),
    (re.compile(r"(?i)^mvn\s+test\b"), 0.65),
)


@dataclass(frozen=True)
class DifficultyDimensions:
    compilation_complexity: float
    edited_files_estimate: float
    test_complexity: float
    dependency_depth: float
    historical_failure_rate: float

    @property
    def as_tuple(self) -> tuple[float, float, float, float, float]:
        return (
            self.compilation_complexity,
            self.edited_files_estimate,
            self.test_complexity,
            self.dependency_depth,
            self.historical_failure_rate,
        )


@dataclass(frozen=True)
class TaskFeatures:
    repository: str
    reference: str
    instruction_path: str
    reference_type: str
    role: str
    test_command: str
    context_snippet: str
    repo_id: str = ""


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def _path_depth(reference: str) -> int:
    return len([p for p in reference.strip("/").split("/") if p and p not in (".", "..")])


def _detect_test_command(text: str, explicit: str = "") -> str:
    if explicit and explicit.strip():
        return explicit.strip()
    for pattern in TEST_COMMAND_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(0).strip()
    if "pytest" in text.lower():
        return "pytest"
    return ""


def score_compilation_complexity(features: TaskFeatures) -> float:
    """Estimate build/typecheck friction before tests can run."""
    score = 0.12
    cmd = features.test_command.lower()
    text = f"{features.instruction_path} {features.context_snippet}".lower()

    if any(cmd.startswith(prefix) for prefix in ("cargo", "mvn", "gradle", "xcodebuild")):
        score = max(score, 0.75)
    elif cmd.startswith("npm") or cmd.startswith("yarn") or cmd.startswith("pnpm"):
        score = max(score, 0.55)
    elif cmd.startswith("go "):
        score = max(score, 0.45)
    elif cmd == "pytest" or cmd.startswith("pytest"):
        score = max(score, 0.18)

    if any(prefix in features.instruction_path for prefix in MONOREPO_PREFIXES):
        score += 0.22
    if any(prefix in features.reference for prefix in MONOREPO_PREFIXES):
        score += 0.12
    if BUILD_LANGUAGE_RE.search(text):
        score += 0.18
    if features.reference_type == "dependency":
        score += 0.25
    if SCOPED_PKG_RE.match(features.reference.strip()):
        score += 0.20

    # Large OSS repos known to be heavy in v1 pilot
    heavy_repos = (
        "automattic/wp-calypso",
        "microsoft/vscode",
        "langgenius/dify",
        "provenance-emu/provenance",
    )
    if features.repository in heavy_repos:
        score += 0.15

    return _clamp(score)


def score_edited_files_estimate(
    features: TaskFeatures,
    *,
    historical_median_files: float | None = None,
) -> float:
    """Estimate how many files an agent must touch (higher → harder)."""
    if historical_median_files is not None and historical_median_files > 0:
        # v1 pilot: success cases ~61 files modified median; failures ~80+
        return _clamp(historical_median_files / 120.0)

    score = 0.25
    role = features.role.lower()
    if role == "edit":
        score = 0.40
    elif role == "execute":
        score = 0.20
    elif role == "inspect":
        score = 0.35

    if features.reference_type == "directory":
        score += 0.35
    elif not SOURCE_EXT_RE.search(features.reference) and not TEST_FILE_RE.search(features.reference):
        score += 0.15

    depth = _path_depth(features.reference)
    if depth >= 6:
        score += 0.15
    elif depth <= 2:
        score -= 0.08

    if TEST_FILE_RE.search(features.reference):
        score -= 0.10

    return _clamp(score)


def score_test_complexity(features: TaskFeatures) -> float:
    """Estimate test-suite friction for the pinned task."""
    cmd = features.test_command.strip()
    score = 0.35
    matched = False
    for pattern, tier in TEST_COMMAND_TIERS:
        if pattern.search(cmd):
            score = tier
            matched = True
            break
    if not matched and cmd:
        score = 0.50

    if E2E_PATH_RE.search(features.instruction_path):
        score = max(score, 0.80)
    if any(prefix in features.instruction_path for prefix in MONOREPO_PREFIXES):
        score += 0.15
    if features.repository in ("automattic/wp-calypso", "microsoft/vscode", "langgenius/dify"):
        score += 0.12
    if TEST_FILE_RE.search(features.reference):
        score -= 0.08

    return _clamp(score)


def score_dependency_depth(features: TaskFeatures) -> float:
    """Estimate discovery / dependency graph depth to reach the anchor."""
    ref = features.reference.strip()
    depth = _path_depth(ref)
    score = _clamp(depth / 8.0)

    if features.reference_type == "dependency":
        score = max(score, 0.70)
    if SCOPED_PKG_RE.match(ref):
        score = max(score, 0.55)
    if any(prefix in ref for prefix in MONOREPO_PREFIXES):
        score += 0.18
    if ref.startswith(".") or ref.startswith("/"):
        score += 0.10

    return _clamp(score)


def score_historical_failure_rate(
    *,
    case_success_rate: float | None,
    repo_success_rate: float | None,
    spec_success_rate: float | None,
    global_failure_rate: float,
) -> float:
    """
    Historical agent failure propensity.

    Uses finest available match: case → (repo, instruction) → repo → global prior.
    """
    if case_success_rate is not None:
        return _clamp(1.0 - case_success_rate)
    if spec_success_rate is not None:
        return _clamp(1.0 - spec_success_rate)
    if repo_success_rate is not None:
        return _clamp(1.0 - repo_success_rate)
    return _clamp(global_failure_rate)


def score_all_dimensions(
    features: TaskFeatures,
    *,
    historical_median_files: float | None = None,
    case_success_rate: float | None = None,
    repo_success_rate: float | None = None,
    spec_success_rate: float | None = None,
    global_failure_rate: float = 0.87,
) -> DifficultyDimensions:
    return DifficultyDimensions(
        compilation_complexity=score_compilation_complexity(features),
        edited_files_estimate=score_edited_files_estimate(
            features, historical_median_files=historical_median_files
        ),
        test_complexity=score_test_complexity(features),
        dependency_depth=score_dependency_depth(features),
        historical_failure_rate=score_historical_failure_rate(
            case_success_rate=case_success_rate,
            repo_success_rate=repo_success_rate,
            spec_success_rate=spec_success_rate,
            global_failure_rate=global_failure_rate,
        ),
    )


def extract_test_command_from_task(task: str) -> str:
    match = re.search(r"Run `([^`]+)` before finishing", task)
    if match:
        return match.group(1).strip()
    return _detect_test_command(task)
