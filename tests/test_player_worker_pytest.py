import asyncio
import types

import pytest

from player_worker import PlayerWorker


class FakeDriver:
    def __init__(self):
        self.cookies = [{"name": "LOGIN_INFO", "value": "x"}]
        self._paused = False
        self.window_size = {"width": 1280, "height": 720}

    def get(self, url):
        return None

    def get_cookies(self):
        return self.cookies

    def get_window_size(self):
        return self.window_size

    def execute_script(self, script):
        if "paused" in script:
            return self._paused is False
        if "document.querySelector('video').duration" in script:
            return 120
        if "document.querySelector('.ytp-error')" in script:
            return None
        return None

    def find_element(self, by=None, value=None):
        class El:
            def click(self):
                pass
        return El()

    def quit(self):
        pass


@pytest.mark.asyncio
async def test_player_worker_basic():
    driver = FakeDriver()
    config = {"MIN_VIDEO_DURATION": 10, "DEFAULT_VIDEO_DURATION": 60}
    worker = PlayerWorker(driver, config)

    video = {"url": "https://youtube.com/watch?v=abc", "title": "t"}
    cookie_data = {}

    # Speed up sleeps
    async def fast_sleep(_):
        return None

    orig_sleep = asyncio.sleep
    try:
        asyncio.sleep = fast_sleep
        # Short-circuit monitoring to avoid time-based loop
        async def instant_monitor(_):
            return True
        worker._monitor_playback = instant_monitor  # type: ignore[attr-defined]
        ok = await worker.play_video(video, cookie_data)
        assert ok is True
    finally:
        asyncio.sleep = orig_sleep


@pytest.mark.asyncio
async def test_player_worker_not_logged_in():
    class D(FakeDriver):
        def get_cookies(self):
            return []  # no login cookies
        def find_element(self, *a, **k):
            raise Exception("no avatar")
    driver = D()
    worker = PlayerWorker(driver, {"MIN_VIDEO_DURATION": 5})
    async def fast_sleep(_):
        return None
    orig_sleep = asyncio.sleep
    try:
        asyncio.sleep = fast_sleep
        ok = await worker.play_video({"url": "https://x"}, {})
        assert ok is False
    finally:
        asyncio.sleep = orig_sleep


@pytest.mark.asyncio
async def test_player_worker_detects_error():
    class E(FakeDriver):
        def execute_script(self, script):
            if "document.querySelector('.ytp-error')" in script:
                return True
            return super().execute_script(script)
    driver = E()
    worker = PlayerWorker(driver, {"MIN_VIDEO_DURATION": 5})
    async def fast_sleep(_):
        return None
    orig_sleep = asyncio.sleep
    try:
        asyncio.sleep = fast_sleep
        ok = await worker.play_video({"url": "https://x"}, {})
        assert ok is False
    finally:
        asyncio.sleep = orig_sleep
