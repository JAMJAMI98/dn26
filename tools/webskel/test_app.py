"""Black-box HTTP tests for app.py (standard library unittest). run: python3 test_app.py"""
import json, threading, unittest, urllib.request, urllib.error
import app


class T(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = app.serve(0)  # free port
        cls.base = f"http://127.0.0.1:{cls.srv.server_address[1]}"
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def get(self, path):
        try:
            with urllib.request.urlopen(self.base + path, timeout=5) as r:
                return r.status, r.read().decode()
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode()

    def test_page(self):
        code, body = self.get("/")
        self.assertEqual(code, 200); self.assertIn("<html", body)

    def test_normal(self):
        code, body = self.get("/api/compute?x=21")
        self.assertEqual(code, 200); self.assertEqual(json.loads(body)["double"], 42)

    def test_bad_input_does_not_kill_server(self):
        code, _ = self.get("/api/compute?x=abc")
        self.assertEqual(code, 400)
        self.assertEqual(self.get("/api/health")[0], 200)

    def test_empty_input(self):
        self.assertEqual(self.get("/api/compute")[0], 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)
