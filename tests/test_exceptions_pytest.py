import pytest

from exceptions import (
    YouTubePlayerError,
    ConfigurationError,
    CookieError,
    CookieNotFoundError,
    CookieExpiredError,
    CookieInvalidError,
    AuthenticationError,
    BrowserError,
    BrowserNotFoundError,
    BrowserLaunchError,
    VideoError,
    VideoNotFoundError,
    VideoPlaybackError,
    VideoFetchError,
    PlayerError,
    ConfigError,
    RateLimitError,
    NetworkError,
    DatabaseError,
)


def test_exception_hierarchy():
    assert issubclass(ConfigurationError, YouTubePlayerError)
    assert issubclass(CookieError, YouTubePlayerError)
    assert issubclass(BrowserError, YouTubePlayerError)
    assert issubclass(VideoError, YouTubePlayerError)
    assert issubclass(PlayerError, YouTubePlayerError)


def test_rate_limit_error_attribute():
    e = RateLimitError("Too many requests", cooldown_seconds=120)
    assert isinstance(e, YouTubePlayerError)
    assert e.cooldown_seconds == 120


@pytest.mark.parametrize("exc_cls", [
    CookieNotFoundError, CookieExpiredError, CookieInvalidError,
    AuthenticationError, BrowserNotFoundError, BrowserLaunchError,
    VideoNotFoundError, VideoPlaybackError, VideoFetchError,
    ConfigError, NetworkError, DatabaseError,
])
def test_raise_each_exception(exc_cls):
    with pytest.raises(exc_cls):
        raise exc_cls("test")
