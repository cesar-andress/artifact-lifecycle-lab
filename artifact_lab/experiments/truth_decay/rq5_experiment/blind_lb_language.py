"""Language detection and English translation cache for packet excerpts."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

CACHE_PATH = Path(
    "artifact_lab/experiments/truth_decay/rq5_experiment/blind_lb_translation_cache.json"
)

_CJK = re.compile(r"[\u4e00-\u9fff]")
_CYR = re.compile(r"[\u0400-\u04ff]")
_HANG = re.compile(r"[\uac00-\ud7af]")
_JP = re.compile(r"[\u3040-\u30ff]")


def detect_language(text: str) -> str:
    if not text:
        return "en"
    cjk = len(_CJK.findall(text))
    cyr = len(_CYR.findall(text))
    hang = len(_HANG.findall(text))
    jap = len(_JP.findall(text))
    n = max(len(text), 1)
    # Threshold: substantial non-Latin script presence
    if cjk / n > 0.05 or cjk > 40:
        return "zh"
    if cyr / n > 0.05 or cyr > 40:
        return "ru"
    if hang / n > 0.05 or hang > 40:
        return "ko"
    if jap / n > 0.02 or jap > 40:
        return "ja"
    return "en"


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_cache(path: Path = CACHE_PATH) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_cache(cache: dict[str, dict[str, str]], path: Path = CACHE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def translate_to_english(text: str, *, cache: dict[str, dict[str, str]] | None = None) -> tuple[str, str]:
    """Return (english_text, language_code). Uses cache for non-English.

    If non-English and missing from cache, returns original with language code and
    caller must exclude or fill cache.
    """
    lang = detect_language(text)
    if lang == "en":
        return text, lang
    store = cache if cache is not None else load_cache()
    key = text_hash(text)
    hit = store.get(key)
    if hit and hit.get("en"):
        return hit["en"], lang
    return text, lang
