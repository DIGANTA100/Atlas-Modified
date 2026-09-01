"""
Atlas-Modified: ai/planner.py
The core Observe -> Think -> Act loop.
Takes a user instruction, queries Gemini, executes tools, and reports back.
"""

import logging
from typing import Any

from ai import gemini_client
from tools.executor import execute_tool, ExecutionError, PermissionDeniedError
from voice.text_to_speech import speak

logger = logging.getLogger(__name__)

# Global chat session to maintain context during a run
_active_chat = None

def get_or_create_chat() -> Any:
    global _active_chat
    if _active_chat is None:
        _active_chat = gemini_client.create_chat_session()
    return _active_chat

def reset_chat() -> None:
    global _active_chat
    _active_chat = None
    logger.info("Chat context reset.")

def process_instruction(instruction: str) -> None:
    """
    The main execution loop for a user instruction.
    Sends the instruction to Gemini and handles any resulting tool calls
    in a loop until Gemini provides a final text response.
    """
    logger.info("Processing user instruction: '%s'", instruction)
    chat = get_or_create_chat()
    
    try:
        # 1. Send the instruction to Gemini
        response = chat.send_message(instruction)
        
        # 2. Enter the Tool Execution Loop
        _handle_response_loop(chat, response)
            
    except Exception as e:
        logger.error("Error during task execution: %s", e)
        speak("I encountered an error while processing that request.")


def _handle_response_loop(chat: Any, response: Any) -> None:
    """
    Loops through Gemini's responses. If it wants to call a tool, we run the tool
    locally and send the result back to Gemini. If it replies with text, we speak it.
    """
    while True:
        # Check if Gemini wants to call tools
        if response.function_calls:
            tool_results = []
            
            for function_call in response.function_calls:
                tool_name = function_call.name
                
                # google-genai function_call.args is a struct/dict
                args = {}
                if hasattr(function_call, 'args') and function_call.args:
                    # Convert protobuf Struct or similar to standard dict if needed
                    # In new google-genai, args is usually a standard dict or dict-like
                    args = dict(function_call.args) 
                    
                logger.info("Gemini requested tool: %s(%s)", tool_name, args)
                
                # Execute it locally
                try:
                    result = execute_tool(tool_name, args)
                    tool_results.append({
                        "name": tool_name,
                        "response": {"result": result if result is not None else "success"}
                    })
                except PermissionDeniedError:
                    tool_results.append({
                        "name": tool_name,
                        "response": {"error": "User denied permission to execute this action."}
                    })
                except ExecutionError as e:
                    tool_results.append({
                        "name": tool_name,
                        "response": {"error": str(e)}
                    })
            
            # Send the tool execution results back to Gemini
            logger.debug("Sending tool results back to Gemini: %s", tool_results)
            response = chat.send_message(tool_results)
            
        else:
            # No tool calls; it's a final text response
            if response.text:
                logger.info("Gemini text response: %s", response.text)
                print(f"\nAtlas: {response.text}")
                speak(response.text)
            break
