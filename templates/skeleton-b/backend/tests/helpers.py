"""Test setup without third-party packages: temp DB/env, an in-process client calling App.handle."""
import json
import os
import tempfile
from pathlib import Path

_tmp = tempfile.mkdtemp()
_front = Path(_tmp) / "front"
(_front / "src").mkdir(parents=True)
(_front / "index.html").write_text("<!doctype html><title>t</title>", encoding="utf-8")
(_front / "src" / "main.js").write_text("export {};", encoding="utf-8")
os.environ.update({
    "DB_URL": f"sqlite:///{_tmp}/test.db",
    "RUNTIME_DIR": _tmp,
    "FRONTEND_DIR": str(_front),
    "ADMIN_ID": "admin", "ADMIN_PASSWORD": "admin-pass",
    "USER_ID": "user", "USER_PASSWORD": "user-pass",
})

from app.main import App  # noqa: E402


class Res:
    def __init__(self, r):
        self.status_code, self.headers, self.content = r.status, {k.lower(): v for k, v in r.headers.items()}, r.body

    def json(self):
        return json.loads(self.content.decode("utf-8"))


class Client:
    def __init__(self, app):
        self.app = app

    def request(self, method, path, json_body=None, headers=None):
        h = dict(headers or {})
        body = b""
        if json_body is not None:
            body = json.dumps(json_body).encode("utf-8")
            h["Content-Type"] = "application/json"
        return Res(self.app.handle(method, path, h, body))

    def get(self, path, **kw):
        return self.request("GET", path, **kw)

    def post(self, path, json=None, headers=None):
        return self.request("POST", path, json_body=json, headers=headers)


client = Client(App())


def login(uid, pw):
    r = client.post("/api/auth/login", json={"id": uid, "password": pw})
    assert r.status_code == 200, r.content
    return {"Authorization": f"Bearer {r.json()['token']}"}
