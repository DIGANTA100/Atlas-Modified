"""
Atlas-Modified: app/state.py
Global agent state — tracks the current task, action history,
conversation context, and execution mode.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any


class AgentMode(Enum):
    IDLE = auto()
    LISTENING = auto()
    THINKING = auto()
    ACTING = auto()
    WAITING_CONFIRMATION = auto()
    DICTATION = auto()
    STOPPED = auto()


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ActionRecord:
    """A single executed action with its outcome."""
    timestamp: datetime = field(default_factory=datetime.now)
    tool: str = ""
    args: dict[str, Any] = field(default_factory=dict)
    result: str = ""
    success: bool = True
    retries: int = 0


@dataclass
class TaskState:
    """Tracks a single user-requested task end-to-end."""
    user_instruction: str = ""
    planned_steps: list[str] = field(default_factory=list)
    completed_steps: list[str] = field(default_factory=list)
    current_step: str = ""
    action_history: list[ActionRecord] = field(default_factory=list)
    retry_count: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    is_complete: bool = False
    needs_clarification: bool = False
    clarification_question: str = ""


class AgentState:
    """
    Thread-safe singleton that holds all global agent state.
    Access via: from app.state import agent_state
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.mode: AgentMode = AgentMode.IDLE
        self.current_task: TaskState | None = None
        self.conversation_history: list[dict[str, Any]] = []
        self.emergency_stop: bool = False
        self.active_application: str = ""
        self.active_url: str = ""

    # ── Mode management ────────────────────────────────────────────────────────

    def set_mode(self, mode: AgentMode) -> None:
        with self._lock:
            self.mode = mode

    def get_mode(self) -> AgentMode:
        with self._lock:
            return self.mode

    # ── Task management ────────────────────────────────────────────────────────

    def start_task(self, instruction: str) -> TaskState:
        with self._lock:
            self.current_task = TaskState(user_instruction=instruction)
            self.mode = AgentMode.THINKING
            return self.current_task

    def record_action(self, record: ActionRecord) -> None:
        with self._lock:
            if self.current_task:
                self.current_task.action_history.append(record)

    def complete_task(self) -> None:
        with self._lock:
            if self.current_task:
                self.current_task.is_complete = True
            self.mode = AgentMode.IDLE

    def clear_task(self) -> None:
        with self._lock:
            self.current_task = None
            self.mode = AgentMode.IDLE

    # ── Conversation history ───────────────────────────────────────────────────

    def add_message(self, role: str, content: Any) -> None:
        """Add a message to the conversation history for multi-turn context."""
        with self._lock:
            self.conversation_history.append({"role": role, "content": content})

    def clear_history(self) -> None:
        with self._lock:
            self.conversation_history.clear()

    # ── Emergency stop ─────────────────────────────────────────────────────────

    def trigger_stop(self) -> None:
        with self._lock:
            self.emergency_stop = True
            self.mode = AgentMode.STOPPED

    def reset_stop(self) -> None:
        with self._lock:
            self.emergency_stop = False
            self.mode = AgentMode.IDLE

    def is_stopped(self) -> bool:
        with self._lock:
            return self.emergency_stop

    # ── Context tracking ───────────────────────────────────────────────────────

    def set_active_application(self, app_name: str) -> None:
        with self._lock:
            self.active_application = app_name

    def set_active_url(self, url: str) -> None:
        with self._lock:
            self.active_url = url

    def get_context_summary(self) -> str:
        """Returns a human-readable summary of the current agent context."""
        with self._lock:
            lines = [
                f"Mode: {self.mode.name}",
                f"Active App: {self.active_application or 'Unknown'}",
                f"Active URL: {self.active_url or 'N/A'}",
            ]
            if self.current_task:
                t = self.current_task
                lines += [
                    f"Task: {t.user_instruction}",
                    f"Current Step: {t.current_step}",
                    f"Steps Done: {len(t.completed_steps)}/{len(t.planned_steps)}",
                    f"Actions Taken: {len(t.action_history)}",
                    f"Retries: {t.retry_count}",
                ]
            return "\n".join(lines)


# ── Global singleton ───────────────────────────────────────────────────────────
agent_state = AgentState()
