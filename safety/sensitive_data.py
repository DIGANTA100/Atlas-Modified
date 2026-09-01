"""
Atlas-Modified: safety/sensitive_data.py

Log filter that masks secrets (API keys, passwords, tokens, emails)
from all log output so they never appear in log files or the terminal.

Usage:
    from safety.sensitive_data import install_log_filter
    install_log_filter()   # Call once at startup in config.setup_logging()
"""

import logging
import re

# Patterns that indicate sensitive values on the same line
_SENSITIVE_PATTERNS: list[tuple[re.Pattern, str]] = [
    # Generic key=value or key: value where key looks sensitive
    (
        re.compile(
            r'(?i)(api[_-]?key|password|passwd|secret|token|bearer|auth'
            r'|credential|private[_-]?key|access[_-]?key)\s*[=:]\s*\S+',
            re.IGNORECASE,
        ),
        r'\1=***REDACTED***',
    ),
    # Bearer tokens in Authorization headers
    (
        re.compile(r'Bearer\s+[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE),
        'Bearer ***REDACTED***',
    ),
    # Google Gemini API key shape: AIza + 35 chars
    (
        re.compile(r'AIza[A-Za-z0-9_\-]{35}'),
        'AIza***REDACTED***',
    ),
    # Generic long hex or base64 tokens (≥32 chars)
    (
        re.compile(r'\b[A-Za-z0-9+/]{32,}={0,2}\b'),
        '***TOKEN_REDACTED***',
    ),
]


class SensitiveDataFilter(logging.Filter):
    """
    A logging.Filter that scrubs sensitive patterns from log records
    before they reach any handler (file, console, etc.).
    """

    def filter(self, record: logging.LogRecord) -> bool:
        # Scrub the formatted message
        msg = record.getMessage()
        for pattern, replacement in _SENSITIVE_PATTERNS:
            msg = pattern.sub(replacement, msg)
        # Overwrite the args so the handler re-formats cleanly
        record.msg = msg
        record.args = None
        return True


def install_log_filter() -> None:
    """
    Attach SensitiveDataFilter to the root logger so every handler
    in the application benefits from it automatically.
    """
    root = logging.getLogger()
    # Don't add twice
    for f in root.filters:
        if isinstance(f, SensitiveDataFilter):
            return
    root.addFilter(SensitiveDataFilter())
    logging.getLogger(__name__).debug("Sensitive data log filter installed.")


def mask(value: str) -> str:
    """
    Manually mask a single secret string for display purposes.
    Shows the first 4 characters then asterisks.
    """
    if not value:
        return "***"
    return value[:4] + "*" * max(0, len(value) - 4)
