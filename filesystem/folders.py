"""
Atlas-Modified: filesystem/folders.py
Folder/directory manipulation operations.
"""

import os
import shutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def create_folder(path: str) -> bool:
    """Create a new directory (including parents if needed)."""
    logger.info("Create folder: %s", path)
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error("Failed to create folder %s: %s", path, e)
        return False

def delete_folder(path: str) -> bool:
    """Delete a directory and all its contents recursively."""
    logger.info("Delete folder: %s", path)
    try:
        shutil.rmtree(path)
        return True
    except Exception as e:
        logger.error("Failed to delete folder %s: %s", path, e)
        return False

def list_folder(path: str) -> list[str]:
    """List the contents of a directory."""
    logger.info("List folder: %s", path)
    try:
        items = os.listdir(path)
        return items
    except Exception as e:
        logger.error("Failed to list folder %s: %s", path, e)
        return []

def open_folder(path: str) -> bool:
    """Open a folder in Windows File Explorer."""
    logger.info("Open folder: %s", path)
    try:
        os.startfile(path)
        return True
    except Exception as e:
        logger.error("Failed to open folder %s: %s", path, e)
        return False
