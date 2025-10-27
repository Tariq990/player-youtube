import os
from pathlib import Path
from datetime import datetime, timedelta

import pytest

from cookie_manager import CookieManager


@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    monkeypatch.delenv("ENCRYPTION_KEY", raising=False)


def test_persist_and_load_with_encryption(tmp_path: Path, monkeypatch):
    # Set encryption key
    monkeypatch.setenv("ENCRYPTION_KEY", "WmR1Qm1hV2J5QnR4R2x1U2R2Qm1hV2J5QnR4R2x1U2Q=")  # dummy base64 44 chars

    db_path = tmp_path / "cookies.json"
    cm = CookieManager(str(db_path))

    cookie = {
        "id": "c1",
        "name": "LOGIN_INFO",
        "value": "secret-token",
        "status": "active",
    }
    cm.add_cookie(cookie)
    cm.persist()

    # Reload and ensure value decrypted transparently
    cm2 = CookieManager(str(db_path))
    actives = cm2.get_active_cookies()
    assert len(actives) == 1
    assert actives[0]["value"] == "secret-token"


def test_rotation_and_status_changes(tmp_path: Path):
    db_path = tmp_path / "cookies.json"
    cm = CookieManager(str(db_path))

    cm.cookies = [
        {"id": "a", "status": "active", "usage_count": 0},
        {"id": "b", "status": "active", "usage_count": 5},
        {"id": "c", "status": "invalid"},
    ]

    # round_robin
    cookie1 = cm.rotate_cookie()
    assert cookie1 is not None and cookie1["id"] == "a"
    cookie2 = cm.rotate_cookie()
    assert cookie2 is not None and cookie2["id"] == "b"
    cookie3 = cm.rotate_cookie()
    assert cookie3 is not None and cookie3["id"] == "a"  # wraps skipping invalid

    # least_used (among actives a(0), b(5)) -> a
    cookie4 = cm.rotate_cookie(policy="least_used")
    assert cookie4 is not None and cookie4["id"] == "a"

    # mark used increments usage_count
    cm.mark_used("a")
    assert next(c for c in cm.cookies if c["id"] == "a")["usage_count"] >= 1

    # mark invalid and delete
    cm.mark_invalid("a")
    assert next(c for c in cm.cookies if c["id"] == "a")["status"] == "invalid"
    cm.delete_cookie("a")
    assert all(c["id"] != "a" for c in cm.cookies)


def test_quarantine_and_summary(tmp_path: Path):
    db_path = tmp_path / "cookies.json"
    cm = CookieManager(str(db_path))
    cm.cookies = [
        {"id": "x", "status": "active"},
        {"id": "y", "status": "invalid"},
    ]

    cm.quarantine("x", duration=60)
    x = next(c for c in cm.cookies if c["id"] == "x")
    assert x["status"] == "quarantine"
    assert "quarantine_until" in x

    summary = cm.get_cookie_summary()
    assert summary["total"] == 2
    assert summary["active"] == 0
    assert summary["invalid"] == 1
    assert summary["quarantine"] == 1


def test_rotation_without_active_returns_none(tmp_path: Path):
    cm = CookieManager(str(tmp_path / "cookies.json"))
    cm.cookies = [{"id": "x", "status": "invalid"}]
    assert cm.rotate_cookie() is None


def test_no_cookie_file_yields_empty(monkeypatch, tmp_path: Path):
    # Ensure no encryption
    monkeypatch.delenv("ENCRYPTION_KEY", raising=False)
    db_path = tmp_path / "missing.json"
    cm = CookieManager(str(db_path))
    assert cm.get_active_cookies() == []
