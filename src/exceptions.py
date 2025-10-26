"""
Custom Exceptions - Project-specific exception classes.

This module defines custom exceptions for better error handling and debugging.
Each exception has a clear purpose and helps identify the exact problem.
"""


class YouTubePlayerError(Exception):
    """Base exception for all YouTube Player errors."""
    pass


class ConfigurationError(YouTubePlayerError):
    """Raised when there's an error in configuration."""
    pass


class CookieError(YouTubePlayerError):
    """Base exception for cookie-related errors."""
    pass


class CookieNotFoundError(CookieError):
    """Raised when no valid cookies are available."""
    pass


class CookieExpiredError(CookieError):
    """Raised when a cookie has expired."""
    pass


class CookieInvalidError(CookieError):
    """Raised when a cookie is invalid or corrupted."""
    pass


class AuthenticationError(YouTubePlayerError):
    """Raised when authentication fails."""
    pass


class BrowserError(YouTubePlayerError):
    """Base exception for browser-related errors."""
    pass


class BrowserNotFoundError(BrowserError):
    """Raised when Brave browser is not found."""
    pass


class BrowserLaunchError(BrowserError):
    """Raised when browser fails to launch."""
    pass


class VideoError(YouTubePlayerError):
    """Base exception for video-related errors."""
    pass


class VideoNotFoundError(VideoError):
    """Raised when video is not found or unavailable."""
    pass


class VideoPlaybackError(VideoError):
    """Raised when video playback fails."""
    pass


class VideoFetchError(VideoError):
    """Raised when fetching videos fails."""
    pass


class PlayerError(YouTubePlayerError):
    """Base exception for player-related errors."""
    pass


class ConfigError(YouTubePlayerError):
    """Raised when configuration is invalid."""
    pass


class RateLimitError(YouTubePlayerError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str, cooldown_seconds: int = 0):
        """
        Initialize rate limit error.
        
        Args:
            message: Error message
            cooldown_seconds: Recommended cooldown period
        """
        super().__init__(message)
        self.cooldown_seconds = cooldown_seconds


class NetworkError(YouTubePlayerError):
    """Raised when network connection fails."""
    pass


class DatabaseError(YouTubePlayerError):
    """Raised when database operation fails."""
    pass
