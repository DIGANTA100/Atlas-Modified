"""
Atlas-Modified: tests/test_mouse.py
Unit tests for the mouse control module.
These tests verify functions work without crashing.
(Visual verification — the mouse will actually move on screen during testing.)
"""

import time
import pytest
import pyautogui


def test_get_position():
    from computer.mouse import get_position
    x, y = get_position()
    assert isinstance(x, int)
    assert isinstance(y, int)
    assert x >= 0
    assert y >= 0


def test_move():
    from computer.mouse import move, get_position
    screen_w, screen_h = pyautogui.size()
    target_x = screen_w // 2
    target_y = screen_h // 2
    move(target_x, target_y, duration=0.1)
    time.sleep(0.2)
    pos_x, pos_y = get_position()
    # Allow ±5px tolerance
    assert abs(pos_x - target_x) <= 5
    assert abs(pos_y - target_y) <= 5


def test_move_relative():
    from computer.mouse import move, move_relative, get_position
    # Start at center
    screen_w, screen_h = pyautogui.size()
    move(screen_w // 2, screen_h // 2, duration=0.1)
    time.sleep(0.1)
    start_x, start_y = get_position()
    # Move right and down by 50
    move_relative(50, 50, duration=0.1)
    time.sleep(0.2)
    end_x, end_y = get_position()
    assert abs(end_x - (start_x + 50)) <= 5
    assert abs(end_y - (start_y + 50)) <= 5


def test_click_no_crash():
    """Verify click() doesn't raise when called at center screen."""
    from computer.mouse import move, click
    screen_w, screen_h = pyautogui.size()
    move(screen_w // 2, screen_h // 2, duration=0.1)
    time.sleep(0.1)
    # Just call click — it should not raise
    click()


def test_move_boundaries():
    """Mouse should clamp within screen bounds gracefully."""
    from computer.mouse import move
    screen_w, screen_h = pyautogui.size()
    # Moving near edges should work without crash
    move(10, 10, duration=0.1)
    time.sleep(0.1)
    move(screen_w - 10, screen_h - 10, duration=0.1)
    time.sleep(0.1)
