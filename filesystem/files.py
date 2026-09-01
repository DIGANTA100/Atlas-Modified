"""
Atlas-Modified: filesystem/files.py
File manipulation operations.
"""

import os
import shutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def create_file(path: str, content: str = "") -> bool:
    """Create a new file with optional content."""
    logger.info("Create file: %s", path)
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        p.write_text(content, encoding="utf-8")
        return True
    except Exception as e:
        logger.error("Failed to create file %s: %s", path, e)
        return False

def move_file(src: str, dest: str) -> bool:
    """Move a file to a new location."""
    logger.info("Move file: %s -> %s", src, dest)
    try:
        shutil.move(src, dest)
        return True
    except Exception as e:
        logger.error("Failed to move file %s -> %s: %s", src, dest, e)
        return False

def copy_file(src: str, dest: str) -> bool:
    """Copy a file to a new location."""
    logger.info("Copy file: %s -> %s", src, dest)
    try:
        shutil.copy2(src, dest)
        return True
    except Exception as e:
        logger.error("Failed to copy file %s -> %s: %s", src, dest, e)
        return False

def rename_file(src: str, new_name: str) -> bool:
    """Rename a file in the same directory."""
    logger.info("Rename file: %s -> %s", src, new_name)
    try:
        p = Path(src)
        p.rename(p.with_name(new_name))
        return True
    except Exception as e:
        logger.error("Failed to rename file %s: %s", src, e)
        return False

def delete_file(path: str) -> bool:
    """Delete a file."""
    logger.info("Delete file: %s", path)
    try:
        os.remove(path)
        return True
    except Exception as e:
        logger.error("Failed to delete file %s: %s", path, e)
        return False

def open_file(path: str) -> bool:
    """Open a file with the default Windows application."""
    logger.info("Open file: %s", path)
    try:
        os.startfile(path)
        return True
    except Exception as e:
        logger.error("Failed to open file %s: %s", path, e)
        return False
