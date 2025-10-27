import json
from types import SimpleNamespace

import pytest

from video_fetcher import VideoFetcher


@pytest.mark.asyncio
async def test_fetch_videos_skips_none_entries(monkeypatch):
    sample = {
        "entries": [None, {"id": "v1", "title": "T1", "duration": 61, "is_live": False, "upload_date": "20240101"}]
    }

    def fake_run(cmd, capture_output, text, timeout):
        return SimpleNamespace(returncode=0, stdout=json.dumps(sample), stderr="")

    import subprocess
    monkeypatch.setattr(subprocess, "run", fake_run)

    vf = VideoFetcher("https://example.com/@c")
    out = await vf.fetch_videos(max_videos=2)
    assert [v["video_id"] for v in out] == ["v1"]


@pytest.mark.asyncio
async def test_fetch_videos_generic_exception(monkeypatch):
    import subprocess
    def fake_run(*a, **k):
        raise RuntimeError("boom")
    monkeypatch.setattr(subprocess, "run", fake_run)
    vf = VideoFetcher("https://example.com")
    assert await vf.fetch_videos() == []
