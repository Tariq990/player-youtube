import pytest
from pathlib import Path

from persistence import Persistence


def test_mark_and_check_seen(tmp_path: Path):
    db_path = tmp_path / "seen.sqlite"
    db = Persistence(str(db_path))

    assert db.get_seen_count() == 0

    db.mark_seen("vid1", title="Title 1", duration=120)
    assert db.is_seen("vid1") is True
    assert db.get_seen_count() == 1


def test_get_unseen_videos(tmp_path: Path):
    db_path = tmp_path / "seen.sqlite"
    db = Persistence(str(db_path))

    db.mark_seen("seen_video")

    videos = [
        {"video_id": "seen_video", "title": "A"},
        {"video_id": "new_video", "title": "B"},
    ]

    unseen = db.get_unseen_videos(videos)
    assert [v["video_id"] for v in unseen] == ["new_video"]


def test_clear_all(tmp_path: Path):
    db = Persistence(str(tmp_path / "seen.sqlite"))
    db.mark_seen("a")
    db.mark_seen("b")
    assert db.get_seen_count() >= 2
    db.clear_all()
    assert db.get_seen_count() == 0
