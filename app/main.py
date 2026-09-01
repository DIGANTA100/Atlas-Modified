"""
Atlas-Modified: app/main.py
Entry point for the Atlas agent.

Phase 1: Simple REPL that lets you test computer control tools directly.
Later phases will replace this with the full voice → AI → computer loop.
"""

import logging
import sys

from app import config
from app.state import agent_state, AgentMode
from tools.executor import execute_tool, PermissionDeniedError, ExecutionError

logger = logging.getLogger(__name__)


def print_banner() -> None:
    print("""
╔══════════════════════════════════════════════════════╗
║         Atlas-Modified — Computer Agent              ║
║   Voice-Controlled General-Purpose Desktop Agent     ║
║                                                      ║
║   Phase 1: Computer Control Foundation               ║
║   Type 'help' for available commands.                ║
║   Type 'quit' or press Ctrl+C to exit.               ║
╚══════════════════════════════════════════════════════╝
""")


def print_help() -> None:
    print("""
Available test commands (Phase 1):
  screenshot              — Take a screenshot
  click <x> <y>           — Click at coordinates
  type <text>             — Type text
  key <key>               — Press a key (e.g. key enter)
  hotkey <k1> <k2> ...    — Press a hotkey (e.g. hotkey ctrl c)
  shortcut <name>         — Named shortcut (e.g. shortcut copy)
  scroll up/down [n]      — Scroll
  move <x> <y>            — Move mouse
  open <app>              — Open an application
  url <url>               — Open a URL
  clipboard read          — Read clipboard
  clipboard write <text>  — Write to clipboard
  windows                 — List open windows
  switch <title>          — Switch to window by title
  state                   — Show agent state
  quit                    — Exit
""")


def handle_command(cmd: str) -> None:
    """Parse and execute a test command from the REPL."""
    parts = cmd.strip().split(maxsplit=1)
    if not parts:
        return
    verb = parts[0].lower()
    rest = parts[1] if len(parts) > 1 else ""

    try:
        if verb == "screenshot":
            execute_tool("take_screenshot", {"save": True})
            print("✓ Screenshot saved to screenshots/")

        elif verb == "click":
            coords = rest.split()
            if len(coords) >= 2:
                execute_tool("mouse_click", {"x": int(coords[0]), "y": int(coords[1])})
                print(f"✓ Clicked ({coords[0]}, {coords[1]})")
            else:
                print("Usage: click <x> <y>")

        elif verb == "type":
            if rest:
                execute_tool("type_text", {"text": rest})
                print(f"✓ Typed: {rest[:40]}...")
            else:
                print("Usage: type <text>")

        elif verb == "key":
            if rest:
                execute_tool("press_key", {"key": rest})
                print(f"✓ Pressed: {rest}")
            else:
                print("Usage: key <key_name>")

        elif verb == "hotkey":
            keys = rest.split()
            if keys:
                execute_tool("hotkey", {"keys": keys})
                print(f"✓ Hotkey: {' + '.join(keys)}")
            else:
                print("Usage: hotkey <key1> <key2> ...")

        elif verb == "shortcut":
            if rest:
                execute_tool("shortcut", {"name": rest})
                print(f"✓ Shortcut: {rest}")
            else:
                print("Usage: shortcut <name>")

        elif verb == "scroll":
            sub_parts = rest.split()
            direction = sub_parts[0].lower() if sub_parts else "down"
            clicks = int(sub_parts[1]) if len(sub_parts) > 1 else 3
            if direction == "up":
                execute_tool("scroll_up", {"clicks": clicks})
            else:
                execute_tool("scroll_down", {"clicks": clicks})
            print(f"✓ Scrolled {direction} {clicks} clicks")

        elif verb == "move":
            coords = rest.split()
            if len(coords) >= 2:
                execute_tool("mouse_move", {"x": int(coords[0]), "y": int(coords[1])})
                print(f"✓ Mouse moved to ({coords[0]}, {coords[1]})")
            else:
                print("Usage: move <x> <y>")

        elif verb == "open":
            if rest:
                ok = execute_tool("open_application", {"name": rest})
                print(f"✓ Opened: {rest}" if ok else f"✗ Failed to open: {rest}")
            else:
                print("Usage: open <app_name>")

        elif verb == "url":
            if rest:
                execute_tool("open_url", {"url": rest})
                print(f"✓ Opened URL: {rest}")
            else:
                print("Usage: url <url>")

        elif verb == "clipboard":
            sub = rest.split(maxsplit=1)
            action = sub[0].lower() if sub else ""
            if action == "read":
                content = execute_tool("read_clipboard", {})
                print(f"Clipboard: {content!r}")
            elif action == "write" and len(sub) > 1:
                execute_tool("write_clipboard", {"text": sub[1]})
                print(f"✓ Written to clipboard")
            else:
                print("Usage: clipboard read | clipboard write <text>")

        elif verb == "windows":
            wins = execute_tool("list_windows", {})
            for w in (wins or [])[:20]:
                print(f"  [{w['hwnd']}] {w['title']} ({w['exe']})")

        elif verb == "switch":
            if rest:
                ok = execute_tool("switch_window", {"title": rest})
                print(f"✓ Switched to window: {rest}" if ok else f"✗ Not found: {rest}")
            else:
                print("Usage: switch <partial_title>")

        elif verb == "state":
            print(agent_state.get_context_summary())

        elif verb in ("exit", "quit", "q"):
            print("Goodbye! 👋")
            sys.exit(0)

        elif verb == "help":
            print_help()

        else:
            print(f"Unknown command: '{verb}'. Type 'help' for available commands.")

    except PermissionDeniedError:
        print("✗ Action cancelled by user.")
    except ExecutionError as e:
        print(f"✗ Execution failed: {e}")
    except Exception as e:
        logger.exception("Unexpected error handling command '%s'", cmd)
        print(f"✗ Error: {e}")


def main() -> None:
    """Main entry point."""
    config.setup_logging()
    print_banner()

    # Phase 1: Don't require API key yet (no Gemini calls in Phase 1)
    # config.validate()

    agent_state.set_mode(AgentMode.IDLE)
    print("Agent ready. Type 'help' for commands.\n")

    try:
        while True:
            try:
                cmd = input("Atlas> ").strip()
                if cmd:
                    handle_command(cmd)
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit cleanly.")
    except SystemExit:
        pass


if __name__ == "__main__":
    main()
