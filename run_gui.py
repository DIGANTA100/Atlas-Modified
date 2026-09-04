"""
Atlas-Modified: run_gui.py
Convenience launcher for the Atlas GUI overlay.

Usage:
    python run_gui.py            # Launch GUI overlay
    python -m app.main           # Launch CLI REPL (for testing/debugging)

The GUI overlay is the primary intended user-facing interface.
"""

import sys
import threading
from pathlib import Path

# Ensure the project root is on sys.path when running directly
sys.path.insert(0, str(Path(__file__).parent))

from app import config
from app.state import agent_state, AgentMode
from safety.emergency_stop import start_listener, register_stop_callback
from gui.overlay import run_gui


def _prewarm_in_background() -> None:
    """
    Pre-warm the Gemini session in a background daemon thread immediately
    at startup, so there is ZERO cold-start delay when the user submits
    their first command.
    """
    try:
        from ai.computer_use import computer_use_agent
        computer_use_agent.prewarm()
    except Exception as e:
        # Non-fatal — the session will be created lazily on first command
        import logging
        logging.getLogger(__name__).warning("Pre-warm failed: %s", e)


def main() -> None:
    config.setup_logging()
    config.validate()

    # Emergency stop (always active)
    register_stop_callback(agent_state.trigger_stop)
    start_listener()

    agent_state.set_mode(AgentMode.IDLE)
    print("🤖 Atlas GUI starting…  (Ctrl+Space to open overlay, Ctrl+Shift+F12 to stop)")

    # ── Kick off pre-warm BEFORE launching the GUI ────────────────────────────
    # This runs in a daemon thread so the GUI window appears instantly,
    # and the Gemini session is ready by the time the user types their command.
    t = threading.Thread(target=_prewarm_in_background, daemon=True, name="AtlasPrewarm")
    t.start()

    run_gui()


if __name__ == "__main__":
    main()
