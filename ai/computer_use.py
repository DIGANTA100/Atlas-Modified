"""
Atlas-Modified: ai/computer_use.py
Full Vision-Grounded Computer Use Agent Loop.

The complete See → Think → Act → Verify cycle:
1. Take a screenshot and send it to Gemini Vision
2. Gemini analyzes the screen and decides what tool(s) to call
3. We execute the tool(s) locally
4. Take another screenshot to verify the result
5. Repeat until task is done or max_steps is reached

This is the primary agent loop for Phase 7+. The text-only loop in planner.py
is kept for fallback and testing without a display.
"""

import logging
import time
from typing import Any

from google.genai import types

from ai import gemini_client
from tools.executor import execute_tool, ExecutionError, PermissionDeniedError
from voice.text_to_speech import speak
from computer.screen import screenshot_to_bytes
from app import config

logger = logging.getLogger(__name__)

# Safety limits
MAX_STEPS = 25            # Max tool-execution cycles per task
SCREENSHOT_PAUSE = 0.5   # Seconds to wait after an action before screenshotting


class ComputerUseAgent:
    """
    Vision-grounded agent that sees the screen and acts on it.
    """

    def __init__(self) -> None:
        self._chat: Any = None

    def _get_or_create_chat(self) -> Any:
        if self._chat is None:
            self._chat = gemini_client.create_chat_session()
        return self._chat

    def reset(self) -> None:
        """Reset the conversation context."""
        self._chat = None
        logger.info("ComputerUseAgent context reset.")

    def _capture_screen_part(self) -> types.Part:
        """Take a screenshot and return it as a Gemini-compatible image Part."""
        raw = screenshot_to_bytes()
        return types.Part.from_bytes(data=raw, mime_type="image/png")

    def run(self, instruction: str) -> str:
        """
        Execute a natural-language instruction using the full see-think-act loop.

        Args:
            instruction: What the user wants the agent to do.

        Returns:
            A summary of what was accomplished, or an error description.
        """
        chat = self._get_or_create_chat()
        logger.info("[ComputerUse] Starting task: %s", instruction)

        # ── Step 0: Take initial screenshot and send with the instruction ─────
        screen_part = self._capture_screen_part()
        initial_message = [
            screen_part,
            types.Part.from_text(
                f"The image above is the current state of the screen.\n\n"
                f"Your task: {instruction}\n\n"
                f"Use the available tools to accomplish this task. "
                f"I will send you an updated screenshot after each action so you can verify progress."
            ),
        ]

        try:
            response = chat.send_message(initial_message)
        except Exception as e:
            logger.error("Gemini API error on initial message: %s", e)
            return f"Failed to start task: {e}"

        # ── Main loop ─────────────────────────────────────────────────────────
        for step in range(1, MAX_STEPS + 1):
            logger.info("[ComputerUse] Step %d/%d", step, MAX_STEPS)

            # No more tool calls → Gemini is done
            if not response.function_calls:
                final_text = response.text or "Task complete."
                logger.info("[ComputerUse] Task complete in %d steps. Response: %s", step - 1, final_text)
                return final_text

            # ── Execute every tool Gemini requested ───────────────────────────
            tool_results = []
            for fc in response.function_calls:
                tool_name = fc.name
                args = dict(fc.args) if fc.args else {}
                logger.info("[ComputerUse] Executing tool: %s(%s)", tool_name, args)

                try:
                    result = execute_tool(tool_name, args)
                    result_payload = result if result is not None else "success"
                    # Serialize non-string results
                    if not isinstance(result_payload, str):
                        result_payload = str(result_payload)
                    tool_results.append({
                        "name": tool_name,
                        "response": {"result": result_payload}
                    })
                except PermissionDeniedError:
                    tool_results.append({
                        "name": tool_name,
                        "response": {"error": "User denied this action."}
                    })
                except ExecutionError as e:
                    tool_results.append({
                        "name": tool_name,
                        "response": {"error": str(e)}
                    })
                except Exception as e:
                    logger.exception("Unexpected error executing tool %s", tool_name)
                    tool_results.append({
                        "name": tool_name,
                        "response": {"error": f"Unexpected error: {e}"}
                    })

            # ── Pause briefly then take verification screenshot ────────────────
            time.sleep(SCREENSHOT_PAUSE)
            screen_part = self._capture_screen_part()

            # ── Send tool results + new screenshot back to Gemini ─────────────
            followup_parts = tool_results + [
                screen_part,
                types.Part.from_text(
                    "The image above shows the screen state after your actions. "
                    "Continue with the next steps or confirm the task is complete."
                ),
            ]

            try:
                response = chat.send_message(followup_parts)
            except Exception as e:
                logger.error("Gemini API error at step %d: %s", step, e)
                return f"Task interrupted at step {step}: {e}"

        # ── Safety: exceeded max steps ─────────────────────────────────────────
        logger.warning("[ComputerUse] Max steps (%d) reached without completion.", MAX_STEPS)
        return (
            f"Task reached the maximum of {MAX_STEPS} steps without a final confirmation. "
            "The agent stopped to prevent unintended actions. Please review the screen."
        )


# ── Global singleton ──────────────────────────────────────────────────────────
computer_use_agent = ComputerUseAgent()
