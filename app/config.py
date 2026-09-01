"""
Atlas-Modified: app/config.py
Loads configuration from .env and exposes typed, validated settings.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# ─── Load .env ─────────────────────────────────────────────────────────────────
_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=_env_path, override=False)


def _get(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def _get_bool(key: str, default: bool = False) -> bool:
    val = _get(key, str(default)).lower()
    return val in ("1", "true", "yes", "on")


def _get_float(key: str, default: float = 0.0) -> float:
    try:
        return float(_get(key, str(default)))
    except ValueError:
        return default


def _get_int(key: str, default: int = 0) -> int:
    try:
        return int(_get(key, str(default)))
    except ValueError:
        return default


# ─── Gemini ───────────────────────────────────────────────────────────────────
GEMINI_API_KEY: str = _get("GEMINI_API_KEY")
GEMINI_TEXT_MODEL: str = _get("GEMINI_TEXT_MODEL", "gemini-2.0-flash")
GEMINI_VISION_MODEL: str = _get("GEMINI_VISION_MODEL", "gemini-2.0-flash")

# ─── Voice / TTS ──────────────────────────────────────────────────────────────
TTS_PROVIDER: str = _get("TTS_PROVIDER", "pyttsx3")
ELEVENLABS_API_KEY: str = _get("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID: str = _get("ELEVENLABS_VOICE_ID")

# ─── Speech Recognition ───────────────────────────────────────────────────────
STT_PROVIDER: str = _get("STT_PROVIDER", "google")

# ─── Wake Word ────────────────────────────────────────────────────────────────
WAKE_WORD: str = _get("WAKE_WORD", "atlas")
WAKE_WORD_ENABLED: bool = _get_bool("WAKE_WORD_ENABLED", False)

# ─── Agent Behavior ───────────────────────────────────────────────────────────
ACTIVATION_HOTKEY: str = _get("ACTIVATION_HOTKEY", "ctrl+space")
ACTION_DELAY: float = _get_float("ACTION_DELAY", 0.5)
MAX_RETRIES: int = _get_int("MAX_RETRIES", 3)

# ─── Safety ───────────────────────────────────────────────────────────────────
CONFIRM_MEDIUM_RISK: bool = _get_bool("CONFIRM_MEDIUM_RISK", True)
CONFIRM_HIGH_RISK: bool = _get_bool("CONFIRM_HIGH_RISK", True)
EMERGENCY_STOP_HOTKEY: str = _get("EMERGENCY_STOP_HOTKEY", "ctrl+shift+F12")

# ─── Browser ──────────────────────────────────────────────────────────────────
BROWSER_TYPE: str = _get("BROWSER_TYPE", "chromium")
BROWSER_HEADLESS: bool = _get_bool("BROWSER_HEADLESS", False)

# ─── Logging ──────────────────────────────────────────────────────────────────
LOG_LEVEL: str = _get("LOG_LEVEL", "INFO").upper()
LOG_DIR: Path = Path(_get("LOG_DIR", "logs"))
REDACT_SENSITIVE: bool = _get_bool("REDACT_SENSITIVE", True)


def validate() -> None:
    """Raise an error if critical config values are missing."""
    if not GEMINI_API_KEY:
        raise EnvironmentError(
            "GEMINI_API_KEY is not set. "
            "Copy .env.example to .env and add your Google AI Studio API key."
        )


def setup_logging() -> None:
    """Configure the root logger."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    level = getattr(logging, LOG_LEVEL, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_DIR / "atlas.log", encoding="utf-8"),
        ],
    )
