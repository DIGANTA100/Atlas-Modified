"""
Atlas-Modified: voice/text_to_speech.py
Offline Text-to-Speech (TTS) using pyttsx3.
"""

import logging
import threading
import pyttsx3

from app import config

logger = logging.getLogger(__name__)

# Initialize pyttsx3 engine globally for the app
try:
    _engine = pyttsx3.init()
    # Set standard properties
    _engine.setProperty('rate', 170)    # Speed percent (can go over 100)
    _engine.setProperty('volume', 1.0)  # Volume 0-1
except Exception as e:
    logger.error("Failed to initialize pyttsx3 TTS engine: %s", e)
    _engine = None

_speak_lock = threading.Lock()

def speak(text: str) -> None:
    """
    Speak text synchronously using local TTS.
    """
    if not _engine:
        logger.warning("TTS Engine unavailable. Cannot speak: %s", text)
        return
        
    logger.info("Agent speaking: %s", text)
    with _speak_lock:
        try:
            _engine.say(text)
            _engine.runAndWait()
        except Exception as e:
            logger.error("Error during speech playback: %s", e)

def set_voice(voice_index: int) -> None:
    """
    Change the TTS voice based on available system voices.
    """
    if not _engine:
        return
    voices = _engine.getProperty('voices')
    if 0 <= voice_index < len(voices):
        _engine.setProperty('voice', voices[voice_index].id)
        logger.info("TTS voice set to: %s", voices[voice_index].name)
    else:
        logger.warning("Invalid voice index: %d", voice_index)
