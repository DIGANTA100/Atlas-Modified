"""
Atlas-Modified: ai/computer_use.py
Full Vision-Grounded Computer Use Agent Loop — Performance Optimized.

The complete See → Think → Act → Verify cycle, with the following optimizations:
  - Session is pre-warmed at startup (no cold-start lag on first command)
  - Tool calls executed in PARALLEL (ThreadPoolExecutor)
  - Verification screenshot ONLY taken for visual tools (click, scroll, etc.)
  - Screenshot pause reduced to 0.1s for visual tools, 0.0s for text tools
  - Screenshots downscaled + JPEG compressed (10x smaller upload)
  - Session reused across tasks (no re-initialization overhead)
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from google.genai import types

from ai import gemini_client
from tools.executor import execute_tool, ExecutionError, PermissionDeniedError
from computer.screen import screenshot_to_bytes
from app import config

logger = logging.getLogger(__name__)

# ── Safety limits ─────────────────────────────────────────────────────────────
MAX_STEPS = 25

# ── Tools that visually change the screen — only these get a verification shot ─
_VISUAL_TOOLS = {
    "mouse_click", "mouse_double_click", "mouse_right_click", "mouse_move",
    "scroll_up", "scroll_down", "scroll_to",
    "open_application", "open_url", "open_file", "open_folder",
    "switch_window", "minimize_window", "maximize_window", "close_window",
    "browser_navigate", "browser_click",
    "hotkey", "shortcut", "press_key",
}

# ── Executor for parallel tool calls ─────────────────────────────────────────
_executor = ThreadPoolExecutor(max_workers=8, thread_name_prefix="atlas-tool")


class ComputerUseAgent:
    """
    Vision-grounded agent that sees the screen and acts on it.
    Pre-warmed at startup to eliminate cold-start delay.
    """

    def __init__(self) -> None:
        self._chat: Any = None

    # ── Session management ────────────────────────────────────────────────────

    def _get_or_create_chat(self) -> Any:
        if self._chat is None:
            self._chat = gemini_client.create_chat_session()
        return self._chat

    def prewarm(self) -> None:
        """
        Pre-initialize the Gemini session in the background.
        Call this once at startup so the first user command has zero cold-start lag.
        """
        logger.info("[ComputerUse] Pre-warming Gemini session…")
        self._get_or_create_chat()
        logger.info("[ComputerUse] Session ready.")

    def reset(self) -> None:
        """Reset the conversation context."""
        self._chat = None
        logger.info("ComputerUseAgent context reset.")

    # ── Screenshot ────────────────────────────────────────────────────────────

    def _capture_screen_part(self) -> types.Part:
        """Take a compressed screenshot and return as a Gemini image Part."""
        raw = screenshot_to_bytes()  # JPEG, 1280px wide, ~30-60 KB
        return types.Part.from_bytes(data=raw, mime_type="image/jpeg")

    # ── Parallel tool execution ───────────────────────────────────────────────

    def _execute_tool_safe(self, tool_name: str, args: dict) -> tuple[str, Any, bool]:
        """
        Execute a single tool call.
        Returns (tool_name, result_or_error, is_visual).
        """
        is_visual = tool_name in _VISUAL_TOOLS
        try:
            result = execute_tool(tool_name, args)
            payload = result if result is not None else "success"
            if not isinstance(payload, str):
                payload = str(payload)
            return (tool_name, payload, is_visual)
        except PermissionDeniedError:
            return (tool_name, "ERROR: User denied this action.", is_visual)
        except ExecutionError as e:
            return (tool_name, f"ERROR: {e}", is_visual)
        except Exception as e:
            logger.exception("Unexpected error executing tool %s", tool_name)
            return (tool_name, f"ERROR: Unexpected error: {e}", is_visual)

    def _run_tools_parallel(self, function_calls) -> tuple[list[types.Part], bool]:
        """
        Execute all tool calls from a single Gemini response in PARALLEL.
        Returns (tool_result_parts, any_visual_action_was_taken).
        """
        futures = {}
        for fc in function_calls:
            tool_name = fc.name
            args = dict(fc.args) if fc.args else {}
            logger.info("[ComputerUse] Dispatching tool: %s(%s)", tool_name, args)
            future = _executor.submit(self._execute_tool_safe, tool_name, args)
            futures[future] = tool_name

        result_parts = []
        any_visual = False

        for future in as_completed(futures):
            tool_name, payload, is_visual = future.result()
            if is_visual:
                any_visual = True
            result_parts.append(
                types.Part.from_function_response(
                    name=tool_name,
                    response={"result": payload}
                )
            )
            logger.info("[ComputerUse] Tool done: %s → %s", tool_name, str(payload)[:80])

        return result_parts, any_visual

    # ── Main agent loop ───────────────────────────────────────────────────────

    def run(self, instruction: str) -> str:
        """
        Execute a natural-language instruction using the full see-think-act loop.
        """
        chat = self._get_or_create_chat()
        logger.info("[ComputerUse] Starting task: %s", instruction)

        # ── Initial message: screenshot + instruction ─────────────────────────
        screen_part = self._capture_screen_part()
        initial_message = [
            screen_part,
            types.Part.from_text(
                text=f"Current screen is shown above.\n\n"
                     f"Task: {instruction}\n\n"
                     f"Execute the task using the available tools. "
                     f"After completing all actions, reply with a short confirmation."
            ),
        ]

        try:
            response = chat.send_message(initial_message)
        except Exception as e:
            logger.error("Gemini API error on initial message: %s", e)
            return f"Failed to start task: {e}"

        # ── Main tool-execution loop ──────────────────────────────────────────
        for step in range(1, MAX_STEPS + 1):
            logger.info("[ComputerUse] Step %d/%d", step, MAX_STEPS)

            # No tool calls → Gemini is done, return its text
            if not response.function_calls:
                final_text = response.text or "Task complete."
                logger.info("[ComputerUse] Finished in %d step(s).", step - 1)
                return final_text

            # Execute all tools in parallel
            result_parts, any_visual = self._run_tools_parallel(response.function_calls)

            # Only pause + screenshot if a visual change actually happened
            if any_visual:
                time.sleep(0.1)  # 0.1s — just enough for the screen to update
                screen_part = self._capture_screen_part()
                followup_parts = result_parts + [
                    screen_part,
                    types.Part.from_text(
                        text="Screen updated (shown above). Continue or confirm done."
                    ),
                ]
            else:
                # Non-visual tools (type text, clipboard, filesystem) — skip screenshot
                followup_parts = result_parts + [
                    types.Part.from_text(
                        text="Actions completed. Continue or confirm done."
                    ),
                ]

            try:
                response = chat.send_message(followup_parts)
            except Exception as e:
                logger.error("Gemini API error at step %d: %s", step, e)
                return f"Task interrupted at step {step}: {e}"

        # ── Safety: exceeded max steps ────────────────────────────────────────
        logger.warning("[ComputerUse] Max steps (%d) reached.", MAX_STEPS)
        return (
            f"Reached the maximum of {MAX_STEPS} steps. "
            "The agent stopped to prevent unintended actions. Please review the screen."
        )


# ── Global singleton ──────────────────────────────────────────────────────────
computer_use_agent = ComputerUseAgent()
