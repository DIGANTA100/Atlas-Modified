"""
Atlas-Modified: vision/ocr.py
Optical Character Recognition (OCR) to find text coordinates on the screen.
Requires Tesseract OCR to be installed on the system (https://github.com/UB-Mannheim/tesseract/wiki).
"""

import logging
import pytesseract
from PIL import Image
from typing import Optional

from computer.screen import take_screenshot

logger = logging.getLogger(__name__)

# Default path for Windows Tesseract installation
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def find_text_on_screen(text_to_find: str) -> Optional[tuple[int, int]]:
    """
    Take a screenshot, run OCR, and return the (x, y) center coordinates of the 
    first occurrence of the specified text.
    """
    logger.info("Searching screen for text: '%s'", text_to_find)
    
    img = take_screenshot()
    
    try:
        # Get detailed OCR data including bounding boxes
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    except pytesseract.TesseractNotFoundError:
        logger.error("Tesseract is not installed or not in PATH. OCR disabled.")
        return None
    except Exception as e:
        logger.error("OCR failed: %s", e)
        return None
        
    text_to_find = text_to_find.lower()
    
    for i in range(len(data['text'])):
        word = data['text'][i].strip().lower()
        
        # Simple substring match
        if word and text_to_find in word:
            # Calculate center of the bounding box
            x = data['left'][i] + (data['width'][i] // 2)
            y = data['top'][i] + (data['height'][i] // 2)
            
            logger.info("Found text '%s' at (%d, %d)", word, x, y)
            return (x, y)
            
    logger.info("Text '%s' not found on screen.", text_to_find)
    return None

def extract_all_text() -> str:
    """Returns all text currently visible on the screen."""
    img = take_screenshot()
    try:
        return pytesseract.image_to_string(img)
    except Exception as e:
        logger.error("Failed to extract text: %s", e)
        return ""
