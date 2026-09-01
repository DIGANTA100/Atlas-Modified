"""
Atlas-Modified: computer/scroll.py
Scroll control — up, down, horizontal, page-level, and element-seeking scroll.
"""

import logging
import time

import pyautogui

logger = logging.getLogger(__name__)

# Pixels per scroll "click"
SCROLL_UNIT = 3


def scroll_down(
    clicks: int = SCROLL_UNIT,
    x: int | None = None,
    y: int | None = None,
) -> None:
    """
    Scroll down at the current position or at (x, y).

    Args:
        clicks: Number of scroll units (positive = down).
        x, y: Optional position to scroll at.
    """
    if x is not None and y is not None:
        pyautogui.moveTo(x, y, duration=0.1)
    logger.info("Scroll down: %d clicks", clicks)
    pyautogui.scroll(-clicks)


def scroll_up(
    clicks: int = SCROLL_UNIT,
    x: int | None = None,
    y: int | None = None,
) -> None:
    """Scroll up at the current position or at (x, y)."""
    if x is not None and y is not None:
        pyautogui.moveTo(x, y, duration=0.1)
    logger.info("Scroll up: %d clicks", clicks)
    pyautogui.scroll(clicks)


def scroll_left(clicks: int = SCROLL_UNIT) -> None:
    """Horizontal scroll left."""
    logger.info("Scroll left: %d clicks", clicks)
    pyautogui.hscroll(-clicks)


def scroll_right(clicks: int = SCROLL_UNIT) -> None:
    """Horizontal scroll right."""
    logger.info("Scroll right: %d clicks", clicks)
    pyautogui.hscroll(clicks)


def page_down() -> None:
    """Scroll down one full page using the Page Down key."""
    logger.info("Page down")
    pyautogui.press("pagedown")


def page_up() -> None:
    """Scroll up one full page using the Page Up key."""
    logger.info("Page up")
    pyautogui.press("pageup")


def scroll_to_top() -> None:
    """Jump to the top of the page/document using Ctrl+Home."""
    logger.info("Scroll to top")
    pyautogui.hotkey("ctrl", "home")


def scroll_to_bottom() -> None:
    """Jump to the bottom of the page/document using Ctrl+End."""
    logger.info("Scroll to bottom")
    pyautogui.hotkey("ctrl", "end")


def scroll_large_down(steps: int = 5) -> None:
    """Scroll down a large amount (multiple page-downs)."""
    for _ in range(steps):
        pyautogui.scroll(-SCROLL_UNIT * 5)
        time.sleep(0.1)


def scroll_large_up(steps: int = 5) -> None:
    """Scroll up a large amount."""
    for _ in range(steps):
        pyautogui.scroll(SCROLL_UNIT * 5)
        time.sleep(0.1)
