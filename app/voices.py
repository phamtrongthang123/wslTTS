from __future__ import annotations

import json

from .config import BASE_DIR, DEFAULT_LANG

VOICES_PATH = BASE_DIR / "data" / "voices.json"

_VOICES: list[dict] | None = None
_VOICE_INDEX: dict[str, dict] | None = None


def get_voices() -> list[dict]:
    global _VOICES
    if _VOICES is None:
        with open(VOICES_PATH, "r", encoding="utf-8") as handle:
            _VOICES = json.load(handle)
    return _VOICES


def get_voice_index() -> dict[str, dict]:
    global _VOICE_INDEX
    if _VOICE_INDEX is None:
        _VOICE_INDEX = {voice["id"]: voice for voice in get_voices()}
    return _VOICE_INDEX


def resolve_lang_code(voice: str | None, lang_code: str | None) -> str:
    if lang_code:
        return lang_code.lower()
    if not voice:
        return DEFAULT_LANG
    voice_info = get_voice_index().get(voice)
    if voice_info:
        return str(voice_info["lang_code"]).lower()
    return DEFAULT_LANG


def get_languages() -> list[dict]:
    seen = {}
    for voice in get_voices():
        code = voice["lang_code"]
        if code not in seen:
            seen[code] = {
                "lang_code": code,
                "language": voice["language"],
            }
    return list(seen.values())
