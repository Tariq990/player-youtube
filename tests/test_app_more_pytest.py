import time
import pytest

import app as app_mod


class FakeElement:
    pass


class FakeDriver:
    def __init__(self, logged_in: bool):
        self.logged_in = logged_in
        self.cookies_added = []
        self.get_calls = []
        self.quit_called = False

    def get(self, url):
        self.get_calls.append(url)

    def add_cookie(self, cookie_dict):
        self.cookies_added.append(cookie_dict)

    def find_element(self, by=None, value=None):
        # Simulate avatar presence when logged_in, otherwise simulate Sign in
        if self.logged_in:
            if value and (value.startswith("#avatar-btn") or value.startswith("button") or value.startswith("ytd-topbar") or value.startswith("#buttons")):
                return FakeElement()
            raise Exception("not found")
        else:
            # When not logged in, return a sign-in element for XPATH query
            if value and "Sign in" in value:
                return FakeElement()
            raise Exception("not found")

    def execute_script(self, *_a, **_k):
        return None

    def quit(self):
        self.quit_called = True


def test_test_cookie_login_success(monkeypatch):
    # Use fake driver and skip real sleeps
    monkeypatch.setattr(app_mod, "create_driver", lambda *a, **k: FakeDriver(logged_in=True))
    monkeypatch.setattr(time, "sleep", lambda *_a, **_k: None)

    cookie_data = {
        "user_agent": "ua",
        "cookies": [
            {"name": "LOGIN_INFO", "value": "v", "domain": ".youtube.com", "path": "/", "secure": False}
        ],
    }

    ok = app_mod.test_cookie_login(cookie_data, brave_path="C:/fake/brave.exe")
    assert ok is True


def test_test_cookie_login_failure(monkeypatch):
    monkeypatch.setattr(app_mod, "create_driver", lambda *a, **k: FakeDriver(logged_in=False))
    monkeypatch.setattr(time, "sleep", lambda *_a, **_k: None)

    cookie_data = {"cookies": []}
    ok = app_mod.test_cookie_login(cookie_data, brave_path="C:/fake/brave.exe")
    assert ok is False


def test_test_and_filter_cookies_filters_and_deletes(monkeypatch):
    # Mock test_cookie_login to accept only first and third
    outcomes = [True, False, True]
    def fake_test_cookie_login(data, brave_path):
        idx = data.get("idx")
        return outcomes[idx]
    monkeypatch.setattr(app_mod, "test_cookie_login", fake_test_cookie_login)

    # Fake CookieManager
    class FakeCookieMgr:
        def __init__(self, *_a, **_k):
            self.deleted = []
            self.persist_called = 0
        def delete_cookie(self, cid):
            self.deleted.append(cid)
        def persist(self):
            self.persist_called += 1

    monkeypatch.setattr(app_mod, "CookieManager", FakeCookieMgr)

    cookies = [
        {"id": "c1", "idx": 0, "account_name": "a"},
        {"id": "c2", "idx": 1, "account_name": "b"},
        {"id": "c3", "idx": 2, "account_name": "c"},
    ]

    valid = app_mod.test_and_filter_cookies(cookies, brave_path="C:/fake/brave.exe")
    assert [c["id"] for c in valid] == ["c1", "c3"]