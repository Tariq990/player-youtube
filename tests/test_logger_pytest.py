from pathlib import Path

from logger_config import setup_logging, get_logger


def test_logger_writes_to_file(tmp_path: Path):
    log_file = tmp_path / "app.log"
    logger = setup_logging(log_path=str(log_file), console_output=False)

    logger.info("hello")
    logger.error("world")

    assert log_file.exists()
    assert log_file.stat().st_size > 0


def test_get_logger_namespace():
    # Ensure namespacing works and logger is retrievable
    lg = get_logger("unit.test")
    lg.info("ping")
    assert lg.name.endswith("unit.test")


def test_logger_console_enabled(tmp_path: Path):
    # Ensure console handler branch executes
    log_file = tmp_path / "app.log"
    logger = setup_logging(log_path=str(log_file), console_output=True)
    logger.info("console on")
    assert any(h.__class__.__name__ == 'StreamHandler' for h in logger.handlers)
