import os
from pathlib import Path

import pytest

from app import get_brave_path, create_driver


def test_get_brave_path_env(monkeypatch, tmp_path: Path):
    fake = tmp_path / "brave.exe"
    fake.write_text("")
    monkeypatch.setenv("BRAVE_BINARY_PATH", str(fake))
    assert get_brave_path() == str(fake)


def test_create_driver_mocks(monkeypatch):
    # Mock webdriver.Chrome to avoid launching browser
    class FakeDriver:
        def execute_script(self, *a, **kw):
            return None
        def quit(self):
            pass

    import selenium.webdriver
    monkeypatch.setattr(selenium.webdriver, "Chrome", lambda *a, **k: FakeDriver())

    driver = create_driver(brave_path="C:/fake/brave.exe", user_agent="ua", headless=True)
    assert hasattr(driver, "execute_script")
    driver.quit()