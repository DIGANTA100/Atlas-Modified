"""
Atlas-Modified: safety/emergency_stop.py

Emergency stop system for Atlas.
Two parallel mechanisms:
  1. FAILSAFE (pyautogui): Move mouse to top-left corner → raises exception in any pyautogui call
  2. Hotkey listener: Ctrl+Shift+F12 → sets agent_state.emergency_stop = True from any thread

The background listener runs as a daemon thread so it is always active
while Atlas is running, regardless of what the agent is doing.
"""

import logging
import threading
from typing import Callable

logger = logging.getLogger(__name__)

# The physical keyboard hotkey to trigger emergency stop
STOP_HOTKEY = "<ctrl>+<shift>+<f12>"

_listener_thread: threading.Thread | None = None
_stop_callbacks: list[Callable[[], None]] = []


def register_stop_callback(fn: Callable[[], None]) -> None:
    """Register a function to be called when emergency stop fires."""
    _stop_callbacks.append(fn)


def _trigger_stop() -> None:
    """Internal: called when the hotkey is detected."""
    logger.critical("⛔ EMERGENCY STOP triggered (Ctrl+Shift+F12)")
    print("\n\n⛔ EMERGENCY STOP! Agent halted. Type 'resume' to continue.\n")
    for cb in _stop_callbacks:
        try:
            cb()
        except Exception as e:
            logger.error("Error in stop callback: %s", e)


def start_listener() -> None:
    """
    Start the background hotkey listener thread.
    Uses pynput.keyboard to listen for Ctrl+Shift+F12.
    Safe to call multiple times — only one listener will run.
    """
    global _listener_thread

    if _listener_thread and _listener_thread.is_alive():
        logger.debug("Emergency stop listener already running.")
        return

    try:
        from pynput import keyboard
    except ImportError:
        logger.warning(
            "pynput not installed. Emergency stop hotkey disabled. "
            "Install with: pip install pynput"
        )
        return

    def _on_activate() -> None:
        _trigger_stop()

    hotkey = keyboard.HotKey(
        keyboard.HotKey.parse(STOP_HOTKEY),
        on_activate=_on_activate,
    )

    def _for_canonical(f):
        def inner(key):
            f(listener.canonical(key))
        return inner

    listener = keyboard.Listener(
        on_press=_for_canonical(hotkey.press),
        on_release=_for_canonical(hotkey.release),
    )

    def _run() -> None:
        logger.info(
            "Emergency stop listener active. Press %s to halt the agent.", STOP_HOTKEY
        )
        listener.start()
        listener.join()

    _listener_thread = threading.Thread(target=_run, daemon=True, name="AtlasStopListener")
    _listener_thread.start()


def stop_listener() -> None:
    """Stop the background listener (called on clean shutdown)."""
    global _listener_thread
    if _listener_thread and _listener_thread.is_alive():
        # pynput listeners stop when the main program exits (daemon=True)
        _listener_thread = None
