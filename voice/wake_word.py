"""
Atlas-Modified: voice/wake_word.py
Basic wake word detection from transcribed text.
"""

import logging
from app import config

logger = logging.getLogger(__name__)

def is_wake_word(transcription: str) -> bool:
    """
    Check if the given transcription contains the wake word.
    Very simple string matching for Phase 2.
    """
    if not transcription:
        return False
        
    if not config.WAKE_WORD_ENABLED:
        # If wake word is disabled, treat everything as a direct command (e.g., push-to-talk)
        return True

    wake = config.WAKE_WORD.lower()
    text = transcription.lower()
    
    if wake in text:
        logger.info("Wake word '%s' detected in phrase: %s", wake, text)
        return True
        
    return False

def strip_wake_word(transcription: str) -> str:
    """
    Remove the wake word from the beginning of the transcription if present,
    so the AI agent doesn't have to parse it out.
    """
    if not config.WAKE_WORD_ENABLED or not transcription:
        return transcription
        
    text = transcription.lower()
    wake = config.WAKE_WORD.lower()
    
    if text.startswith(wake):
        # Remove wake word and trim
        return transcription[len(wake):].strip()
        
    return transcription
