"""
Constants - Project-wide constants and configuration values.

This module contains all constant values used across the project.
Centralized constants make the code more maintainable and prevent magic numbers.
"""

# Standard library imports
from typing import List, Tuple

# ============================================================================
# Browser Configuration
# ============================================================================

BRAVE_PATHS_WINDOWS: List[str] = [
    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
]

USER_AGENTS: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

VIEWPORT_SIZES: List[Tuple[int, int]] = [
    (1920, 1080),  # Full HD
    (1366, 768),   # Common laptop
    (1536, 864),   # 125% scaled
    (2560, 1440),  # 2K
]

# ============================================================================
# YouTube Specific
# ============================================================================

IMPORTANT_COOKIES: List[str] = [
    'LOGIN_INFO',
    'SAPISID',
    'SID',
    '__Secure-3PSID',
    '__Secure-1PSID',
    'SSID',
]

YOUTUBE_DOMAINS: List[str] = [
    '.youtube.com',
    'www.youtube.com',
    '.google.com',
]

# ============================================================================
# Timing Configuration (in seconds)
# ============================================================================

# Delays
MIN_DELAY_BETWEEN_ACTIONS: float = 0.5
MAX_DELAY_BETWEEN_ACTIONS: float = 2.0

MIN_DELAY_BETWEEN_VIDEOS: int = 30
MAX_DELAY_BETWEEN_VIDEOS: int = 60

# Timeouts
PAGE_LOAD_TIMEOUT: int = 30
ELEMENT_WAIT_TIMEOUT: int = 10
VIDEO_START_TIMEOUT: int = 15

# Intervals
PLAYBACK_CHECK_INTERVAL: int = 5
HEALTH_CHECK_INTERVAL: int = 60

# ============================================================================
# Rate Limiting
# ============================================================================

MAX_VIDEOS_PER_HOUR: int = 15
MAX_VIDEOS_PER_DAY: int = 100
MAX_CONCURRENT_WINDOWS: int = 4

# Cooldown periods (in seconds)
COOLDOWN_AFTER_ERROR: int = 60
COOLDOWN_AFTER_403: int = 3600  # 1 hour
COOLDOWN_AFTER_429: int = 7200  # 2 hours
COOLDOWN_AFTER_CAPTCHA: int = 14400  # 4 hours

# ============================================================================
# Cookie Management
# ============================================================================

COOKIE_ROTATION_POLICIES: List[str] = [
    'round_robin',
    'least_used',
    'random',
    'failover',
]

COOKIE_STATUSES: List[str] = [
    'active',
    'expired',
    'invalid',
    'banned',
    'quarantine',
]

# ============================================================================
# Video Filtering
# ============================================================================

MIN_VIDEO_DURATION: int = 30  # seconds
MAX_VIDEO_DURATION: int = 7200  # 2 hours
SHORT_VIDEO_THRESHOLD: int = 60  # Videos under this are considered Shorts

# ============================================================================
# Logging
# ============================================================================

LOG_FORMAT_FILE: str = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
LOG_FORMAT_CONSOLE: str = '%(asctime)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT: str = '%Y-%m-%d %H:%M:%S'

MAX_LOG_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT: int = 5

# ============================================================================
# Database
# ============================================================================

DB_TIMEOUT: int = 30  # seconds
DB_CHECK_SAME_THREAD: bool = False

# ============================================================================
# Error Messages
# ============================================================================

ERROR_NO_COOKIES: str = "No cookies found. Run: python scripts/save_cookies.py"
ERROR_BRAVE_NOT_FOUND: str = "Brave browser not found. Please install Brave or set BRAVE_BINARY_PATH in .env"
ERROR_NO_VIDEOS: str = "No videos found in channel"
ERROR_INVALID_CONFIG: str = "Invalid configuration file"

# ============================================================================
# Success Messages
# ============================================================================

SUCCESS_COOKIE_LOADED: str = "✅ Cookies loaded successfully"
SUCCESS_VIDEO_COMPLETE: str = "✅ Video completed successfully"
SUCCESS_LOGIN_VERIFIED: str = "✅ User is logged in"
