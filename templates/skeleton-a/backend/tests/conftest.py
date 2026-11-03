import os
import tempfile

_tmp = tempfile.mkdtemp()
os.environ.update({
    "DB_URL": f"sqlite:///{_tmp}/test.db",
    "RUNTIME_DIR": _tmp,
    "FRONTEND_DIST": f"{_tmp}/no-dist",
    "ADMIN_ID": "admin", "ADMIN_PASSWORD": "admin-pass",
    "USER_ID": "user", "USER_PASSWORD": "user-pass",
})

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


def login(client, uid, pw):
    r = client.post("/api/auth/login", json={"id": uid, "password": pw})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


@pytest.fixture
def admin_h(client):
    return login(client, "admin", "admin-pass")


@pytest.fixture
def user_h(client):
    return login(client, "user", "user-pass")
