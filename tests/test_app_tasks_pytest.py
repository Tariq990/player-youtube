import asyncio
import time
import pytest

import app as app_mod


class DummyDriver:
    def __init__(self):
        self.gotten = []
        self.added = []
        self.quit_called = False
    def get(self, url):
        self.gotten.append(url)
    def add_cookie(self, c):
        self.added.append(c)
    def quit(self):
        self.quit_called = True


class FakeWorker:
    def __init__(self, _driver, config):
        self.config = config
        self.calls = []
        self.return_value = True
    async def play_video(self, video, cookie_data):
        self.calls.append((video, cookie_data))
        return self.return_value


class FakePersistence:
    def __init__(self):
        self.marks = []
    def mark_seen(self, vid, title, duration):
        self.marks.append((vid, title, duration))


class FakeCookieMgr:
    def __init__(self):
        self.used = []
    def mark_used(self, cid):
        self.used.append(cid)


@pytest.mark.asyncio
async def test_play_video_task_success(monkeypatch):
    monkeypatch.setattr(app_mod, "get_brave_path", lambda: "C:/fake/brave.exe")
    monkeypatch.setattr(app_mod, "create_driver", lambda *a, **k: DummyDriver())

    worker = FakeWorker(None, {})
    worker.return_value = True
    monkeypatch.setattr(app_mod, "PlayerWorker", lambda driver, config: worker)

    # Speed up sleeps inside task
    monkeypatch.setattr(asyncio, "sleep", lambda *_a, **_k: asyncio.Future())

    sem = asyncio.Semaphore(1)
    persist = FakePersistence()
    cm = FakeCookieMgr()

    video = {"video_id": "v1", "url": "https://youtube.com/watch?v=v1", "title": "T", "duration": 33}
    cookie = {"id": "c1", "cookies": [{"name": "n", "value": "x"}], "user_agent": "ua"}
    config = {"USE_HEADLESS": False}

    # Monkeypatch asyncio.sleep to immediate-complete future
    async def fast_sleep(_):
        return None
    monkeypatch.setattr(asyncio, "sleep", fast_sleep)

    ok = await app_mod.play_video_task(video, cookie, config, sem, persist, cm)
    assert ok is True
    assert persist.marks == [("v1", "T", 33)]
    assert cm.used == ["c1"]


@pytest.mark.asyncio
async def test_play_video_task_failure(monkeypatch):
    monkeypatch.setattr(app_mod, "get_brave_path", lambda: "C:/fake/brave.exe")
    monkeypatch.setattr(app_mod, "create_driver", lambda *a, **k: DummyDriver())

    worker = FakeWorker(None, {})
    worker.return_value = False
    monkeypatch.setattr(app_mod, "PlayerWorker", lambda driver, config: worker)

    async def fast_sleep(_):
        return None
    monkeypatch.setattr(asyncio, "sleep", fast_sleep)

    sem = asyncio.Semaphore(1)
    persist = FakePersistence()
    cm = FakeCookieMgr()

    video = {"video_id": "v2", "url": "https://youtube.com/watch?v=v2", "title": "T2", "duration": 10}
    cookie = {"id": "c2", "cookies": [], "user_agent": "ua"}
    config = {"USE_HEADLESS": True}

    ok = await app_mod.play_video_task(video, cookie, config, sem, persist, cm)
    assert ok is False
    assert persist.marks == []
    assert cm.used == []


@pytest.mark.asyncio
async def test_play_video_task_with_retry_and_fallback(monkeypatch):
    # Force original cookie to fail regardless of retries; fallback succeeds
    calls = []
    async def fake_play_video_task(video, cookie, config, sem, persist, cm):
        calls.append(cookie["id"])
        return cookie["id"] == "c2"

    monkeypatch.setattr(app_mod, "play_video_task", fake_play_video_task)

    # test_cookie_login validates fallback cookie
    monkeypatch.setattr(app_mod, "test_cookie_login", lambda data, brave: True)

    # Fast sleep
    async def fast_sleep(_):
        return None
    monkeypatch.setattr(asyncio, "sleep", fast_sleep)

    sem = asyncio.Semaphore(1)
    persist = FakePersistence()
    cm = FakeCookieMgr()

    video = {"video_id": "vx", "title": "Tx"}
    config = {}
    all_valid = [
        {"id": "c1", "account_name": "A"},
        {"id": "c2", "account_name": "B"},
    ]

    ok = await app_mod.play_video_task_with_retry(
        video, {"id": "c1"}, config, sem, persist, cm, all_valid, brave_path="C:/fake/brave.exe"
    )

    assert ok is True
    # Ensure we tried original cookie through all retries, then fallback once
    assert calls == ["c1", "c1", "c1", "c2"]
