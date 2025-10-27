from pathlib import Path
import json
import pytest

from config_loader import load_config


def test_load_config_from_temp_file(tmp_path: Path):
    cfg_path = tmp_path / "config.json"
    logs_dir = tmp_path / "logs"
    data_dir = tmp_path / "data"

    cfg = {
        "CHANNEL_URL": "https://example.com/@ch",
        "MAX_WINDOWS": 2,
        "COOKIE_DB_PATH": str(data_dir / "cookies.json"),
        "SEEN_DB_PATH": str(data_dir / "seen.sqlite"),
        "LOG_PATH": str(logs_dir / "app.log"),
        "SKIP_SHORTS": True,
        "SKIP_LIVE": True,
        "MIN_VIDEO_DURATION": 60,
    }

    cfg_path.write_text(json.dumps(cfg), encoding="utf-8")

    c = load_config(str(cfg_path))

    # Required keys accessible
    assert c.get("CHANNEL_URL").startswith("https://example.com/")
    assert c.get("MAX_WINDOWS") == 2

    # Ensure directories auto-created
    assert (data_dir).exists()
    assert (logs_dir).exists()
    
    # Nested get should return default when missing
    assert c.get("RATE_LIMITING.MAX_VIDEOS_PER_DAY", 100) == 100


def test_invalid_or_missing_config(tmp_path: Path):
    # Missing file
    missing = tmp_path / "missing.json"
    with pytest.raises(FileNotFoundError):
        load_config(str(missing))

    # Invalid JSON
    bad = tmp_path / "bad.json"
    bad.write_text("{not json}", encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(str(bad))


def test_missing_required_fields(tmp_path: Path):
    cfg_path = tmp_path / "config.json"
    # Missing LOG_PATH and others
    cfg = {
        "CHANNEL_URL": "https://example.com/@ch",
        "MAX_WINDOWS": 2,
        "COOKIE_DB_PATH": str(tmp_path / "cookies.json"),
        # "SEEN_DB_PATH" missing
        # "LOG_PATH" missing
    }
    cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(str(cfg_path))
