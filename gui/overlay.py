"""
Atlas-Modified: gui/overlay.py

The main Atlas GUI overlay window.
- Transparent, frameless, always-on-top window
- Activated by Ctrl+Space (global hotkey via pynput)
- Contains a text input field + mic button
- Shows agent responses inline
- Pressing Enter or clicking the mic button runs the vision loop
- ESC hides the window back to the status indicator

Architecture:
  - QApplication runs in the main thread
  - Agent tasks (computer_use_agent.run) execute in a QThread worker
    so the GUI never freezes during long tasks
  - QThread emits signals to update the GUI safely from the worker thread
"""

import sys
import threading
import logging

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QSizePolicy,
)
from PySide6.QtCore import (
    Qt, QThread, Signal, QObject, QTimer,
)
from PySide6.QtGui import QFont, QColor, QPalette, QKeySequence, QShortcut

logger = logging.getLogger(__name__)


# ─── Worker thread for async agent execution ─────────────────────────────────

class AgentWorker(QObject):
    """Runs the agent task in a background thread, emits result when done."""
    finished = Signal(str)   # emits the final agent text response
    error    = Signal(str)   # emits error message on failure
    status   = Signal(str)   # emits intermediate status updates

    def __init__(self, instruction: str) -> None:
        super().__init__()
        self.instruction = instruction

    def run(self) -> None:
        try:
            from ai.computer_use import computer_use_agent
            self.status.emit("🤖 Thinking and acting…")
            result = computer_use_agent.run(self.instruction)
            self.finished.emit(result)
        except Exception as e:
            logger.exception("AgentWorker error: %s", e)
            self.error.emit(str(e))


# ─── Main overlay window ──────────────────────────────────────────────────────

class AtlasOverlay(QWidget):
    """
    Transparent, always-on-top, frameless overlay window.
    Appears on Ctrl+Space, disappears on ESC.
    """

    def __init__(self) -> None:
        super().__init__()
        self._thread: QThread | None = None
        self._worker: AgentWorker | None = None
        self._setup_ui()
        self._setup_global_hotkey()

    # ── UI Setup ──────────────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        # Window flags: frameless, always on top, transparent background
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedWidth(680)

        # ── Outer container with rounded, semi-transparent dark background ────
        container = QWidget(self)
        container.setObjectName("container")
        container.setStyleSheet("""
            QWidget#container {
                background: rgba(20, 20, 30, 220);
                border-radius: 18px;
                border: 1px solid rgba(255, 255, 255, 40);
            }
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(container)

        inner = QVBoxLayout(container)
        inner.setContentsMargins(18, 14, 18, 18)
        inner.setSpacing(10)

        # ── Top row: Atlas logo label + close button ──────────────────────────
        top_row = QHBoxLayout()
        logo = QLabel("🤖 Atlas")
        logo.setFont(QFont("Segoe UI", 13, QFont.Bold))
        logo.setStyleSheet("color: #a0c4ff;")

        self._close_btn = QPushButton("✕")
        self._close_btn.setFixedSize(26, 26)
        self._close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: rgba(255,255,255,120);
                border: none;
                font-size: 13px;
            }
            QPushButton:hover { color: white; }
        """)
        self._close_btn.clicked.connect(self.hide)

        top_row.addWidget(logo)
        top_row.addStretch()
        top_row.addWidget(self._close_btn)
        inner.addLayout(top_row)

        # ── Status label (shows "Thinking…" or the agent's response) ─────────
        self._status_label = QLabel("What would you like me to do?")
        self._status_label.setWordWrap(True)
        self._status_label.setFont(QFont("Segoe UI", 10))
        self._status_label.setStyleSheet("color: rgba(255,255,255,180);")
        self._status_label.setMinimumHeight(22)
        inner.addWidget(self._status_label)

        # ── Input row: text field + mic button + send button ─────────────────
        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Type a task or press 🎤 to speak…")
        self._input.setFont(QFont("Segoe UI", 11))
        self._input.setStyleSheet("""
            QLineEdit {
                background: rgba(255,255,255,15);
                border: 1px solid rgba(255,255,255,60);
                border-radius: 10px;
                color: white;
                padding: 8px 12px;
            }
            QLineEdit:focus {
                border: 1px solid #a0c4ff;
            }
        """)
        self._input.returnPressed.connect(self._on_submit)

        self._mic_btn = QPushButton("🎤")
        self._mic_btn.setFixedSize(40, 40)
        self._mic_btn.setToolTip("Click to speak (microphone)")
        self._mic_btn.setStyleSheet(self._action_btn_style())
        self._mic_btn.clicked.connect(self._on_mic)

        self._send_btn = QPushButton("▶")
        self._send_btn.setFixedSize(40, 40)
        self._send_btn.setToolTip("Run task")
        self._send_btn.setStyleSheet(self._action_btn_style(accent=True))
        self._send_btn.clicked.connect(self._on_submit)

        input_row.addWidget(self._input)
        input_row.addWidget(self._mic_btn)
        input_row.addWidget(self._send_btn)
        inner.addLayout(input_row)

        # ── Response label ────────────────────────────────────────────────────
        self._response_label = QLabel("")
        self._response_label.setWordWrap(True)
        self._response_label.setFont(QFont("Segoe UI", 10))
        self._response_label.setStyleSheet("color: #b0ffb0; padding-top: 4px;")
        self._response_label.hide()
        inner.addWidget(self._response_label)

        # Position in screen center (top-third)
        self._center_on_screen()

    def _action_btn_style(self, accent: bool = False) -> str:
        bg = "rgba(100, 160, 255, 200)" if accent else "rgba(255,255,255,20)"
        hover = "rgba(120, 180, 255, 255)" if accent else "rgba(255,255,255,40)"
        return f"""
            QPushButton {{
                background: {bg};
                border-radius: 10px;
                color: white;
                font-size: 16px;
                border: none;
            }}
            QPushButton:hover {{ background: {hover}; }}
            QPushButton:pressed {{ background: rgba(60,120,200,255); }}
        """

    def _center_on_screen(self) -> None:
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            screen.height() // 5,
        )

    # ── Global hotkey (Ctrl+Space) ────────────────────────────────────────────

    def _setup_global_hotkey(self) -> None:
        """Start a pynput listener for Ctrl+Space in a background daemon thread."""
        def _listen() -> None:
            try:
                from pynput import keyboard
                hotkey = keyboard.GlobalHotKeys({
                    "<ctrl>+<space>": self._show_from_thread,
                })
                hotkey.start()
                hotkey.join()
            except Exception as e:
                logger.warning("Global hotkey listener failed: %s", e)

        t = threading.Thread(target=_listen, daemon=True, name="AtlasHotkeyListener")
        t.start()

    def _show_from_thread(self) -> None:
        """Called from background thread — schedule show() on the main thread."""
        QTimer.singleShot(0, self._show_and_focus)

    def _show_and_focus(self) -> None:
        self._center_on_screen()
        self._input.clear()
        self._response_label.hide()
        self._status_label.setText("What would you like me to do?")
        self.show()
        self.raise_()
        self.activateWindow()
        self._input.setFocus()

    # ── Keyboard: ESC hides overlay ───────────────────────────────────────────

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Escape:
            self.hide()
        else:
            super().keyPressEvent(event)

    # ── Task submission ───────────────────────────────────────────────────────

    def _on_submit(self) -> None:
        instruction = self._input.text().strip()
        if not instruction:
            return
        self._run_task(instruction)

    def _on_mic(self) -> None:
        """Capture one voice command, then run it."""
        self._status_label.setText("🎤 Listening… speak now")
        self._input.setEnabled(False)
        self._mic_btn.setEnabled(False)
        self._send_btn.setEnabled(False)

        def _capture() -> None:
            try:
                from voice.speech_to_text import listen_and_transcribe
                from voice.wake_word import strip_wake_word
                text = listen_and_transcribe(timeout=5, phrase_time_limit=15)
                if text:
                    clean = strip_wake_word(text)
                    QTimer.singleShot(0, lambda: self._after_mic(clean))
                else:
                    QTimer.singleShot(0, lambda: self._after_mic(None))
            except Exception as e:
                QTimer.singleShot(0, lambda: self._after_mic(None))

        threading.Thread(target=_capture, daemon=True).start()

    def _after_mic(self, text: str | None) -> None:
        self._input.setEnabled(True)
        self._mic_btn.setEnabled(True)
        self._send_btn.setEnabled(True)
        if text:
            self._input.setText(text)
            self._run_task(text)
        else:
            self._status_label.setText("❌ Could not understand speech. Try again.")

    def _run_task(self, instruction: str) -> None:
        """Launch agent task in a QThread so the GUI stays responsive."""
        if self._thread and self._thread.isRunning():
            self._status_label.setText("⚠️ Already running a task. Please wait.")
            return

        self._status_label.setText("🤖 Working…")
        self._response_label.hide()
        self._send_btn.setEnabled(False)
        self._mic_btn.setEnabled(False)

        self._thread = QThread()
        self._worker = AgentWorker(instruction)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.status.connect(lambda s: self._status_label.setText(s))
        self._worker.finished.connect(self._on_task_done)
        self._worker.error.connect(self._on_task_error)
        self._worker.finished.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()

    def _on_task_done(self, result: str) -> None:
        self._status_label.setText("✅ Done")
        self._response_label.setText(result[:400])  # Truncate very long responses
        self._response_label.show()
        self._send_btn.setEnabled(True)
        self._mic_btn.setEnabled(True)
        self._input.clear()
        self._input.setFocus()
        # Speak the result
        try:
            from voice.text_to_speech import speak
            threading.Thread(target=speak, args=(result,), daemon=True).start()
        except Exception:
            pass

    def _on_task_error(self, error: str) -> None:
        self._status_label.setText(f"❌ Error: {error[:120]}")
        self._send_btn.setEnabled(True)
        self._mic_btn.setEnabled(True)


# ─── Status indicator (small always-on-top badge when overlay is hidden) ─────

class StatusIndicator(QWidget):
    """
    A tiny floating badge (bottom-right corner) that shows the agent's mode.
    Click it to toggle the main overlay.
    """

    def __init__(self, overlay: AtlasOverlay) -> None:
        super().__init__()
        self._overlay = overlay
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(52, 52)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._btn = QPushButton("🤖")
        self._btn.setFixedSize(52, 52)
        self._btn.setToolTip("Atlas — Click to open  |  Ctrl+Space")
        self._btn.setStyleSheet("""
            QPushButton {
                background: rgba(20, 20, 30, 210);
                border-radius: 26px;
                font-size: 26px;
                border: 1px solid rgba(255,255,255,40);
            }
            QPushButton:hover {
                background: rgba(50, 80, 160, 230);
            }
        """)
        self._btn.clicked.connect(self._toggle_overlay)
        layout.addWidget(self._btn)

        # Position bottom-right
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 70, screen.height() - 80)

    def _toggle_overlay(self) -> None:
        if self._overlay.isVisible():
            self._overlay.hide()
        else:
            self._overlay._show_and_focus()

    def set_mode(self, label: str) -> None:
        self._btn.setText(label)


# ─── Application entry point ──────────────────────────────────────────────────

def run_gui() -> None:
    """
    Launch the Atlas GUI overlay.
    Blocks until the application is closed.
    Call this from a separate thread or as the main entry point.
    """
    app = QApplication.instance() or QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running even when overlay is hidden

    overlay = AtlasOverlay()
    indicator = StatusIndicator(overlay)
    indicator.show()

    # Show the overlay immediately on first launch
    overlay._show_and_focus()

    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui()
