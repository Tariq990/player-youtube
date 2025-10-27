import sys
from pathlib import Path

import pytest

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from video_fetcher import VideoFetcher


@pytest.fixture()
def config_stub():
    # Deterministic config for tests
    return {
        'SKIP_SHORTS': True,
        'SKIP_LIVE': True,
        'MIN_VIDEO_DURATION': 60,
    }


def test_filters_shorts_and_min_duration(config_stub):
    vf = VideoFetcher(channel_url="https://example.com/@test")
    videos = [
        {"id": "v1", "title": "Long", "duration": 600, "url": "u1", "is_short": False, "is_live": False},
        {"id": "v2", "title": "Short", "duration": 30, "url": "u2", "is_short": True, "is_live": False},
        {"id": "v3", "title": "Edge60", "duration": 60, "url": "u3", "is_short": False, "is_live": False},
        {"id": "v4", "title": "Live", "duration": 0, "url": "u4", "is_short": False, "is_live": True},
    ]

    out = vf.filter_videos(videos, config_stub)
    ids = [v["id"] for v in out]

    # shorts and live filtered, min_duration applied
    assert "v2" not in ids  # short
    assert "v4" not in ids  # live
    assert set(ids) == {"v1", "v3"}


def test_sorting_by_upload_date_oldest_first(config_stub):
    vf = VideoFetcher(channel_url="https://example.com/@test")
    vids = [
        {"id": "old", "title": "Old", "duration": 300, "url": "o", "upload_date": "20240110"},
        {"id": "new", "title": "New", "duration": 300, "url": "n", "upload_date": "20240115"},
        {"id": "newest", "title": "Newest", "duration": 300, "url": "nn", "upload_date": "20240120"},
    ]

    out = vf.filter_videos(vids, config_stub)
    assert [v["id"] for v in out] == ["old", "new", "newest"]
