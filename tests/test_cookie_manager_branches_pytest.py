import json
import os
from pathlib import Path
import pytest

from cookie_manager import CookieManager


def test_load_missing_file_returns_empty(tmp_path: Path, monkeypatch):
    cm = CookieManager(str(tmp_path / "cookies.json"))
    assert cm.cookies == []


def test_load_invalid_json_logs_and_empty(tmp_path: Path, monkeypatch):
    p = tmp_path / "cookies.json"
    p.write_text("{ invalid json", encoding="utf-8")
    cm = CookieManager(str(p))
    assert cm.cookies == []


def test_persist_encryption_enabled(monkeypatch, tmp_path: Path):
    # Provide a valid key
    monkeypatch.setenv("ENCRYPTION_KEY", """MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDE=""")
    p = tmp_path / "cookies.json"
    cm = CookieManager(str(p))
    cm.cookies = [{"id": "c1", "value": "secret", "status": "active"}]
    cm.persist()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data[0]["encrypted"] is True
    assert data[0]["value"] != "secret"


def test_persist_handles_io_error(monkeypatch, tmp_path: Path):
    p = tmp_path / "cookies.json"
    cm = CookieManager(str(p))
    cm.cookies = [{"id": "c1", "value": "v"}]

    def raising_open(*a, **k):
        raise OSError("disk full")

    # Patch builtins.open to simulate IO error during persist
    monkeypatch.setattr("builtins.open", raising_open)
    cm.persist()  # Should not raise despite open() failing


def test_init_invalid_encryption_key_disables(monkeypatch, tmp_path: Path):
    monkeypatch.delenv("ENCRYPTION_KEY", raising=False)
    monkeypatch.setenv("ENCRYPTION_KEY", "invalid-key")
    cm = CookieManager(str(tmp_path / "cookies.json"))
    # Encryption should be disabled due to invalid key
    assert getattr(cm, "encryption_enabled", False) is False


def test_load_decrypt_success_and_failure(monkeypatch, tmp_path: Path):
    # Valid key
    key = "MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDE="
    monkeypatch.setenv("ENCRYPTION_KEY", key)

    # Build an encrypted cookie value
    from cryptography.fernet import Fernet
    cipher = Fernet(key.encode())
    enc = cipher.encrypt(b"tok").decode()

    p = tmp_path / "cookies.json"
    p.write_text(json.dumps([{ "id": "c1", "name": "LOGIN_INFO", "value": enc, "encrypted": True }]), encoding="utf-8")

    cm = CookieManager(str(p))
    # Should decrypt on load
    assert cm.cookies and cm.cookies[0]["value"] == "tok" and cm.cookies[0].get("encrypted") is False

    # Now write invalid encrypted value to trigger decrypt error path
    p.write_text(json.dumps([{ "id": "c2", "name": "LOGIN_INFO", "value": "not-a-token", "encrypted": True }]), encoding="utf-8")
    cm2 = CookieManager(str(p))
    # Should not raise; error logged internally and cookie remains with same value/encrypted flag may persist
    assert isinstance(cm2.cookies, list)


def test_add_cookie_duplicate_branches(tmp_path: Path):
    p = tmp_path / "cookies.json"
    p.write_text("[]", encoding="utf-8")
    cm = CookieManager(str(p))
    cm.add_cookie({"id": "x", "value": "v"})
    # Duplicate without overwrite -> warning path, no change in length
    cm.add_cookie({"id": "x", "value": "v2"}, overwrite=False)
    assert len(cm.cookies) == 1 and cm.cookies[0]["value"] == "v"
    # With overwrite -> replaced
    cm.add_cookie({"id": "x", "value": "v3"}, overwrite=True)
    assert len(cm.cookies) == 1 and cm.cookies[0]["value"] == "v3"


def test_rotate_policies_and_no_active(tmp_path: Path):
    p = tmp_path / "cookies.json"
    p.write_text("[]", encoding="utf-8")
    cm = CookieManager(str(p))
    # No active
    assert cm.rotate_cookie() is None

    # Add cookies
    cm.cookies = [
        {"id": "a", "status": "active", "usage_count": 2},
        {"id": "b", "status": "active", "usage_count": 0},
    ]
    # round_robin
    cookie1 = cm.rotate_cookie()
    assert cookie1 is not None and cookie1["id"] == "a"
    cookie2 = cm.rotate_cookie()
    assert cookie2 is not None and cookie2["id"] == "b"
    cookie3 = cm.rotate_cookie()
    assert cookie3 is not None and cookie3["id"] == "a"
    # least_used
    cookie4 = cm.rotate_cookie(policy="least_used")
    assert cookie4 is not None and cookie4["id"] == "b"
    # failover/other
    cookie5 = cm.rotate_cookie(policy="other")
    assert cookie5 is not None and cookie5["id"] == "a"


def test_mark_invalid_delete_quarantine_and_summary(tmp_path: Path):
    p = tmp_path / "cookies.json"
    p.write_text("[]", encoding="utf-8")
    cm = CookieManager(str(p))
    cm.cookies = [
        {"id": "a", "status": "active"},
        {"id": "b", "status": "active"},
    ]
    cm.mark_invalid("a")
    assert [c["status"] for c in cm.cookies] == ["invalid", "active"]
    cm.quarantine("b", duration=1)
    assert cm.cookies[1]["status"] == "quarantine"
    cm.delete_cookie("a")
    assert [c["id"] for c in cm.cookies] == ["b"]
    s = cm.get_cookie_summary()
    assert s["total"] == 1 and s["quarantine"] == 1 and s["invalid"] == 0