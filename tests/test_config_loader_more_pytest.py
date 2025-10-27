import json
from pathlib import Path

from config_loader import Config


def test_config_getitem_and_contains(tmp_path: Path):
    cfg_path = tmp_path / "c.json"
    data = {
        "CHANNEL_URL": "u",
        "MAX_WINDOWS": 1,
        "COOKIE_DB_PATH": str(tmp_path / "cookies.json"),
        "SEEN_DB_PATH": str(tmp_path / "seen.sqlite"),
        "LOG_PATH": str(tmp_path / "app.log"),
        "NEST": {"X": 1}
    }
    cfg_path.write_text(json.dumps(data), encoding="utf-8")
    cfg = Config(str(cfg_path))
    # __getitem__ uses get
    assert cfg["NEST.X"] == 1
    # __contains__ uses get != None semantics
    assert ("NEST.X" in cfg) is True
    assert ("NEST.Y" in cfg) is False