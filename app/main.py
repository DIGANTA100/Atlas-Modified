"""
Atlas-Modified: app/main.py
Entry point for the Atlas agent.

Phase 7: Full Vision-Grounded Computer Use Agent.
- 'do <task>'   → Vision loop: screenshot → Gemini → tool → screenshot → verify
- 'ask <task>'  → Text-only loop (no screenshot, for quick tests)
- 'voice'       → Microphone → STT → vision loop
"""

import logging
import sys

from app import config
from app.state import agent_state, AgentMode
from tools.executor import execute_tool, PermissionDeniedError, ExecutionError
from ai.planner import process_instruction, reset_chat
from ai.computer_use import computer_use_agent
from voice.speech_to_text import listen_and_transcribe
from voice.wake_word import strip_wake_word
from voice.text_to_speech import speak

logger = logging.getLogger(__name__)


def print_banner() -> None:
    print("""
╔══════════════════════════════════════════════════════════════╗
║         Atlas-Modified — Voice Computer Agent v0.7           ║
║   Voice-Controlled General-Purpose Desktop Agent             ║
║                                                              ║
║  'do <task>'   → AI sees your screen and acts               ║
║  'voice'       → Speak your instruction (microphone)         ║
║  'ask <task>'  → Text-only AI (no screen capture)            ║
║  Type 'help' for all commands.  Type 'quit' to exit.         ║
╚══════════════════════════════════════════════════════════════╝
""")


def print_help() -> None:
    print("""
═══════════════ Atlas Command Reference ═══════════════

  AI Agent Commands:
    do <instruction>      → Full vision loop (RECOMMENDED)
                            Atlas sees screen, acts, verifies
    voice                 → Speak instruction via microphone
    ask <instruction>     → Text-only Gemini (no screenshot)
    reset                 → Reset AI conversation context

  Direct Computer Control:
    screenshot            — Save a screenshot to disk
    click <x> <y>         — Click at coordinates
    move <x> <y>          — Move mouse to coordinates
    type <text>           — Type text
    key <key>             — Press a key (enter, esc, f5…)
    hotkey <k1> <k2>      — Hotkey (e.g. hotkey ctrl c)
    shortcut <name>       — Named shortcut (copy, paste…)
    scroll up/down [n]    — Scroll the page
    open <app>            — Launch an application
    url <url>             — Open URL in default browser
    clipboard read        — Read clipboard contents
    clipboard write <txt> — Write to clipboard
    windows               — List open windows
    switch <title>        — Focus a window by title

  System:
    state                 — Show agent state
    help                  — Show this help
    quit                  — Exit Atlas
""")


def handle_command(cmd: str) -> None:
    """Parse and dispatch a REPL command."""
    parts = cmd.strip().split(maxsplit=1)
    if not parts:
        return
    verb = parts[0].lower()
    rest = parts[1] if len(parts) > 1 else ""

    try:
        # ── AI Vision Loop (Phase 7) ──────────────────────────────────────────
        if verb == "do":
            if rest:
                agent_state.set_mode(AgentMode.ACTING)
                print(f"🤖 Starting vision task: {rest}")
                result = computer_use_agent.run(rest)
                agent_state.set_mode(AgentMode.IDLE)
                print(f"\n✅ Atlas: {result}")
                speak(result)
            else:
                print("Usage: do <your instruction>")

        # ── Voice Input (Phase 2+7) ───────────────────────────────────────────
        elif verb == "voice":
            print("🎤 Listening... (Speak now)")
            transcription = listen_and_transcribe(timeout=5, phrase_time_limit=15)
            if transcription:
                clean_text = strip_wake_word(transcription)
                print(f"You said: {clean_text}")
                if clean_text:
                    agent_state.set_mode(AgentMode.ACTING)
                    result = computer_use_agent.run(clean_text)
                    agent_state.set_mode(AgentMode.IDLE)
                    print(f"\n✅ Atlas: {result}")
                    speak(result)
            else:
                print("Could not hear or understand speech.")

        # ── Text-Only AI Loop (Phase 3, no screenshot) ─────────────────────────
        elif verb == "ask":
            if rest:
                process_instruction(rest)
            else:
                print("Usage: ask <instruction>")

        # ── Reset AI memory ───────────────────────────────────────────────────
        elif verb == "reset":
            reset_chat()
            computer_use_agent.reset()
            print("✓ Conversation context reset.")

        # ── Direct tool commands ──────────────────────────────────────────────
        elif verb == "screenshot":
            execute_tool("take_screenshot", {"save": True})
            print("✓ Screenshot saved to screenshots/")

        elif verb == "click":
            coords = rest.split()
            if len(coords) >= 2:
                execute_tool("mouse_click", {"x": int(coords[0]), "y": int(coords[1])})
                print(f"✓ Clicked ({coords[0]}, {coords[1]})")
            else:
                print("Usage: click <x> <y>")

        elif verb == "move":
            coords = rest.split()
            if len(coords) >= 2:
                execute_tool("mouse_move", {"x": int(coords[0]), "y": int(coords[1])})
                print(f"✓ Mouse moved to ({coords[0]}, {coords[1]})")
            else:
                print("Usage: move <x> <y>")

        elif verb == "type":
            if rest:
                execute_tool("type_text", {"text": rest})
                print(f"✓ Typed: {rest[:40]}")
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
                print("✓ Written to clipboard")
            else:
                print("Usage: clipboard read | clipboard write <text>")

        elif verb == "windows":
            wins = execute_tool("list_windows", {})
            for w in (wins or [])[:20]:
                print(f"  [{w['hwnd']}] {w['title']} ({w['exe']})")

        elif verb == "switch":
            if rest:
                ok = execute_tool("switch_window", {"title": rest})
                print(f"✓ Switched to: {rest}" if ok else f"✗ Not found: {rest}")
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
            print(f"Unknown command: '{verb}'. Type 'help' for commands.")

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

    # Validate config (warns if GEMINI_API_KEY is missing)
    config.validate()

    agent_state.set_mode(AgentMode.IDLE)
    print("✅ Agent ready. Type 'help' for all commands.\n")

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
