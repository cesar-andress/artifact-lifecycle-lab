"""Deterministic repository identifiers from normalized URLs.

Normalization rules (applied in order):

1. Strip leading/trailing whitespace.
2. Parse known GitHub HTTPS URLs as ``https://github.com/{owner}/{repo}`` with
   lowercase owner and repo; strip a trailing ``.git`` suffix from the repo name.
3. For other URLs: lowercase the scheme and host, remove trailing slashes,
   strip a trailing ``.git`` suffix from the path.
4. ``repo_id`` is the first 16 hex characters of SHA-256(utf-8 normalized URL).

The normalized URL string is stable across equivalent forms such as
``https://github.com/Org/Repo.git`` and ``https://github.com/org/repo``.
"""

from __future__ import annotations

import hashlib
import re
from urllib.parse import urlparse, urlunparse


def normalize_repo_url(url: str) -> str:
    raw = url.strip()
    gh = _parse_github_https(raw)
    if gh is not None:
        owner, repo = gh
        return f"https://github.com/{owner.lower()}/{repo.lower()}"

    parsed = urlparse(raw)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"cannot normalize repository URL: {url!r}")

    path = parsed.path.rstrip("/")
    if path.endswith(".git"):
        path = path[:-4]
    path = re.sub(r"/+", "/", path.lower())

    return urlunparse(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            path,
            "",
            "",
            "",
        )
    )


def repo_id_from_url(url: str) -> str:
    normalized = normalize_repo_url(url)
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return digest[:16]


def _parse_github_https(url: str) -> tuple[str, str] | None:
    m = re.match(r"https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$", url.strip(), re.IGNORECASE)
    if not m:
        return None
    return m.group(1), m.group(2)
