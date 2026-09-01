"""
Atlas-Modified: voice/speech_to_text.py
Speech-to-Text handling using the SpeechRecognition library.
Currently defaults to Google's free online STT for ease of setup.
"""

import logging
import speech_recognition as sr
from typing import Optional

logger = logging.getLogger(__name__)

# Initialize recognizer
recognizer = sr.Recognizer()
# Adjust for ambient noise on first use
_noise_adjusted = False

def listen_and_transcribe(timeout: int = 5, phrase_time_limit: int = 10) -> Optional[str]:
    """
    Listen to the default system microphone and transcribe the speech to text.
    
    Args:
        timeout: Seconds to wait for speech to start.
        phrase_time_limit: Max seconds to record after speech starts.
        
    Returns:
        Transcribed string, or None if no speech was detected/recognized.
    """
    global _noise_adjusted
    
    with sr.Microphone() as source:
        if not _noise_adjusted:
            logger.info("Adjusting for ambient noise (1 sec)...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            _noise_adjusted = True
            
        logger.info("Listening for speech...")
        try:
            # Capture audio from the microphone
            audio = recognizer.listen(
                source, 
                timeout=timeout, 
                phrase_time_limit=phrase_time_limit
            )
            logger.debug("Audio captured, transcribing...")
        except sr.WaitTimeoutError:
            logger.debug("Listening timed out, no speech detected.")
            return None
        except Exception as e:
            logger.error("Microphone error: %s", e)
            return None

    # Transcribe using Google's free STT
    try:
        text = recognizer.recognize_google(audio)
        logger.info("Transcription: '%s'", text)
        return text
    except sr.UnknownValueError:
        logger.debug("Google STT could not understand the audio.")
        return None
    except sr.RequestError as e:
        logger.error("Could not request results from Google STT service; %s", e)
        return None
