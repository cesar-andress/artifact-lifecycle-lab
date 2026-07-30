"""Reproducibility metadata for Phase 0 analysis artifacts."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _sha256_file(path: Path) -> str:
    if not path.exists():
        return "missing"
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def git_commit(cwd: Path | None = None) -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=cwd or Path.cwd(),
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return out or "unknown"
    except (subprocess.CalledProcessError, OSError):
        return "unknown"


def collect_provenance(
    *,
    manifest_path: Path,
    script_paths: list[Path],
    cwd: Path | None = None,
) -> dict[str, str]:
    ts = datetime.now(timezone.utc).isoformat()
    return {
        "generated_at": ts,
        "git_commit": git_commit(cwd=cwd),
        "manifest_sha256": _sha256_file(manifest_path),
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "analysis_script_hashes": {
            str(p.name): _sha256_file(p) for p in script_paths
        },
    }


def provenance_block(provenance: dict[str, str]) -> str:
    lines = [
        "---",
        "## Reproducibility",
        "",
        f"- **Generated at (UTC):** {provenance['generated_at']}",
        f"- **Git commit:** `{provenance['git_commit']}`",
        f"- **Manifest SHA-256:** `{provenance['manifest_sha256']}`",
        f"- **Python:** {provenance['python_version']}",
        f"- **Platform:** {provenance['platform']}",
        "",
        "**Analysis script hashes (SHA-256):**",
        "",
    ]
    hashes = provenance.get("analysis_script_hashes") or {}
    for name, digest in sorted(hashes.items()):
        lines.append(f"- `{name}`: `{digest}`")
    lines.append("")
    lines.append("---")
    return "\n".join(lines)


def provenance_json(provenance: dict[str, str]) -> str:
    return json.dumps(provenance, indent=2, sort_keys=True)
