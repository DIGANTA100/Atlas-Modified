"""
Atlas-Modified: run_gui.py
Convenience launcher for the Atlas GUI overlay.

Usage:
    python run_gui.py            # Launch GUI overlay
    python -m app.main           # Launch CLI REPL (for testing/debugging)

The GUI overlay is the primary intended user-facing interface.
"""

import sys
from pathlib import Path

# Ensure the project root is on sys.path when running directly
sys.path.insert(0, str(Path(__file__).parent))

from app import config
from app.state import agent_state, AgentMode
from safety.emergency_stop import start_listener, register_stop_callback
from gui.overlay import run_gui


def main() -> None:
    config.setup_logging()
    config.validate()

    # Emergency stop (always active)
    register_stop_callback(agent_state.trigger_stop)
    start_listener()

    agent_state.set_mode(AgentMode.IDLE)
    print("🤖 Atlas GUI starting…  (Ctrl+Space to open overlay, Ctrl+Shift+F12 to stop)")
    run_gui()


if __name__ == "__main__":
    main()
