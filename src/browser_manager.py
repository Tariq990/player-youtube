"""
Browser Management Module
Handles driver creation, cookie management, and browser lifecycle
"""

import asyncio
import contextlib
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

logger = logging.getLogger(__name__)


def get_brave_path() -> Optional[str]:
    """Get Brave browser executable path"""
    env_path = os.getenv('BRAVE_BINARY_PATH')
    if env_path and os.path.exists(env_path):
        return env_path
    
    # Platform-specific paths
    import platform
    system = platform.system()
    
    if system == "Linux":
        brave_paths = [
            "/usr/bin/brave-browser",
            "/usr/bin/brave",
            "/snap/bin/brave",
            "/usr/local/bin/brave-browser",
            "/usr/local/bin/brave",
        ]
    elif system == "Darwin":  # macOS
        brave_paths = [
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        ]
    else:  # Windows
        brave_paths = [
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
            os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"),
        ]
    
    for path in brave_paths:
        if os.path.exists(path):
            return path
    return None


def create_driver(brave_path: str, user_agent: Optional[str] = None, headless: bool = False):
    """Create a Brave browser driver with anti-detection"""
    chrome_options = Options()
    chrome_options.binary_location = brave_path
    
    if headless:
        chrome_options.add_argument('--headless=new')
    else:
        chrome_options.add_argument('--start-maximized')
    
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    if user_agent:
        chrome_options.add_argument(f'user-agent={user_agent}')
    
    # Anti-detection
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e:
        try:
            service = Service(ChromeDriverManager(chrome_type=ChromeType.BRAVE).install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except:
            driver = webdriver.Chrome(options=chrome_options)
    
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver


@contextlib.asynccontextmanager
async def managed_driver(brave_path: str, user_agent: Optional[str] = None, headless: bool = False):
    """
    Context manager for browser driver with proper cleanup and timeout.
    
    Usage:
        async with managed_driver(brave_path, user_agent, headless) as driver:
            driver.get("https://youtube.com")
    """
    driver = None
    try:
        driver = create_driver(brave_path, user_agent, headless)
        yield driver
    finally:
        if driver:
            try:
                with contextlib.suppress(asyncio.TimeoutError):
                    await asyncio.wait_for(
                        asyncio.to_thread(driver.quit), 
                        timeout=5.0
                    )
            except Exception as e:
                logger.error(f"Failed to quit driver: {e}")


def add_cookies_to_driver(driver, cookies: List[Dict]) -> int:
    """
    Add cookies to driver with error handling.
    
    Args:
        driver: Selenium WebDriver instance
        cookies: List of cookie dictionaries
        
    Returns:
        Number of successfully added cookies
    """
    added = 0
    for cookie in cookies:
        try:
            cookie_dict = {
                'name': cookie['name'],
                'value': cookie['value'],
                'domain': cookie.get('domain', '.youtube.com'),
                'path': cookie.get('path', '/'),
                'secure': cookie.get('secure', False),
            }
            
            # Handle expiry
            for exp_key in ['expiry', 'expirationDate']:
                if exp_key in cookie:
                    cookie_dict['expiry'] = int(cookie[exp_key])
                    break
            
            driver.add_cookie(cookie_dict)
            added += 1
        except Exception as e:
            logger.warning(f"Failed to add cookie {cookie.get('name')}: {e}")
    
    return added
