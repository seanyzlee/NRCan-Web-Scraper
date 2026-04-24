"""
settings.py — Load, save, and merge user settings with config.py defaults.

user_settings.json is a sparse override file — it only stores what the
user has changed from the defaults in config.py.
"""

import json
import os
from pathlib import Path

import config

_DATA_DIR     = Path(os.environ.get("DATA_DIR", "."))
SETTINGS_FILE = _DATA_DIR / "user_settings.json"

_DEFAULTS = {
    "lookback_days": config.LOOKBACK_DAYS,
    "keywords_extra": [],
    "keywords_removed": [],
    "disabled_sources": [],
}


def load_raw() -> dict:
    """Return the raw user_settings.json contents (or empty dict)."""
    if not SETTINGS_FILE.exists():
        return {}
    try:
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save(data: dict) -> None:
    """Persist the settings dict to user_settings.json."""
    SETTINGS_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def get_effective() -> dict:
    """
    Merge user_settings.json on top of config.py defaults.
    Returns a dict ready for the scraper and templates.
    """
    user = load_raw()

    removed = set(user.get("keywords_removed", []))
    extra   = user.get("keywords_extra", [])

    effective_keywords = [kw for kw in config.KEYWORDS if kw not in removed] + extra

    disabled = set(user.get("disabled_sources", []))
    effective_sources = [s for s in config.SOURCES if s["name"] not in disabled]

    return {
        # --- for the scraper ---
        "lookback_days":    user.get("lookback_days", config.LOOKBACK_DAYS),
        "keywords":         effective_keywords,
        "sources":          effective_sources,
        # --- for the settings UI ---
        "all_sources":      config.SOURCES,
        "disabled_sources": list(disabled),
        "keyword_groups":   config.KEYWORD_GROUPS,
        "keywords_extra":   extra,
        "keywords_removed": list(removed),
    }


def save_from_form(form: dict) -> None:
    """
    Parse a Flask request.form MultiDict and persist to user_settings.json.
    Expects:
      lookback_days       — int as string
      disabled_sources    — repeated field, one value per disabled source name
      keywords_removed    — repeated field, one value per removed keyword
      keywords_extra      — newline-separated string of extra keywords
    """
    try:
        days = int(form.get("lookback_days", config.LOOKBACK_DAYS))
    except ValueError:
        days = config.LOOKBACK_DAYS

    disabled = form.getlist("disabled_sources")

    removed = form.getlist("keywords_removed")

    extra_raw = form.get("keywords_extra", "")
    extra = [kw.strip() for kw in extra_raw.splitlines() if kw.strip()]

    save({
        "lookback_days":    days,
        "disabled_sources": disabled,
        "keywords_removed": removed,
        "keywords_extra":   extra,
    })
