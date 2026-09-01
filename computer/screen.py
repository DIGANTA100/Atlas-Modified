"""
Atlas-Modified: computer/screen.py
Screenshot capture and screen information utilities.
Uses mss for fast multi-monitor capture, Pillow for image processing.
"""

import io
import logging
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

import mss
import mss.tools
from PIL import Image

logger = logging.getLogger(__name__)

SCREENSHOT_DIR = Path("screenshots")


class ScreenRegion(NamedTuple):
    left: int
    top: int
    width: int
    height: int


def get_screen_size(monitor: int = 1) -> tuple[int, int]:
    """
    Return the (width, height) of the specified monitor.
    Monitor 0 = combined virtual screen, 1 = primary, 2 = secondary, etc.
    """
    with mss.mss() as sct:
        m = sct.monitors[monitor]
        return (m["width"], m["height"])


def take_screenshot(
    region: ScreenRegion | None = None,
    monitor: int = 1,
    save: bool = False,
    filename: str | None = None,
) -> Image.Image:
    """
    Capture a screenshot and return it as a Pillow Image.

    Args:
        region: Optional (left, top, width, height) to capture a sub-region.
        monitor: Which monitor to capture (1 = primary).
        save: If True, save the screenshot to the screenshots/ folder.
        filename: Optional filename for saving (auto-generated if None).

    Returns:
        PIL.Image.Image in RGB mode.
    """
    with mss.mss() as sct:
        if region:
            grab_region = {
                "left": region.left,
                "top": region.top,
                "width": region.width,
                "height": region.height,
            }
        else:
            grab_region = sct.monitors[monitor]

        raw = sct.grab(grab_region)
        img = Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")

    logger.debug("Screenshot captured: %dx%d", img.width, img.height)

    if save:
        _save_screenshot(img, filename)

    return img


def screenshot_to_bytes(
    region: ScreenRegion | None = None,
    monitor: int = 1,
    fmt: str = "PNG",
) -> bytes:
    """
    Capture a screenshot and return it as raw bytes (PNG by default).
    Used for sending to Gemini Vision API.
    """
    img = take_screenshot(region=region, monitor=monitor)
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def screenshot_to_base64(
    region: ScreenRegion | None = None,
    monitor: int = 1,
) -> str:
    """
    Capture screenshot and return as base64-encoded PNG string.
    Suitable for embedding in Gemini API requests.
    """
    import base64
    raw = screenshot_to_bytes(region=region, monitor=monitor)
    return base64.b64encode(raw).decode("utf-8")


def _save_screenshot(img: Image.Image, filename: str | None = None) -> Path:
    """Save a Pillow Image to the screenshots/ directory."""
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    if not filename:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"screenshot_{ts}.png"
    path = SCREENSHOT_DIR / filename
    img.save(path)
    logger.info("Screenshot saved: %s", path)
    return path


def list_monitors() -> list[dict]:
    """Return a list of all detected monitors with their geometry."""
    with mss.mss() as sct:
        return list(sct.monitors)
