import asyncio
import time
import types
import pytest

import player_worker as pw_mod
from selenium.webdriver.common.by import By


class DummyDriver:
    def __init__(self):
        self.cookies = []
        self.window_size = {"width": 800, "height": 600}
        self.quit_called = False
        self._paused_calls = 0
    def get(self, url):
        self.url = url
    def get_cookies(self):
        return list(self.cookies)
    def get_window_size(self):
        return dict(self.window_size)
    def execute_script(self, script):
        if "document.querySelector('video').duration" in script:
            return 0  # force fallback
        if "document.querySelector('video').paused" in script:
            self._paused_calls += 1
            return False  # is_playing = False to trigger resume branch
        if "document.querySelector('.ytp-error')" in script:
            return False
        if script.startswith("window.scroll"):
            raise Exception("scroll error")
        return None
    def find_element(self, by=None, value=None):
        raise Exception("no play button")
    def quit(self):
        self.quit_called = True


@pytest.mark.asyncio
async def test_verify_login_avatar_success(monkeypatch):
    class AvatarEl: ...
    # Stub WebDriverWait to return a fake avatar element
    class StubWait:
        def __init__(self, driver, timeout):
            pass
        def until(self, condition):
            return AvatarEl()
    monkeypatch.setattr(pw_mod, "WebDriverWait", StubWait)

    drv = DummyDriver()
    worker = pw_mod.PlayerWorker(drv, {})
    assert await worker._verify_login() is True


@pytest.mark.asyncio
async def test_verify_login_cookie_fallback(monkeypatch):
    # Make WebDriverWait raise to trigger fallback
    class StubWait:
        def __init__(self, driver, timeout):
            pass
        def until(self, condition):
            raise Exception("no avatar")
    monkeypatch.setattr(pw_mod, "WebDriverWait", StubWait)

    drv = DummyDriver()
    drv.cookies = [{"name": "LOGIN_INFO"}]
    worker = pw_mod.PlayerWorker(drv, {})
    assert await worker._verify_login() is True


@pytest.mark.asyncio
async def test_get_video_duration_from_dict_and_zero_script(monkeypatch):
    drv = DummyDriver()
    worker = pw_mod.PlayerWorker(drv, {"ENABLE_HUMAN_SIMULATION": False, "DEFAULT_VIDEO_DURATION": 12})
    # From dict
    assert await worker._get_video_duration({"duration": "7"}) == 7
    # From script returns 0 -> None
    assert await worker._get_video_duration({}) is None


@pytest.mark.asyncio
async def test_get_video_duration_from_dom_positive():
    class D(DummyDriver):
        def execute_script(self, script):
            if "duration" in script:
                # Return a truthy float like real DOM API would
                return 42.0
            return super().execute_script(script)
    worker = pw_mod.PlayerWorker(D(), {"ENABLE_HUMAN_SIMULATION": False})
    assert await worker._get_video_duration({}) == 42


@pytest.mark.asyncio
async def test_random_mouse_movements_exception_swallowed(monkeypatch):
    class RaisingActions:
        def __init__(self, driver):
            raise RuntimeError("boom")
    monkeypatch.setattr(pw_mod, "ActionChains", RaisingActions)
    worker = pw_mod.PlayerWorker(DummyDriver(), {})
    # Should not raise
    await worker._random_mouse_movements()


@pytest.mark.asyncio
async def test_random_scroll_exception_swallowed():
    worker = pw_mod.PlayerWorker(DummyDriver(), {})
    # Should not raise due to internal try/except
    await worker._random_scroll()


@pytest.mark.asyncio
async def test_simulate_human_behavior_normal(monkeypatch):
    # Make ActionChains no-op
    class AC:
        def __init__(self, driver):
            pass
        def move_by_offset(self, x, y):
            return self
        def perform(self):
            return None
    monkeypatch.setattr(pw_mod, "ActionChains", AC)

    # Make random values deterministic and minimal
    monkeypatch.setattr(pw_mod.random, "randint", lambda a, b: 1)
    monkeypatch.setattr(pw_mod.random, "uniform", lambda a, b: 0)
    async def fast_sleep(_):
        return None
    monkeypatch.setattr(asyncio, "sleep", fast_sleep)

    worker = pw_mod.PlayerWorker(DummyDriver(), {
        "ENABLE_HUMAN_SIMULATION": True,
        "ANTI_DETECTION": {
            "ENABLE_MOUSE_SIMULATION": True,
            "ENABLE_SCROLL_SIMULATION": True,
            "RANDOM_DELAY_MIN": 0,
            "RANDOM_DELAY_MAX": 0,
            "MOUSE_MOVE_COUNT_MIN": 1,
            "MOUSE_MOVE_COUNT_MAX": 1,
            "SCROLL_COUNT_MIN": 1,
            "SCROLL_COUNT_MAX": 1,
        }
    })
    await worker._simulate_human_behavior_before_play()


@pytest.mark.asyncio
async def test_monitor_playback_resume_try_except(monkeypatch):
    # Time control
    class TimeStub:
        def __init__(self, start):
            self.t = start
        def time(self):
            return self.t
        def advance(self, s):
            self.t += s
    ts = TimeStub(time.time())
    monkeypatch.setattr(time, "time", ts.time)

    async def fast_sleep(sec):
        ts.advance(sec)
        return None
    monkeypatch.setattr(asyncio, "sleep", fast_sleep)

    worker = pw_mod.PlayerWorker(DummyDriver(), {"MIN_VIDEO_DURATION": 5, "ENABLE_HUMAN_SIMULATION": False})
    ok = await worker._monitor_playback(5)
    assert ok is True


@pytest.mark.asyncio
async def test_monitor_playback_exception_continue(monkeypatch):
    class ErrDriver(DummyDriver):
        def execute_script(self, script):
            raise RuntimeError("js error")
    # Time control
    class TimeStub:
        def __init__(self, start):
            self.t = start
        def time(self):
            return self.t
        def advance(self, s):
            self.t += s
    ts = TimeStub(time.time())
    monkeypatch.setattr(time, "time", ts.time)
    async def fast_sleep(sec):
        ts.advance(sec)
        return None
    monkeypatch.setattr(asyncio, "sleep", fast_sleep)

    worker = pw_mod.PlayerWorker(ErrDriver(), {"MIN_VIDEO_DURATION": 5, "ENABLE_HUMAN_SIMULATION": False})
    ok = await worker._monitor_playback(5)
    assert ok is True


def test_close_swallow_quit_exception():
    class Q(DummyDriver):
        def quit(self):
            raise RuntimeError("cannot quit")
    worker = pw_mod.PlayerWorker(Q(), {})
    worker.close()  # should not raise


@pytest.mark.asyncio
async def test_play_video_with_worker_always_closes(monkeypatch):
    # Replace PlayerWorker with a fake that raises on play and tracks close
    class FakeW:
        def __init__(self, driver, config):
            self.closed = False
        async def play_video(self, v, c):
            raise RuntimeError("boom")
        def close(self):
            self.closed = True
    monkeypatch.setattr(pw_mod, "PlayerWorker", FakeW)

    class D:
        def quit(self):
            pass

    # Spy to capture the FakeW instance
    captured = {}
    orig_cls = pw_mod.PlayerWorker
    def factory(driver, config):
        inst = FakeW(driver, config)
        captured['inst'] = inst
        return inst
    monkeypatch.setattr(pw_mod, "PlayerWorker", factory)

    caught = None
    try:
        await pw_mod.play_video_with_worker(D(), {"url": "u"}, {}, {})
    except RuntimeError as e:
        caught = e
    assert isinstance(caught, RuntimeError)
    assert captured['inst'].closed is True


@pytest.mark.asyncio
async def test_play_video_with_worker_success(monkeypatch):
    class FakeW:
        def __init__(self, driver, config):
            self.closed = False
        async def play_video(self, v, c):
            return True
        def close(self):
            self.closed = True
    captured = {}
    def factory(driver, config):
        inst = FakeW(driver, config)
        captured['inst'] = inst
        return inst
    monkeypatch.setattr(pw_mod, "PlayerWorker", factory)
    class D:
        def quit(self):
            pass
    ok = await pw_mod.play_video_with_worker(D(), {"url": "u"}, {}, {})
    assert ok is True
    assert captured['inst'].closed is True