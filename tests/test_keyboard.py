"""
Atlas-Modified: tests/test_keyboard.py
Tests for keyboard control module.
"""

import pytest


def test_key_aliases():
    from computer.keyboard import _resolve_key
    assert _resolve_key("enter") == "enter"
    assert _resolve_key("escape") == "esc"
    assert _resolve_key("esc") == "esc"
    assert _resolve_key("page up") == "pageup"
    assert _resolve_key("windows") == "win"
    assert _resolve_key("delete") == "delete"
    assert _resolve_key("ENTER") == "enter"  # case-insensitive


def test_shortcut_aliases_exist():
    from computer.keyboard import SHORTCUT_ALIASES
    for name in ["copy", "paste", "undo", "redo", "select all", "save", "close tab"]:
        assert name in SHORTCUT_ALIASES, f"Missing shortcut alias: '{name}'"


def test_hotkey_by_name_known():
    from computer.keyboard import hotkey_by_name
    # 'undo' should return True (it's in the alias map)
    # We don't actually press the keys in unit test — just check it finds the alias
    # Use a mock approach: check the alias exists first
    from computer.keyboard import SHORTCUT_ALIASES
    assert "undo" in SHORTCUT_ALIASES


def test_hotkey_by_name_unknown():
    from computer.keyboard import hotkey_by_name
    # Unknown shortcut should return False without raising
    result = hotkey_by_name("not_a_real_shortcut_xyz")
    assert result is False


def test_type_text_does_not_crash(monkeypatch):
    """Verify type_text calls pyautogui.write without raising."""
    import computer.keyboard as kb
    called_with = {}

    def mock_write(text, interval=0.02):
        called_with["text"] = text

    monkeypatch.setattr("pyautogui.write", mock_write)
    kb.type_text("hello world")
    assert called_with.get("text") == "hello world"


def test_press_key_does_not_crash(monkeypatch):
    import computer.keyboard as kb
    pressed = {}

    def mock_press(key):
        pressed["key"] = key

    monkeypatch.setattr("pyautogui.press", mock_press)
    kb.press_key("enter")
    assert pressed.get("key") == "enter"
