"""
Atlas-Modified: filesystem/search.py
File and folder searching operations.
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def find_file(name: str, root_dir: str = "~", max_depth: int = 4) -> list[str]:
    """
    Search for a file or folder by partial name starting from root_dir.
    By default starts at the user's home directory.
    To avoid long hangs, max_depth restricts the recursive search.
    """
    if root_dir == "~":
        root_dir = os.path.expanduser("~")
        
    logger.info("Search for '%s' in %s (max depth %d)", name, root_dir, max_depth)
    
    root_path = Path(root_dir)
    if not root_path.exists() or not root_path.is_dir():
        return []

    results = []
    name_lower = name.lower()
    
    # We use os.walk to control search depth
    start_depth = len(root_path.parts)
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        current_depth = len(Path(dirpath).parts)
        if current_depth - start_depth >= max_depth:
            dirnames.clear() # Stop walking deeper
            continue
            
        # Check folders
        for d in dirnames:
            if name_lower in d.lower():
                results.append(os.path.join(dirpath, d))
                
        # Check files
        for f in filenames:
            if name_lower in f.lower():
                results.append(os.path.join(dirpath, f))
                
        if len(results) >= 50:
            break # Cap at 50 results to prevent massive payloads

    logger.info("Found %d matches for '%s'", len(results), name)
    return results[:50]
