"""
Atlas-Modified: tests/test_clipboard.py
Tests for clipboard read/write/clear operations.
"""

import pytest


def test_write_and_read():
    from computer.clipboard import write_clipboard, read_clipboard
    test_text = "Atlas clipboard test 12345"
    write_clipboard(test_text)
    result = read_clipboard()
    assert result == test_text


def test_clear_clipboard():
    from computer.clipboard import write_clipboard, read_clipboard, clear_clipboard
    write_clipboard("some content")
    clear_clipboard()
    result = read_clipboard()
    assert result == ""


def test_read_empty_clipboard():
    from computer.clipboard import clear_clipboard, read_clipboard
    clear_clipboard()
    result = read_clipboard()
    assert isinstance(result, str)


def test_unicode_clipboard():
    from computer.clipboard import write_clipboard, read_clipboard
    unicode_text = "Hello 世界 🌍 مرحبا Привет"
    write_clipboard(unicode_text)
    result = read_clipboard()
    assert result == unicode_text
