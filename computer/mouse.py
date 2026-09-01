"""
Atlas-Modified: computer/mouse.py
Full mouse control — move, click, double-click, right-click, drag.
Uses pyautogui with FAILSAFE enabled (move mouse to top-left corner to abort).
"""

import logging
import time

import pyautogui

from app import config

logger = logging.getLogger(__name__)

# ── Safety settings ────────────────────────────────────────────────────────────
pyautogui.FAILSAFE = True          # Move to top-left corner to abort
pyautogui.PAUSE = config.ACTION_DELAY  # Small pause between actions


def get_position() -> tuple[int, int]:
    """Return the current mouse cursor position as (x, y)."""
    pos = pyautogui.position()
    logger.debug("Mouse position: %s", pos)
    return (pos.x, pos.y)


def move(x: int, y: int, duration: float = 0.3) -> None:
    """
    Move the mouse to absolute screen coordinates (x, y).

    Args:
        x: Target X coordinate (pixels from left).
        y: Target Y coordinate (pixels from top).
        duration: Animation duration in seconds (0 = instant).
    """
    logger.info("Move mouse → (%d, %d)", x, y)
    pyautogui.moveTo(x, y, duration=duration, tween=pyautogui.easeOutQuad)


def move_relative(dx: int, dy: int, duration: float = 0.2) -> None:
    """Move mouse relative to its current position."""
    logger.info("Move mouse relative → (%+d, %+d)", dx, dy)
    pyautogui.moveRel(dx, dy, duration=duration)


def click(
    x: int | None = None,
    y: int | None = None,
    button: str = "left",
    duration: float = 0.2,
) -> None:
    """
    Left-click (or right/middle-click) at position (x, y).
    If x and y are None, clicks at the current cursor position.
    """
    if x is not None and y is not None:
        move(x, y, duration=duration)
    logger.info("Click [%s] at (%s, %s)", button, x, y)
    pyautogui.click(button=button)


def double_click(x: int | None = None, y: int | None = None, duration: float = 0.2) -> None:
    """Double-click at position (x, y)."""
    if x is not None and y is not None:
        move(x, y, duration=duration)
    logger.info("Double-click at (%s, %s)", x, y)
    pyautogui.doubleClick()


def right_click(x: int | None = None, y: int | None = None, duration: float = 0.2) -> None:
    """Right-click at position (x, y)."""
    if x is not None and y is not None:
        move(x, y, duration=duration)
    logger.info("Right-click at (%s, %s)", x, y)
    pyautogui.rightClick()


def middle_click(x: int | None = None, y: int | None = None, duration: float = 0.2) -> None:
    """Middle-click at position (x, y)."""
    if x is not None and y is not None:
        move(x, y, duration=duration)
    logger.info("Middle-click at (%s, %s)", x, y)
    pyautogui.middleClick()


def drag(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration: float = 0.5,
    button: str = "left",
) -> None:
    """
    Click-and-drag from (start_x, start_y) to (end_x, end_y).

    Useful for:
    - Dragging files
    - Selecting text regions
    - Moving windows
    - Scrollbars
    """
    logger.info(
        "Drag [%s] (%d,%d) → (%d,%d)", button, start_x, start_y, end_x, end_y
    )
    pyautogui.moveTo(start_x, start_y, duration=0.2)
    pyautogui.mouseDown(button=button)
    time.sleep(0.05)
    pyautogui.moveTo(end_x, end_y, duration=duration, tween=pyautogui.easeInOutQuad)
    time.sleep(0.05)
    pyautogui.mouseUp(button=button)


def mouse_down(x: int | None = None, y: int | None = None, button: str = "left") -> None:
    """Press and hold a mouse button (without releasing)."""
    if x is not None and y is not None:
        move(x, y)
    pyautogui.mouseDown(button=button)


def mouse_up(button: str = "left") -> None:
    """Release a held mouse button."""
    pyautogui.mouseUp(button=button)
