def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["db"] is True
    assert r.headers["x-content-type-options"] == "nosniff"


def test_login_wrong_password(client):
    r = client.post("/api/auth/login", json={"id": "admin", "password": "nope"})
    assert r.status_code == 401 and r.json()["code"] == "invalid_credentials"


def test_me_requires_token(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401 and r.json()["code"] == "unauthorized"


def test_me_with_bearer_no_cookie(client, user_h):
    r = client.get("/api/auth/me", headers=user_h)
    assert r.status_code == 200 and r.json() == {"user_id": "user", "role": "user"}


def test_role_guard(client, user_h):
    r = client.post("/api/jobs/example", headers=user_h)
    assert r.status_code == 403 and r.json()["code"] == "forbidden"


def test_logout_invalidates(client):
    from tests.conftest import login
    h = login(client, "user", "user-pass")
    assert client.post("/api/auth/logout", headers=h).status_code == 204
    assert client.get("/api/auth/me", headers=h).status_code == 401


def test_validation_error_shape(client):
    r = client.post("/api/auth/login", json={"id": ""})
    assert r.status_code == 422 and r.json()["code"] == "invalid_input" and r.json()["details"]


def test_unknown_api_404(client):
    assert client.get("/api/nope").status_code == 404
