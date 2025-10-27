"""
Retry Logic Module
Enhanced retry mechanism with exponential backoff and error classification
"""

import asyncio
import logging
import random
from enum import Enum
from typing import Callable, Optional, Tuple, Any

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Classification of error types for retry decisions"""
    TRANSIENT = "transient"  # Network, timeout - retry
    AUTH_FAILED = "auth_failed"  # Cookie invalid - don't retry
    RATE_LIMITED = "rate_limited"  # Rate limit - backoff longer
    VIDEO_UNAVAILABLE = "video_unavailable"  # Video gone - don't retry
    UNKNOWN = "unknown"  # Unknown - retry with caution


class RetryConfig:
    """Configuration for retry behavior"""
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 5.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and optional jitter"""
        delay = min(
            self.base_delay * (self.exponential_base ** attempt),
            self.max_delay
        )
        
        if self.jitter:
            # Add random jitter (0-25% of delay)
            delay += random.uniform(0, delay * 0.25)
        
        return delay


async def retry_async(
    func: Callable,
    *args,
    config: Optional[RetryConfig] = None,
    error_classifier: Optional[Callable[[Exception], ErrorType]] = None,
    **kwargs
) -> Tuple[Any, Optional[Exception]]:
    """
    Retry async function with exponential backoff and error classification.
    
    Args:
        func: Async function to retry
        *args: Positional arguments for func
        config: RetryConfig instance
        error_classifier: Function to classify exceptions
        **kwargs: Keyword arguments for func
        
    Returns:
        Tuple of (result, error) - error is None on success
        
    Example:
        result, error = await retry_async(
            my_async_func,
            arg1, arg2,
            config=RetryConfig(max_retries=5),
            error_classifier=lambda e: ErrorType.TRANSIENT if isinstance(e, TimeoutError) else ErrorType.UNKNOWN
        )
    """
    if config is None:
        config = RetryConfig()
    
    if error_classifier is None:
        error_classifier = lambda e: ErrorType.UNKNOWN
    
    last_error = None
    
    for attempt in range(config.max_retries):
        try:
            result = await func(*args, **kwargs)
            return result, None
        
        except Exception as e:
            last_error = e
            error_type = error_classifier(e)
            
            logger.warning(
                f"Attempt {attempt + 1}/{config.max_retries} failed: {e} "
                f"(type: {error_type.value})"
            )
            
            # Don't retry on permanent errors
            if error_type in [ErrorType.AUTH_FAILED, ErrorType.VIDEO_UNAVAILABLE]:
                logger.error(f"Permanent error detected, stopping retries: {error_type.value}")
                return None, e
            
            # Last attempt - don't sleep
            if attempt >= config.max_retries - 1:
                break
            
            # Calculate delay
            if error_type == ErrorType.RATE_LIMITED:
                # Longer delay for rate limits
                delay = config.get_delay(attempt) * 2
            else:
                delay = config.get_delay(attempt)
            
            logger.info(f"Retrying in {delay:.2f} seconds...")
            await asyncio.sleep(delay)
    
    logger.error(f"All {config.max_retries} retry attempts failed")
    return None, last_error


def classify_video_playback_error(exception: Exception) -> ErrorType:
    """Classify exceptions from video playback"""
    error_str = str(exception).lower()
    
    if "timeout" in error_str or "connection" in error_str:
        return ErrorType.TRANSIENT
    
    if "cookie" in error_str or "login" in error_str or "auth" in error_str:
        return ErrorType.AUTH_FAILED
    
    if "rate" in error_str or "limit" in error_str or "429" in error_str:
        return ErrorType.RATE_LIMITED
    
    if "unavailable" in error_str or "404" in error_str or "not found" in error_str:
        return ErrorType.VIDEO_UNAVAILABLE
    
    return ErrorType.UNKNOWN
