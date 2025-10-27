from logger_config import get_logger


def test_get_logger_default_root():
    lg = get_logger()
    # Should return base namespace logger
    assert lg.name == "youtube_player"
