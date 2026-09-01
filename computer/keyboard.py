"""
Atlas-Modified: computer/keyboard.py
Complete keyboard control — individual keys, text typing, hotkeys.
Supports all standard keys including function keys, media keys, Win key.
"""

import logging
import time

import pyautogui

logger = logging.getLogger(__name__)

# ── Key name mapping (natural language → pyautogui key names) ─────────────────
KEY_ALIASES: dict[str, str] = {
    "enter": "enter",
    "return": "enter",
    "escape": "esc",
    "esc": "esc",
    "tab": "tab",
    "space": "space",
    "backspace": "backspace",
    "delete": "delete",
    "del": "delete",
    "home": "home",
    "end": "end",
    "page up": "pageup",
    "pageup": "pageup",
    "page down": "pagedown",
    "pagedown": "pagedown",
    "insert": "insert",
    "up": "up",
    "down": "down",
    "left": "left",
    "right": "right",
    "f1": "f1", "f2": "f2", "f3": "f3", "f4": "f4",
    "f5": "f5", "f6": "f6", "f7": "f7", "f8": "f8",
    "f9": "f9", "f10": "f10", "f11": "f11", "f12": "f12",
    "windows": "win",
    "win": "win",
    "ctrl": "ctrl",
    "control": "ctrl",
    "alt": "alt",
    "shift": "shift",
    "caps lock": "capslock",
    "num lock": "numlock",
    "scroll lock": "scrolllock",
    "print screen": "printscreen",
    "pause": "pause",
    "break": "pause",
}

# Common shortcuts as high-level aliases
SHORTCUT_ALIASES: dict[str, list[str]] = {
    "copy": ["ctrl", "c"],
    "cut": ["ctrl", "x"],
    "paste": ["ctrl", "v"],
    "undo": ["ctrl", "z"],
    "redo": ["ctrl", "y"],
    "select all": ["ctrl", "a"],
    "save": ["ctrl", "s"],
    "save as": ["ctrl", "shift", "s"],
    "find": ["ctrl", "f"],
    "print": ["ctrl", "p"],
    "close tab": ["ctrl", "w"],
    "new tab": ["ctrl", "t"],
    "open new window": ["ctrl", "n"],
    "switch window": ["alt", "tab"],
    "close window": ["alt", "f4"],
    "show desktop": ["win", "d"],
    "open explorer": ["win", "e"],
    "open run": ["win", "r"],
    "open settings": ["win", "i"],
    "screenshot": ["win", "shift", "s"],
    "zoom in": ["ctrl", "+"],
    "zoom out": ["ctrl", "-"],
    "refresh": ["f5"],
    "full screen": ["f11"],
    "address bar": ["alt", "d"],
    "go back": ["alt", "left"],
    "go forward": ["alt", "right"],
}


def _resolve_key(key: str) -> str:
    """Normalize a key name to pyautogui's expected format."""
    return KEY_ALIASES.get(key.lower(), key.lower())


def press_key(key: str) -> None:
    """
    Press and release a single key.
    Accepts natural language key names (e.g. 'enter', 'escape', 'f5').
    """
    resolved = _resolve_key(key)
    logger.info("Press key: %s (resolved: %s)", key, resolved)
    pyautogui.press(resolved)


def hotkey(*keys: str) -> None:
    """
    Press a keyboard shortcut (multiple keys held simultaneously).
    Example: hotkey('ctrl', 'c') → Ctrl+C
    Example: hotkey('ctrl', 'shift', 's') → Ctrl+Shift+S
    """
    resolved = [_resolve_key(k) for k in keys]
    logger.info("Hotkey: %s", " + ".join(resolved))
    pyautogui.hotkey(*resolved)


def hotkey_by_name(shortcut_name: str) -> bool:
    """
    Press a common shortcut by its natural language name.
    E.g. hotkey_by_name('copy') → Ctrl+C
    Returns True if the shortcut was found, False otherwise.
    """
    keys = SHORTCUT_ALIASES.get(shortcut_name.lower())
    if keys:
        logger.info("Shortcut '%s' → %s", shortcut_name, keys)
        pyautogui.hotkey(*keys)
        return True
    logger.warning("Unknown shortcut alias: '%s'", shortcut_name)
    return False


def type_text(text: str, interval: float = 0.02) -> None:
    """
    Type a string of text with realistic key-press intervals.
    Handles normal characters, punctuation, numbers, and most symbols.
    For Unicode/special characters that pyautogui can't type, uses clipboard paste.

    Args:
        text: The text to type.
        interval: Seconds between each key press (simulates human typing speed).
    """
    logger.info("Type text (%d chars): %s…", len(text), text[:40])
    try:
        pyautogui.write(text, interval=interval)
    except Exception:
        # Fallback: paste via clipboard for non-ASCII or special characters
        logger.debug("pyautogui.write failed, falling back to clipboard paste")
        _type_via_clipboard(text)


def _type_via_clipboard(text: str) -> None:
    """
    Paste text using the clipboard — handles Unicode, code, symbols.
    Saves and restores existing clipboard content.
    """
    import pyperclip
    previous = ""
    try:
        previous = pyperclip.paste()
    except Exception:
        pass

    try:
        pyperclip.copy(text)
        time.sleep(0.05)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.1)
    finally:
        try:
            if previous:
                pyperclip.copy(previous)
        except Exception:
            pass


def key_down(key: str) -> None:
    """Hold a key down without releasing."""
    resolved = _resolve_key(key)
    pyautogui.keyDown(resolved)


def key_up(key: str) -> None:
    """Release a held key."""
    resolved = _resolve_key(key)
    pyautogui.keyUp(resolved)
