import asyncio
import time
import pytest

from player_worker import PlayerWorker
from selenium.webdriver.common.by import By


class FakeElement:
    def click(self):
        self.clicked = True


class FakeDriver:
    def __init__(self, playing_sequence=None, error_at=None):
        # playing_sequence: list[bool] return values for paused (False means playing, True means paused)
        self._call = 0
        self.playing_sequence = playing_sequence or [False] * 5
        self.error_at = error_at
        self.scrolled = []
        self.window_size = {'width': 1280, 'height': 720}
        self.cookies = [{'name': 'LOGIN_INFO'}]

    def get(self, url):
        self.url = url

    def get_cookies(self):
        return list(self.cookies)

    def get_window_size(self):
        return dict(self.window_size)

    def execute_script(self, script):
        if "document.querySelector('video').duration" in script:
            return 60
        if "document.querySelector('video').paused" in script:
            idx = min(self._call, len(self.playing_sequence) - 1)
            paused = self.playing_sequence[idx]
            self._call += 1
            return not paused  # is_playing
        if "document.querySelector('.ytp-error')" in script:
            if self.error_at is not None and self._call >= self.error_at:
                return True
            return False
        if script.startswith("window.scrollBy"):
            self.scrolled.append(script)
            return None
        if script.startswith("window.scrollTo"):
            self.scrolled.append(script)
            return None
        return None

    def find_element(self, by, value=None):
        if by == By.CLASS_NAME and value == "ytp-play-button":
            return FakeElement()
        raise Exception("not found")

    def quit(self):
        self.quit_called = True


@pytest.mark.asyncio
async def test_monitor_resume_from_pause(monkeypatch):
    # Time stub to control time progression deterministically
    class TimeStub:
        def __init__(self, start):
            self.t = start
        def time(self):
            return self.t
        def advance(self, sec):
            self.t += sec

    ts = TimeStub(time.time())
    monkeypatch.setattr(time, "time", ts.time)

    # Not playing initially (paused True), then playing
    driver = FakeDriver(playing_sequence=[True, False, False, False])
    worker = PlayerWorker(driver, config={"MIN_VIDEO_DURATION": 5, "ENABLE_HUMAN_SIMULATION": False})

    # Patch _get_video_duration to avoid script call
    async def fake_get_duration(video):
        return 6
    worker._get_video_duration = fake_get_duration

    # Advance time within loop checks
    async def sleep_and_advance(sec):
        ts.advance(sec)
        return None
    monkeypatch.setattr(asyncio, "sleep", sleep_and_advance)

    # Also patch _verify_login to True
    async def ok_login():
        return True
    worker._verify_login = ok_login

    # Run play_video and ensure success
    result = await worker.play_video({"url": "https://youtu.be?v=abc", "title": "t"}, {})
    assert result is True


@pytest.mark.asyncio
async def test_monitor_detects_error_and_stops(monkeypatch):
    # Patch sleeps to be instant and advance time with a TimeStub
    class TimeStub:
        def __init__(self, start):
            self.t = start
        def time(self):
            return self.t
        def advance(self, sec):
            self.t += sec

    ts = TimeStub(time.time())

    async def sleep_and_advance(sec):
        ts.advance(sec)
        return None

    monkeypatch.setattr(asyncio, "sleep", sleep_and_advance)
    monkeypatch.setattr(time, "time", ts.time)

    # Playing then error appears
    driver = FakeDriver(playing_sequence=[False, False, False], error_at=1)
    worker = PlayerWorker(driver, config={"MIN_VIDEO_DURATION": 5, "ENABLE_HUMAN_SIMULATION": False})

    async def fake_get_duration(video):
        return 10
    worker._get_video_duration = fake_get_duration

    async def ok_login():
        return True
    worker._verify_login = ok_login

    result = await worker.play_video({"url": "https://youtu.be?v=xyz"}, {})
    assert result is False
