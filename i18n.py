"""Offline UI localization for Cloudflare Telegram Manager.

The source language is Persian. The catalog consists of exact user-visible source
fragments (including f-string fragments), not machine-translated runtime text.
HTML tags, API data, callback_data and credentials are never changed by the
localization layer itself.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

LANGUAGES = ("fa", "en", "ru")
CATALOG: dict[str, dict[str, str]] = json.loads(
    Path(__file__).with_name("locales.json").read_text(encoding="utf-8")
)
_PATTERN = re.compile("|".join(re.escape(key) for key in sorted(CATALOG, key=len, reverse=True)))


def translate_text(text: str, language: str = "fa") -> str:
    """Render a Persian UI template in the selected language.

    Dynamic account names, domain names, IDs and technical values remain intact.
    Keep placeholders already escaped by the caller when emitting HTML.
    """
    if not isinstance(text, str) or language not in ("en", "ru"):
        return text
    return _PATTERN.sub(lambda match: CATALOG[match.group(0)][language], text)
