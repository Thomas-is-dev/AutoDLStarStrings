import ctypes
import json
import locale
import os
import sys
from pathlib import Path

DEFAULT_LANG = 'en'
LOCALE_NAME_MAX_LENGTH = 85  # Windows constant for locale name buffers

# Works both from source and from a PyInstaller bundle (--add-data "locales;locales")
BASE_DIR = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))
LOCALES_DIR = BASE_DIR / 'locales'


def _load_catalog(code: str) -> dict[str, str] | None:
    """Load locales/<code>.json, or None if missing or invalid"""
    try:
        with open(LOCALES_DIR / f'{code}.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    return {key: value for key, value in data.items() if isinstance(value, str)}


def available_languages() -> list[str]:
    """List the language codes that have a catalog in the locales folder"""
    if not LOCALES_DIR.is_dir():
        return []
    return sorted(path.stem.lower() for path in LOCALES_DIR.glob('*.json'))


def _normalize(tag: str) -> str:
    """Normalize 'fr-FR', 'fr_FR.UTF-8' or 'FR' to 'fr_fr' / 'fr'"""
    return tag.split('.')[0].split('@')[0].replace('-', '_').lower().strip()


def _system_languages() -> list[str]:
    """Return the language tags reported by the system"""
    tags = []
    try:
        kernel32 = ctypes.windll.kernel32
        buffer = ctypes.create_unicode_buffer(LOCALE_NAME_MAX_LENGTH)
        if kernel32.LCIDToLocaleName(kernel32.GetUserDefaultUILanguage(), buffer, len(buffer), 0):
            tags.append(buffer.value)
        if kernel32.GetUserDefaultLocaleName(buffer, len(buffer)):
            tags.append(buffer.value)
    except (AttributeError, OSError):
        pass

    for variable in ('LC_ALL', 'LC_MESSAGES', 'LANG'):
        if os.getenv(variable):
            tags.append(os.environ[variable])
    tags.append(locale.getlocale()[0] or '')
    return [_normalize(tag) for tag in tags if tag]


def _match(tag: str, available: list[str]) -> str | None:
    """Match a tag against the catalogs: exact ('pt_br') first, then primary language ('pt')"""
    for candidate in (tag, tag.split('_')[0]):
        if candidate in available:
            return candidate
    return None


def detect_language() -> str:
    """APP_LANG wins; otherwise the first system language with a non-default catalog"""
    available = available_languages()

    forced = _match(_normalize(os.getenv('APP_LANG') or ''), available)
    if forced:
        return forced

    for tag in _system_languages():
        code = _match(tag, available)
        if code and code != DEFAULT_LANG:
            return code
    return DEFAULT_LANG


_fallback = _load_catalog(DEFAULT_LANG) or {}
LANG = DEFAULT_LANG
_catalog = _fallback


def set_language(code: str | None = None) -> str | None:
    """Select a language by code (None = auto-detect). Returns the code used, or None if unknown"""
    global LANG, _catalog
    if code is None:
        code = detect_language()
    else:
        code = _match(_normalize(code), available_languages())
        if code is None:
            return None
    LANG = code
    _catalog = _fallback if code == DEFAULT_LANG else {**_fallback, **(_load_catalog(code) or {})}
    return code


set_language()


def t(key: str, **kwargs) -> str:
    """Return the translated message; missing keys fall back to English, then to the key itself"""
    message = _catalog.get(key, key)
    try:
        return message.format(**kwargs)
    except (KeyError, IndexError, ValueError):
        return _fallback.get(key, key).format(**kwargs)


if __name__ == '__main__':
    # Used by the .bat scripts: python src\i18n.py <key> prints the translated message
    if len(sys.argv) > 1:
        print(t(sys.argv[1]))
