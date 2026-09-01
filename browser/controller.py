"""
Atlas-Modified: browser/controller.py
Playwright-based browser controller for precise web automation.
Maintains a persistent browser session so logins and cookies are kept.
"""

import os
import logging
from typing import Optional
from pathlib import Path
from playwright.sync_api import sync_playwright, Playwright, BrowserContext, Page

logger = logging.getLogger(__name__)

USER_DATA_DIR = Path("browser_data")

class BrowserController:
    def __init__(self):
        self._playwright: Optional[Playwright] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        
    def _ensure_running(self) -> None:
        """Ensure the browser and page are initialized."""
        if self._page and not self._page.is_closed():
            return
            
        logger.info("Starting Playwright browser session...")
        if not self._playwright:
            self._playwright = sync_playwright().start()
            
        USER_DATA_DIR.mkdir(exist_ok=True)
        
        # Use persistent context to save cookies, logins, history
        self._context = self._playwright.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR.absolute()),
            headless=False,  # Agent is a visible desktop assistant!
            channel="chrome", # Try to use the local Chrome install if available
            viewport={"width": 1280, "height": 720}
        )
        
        # Get the default page
        pages = self._context.pages
        self._page = pages[0] if pages else self._context.new_page()

    def navigate(self, url: str) -> str:
        """Navigate to a URL."""
        self._ensure_running()
        if not url.startswith("http"):
            url = "https://" + url
            
        logger.info("Browser navigating to: %s", url)
        self._page.goto(url, wait_until="domcontentloaded")
        return self._page.title()

    def click(self, selector: str) -> bool:
        """Click an element by CSS selector or text."""
        self._ensure_running()
        logger.info("Browser click: %s", selector)
        try:
            self._page.click(selector, timeout=5000)
            return True
        except Exception as e:
            logger.error("Click failed for %s: %s", selector, e)
            return False

    def fill(self, selector: str, text: str) -> bool:
        """Fill a text input field."""
        self._ensure_running()
        logger.info("Browser fill '%s' into %s", text, selector)
        try:
            self._page.fill(selector, text, timeout=5000)
            return True
        except Exception as e:
            logger.error("Fill failed for %s: %s", selector, e)
            return False

    def press_key(self, selector: str, key: str) -> bool:
        """Press a keyboard key on a specific element (e.g., 'Enter')."""
        self._ensure_running()
        logger.info("Browser press %s on %s", key, selector)
        try:
            self._page.press(selector, key, timeout=5000)
            return True
        except Exception as e:
            logger.error("Key press failed for %s: %s", selector, e)
            return False

    def get_text(self, selector: str = "body") -> str:
        """Extract text content from the page or a specific element."""
        self._ensure_running()
        try:
            return self._page.inner_text(selector, timeout=5000)
        except Exception as e:
            logger.error("Extract text failed for %s: %s", selector, e)
            return f"Error: {e}"
            
    def run_script(self, script: str) -> any:
        """Execute arbitrary Javascript on the page."""
        self._ensure_running()
        try:
            return self._page.evaluate(script)
        except Exception as e:
            logger.error("Script execution failed: %s", e)
            return f"Error: {e}"

    def close(self) -> None:
        """Close the browser context."""
        logger.info("Closing browser session...")
        if self._context:
            self._context.close()
            self._context = None
            self._page = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None

# Global singleton
browser_controller = BrowserController()
