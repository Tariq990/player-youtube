import json
from types import SimpleNamespace

import pytest

from video_fetcher import VideoFetcher


@pytest.mark.asyncio
async def test_fetch_videos_flattens_nested_playlists(monkeypatch):
    sample = {
        "entries": [
            {
                "_type": "playlist",
                "entries": [
                    {"id": "v1", "title": "T1", "duration": 100, "is_live": False, "upload_date": "20240101"},
                    {"id": "v2", "title": "T2", "duration": 30, "is_live": False, "upload_date": "20240102"},
                ],
            }
        ]
    }

    def fake_run(cmd, capture_output, text, timeout):
        return SimpleNamespace(returncode=0, stdout=json.dumps(sample), stderr="")

    import subprocess
    monkeypatch.setattr(subprocess, "run", fake_run)

    vf = VideoFetcher("https://example.com/@c")
    out = await vf.fetch_videos(max_videos=3)
    assert [v["video_id"] for v in out] == ["v1", "v2"]
    assert out[1]["is_short"] is True


@pytest.mark.asyncio
async def test_fetch_videos_skips_playlist_entries(monkeypatch):
    sample = {
        "entries": [
            {"id": "x", "title": "X", "duration": 61, "is_live": False, "upload_date": "20240101"},
            {"_type": "playlist", "entries": []},
        ]
    }

    def fake_run(cmd, capture_output, text, timeout):
        return SimpleNamespace(returncode=0, stdout=json.dumps(sample), stderr="")

    import subprocess
    monkeypatch.setattr(subprocess, "run", fake_run)

    vf = VideoFetcher("https://example.com/channel")
    out = await vf.fetch_videos(max_videos=2)
    assert [v["title"] for v in out] == ["X"]


def test_filter_videos_missing_upload_date_and_skip_shorts_false():
    vf = VideoFetcher("u")
    vids = [
        {"title": "s", "duration": 10, "is_short": True, "is_live": False},
        {"title": "n", "duration": 10, "is_short": False, "is_live": False},
        {"title": "ok", "duration": 100, "is_short": True, "is_live": False},
    ]
    cfg = {"SKIP_SHORTS": False, "SKIP_LIVE": True, "MIN_VIDEO_DURATION": 60}
    out = vf.filter_videos(vids, cfg)
    # Only the 100s video passes min duration, upload_date missing should not crash
    assert [v["title"] for v in out] == ["ok"]


def test_fetch_videos_channel_url_already_has_videos(monkeypatch):
    captured = {}
    def fake_run(cmd, capture_output, text, timeout):
        # Ensure last arg ends with /videos and not duplicated
        captured['arg'] = cmd[-1]
        sample = {"entries": []}
        return SimpleNamespace(returncode=0, stdout=json.dumps(sample), stderr="")

    import subprocess
    monkeypatch.setattr(subprocess, "run", fake_run)

    url = "https://example.com/@c/videos"
    vf = VideoFetcher(url)
    _ = vf.fetch_videos(max_videos=1)
    assert captured['arg'].endswith('/videos') and captured['arg'].count('/videos') == 1