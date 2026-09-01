"""
Atlas-Modified: ai/gemini_client.py
Wraps the google-genai SDK to communicate with Gemini.
"""

import logging
from typing import Any
from google import genai
from google.genai import types

from app import config
from ai.prompts import SYSTEM_PROMPT
from tools.registry import registry

logger = logging.getLogger(__name__)

_client = None

def get_client() -> genai.Client:
    global _client
    if _client is None:
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in .env")
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client

def create_chat_session() -> Any:
    """
    Create a new chat session with the system prompt and all tools registered.
    """
    client = get_client()
    
    # We pass the raw JSON schema list to Gemini's tool configuration
    tool_declarations = registry.get_declarations()
    
    # Convert our generic dict schemas to google-genai Tool objects
    # Note: In the new google-genai SDK, we can pass standard JSON Schema dicts
    # wrapped in types.Tool(function_declarations=[...])
    gemini_tools = [
        types.Tool(
            function_declarations=[
                types.FunctionDeclaration(
                    name=t["name"],
                    description=t["description"],
                    parameters=t.get("parameters")
                ) for t in tool_declarations
            ]
        )
    ]
    
    config_params = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.2, # Low temperature for more deterministic tool use
        tools=gemini_tools
    )
    
    logger.info("Initializing new Gemini chat session with %d tools", len(tool_declarations))
    chat = client.chats.create(
        model=config.GEMINI_TEXT_MODEL,
        config=config_params
    )
    return chat
