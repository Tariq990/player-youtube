"""
Cookie File Watcher
Monitors cookies.json for changes and reloads automatically.
"""

import asyncio
import logging
from pathlib import Path
from typing import Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

logger = logging.getLogger(__name__)


class CookieFileHandler(FileSystemEventHandler):
    """Handler for cookie file modification events."""
    
    def __init__(
        self,
        cookie_path: Path,
        reload_callback: Callable[[], None],
        debounce_seconds: float = 2.0
    ):
        """
        Initialize cookie file handler.
        
        Args:
            cookie_path: Path to cookies.json file
            reload_callback: Function to call when cookies need reload
            debounce_seconds: Wait time to avoid multiple reloads
        """
        self.cookie_path = cookie_path.resolve()
        self.reload_callback = reload_callback
        self.debounce_seconds = debounce_seconds
        self._last_reload: float = 0
        self._reload_task: Optional[asyncio.Task] = None
        
    def on_modified(self, event: FileModifiedEvent) -> None:
        """Handle file modification event."""
        if event.is_directory:
            return
            
        # Check if modified file is our cookies.json
        src_path = event.src_path
        if isinstance(src_path, bytes):
            src_path = src_path.decode('utf-8')
        modified_path = Path(str(src_path)).resolve()
        if modified_path != self.cookie_path:
            return
            
        # Debounce multiple rapid modifications
        current_time = asyncio.get_event_loop().time()
        if current_time - self._last_reload < self.debounce_seconds:
            logger.debug(f"Debouncing cookie reload (last reload {current_time - self._last_reload:.1f}s ago)")
            return
            
        self._last_reload = current_time
        
        # Schedule reload in asyncio event loop
        try:
            loop = asyncio.get_event_loop()
            if self._reload_task and not self._reload_task.done():
                self._reload_task.cancel()
            self._reload_task = loop.create_task(self._async_reload())
        except RuntimeError:
            # No event loop running, call directly
            logger.warning("No event loop running, calling reload directly")
            self.reload_callback()
    
    async def _async_reload(self) -> None:
        """Async wrapper for reload callback."""
        try:
            logger.info(f"Cookie file modified, reloading: {self.cookie_path.name}")
            self.reload_callback()
            logger.info("Cookies reloaded successfully")
        except Exception as e:
            logger.error(f"Failed to reload cookies: {e}", exc_info=True)


class CookieWatcher:
    """Watches cookie file for changes and triggers reload."""
    
    def __init__(
        self,
        cookie_path: Path,
        reload_callback: Callable[[], None],
        debounce_seconds: float = 2.0
    ):
        """
        Initialize cookie watcher.
        
        Args:
            cookie_path: Path to cookies.json file
            reload_callback: Function to call when cookies need reload
            debounce_seconds: Wait time to avoid multiple reloads
        """
        self.cookie_path = cookie_path
        self.reload_callback = reload_callback
        self.debounce_seconds = debounce_seconds
        
        self._observer: Observer | None = None
        self._handler: CookieFileHandler | None = None
        
    def start(self) -> None:
        """Start watching cookie file."""
        if self._observer and self._observer.is_alive():
            logger.warning("Cookie watcher already running")
            return
            
        if not self.cookie_path.exists():
            logger.error(f"Cookie file not found: {self.cookie_path}")
            return
            
        # Create handler and observer
        self._handler = CookieFileHandler(
            self.cookie_path,
            self.reload_callback,
            self.debounce_seconds
        )
        
        self._observer = Observer()
        
        # Watch the directory containing the cookie file
        watch_dir = self.cookie_path.parent
        if self._observer is not None:  # Type guard
            self._observer.schedule(self._handler, str(watch_dir), recursive=False)
            self._observer.start()
            logger.info(f"Started watching cookie file: {self.cookie_path.name}")
        
    def stop(self) -> None:
        """Stop watching cookie file."""
        if self._observer and self._observer.is_alive():
            self._observer.stop()
            self._observer.join(timeout=5.0)
            logger.info("Stopped cookie watcher")
        
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
        return False


async def demo():
    """Demo usage of cookie watcher."""
    from pathlib import Path
    
    def on_cookie_reload():
        print("🔄 Cookies reloaded!")
    
    cookie_path = Path("data/cookies.json")
    
    watcher = CookieWatcher(cookie_path, on_cookie_reload)
    watcher.start()
    
    try:
        print(f"Watching {cookie_path.name}... (modify the file to see reload)")
        await asyncio.sleep(60)
    finally:
        watcher.stop()


if __name__ == "__main__":
    asyncio.run(demo())
