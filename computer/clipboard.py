"""
Atlas-Modified: computer/clipboard.py
Clipboard read/write — uses pyperclip for cross-format text clipboard support.
"""

import logging

import pyperclip

logger = logging.getLogger(__name__)


def read_clipboard() -> str:
    """
    Read and return the current text content of the clipboard.
    Returns empty string if clipboard is empty or contains non-text content.
    """
    try:
        content = pyperclip.paste() or ""
        logger.info("Read clipboard (%d chars)", len(content))
        return content
    except Exception as e:
        logger.warning("Could not read clipboard: %s", e)
        return ""


def write_clipboard(text: str) -> None:
    """
    Write text to the clipboard.

    Args:
        text: The text to place on the clipboard.
    """
    logger.info("Write clipboard (%d chars): %s…", len(text), text[:40])
    pyperclip.copy(text)


def clear_clipboard() -> None:
    """Clear the clipboard by writing an empty string."""
    logger.info("Clear clipboard")
    pyperclip.copy("")


def append_to_clipboard(text: str) -> None:
    """Append text to whatever is currently on the clipboard."""
    current = read_clipboard()
    write_clipboard(current + text)
