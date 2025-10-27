import json
from types import SimpleNamespace

import pytest

from video_fetcher import VideoFetcher


def test_filter_videos_basic():
    vf = VideoFetcher("https://example.com/@c")
    cfg = {"SKIP_SHORTS": True, "SKIP_LIVE": True, "MIN_VIDEO_DURATION": 60}
    vids = [
        {"title": "short", "duration": 20, "is_short": True, "is_live": False},
        {"title": "live", "duration": 0, "is_short": False, "is_live": True},
        {"title": "ok1", "duration": 120, "is_short": False, "is_live": False, "upload_date": "20240101"},
        {"title": "ok2", "duration": 60, "is_short": False, "is_live": False, "upload_date": "20240102"},
    ]
    out = vf.filter_videos(vids, cfg)
    assert [v["title"] for v in out] == ["ok1", "ok2"]


@pytest.mark.asyncio
async def test_fetch_videos_with_mock(monkeypatch):
    # Mock subprocess.run to return a fake yt-dlp JSON
    sample = {
        "entries": [
            {"id": "v1", "title": "T1", "duration": 100, "is_live": False, "upload_date": "20240101"},
            {"id": "v2", "title": "T2", "duration": 30, "is_live": False, "upload_date": "20240102"},
        ]
    }

    def fake_run(cmd, capture_output, text, timeout):
        return SimpleNamespace(returncode=0, stdout=json.dumps(sample), stderr="")

    import subprocess
    monkeypatch.setattr(subprocess, "run", fake_run)

    vf = VideoFetcher("https://example.com/@c")
    got = await vf.fetch_videos(max_videos=5)
    assert len(got) == 2
    assert got[0]["video_id"] == "v1"
    assert got[1]["is_short"] is True  # duration 30 -> short per implementation


@pytest.mark.asyncio
async def test_convenience_fetch_channel_videos(monkeypatch):
    from video_fetcher import fetch_channel_videos

    # Patch fetch_videos to return fixed list
    async def fake_fetch(self, max_videos=50):
        return [
            {"video_id": "a", "title": "A", "duration": 120, "is_live": False, "upload_date": "20240101"},
            {"video_id": "b", "title": "B", "duration": 20, "is_live": False, "upload_date": "20240102", "is_short": True},
        ]

    monkeypatch.setattr(VideoFetcher, "fetch_videos", fake_fetch)

    cfg = {"SKIP_SHORTS": True, "SKIP_LIVE": True, "MIN_VIDEO_DURATION": 60}
    out = await fetch_channel_videos("https://example.com/@c", cfg, max_videos=10)
    assert [v["video_id"] for v in out] == ["a"]


@pytest.mark.asyncio
async def test_fetch_videos_error_nonzero(monkeypatch):
    import subprocess
    def fake_run(*a, **k):
        class R: returncode=1; stdout=""; stderr="boom"
        return R()
    monkeypatch.setattr(subprocess, "run", fake_run)
    vf = VideoFetcher("https://example.com")
    assert await vf.fetch_videos() == []


@pytest.mark.asyncio
async def test_fetch_videos_json_error(monkeypatch):
    import subprocess
    def fake_run(*a, **k):
        class R: returncode=0; stdout="not json"; stderr=""
        return R()
    monkeypatch.setattr(subprocess, "run", fake_run)
    vf = VideoFetcher("https://example.com")
    assert await vf.fetch_videos() == []


@pytest.mark.asyncio
async def test_fetch_videos_timeout(monkeypatch):
    import subprocess
    class TE(Exception): pass
    monkeypatch.setattr(subprocess, "TimeoutExpired", TimeoutError)
    def fake_run(*a, **k):
        raise TimeoutError()
    monkeypatch.setattr(subprocess, "run", fake_run)
    vf = VideoFetcher("https://example.com")
    assert await vf.fetch_videos() == []
