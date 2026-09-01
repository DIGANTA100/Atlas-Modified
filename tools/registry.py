"""
Atlas-Modified: tools/registry.py
Central tool registry — maps tool names to their Python implementations
and exports Gemini-compatible function declarations.
"""

import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)

# ── Lazy imports (avoid importing heavy libs at module load time) ──────────────
def _get_computer_tools() -> dict[str, Callable]:
    from computer import mouse, keyboard, scroll, screen, clipboard, windows
    from filesystem import files, folders, search
    return {
        # Mouse
        "mouse_move": lambda x, y, duration=0.3: mouse.move(int(x), int(y), duration),
        "mouse_click": lambda x=None, y=None, button="left": mouse.click(
            int(x) if x is not None else None,
            int(y) if y is not None else None,
            button,
        ),
        "mouse_double_click": lambda x=None, y=None: mouse.double_click(
            int(x) if x is not None else None,
            int(y) if y is not None else None,
        ),
        "mouse_right_click": lambda x=None, y=None: mouse.right_click(
            int(x) if x is not None else None,
            int(y) if y is not None else None,
        ),
        "mouse_drag": lambda sx, sy, ex, ey, duration=0.5: mouse.drag(
            int(sx), int(sy), int(ex), int(ey), duration
        ),
        # Keyboard
        "press_key": lambda key: keyboard.press_key(key),
        "type_text": lambda text, interval=0.02: keyboard.type_text(text, interval),
        "hotkey": lambda keys: keyboard.hotkey(*keys) if isinstance(keys, list) else keyboard.hotkey(keys),
        "shortcut": lambda name: keyboard.hotkey_by_name(name),
        # Scroll
        "scroll_up": lambda clicks=3, x=None, y=None: scroll.scroll_up(clicks, x, y),
        "scroll_down": lambda clicks=3, x=None, y=None: scroll.scroll_down(clicks, x, y),
        "scroll_to_top": lambda: scroll.scroll_to_top(),
        "scroll_to_bottom": lambda: scroll.scroll_to_bottom(),
        "page_up": lambda: scroll.page_up(),
        "page_down": lambda: scroll.page_down(),
        # Screen
        "take_screenshot": lambda save=False: screen.take_screenshot(save=save),
        "get_screen_size": lambda: screen.get_screen_size(),
        # Clipboard
        "read_clipboard": lambda: clipboard.read_clipboard(),
        "write_clipboard": lambda text: clipboard.write_clipboard(text),
        "clear_clipboard": lambda: clipboard.clear_clipboard(),
        # Windows
        "open_application": lambda name: windows.open_application(name),
        "open_url": lambda url: windows.open_url_in_browser(url),
        "switch_window": lambda title: windows.switch_to_window(title),
        "minimize_window": lambda: windows.minimize_window(),
        "maximize_window": lambda: windows.maximize_window(),
        "close_active_window": lambda: windows.close_active_window(),
        "show_desktop": lambda: windows.show_desktop(),
        "switch_app": lambda forward=True: windows.switch_app(forward),
        "list_windows": lambda: windows.list_windows(),
        # Filesystem
        "create_file": lambda path, content="": files.create_file(path, content),
        "move_file": lambda src, dest: files.move_file(src, dest),
        "copy_file": lambda src, dest: files.copy_file(src, dest),
        "rename_file": lambda src, new_name: files.rename_file(src, new_name),
        "delete_file": lambda path: files.delete_file(path),
        "open_file": lambda path: files.open_file(path),
        "create_folder": lambda path: folders.create_folder(path),
        "delete_folder": lambda path: folders.delete_folder(path),
        "list_folder": lambda path: folders.list_folder(path),
        "open_folder": lambda path: folders.open_folder(path),
        "find_file": lambda name, root_dir="~", max_depth=4: search.find_file(name, root_dir, max_depth),
    }


# ── Gemini function declaration schemas ───────────────────────────────────────
GEMINI_TOOL_DECLARATIONS = [
    {
        "name": "mouse_move",
        "description": "Move the mouse cursor to absolute screen coordinates.",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "X coordinate in pixels"},
                "y": {"type": "integer", "description": "Y coordinate in pixels"},
                "duration": {"type": "number", "description": "Animation duration in seconds"},
            },
            "required": ["x", "y"],
        },
    },
    {
        "name": "mouse_click",
        "description": "Click the mouse at optional coordinates. If no coordinates, clicks at current position.",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "X coordinate"},
                "y": {"type": "integer", "description": "Y coordinate"},
                "button": {"type": "string", "enum": ["left", "right", "middle"], "description": "Mouse button"},
            },
        },
    },
    {
        "name": "mouse_double_click",
        "description": "Double-click at optional coordinates.",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {"type": "integer"},
                "y": {"type": "integer"},
            },
        },
    },
    {
        "name": "mouse_right_click",
        "description": "Right-click at optional coordinates.",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {"type": "integer"},
                "y": {"type": "integer"},
            },
        },
    },
    {
        "name": "mouse_drag",
        "description": "Click and drag from one position to another.",
        "parameters": {
            "type": "object",
            "properties": {
                "sx": {"type": "integer", "description": "Start X"},
                "sy": {"type": "integer", "description": "Start Y"},
                "ex": {"type": "integer", "description": "End X"},
                "ey": {"type": "integer", "description": "End Y"},
            },
            "required": ["sx", "sy", "ex", "ey"],
        },
    },
    {
        "name": "press_key",
        "description": "Press a single keyboard key (e.g. 'enter', 'escape', 'tab', 'f5').",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Key name"},
            },
            "required": ["key"],
        },
    },
    {
        "name": "type_text",
        "description": "Type a string of text into the currently focused field.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to type"},
                "interval": {"type": "number", "description": "Delay between keystrokes"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "hotkey",
        "description": "Press a keyboard shortcut (list of keys held simultaneously). E.g. ['ctrl','c'] for copy.",
        "parameters": {
            "type": "object",
            "properties": {
                "keys": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of keys to press simultaneously",
                },
            },
            "required": ["keys"],
        },
    },
    {
        "name": "shortcut",
        "description": "Execute a named shortcut like 'copy', 'paste', 'undo', 'save', 'select all', 'close tab'.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Shortcut name"},
            },
            "required": ["name"],
        },
    },
    {
        "name": "scroll_up",
        "description": "Scroll up on the screen.",
        "parameters": {
            "type": "object",
            "properties": {
                "clicks": {"type": "integer", "description": "Number of scroll units"},
            },
        },
    },
    {
        "name": "scroll_down",
        "description": "Scroll down on the screen.",
        "parameters": {
            "type": "object",
            "properties": {
                "clicks": {"type": "integer", "description": "Number of scroll units"},
            },
        },
    },
    {
        "name": "scroll_to_top",
        "description": "Scroll to the very top of the page or document.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "scroll_to_bottom",
        "description": "Scroll to the very bottom of the page or document.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "take_screenshot",
        "description": "Take a screenshot of the current screen state.",
        "parameters": {
            "type": "object",
            "properties": {
                "save": {"type": "boolean", "description": "Whether to save to disk"},
            },
        },
    },
    {
        "name": "read_clipboard",
        "description": "Read the current clipboard text content.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "write_clipboard",
        "description": "Write text to the clipboard.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "open_application",
        "description": "Open/launch an application by name (e.g. 'Chrome', 'Notepad', 'VS Code', 'Discord').",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Application name or executable"},
            },
            "required": ["name"],
        },
    },
    {
        "name": "open_url",
        "description": "Open a URL in the default browser.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to open (include https://)"},
            },
            "required": ["url"],
        },
    },
    {
        "name": "switch_window",
        "description": "Switch focus to a window whose title contains the given text.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Partial window title"},
            },
            "required": ["title"],
        },
    },
    {
        "name": "minimize_window",
        "description": "Minimize the current window.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "maximize_window",
        "description": "Maximize the current window.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "close_active_window",
        "description": "Close the currently focused window.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "show_desktop",
        "description": "Minimize all windows to show the desktop.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "switch_app",
        "description": "Switch to the next application (Alt+Tab).",
        "parameters": {
            "type": "object",
            "properties": {
                "forward": {"type": "boolean", "description": "True = next app, False = previous"},
            },
        },
    },
    {
        "name": "list_windows",
        "description": "List all open windows with their titles.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "create_file",
        "description": "Create a new file with optional content.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute or relative path to the new file"},
                "content": {"type": "string", "description": "Optional text content"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "move_file",
        "description": "Move a file to a new location.",
        "parameters": {
            "type": "object",
            "properties": {
                "src": {"type": "string"},
                "dest": {"type": "string"}
            },
            "required": ["src", "dest"]
        }
    },
    {
        "name": "copy_file",
        "description": "Copy a file.",
        "parameters": {
            "type": "object",
            "properties": {
                "src": {"type": "string"},
                "dest": {"type": "string"}
            },
            "required": ["src", "dest"]
        }
    },
    {
        "name": "rename_file",
        "description": "Rename a file in the same directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "src": {"type": "string"},
                "new_name": {"type": "string", "description": "Just the new file name, not a full path"}
            },
            "required": ["src", "new_name"]
        }
    },
    {
        "name": "delete_file",
        "description": "Delete a file.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "open_file",
        "description": "Open a file using the default Windows application.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "create_folder",
        "description": "Create a new directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "delete_folder",
        "description": "Delete a directory and all its contents recursively.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "list_folder",
        "description": "List all files and subdirectories in a directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "open_folder",
        "description": "Open a folder in Windows File Explorer.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "find_file",
        "description": "Search for a file or folder by partial name.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Partial name to search for"},
                "root_dir": {"type": "string", "description": "Directory to start search from (defaults to ~)"},
                "max_depth": {"type": "integer", "description": "Maximum folder depth to search"}
            },
            "required": ["name"]
        }
    }
]


class ToolRegistry:
    """
    Central registry of all tools available to the agent.
    Tools are loaded lazily and can be called by name.
    """

    def __init__(self) -> None:
        self._tools: dict[str, Callable] | None = None

    def _load(self) -> None:
        if self._tools is None:
            self._tools = _get_computer_tools()

    def call(self, tool_name: str, **kwargs: Any) -> Any:
        """Execute a tool by name with the given arguments."""
        self._load()
        fn = self._tools.get(tool_name)
        if fn is None:
            raise ValueError(f"Unknown tool: '{tool_name}'")
        logger.info("Executing tool: %s(%s)", tool_name, kwargs)
        return fn(**kwargs)

    def has(self, tool_name: str) -> bool:
        self._load()
        return tool_name in self._tools

    def get_declarations(self) -> list[dict]:
        """Return Gemini-compatible function declarations for all registered tools."""
        return GEMINI_TOOL_DECLARATIONS


# ── Global singleton ───────────────────────────────────────────────────────────
registry = ToolRegistry()
