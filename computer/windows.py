"""
Atlas-Modified: computer/windows.py
Windows application and window management.
Uses subprocess for launching, pywin32/win32gui for window control.
Falls back gracefully if pywin32 is unavailable.
"""

import logging
import subprocess
import time
from typing import Optional

logger = logging.getLogger(__name__)

# ── Optional pywin32 import ────────────────────────────────────────────────────
try:
    import win32gui
    import win32con
    import win32process
    import psutil
    _WIN32_AVAILABLE = True
except ImportError:
    logger.warning("pywin32/psutil not available — some window functions limited")
    _WIN32_AVAILABLE = False


# ─── Application Launching ────────────────────────────────────────────────────

# Common application name → executable mapping
APP_ALIASES: dict[str, str] = {
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "firefox": "firefox.exe",
    "edge": "msedge.exe",
    "microsoft edge": "msedge.exe",
    "notepad": "notepad.exe",
    "notepad++": "notepad++.exe",
    "vs code": "code.exe",
    "vscode": "code.exe",
    "visual studio code": "code.exe",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "discord": "discord.exe",
    "spotify": "spotify.exe",
    "task manager": "taskmgr.exe",
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",
    "powershell": "powershell.exe",
    "terminal": "wt.exe",
    "windows terminal": "wt.exe",
}


def open_application(name: str) -> bool:
    """
    Launch an application by name or executable path.

    Args:
        name: Application name (e.g. "Chrome", "VS Code") or full path.

    Returns:
        True if launched successfully, False otherwise.
    """
    exe = APP_ALIASES.get(name.lower(), name)
    logger.info("Open application: %s (exe: %s)", name, exe)
    try:
        subprocess.Popen(
            [exe],
            shell=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
        time.sleep(1.0)  # Give app time to start
        return True
    except FileNotFoundError:
        logger.error("Application not found: %s", exe)
        return False
    except Exception as e:
        logger.error("Failed to open %s: %s", name, e)
        return False


def open_url_in_browser(url: str, browser: str = "chrome") -> bool:
    """Open a URL in the default or specified browser."""
    import webbrowser
    logger.info("Open URL: %s", url)
    try:
        webbrowser.open(url)
        time.sleep(1.5)
        return True
    except Exception as e:
        logger.error("Failed to open URL %s: %s", url, e)
        return False


# ─── Window Management ────────────────────────────────────────────────────────

def list_windows() -> list[dict]:
    """
    Return a list of all visible, non-minimized windows.
    Each dict has keys: hwnd, title, pid, exe.
    """
    if not _WIN32_AVAILABLE:
        logger.warning("pywin32 unavailable — cannot list windows")
        return []

    windows = []

    def _enum_callback(hwnd: int, _: None) -> None:
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            title = win32gui.GetWindowText(hwnd)
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    proc = psutil.Process(pid)
                    exe = proc.name()
                except Exception:
                    exe = ""
            except Exception:
                pid, exe = 0, ""
            windows.append({"hwnd": hwnd, "title": title, "pid": pid, "exe": exe})

    win32gui.EnumWindows(_enum_callback, None)
    return windows


def find_window(title_contains: str) -> Optional[int]:
    """Find the first window whose title contains the given string. Returns hwnd or None."""
    if not _WIN32_AVAILABLE:
        return None
    for w in list_windows():
        if title_contains.lower() in w["title"].lower():
            logger.info("Found window: '%s' (hwnd=%d)", w["title"], w["hwnd"])
            return w["hwnd"]
    logger.warning("Window not found: '%s'", title_contains)
    return None


def focus_window(hwnd: int) -> bool:
    """Bring a window to the foreground by its handle."""
    if not _WIN32_AVAILABLE:
        return False
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.3)
        logger.info("Focused window: hwnd=%d", hwnd)
        return True
    except Exception as e:
        logger.error("Failed to focus window %d: %s", hwnd, e)
        return False


def switch_to_window(title_contains: str) -> bool:
    """Find and focus a window by partial title match."""
    hwnd = find_window(title_contains)
    if hwnd:
        return focus_window(hwnd)
    return False


def minimize_window(hwnd: Optional[int] = None) -> bool:
    """Minimize a window (or the active window if hwnd is None)."""
    if not _WIN32_AVAILABLE:
        import pyautogui
        pyautogui.hotkey("win", "down")
        return True
    if hwnd is None:
        hwnd = win32gui.GetForegroundWindow()
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
    logger.info("Minimized window: hwnd=%d", hwnd)
    return True


def maximize_window(hwnd: Optional[int] = None) -> bool:
    """Maximize a window (or the active window if hwnd is None)."""
    if not _WIN32_AVAILABLE:
        import pyautogui
        pyautogui.hotkey("win", "up")
        return True
    if hwnd is None:
        hwnd = win32gui.GetForegroundWindow()
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
    logger.info("Maximized window: hwnd=%d", hwnd)
    return True


def restore_window(hwnd: Optional[int] = None) -> bool:
    """Restore a minimized/maximized window to normal size."""
    if not _WIN32_AVAILABLE:
        return False
    if hwnd is None:
        hwnd = win32gui.GetForegroundWindow()
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    return True


def close_active_window() -> None:
    """Close the currently focused window using Alt+F4."""
    import pyautogui
    logger.info("Close active window (Alt+F4)")
    pyautogui.hotkey("alt", "f4")


def show_desktop() -> None:
    """Minimize all windows and show the desktop."""
    import pyautogui
    logger.info("Show desktop (Win+D)")
    pyautogui.hotkey("win", "d")


def switch_app(forward: bool = True) -> None:
    """
    Switch to the next (or previous) application using Alt+Tab.

    Args:
        forward: True = next window, False = previous (Alt+Shift+Tab).
    """
    import pyautogui
    if forward:
        pyautogui.hotkey("alt", "tab")
    else:
        pyautogui.hotkey("alt", "shift", "tab")
    time.sleep(0.3)
