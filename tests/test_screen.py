"""
Atlas-Modified: tests/test_screen.py
Tests for the screenshot/screen capture module.
"""

import pytest
from PIL import Image


def test_get_screen_size():
    from computer.screen import get_screen_size
    w, h = get_screen_size()
    assert w > 0
    assert h > 0
    assert w > 100   # Sanity: screen should be at least 100px wide
    assert h > 100


def test_take_screenshot_returns_image():
    from computer.screen import take_screenshot
    img = take_screenshot()
    assert isinstance(img, Image.Image)
    assert img.width > 0
    assert img.height > 0
    assert img.mode == "RGB"


def test_screenshot_to_bytes():
    from computer.screen import screenshot_to_bytes
    raw = screenshot_to_bytes()
    assert isinstance(raw, bytes)
    assert len(raw) > 1000  # Should be non-trivial size


def test_screenshot_to_base64():
    from computer.screen import screenshot_to_base64
    import base64
    b64 = screenshot_to_base64()
    assert isinstance(b64, str)
    # Verify it's valid base64
    decoded = base64.b64decode(b64)
    assert len(decoded) > 1000


def test_list_monitors():
    from computer.screen import list_monitors
    monitors = list_monitors()
    # Monitor 0 is the virtual combined screen; 1+ are physical monitors
    assert len(monitors) >= 2  # At least virtual + one physical
    for m in monitors:
        assert "width" in m
        assert "height" in m
