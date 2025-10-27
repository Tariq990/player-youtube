"""
Rate Limiting Module
Provides rate limiting for external API calls
"""

import asyncio
import time
from collections import deque
from typing import Optional


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for async operations.
    
    Example:
        limiter = TokenBucketRateLimiter(rate=5, period=60)  # 5 calls per minute
        async with limiter:
            await make_api_call()
    """
    
    def __init__(self, rate: int, period: float = 60.0):
        """
        Args:
            rate: Maximum number of operations allowed
            period: Time period in seconds
        """
        self.rate = rate
        self.period = period
        self.tokens = rate
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire a token, waiting if necessary"""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_update
            
            # Refill tokens based on elapsed time
            self.tokens = min(
                self.rate,
                self.tokens + (elapsed * self.rate / self.period)
            )
            self.last_update = now
            
            # Wait if no tokens available
            if self.tokens < 1:
                sleep_time = (1 - self.tokens) * self.period / self.rate
                await asyncio.sleep(sleep_time)
                self.tokens = 0
            else:
                self.tokens -= 1
    
    async def __aenter__(self):
        await self.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False


class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter with precise control.
    
    Example:
        limiter = SlidingWindowRateLimiter(max_calls=10, window=60)  # 10 calls per minute
        async with limiter:
            await make_api_call()
    """
    
    def __init__(self, max_calls: int, window: float = 60.0):
        """
        Args:
            max_calls: Maximum number of calls in window
            window: Time window in seconds
        """
        self.max_calls = max_calls
        self.window = window
        self.calls = deque()
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make a call"""
        async with self._lock:
            now = time.monotonic()
            
            # Remove old calls outside window
            while self.calls and now - self.calls[0] > self.window:
                self.calls.popleft()
            
            # Wait if at limit
            if len(self.calls) >= self.max_calls:
                sleep_time = self.window - (now - self.calls[0]) + 0.1
                await asyncio.sleep(sleep_time)
                
                # Refresh after sleep
                now = time.monotonic()
                while self.calls and now - self.calls[0] > self.window:
                    self.calls.popleft()
            
            self.calls.append(now)
    
    async def __aenter__(self):
        await self.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False
