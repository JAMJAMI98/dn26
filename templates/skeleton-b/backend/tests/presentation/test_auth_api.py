import unittest

from tests.helpers import client, login


class AuthApiTest(unittest.TestCase):
    def test_health(self):
        r = client.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assertIs(r.json()["db"], True)
        self.assertEqual(r.headers["x-content-type-options"], "nosniff")

    def test_login_wrong_password(self):
        r = client.post("/api/auth/login", json={"id": "admin", "password": "nope"})
        self.assertEqual((r.status_code, r.json()["code"]), (401, "invalid_credentials"))

    def test_me_requires_token(self):
        r = client.get("/api/auth/me")
        self.assertEqual((r.status_code, r.json()["code"]), (401, "unauthorized"))

    def test_me_with_bearer_no_cookie(self):
        r = client.get("/api/auth/me", headers=login("user", "user-pass"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"user_id": "user", "role": "user"})

    def test_role_guard(self):
        r = client.post("/api/jobs/example", headers=login("user", "user-pass"))
        self.assertEqual((r.status_code, r.json()["code"]), (403, "forbidden"))

    def test_logout_invalidates(self):
        h = login("user", "user-pass")
        self.assertEqual(client.post("/api/auth/logout", headers=h).status_code, 204)
        self.assertEqual(client.get("/api/auth/me", headers=h).status_code, 401)

    def test_validation_error_shape(self):
        r = client.post("/api/auth/login", json={"id": ""})
        self.assertEqual((r.status_code, r.json()["code"]), (422, "invalid_input"))
        self.assertTrue(r.json()["details"])

    def test_broken_json_is_422(self):
        r = client.app.handle("POST", "/api/auth/login", {"Content-Type": "application/json"}, b"{oops")
        self.assertEqual(r.status, 422)

    def test_unknown_api_404(self):
        self.assertEqual(client.get("/api/nope").status_code, 404)


class StaticFilesTest(unittest.TestCase):
    def test_spa_fallback_and_assets(self):
        self.assertIn(b"<title>t</title>", client.get("/admin").content)
        r = client.get("/src/main.js")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.headers["content-type"].startswith("text/javascript"))

    def test_no_path_escape(self):
        r = client.get("/../../etc/passwd")
        self.assertNotIn(b"root:", r.content)


if __name__ == "__main__":
    unittest.main()
