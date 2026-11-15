"""Free optional translation backends for Space on Earth.

Order: bundled dictionaries (handled by i18n) > saved translation cache >
installed Argos offline model > free public GoogleTranslator via deep-translator.
No Google Cloud credentials or billing required. Online service is unofficial,
may rate limit or be unreachable. Never translate NASA dataset identifiers.
"""
from __future__ import annotations
from pathlib import Path
import json
import threading
import time
from functools import lru_cache

_ROOT = Path(__file__).resolve().parent
_CACHE = _ROOT / 'translations' / 'cache.json'
_LOCK = threading.RLock()
_MEMORY = None
_BACKOFF_UNTIL = 0.0
_LAST_ERROR = ''


def status():
    """Report what actually works on this machine, without API guesses."""
    return {'online_cooldown': max(0, round(_BACKOFF_UNTIL - time.monotonic())),
            'last_error': _LAST_ERROR}


def _entries():
    global _MEMORY
    with _LOCK:
        if _MEMORY is None:
            try:
                value = json.loads(_CACHE.read_text(encoding='utf-8'))
                _MEMORY = value if isinstance(value, dict) else {}
            except (OSError, ValueError):
                _MEMORY = {}
        return _MEMORY


def get_saved(message, language):
    with _LOCK:
        return _entries().get(language + '\x1f' + message)


def save(message, language, translated):
    if not translated or translated == message:
        return
    with _LOCK:
        data = _entries()
        key = language + '\x1f' + message
        if data.get(key) == translated:
            return
        data[key] = translated
        try:
            _CACHE.parent.mkdir(exist_ok=True, parents=True)
            tmp = _CACHE.with_suffix('.tmp')
            tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            tmp.replace(_CACHE)
        except OSError:
            pass


@lru_cache(maxsize=96)
def _get_argos_translator(language):
    try:
        from argostranslate import translate
        src = next((x for x in translate.get_installed_languages() if x.code == 'en'), None)
        dst = next((x for x in translate.get_installed_languages() if x.code == language), None)
        return src.get_translation(dst) if src and dst else None
    except Exception:
        return None


def _argos_translate(message, language):
    translator = _get_argos_translator(language)
    return translator.translate(message) if translator else None


@lru_cache(maxsize=1)
def _static_labels():
    try:
        path = _ROOT / 'static_labels.json'
        if not path.is_file():
            path = _ROOT / 'translations' / 'static_labels.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        return frozenset(data) if isinstance(data, (list, dict)) else frozenset()
    except (OSError, ValueError):
        return frozenset()


def translate(message, language):
    global _BACKOFF_UNTIL, _LAST_ERROR
    if language == 'en' or not message or len(message) > 4800:
        return message
    if message.startswith(('http:', 'https:', '<style', '<script')):
