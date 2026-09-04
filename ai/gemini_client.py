"""
Atlas-Modified: ai/gemini_client.py
Wraps the google-genai SDK to communicate with Gemini.

Optimizations:
  - Gemini FunctionDeclaration objects are built ONCE and cached at module load
  - Client object is a singleton (one HTTP connection pool reused across all calls)
  - create_chat_session() is now nearly free to call
"""

import logging
from typing import Any
from google import genai
from google.genai import types

from app import config
from ai.prompts import SYSTEM_PROMPT
from tools.registry import registry

logger = logging.getLogger(__name__)

# ── Singleton client ──────────────────────────────────────────────────────────
_client: genai.Client | None = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in .env")
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
        logger.info("Gemini client initialized.")
    return _client


# ── Pre-built tool declarations (cached at import time, never rebuilt) ────────
def _build_gemini_tools() -> list[types.Tool]:
    """
    Convert our JSON schema list into a single types.Tool object.
    This is done ONCE and cached — subsequent calls to create_chat_session()
    reuse the exact same Python objects with no rebuild overhead.
    """
    declarations = registry.get_declarations()
    func_decls = [
        types.FunctionDeclaration(
            name=t["name"],
            description=t["description"],
            parameters=t.get("parameters"),
        )
        for t in declarations
    ]
    logger.debug("Built %d tool declarations.", len(func_decls))
    return [types.Tool(function_declarations=func_decls)]


# Build once at import time
_GEMINI_TOOLS: list[types.Tool] = _build_gemini_tools()

# GenerateContentConfig is also stateless — build once and reuse
_CHAT_CONFIG = types.GenerateContentConfig(
    system_instruction=SYSTEM_PROMPT,
    temperature=0.1,   # Lower = more deterministic, faster to token-select
    tools=_GEMINI_TOOLS,
)


# ── Session factory ───────────────────────────────────────────────────────────

def create_chat_session() -> Any:
    """
    Create a new multi-turn chat session.
    The client, tool declarations, and config are all cached — this call
    is now just a lightweight object creation with no schema rebuilding.
    """
    client = get_client()
    logger.info("Opening Gemini chat session (model=%s, tools=%d)",
                config.GEMINI_TEXT_MODEL, len(_GEMINI_TOOLS[0].function_declarations))
    return client.chats.create(
        model=config.GEMINI_TEXT_MODEL,
        config=_CHAT_CONFIG,
    )
