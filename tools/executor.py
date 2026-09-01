"""
Atlas-Modified: tools/executor.py
Tool executor — validates, permission-checks, and runs tools from the registry.
This is the ONLY place where Gemini-requested actions become real computer actions.
"""

import logging
import time
from typing import Any

from tools.registry import registry
from tools.permissions import get_risk, RiskLevel
from app import config
from app.state import agent_state, ActionRecord

logger = logging.getLogger(__name__)


class PermissionDeniedError(Exception):
    """Raised when a user declines a risky action."""
    pass


class ExecutionError(Exception):
    """Raised when a tool execution fails."""
    pass


def execute_tool(tool_name: str, args: dict[str, Any]) -> Any:
    """
    The main execution entry point.

    Flow:
        1. Check emergency stop
        2. Validate tool exists
        3. Check risk level and request confirmation if needed
        4. Execute the tool
        5. Record the action
        6. Return result

    Args:
        tool_name: Name of the tool to execute.
        args: Arguments to pass to the tool.

    Returns:
        The tool's return value (or None for void tools).

    Raises:
        PermissionDeniedError: If user declines a risky action.
        ExecutionError: If the tool fails after max retries.
    """
    # 1. Emergency stop check
    if agent_state.is_stopped():
        logger.warning("Emergency stop active — tool '%s' blocked", tool_name)
        raise ExecutionError("Emergency stop is active. Reset to continue.")

    # 2. Validate tool
    if not registry.has(tool_name):
        raise ValueError(f"Unknown tool: '{tool_name}'")

    # 3. Permission check
    risk = get_risk(tool_name)
    if not _check_permission(tool_name, args, risk):
        raise PermissionDeniedError(f"User declined action: {tool_name}")

    # 4. Execute with retry
    result = None
    last_error = None
    for attempt in range(1, config.MAX_RETRIES + 1):
        try:
            result = registry.call(tool_name, **args)
            break
        except Exception as e:
            last_error = e
            logger.warning(
                "Tool '%s' failed (attempt %d/%d): %s",
                tool_name, attempt, config.MAX_RETRIES, e,
            )
            if attempt < config.MAX_RETRIES:
                time.sleep(0.5 * attempt)

    if last_error and result is None and attempt == config.MAX_RETRIES:
        record = ActionRecord(
            tool=tool_name,
            args=args,
            result=str(last_error),
            success=False,
            retries=attempt,
        )
        agent_state.record_action(record)
        raise ExecutionError(f"Tool '{tool_name}' failed after {attempt} attempts: {last_error}")

    # 5. Record success
    record = ActionRecord(
        tool=tool_name,
        args=args,
        result=str(result) if result is not None else "ok",
        success=True,
        retries=attempt - 1,
    )
    agent_state.record_action(record)
    logger.info("Tool '%s' completed successfully", tool_name)
    return result


def _check_permission(tool_name: str, args: dict[str, Any], risk: RiskLevel) -> bool:
    """
    Check if a tool is allowed to execute given its risk level and config.

    Returns:
        True = proceed, False = denied.
    """
    if risk == RiskLevel.LOW:
        return True

    if risk == RiskLevel.MEDIUM and not config.CONFIRM_MEDIUM_RISK:
        return True

    if risk == RiskLevel.HIGH and not config.CONFIRM_HIGH_RISK:
        return True

    # Ask user for confirmation via stdin (Phase 9 will use a UI dialog)
    risk_label = risk.value.upper()
    print(f"\n⚠️  [{risk_label} RISK] Action requested: {tool_name}")
    if args:
        print(f"   Arguments: {args}")
    response = input("   Proceed? (y/n): ").strip().lower()
    return response in ("y", "yes")
