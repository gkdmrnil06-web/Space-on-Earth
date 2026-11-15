"""Google Cloud Translation Basic v2 (API key), optional.
Only send fixed UI strings. Never translate passwords, user input or NASA data.
"""
import json
import os
from pathlib import Path
import re
import threading
import requests

_CACHE_PATH = Path(__file__).parent / "translations" / "cache.json"
_LOCK = threading.RLock()
_MEMORY = None
MAX_TEXT_LENGTH = 3000

def api_key():
    key = os.environ.get("GOOGLE_TRANSLATE_API_KEY", "").strip()
    if key:
        return key
    try:
        import streamlit as st
        return str(st.secrets.get("GOOGLE_TRANSLATE_API_KEY", "")).strip()
    except Exception:
        return ""

def configured():
    return bool(api_key())

def _cache():
    global _MEMORY
    if _MEMORY is None:
        with _LOCK:
            try:
                _MEMORY = json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                _MEMORY = {}
    return _MEMORY

def translate(text, language):
    if not isinstance(text, str) or language == "en" or not text.strip():
        return text
    if len(text) > MAX_TEXT_LENGTH:
        return text
    # Only English UI strings are input; don't retranslate rendered content.
    if text.lstrip().startswith(("http:", "https:", "<style", "<script")):
        return text
    cache_id = language + "|" + text
    with _LOCK:
        cached = _cache().get(cache_id)
    if cached:
        return cached
    key = api_key()
    if not key:
        raise RuntimeError("Google Cloud Translation API key not configured")
    # Placeholder safety: only named Python format fields are accepted.
    fields = re.findall(r"\{[A-Za-z_][A-Za-z_0-9]*\}", text)
    placeholders = {f"ZXQPLACEHOLDER{i}ZXQ": field for i, field in enumerate(fields)}
    safe = text
    for marker, field in placeholders.items():
        safe = safe.replace(field, marker)
    response = requests.post(
        "https://translation.googleapis.com/language/translate/v2",
        params={"key": key},
        json={"q": safe, "source": "en", "target": language, "format": "text"},
        timeout=12,
    )
    response.raise_for_status()
    import html
    translated = html.unescape(response.json()["data"]["translations"][0]["translatedText"])
    for marker, field in placeholders.items():
        translated = translated.replace(marker, field)
    with _LOCK:
        _cache()[cache_id] = translated
        try:
            _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
            tmp = _CACHE_PATH.with_suffix(".tmp")
            tmp.write_text(json.dumps(_MEMORY, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(_CACHE_PATH)
        except OSError:
            pass  # still cached in memory for this process
    return translated
