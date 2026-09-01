"""
Atlas-Modified: vision/ui_detection.py
Computer vision tools to locate image templates/icons on the screen.
"""

import logging
import pyautogui
from typing import Optional

logger = logging.getLogger(__name__)

def find_image_on_screen(template_path: str, confidence: float = 0.8) -> Optional[tuple[int, int]]:
    """
    Locates an image template (e.g. an icon or button) on the screen.
    Returns the (x, y) center coordinates if found.
    Requires opencv-python to be installed for the 'confidence' parameter to work.
    """
    logger.info("Searching screen for image template: '%s' (confidence >= %.2f)", template_path, confidence)
    
    try:
        # pyautogui.locateCenterOnScreen takes a screenshot and uses cv2.matchTemplate
        center = pyautogui.locateCenterOnScreen(template_path, confidence=confidence)
        
        if center:
            logger.info("Found image at (%d, %d)", center.x, center.y)
            return (int(center.x), int(center.y))
        else:
            logger.info("Image template not found on screen.")
            return None
            
    except pyautogui.ImageNotFoundException:
        logger.info("Image template not found on screen.")
        return None
    except FileNotFoundError:
        logger.error("Template image file not found: %s", template_path)
        return None
    except Exception as e:
        logger.error("Failed to search for image: %s", e)
        return None
