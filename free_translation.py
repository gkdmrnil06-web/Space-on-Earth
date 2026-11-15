
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
    return {
        'online_cooldown': max(0, round(_BACKOFF_UNTIL - time.monotonic())),
        'last_error': _LAST_ERROR
    }


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
            tmp.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
            tmp.replace(_CACHE)
        except OSError:
            pass


@lru_cache(maxsize=96)
def _get_argos_translator(language):
    try:
        from argostranslate import translate
        src = next(
            (x for x in translate.get_installed_languages() if x.code == 'en'),
            None
        )
        dst = next(
            (x for x in translate.get_installed_languages() if x.code == language),
            None
        )
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
        return message

    saved = get_saved(message, language)
    if saved:
        return saved

    try:
        result = _argos_translate(message, language)
        if result and result != message:
            save(message, language, result)
            return result
    except Exception:
        pass

    if time.monotonic() < _BACKOFF_UNTIL:
        return message

    if message not in _static_labels():
        return message

    try:
        from deep_translator import GoogleTranslator
        result = GoogleTranslator(
            source='en',
            target=language
        ).translate(message)

        if result and isinstance(result, str):
            save(message, language, result)
            _LAST_ERROR = ''
            return result

    except Exception as exc:
        _LAST_ERROR = type(exc).__name__
        _BACKOFF_UNTIL = time.monotonic() + 300

    return message


def install_offline_model(language):
    """Explicit user action only: download public model for en -> target language."""

    if language == 'en':
        return True, 'English is the source language.'

    try:
        import argostranslate.package as package
        package.update_package_index()
        available = package.get_available_packages()

        match = next(
            (
                item for item in available
                if item.from_code == 'en' and item.to_code == language
            ),
            None
        )

        if match is None:
            return (
                False,
                'No English → ' + language +
                ' model is listed. English fallback remains available.'
            )

        package.install_from_path(match.download())
        _get_argos_translator.cache_clear()

        return (
            True,
            'Downloaded and installed English → ' + language + ' model.'
        )

    except ImportError:
        return (
            False,
            'Optional argostranslate package is not installed. '
            'See FREE_TRANSLATION_GUIDE.txt.'
        )

    except Exception as exc:
        return False, 'Model download failed: ' + type(exc).__name__
