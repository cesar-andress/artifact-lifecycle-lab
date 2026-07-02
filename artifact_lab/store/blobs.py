"""Content-addressed blob store for matched text files."""

from __future__ import annotations

import hashlib
from pathlib import Path


class BlobStore:
    """Filesystem blob store keyed by SHA-256 of raw bytes."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def _path_for(self, sha: str) -> Path:
        prefix = sha[:2]
        return self.root / prefix / f"{sha}.txt"

    def has(self, sha: str) -> bool:
        return self._path_for(sha).exists()

    def put_text(self, content: bytes) -> str:
        if b"\x00" in content:
            raise ValueError("refusing to store binary blob")
        sha = self.sha256(content)
        dest = self._path_for(sha)
        if dest.exists():
            return sha
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(content)
        return sha

    def get_text(self, sha: str) -> bytes:
        path = self._path_for(sha)
        if not path.exists():
            raise FileNotFoundError(sha)
        return path.read_bytes()
