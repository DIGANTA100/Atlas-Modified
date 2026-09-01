"""
Atlas-Modified: tools/permissions.py
Risk classification for all agent actions.
Low risk = auto-execute, Medium = ask, High = require explicit confirmation.
"""

from enum import Enum


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# ── Tool risk registry ─────────────────────────────────────────────────────────
TOOL_RISK: dict[str, RiskLevel] = {
    # LOW RISK — auto-execute
    "mouse_move": RiskLevel.LOW,
    "mouse_click": RiskLevel.LOW,
    "mouse_double_click": RiskLevel.LOW,
    "mouse_right_click": RiskLevel.LOW,
    "scroll_up": RiskLevel.LOW,
    "scroll_down": RiskLevel.LOW,
    "scroll_to_top": RiskLevel.LOW,
    "scroll_to_bottom": RiskLevel.LOW,
    "page_up": RiskLevel.LOW,
    "page_down": RiskLevel.LOW,
    "press_key": RiskLevel.LOW,
    "type_text": RiskLevel.LOW,
    "hotkey": RiskLevel.LOW,
    "copy": RiskLevel.LOW,
    "paste": RiskLevel.LOW,
    "undo": RiskLevel.LOW,
    "redo": RiskLevel.LOW,
    "take_screenshot": RiskLevel.LOW,
    "read_clipboard": RiskLevel.LOW,
    "open_application": RiskLevel.LOW,
    "open_url": RiskLevel.LOW,
    "switch_window": RiskLevel.LOW,
    "minimize_window": RiskLevel.LOW,
    "maximize_window": RiskLevel.LOW,
    "close_active_window": RiskLevel.LOW,
    "show_desktop": RiskLevel.LOW,
    "switch_app": RiskLevel.LOW,
    "open_folder": RiskLevel.LOW,
    "list_folder": RiskLevel.LOW,
    "find_file": RiskLevel.LOW,
    "browser_back": RiskLevel.LOW,
    "browser_forward": RiskLevel.LOW,
    "browser_refresh": RiskLevel.LOW,
    "new_tab": RiskLevel.LOW,
    "close_tab": RiskLevel.LOW,

    # MEDIUM RISK — ask before executing
    "write_clipboard": RiskLevel.MEDIUM,
    "move_file": RiskLevel.MEDIUM,
    "rename_file": RiskLevel.MEDIUM,
    "rename_folder": RiskLevel.MEDIUM,
    "copy_file": RiskLevel.MEDIUM,
    "download_file": RiskLevel.MEDIUM,
    "upload_file": RiskLevel.MEDIUM,
    "create_file": RiskLevel.MEDIUM,
    "create_folder": RiskLevel.MEDIUM,
    "send_message": RiskLevel.MEDIUM,
    "submit_form": RiskLevel.MEDIUM,
    "drag": RiskLevel.MEDIUM,

    # HIGH RISK — require explicit confirmation
    "delete_file": RiskLevel.HIGH,
    "delete_folder": RiskLevel.HIGH,
    "execute_command": RiskLevel.HIGH,
    "run_script": RiskLevel.HIGH,
    "change_settings": RiskLevel.HIGH,
    "purchase": RiskLevel.HIGH,
    "shutdown": RiskLevel.HIGH,
    "restart": RiskLevel.HIGH,
    "format_drive": RiskLevel.HIGH,
    "uninstall_app": RiskLevel.HIGH,
}


def get_risk(tool_name: str) -> RiskLevel:
    """Return the risk level for a given tool name. Defaults to MEDIUM if unknown."""
    return TOOL_RISK.get(tool_name, RiskLevel.MEDIUM)


def is_auto_executable(tool_name: str) -> bool:
    """Return True if this tool can be executed without user confirmation."""
    return get_risk(tool_name) == RiskLevel.LOW
