#!/usr/bin/env python3
"""Minimal web skeleton (standard library only). Copy, then replace compute().

run:   PORT=8000 python3 app.py        (binds 0.0.0.0 for the IDE Browser preview)
test:  python3 test_app.py

Design choices (explainable):
- No framework: zero install risk. Swap to FastAPI only if it is already installed and needed.
- Calculation lives in compute() (fixed code, testable); HTTP layer only routes and serializes.
- Every request is isolated by try/except: one bad input returns a JSON error, the server keeps running.
"""
import json, os
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))


def compute(params):
    """Replace with the task logic. Keep it pure: input dict -> output dict."""
    x = float(params.get("x", ["0"])[0])
    return {"input": x, "double": x * 2}


class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code); self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)

    def do_GET(self):
        u = urlparse(self.path)
        try:
            if u.path in ("/", "/index.html"):
                with open(os.path.join(HERE, "static", "index.html"), "rb") as f:
                    return self._send(200, f.read(), "text/html; charset=utf-8")
            if u.path == "/api/health":
                return self._send(200, {"ok": True})
            if u.path == "/api/compute":
                return self._send(200, compute(parse_qs(u.query)))
            return self._send(404, {"error": "not found"})
        except ValueError as e:
            return self._send(400, {"error": f"bad input: {e}"})
        except Exception as e:  # isolate failures per request
            return self._send(500, {"error": type(e).__name__})

    def log_message(self, fmt, *args):
        pass  # keep terminal quiet; add logging if needed


def serve(port=None):
    port = int(port or os.environ.get("PORT", "8000"))
    srv = ThreadingHTTPServer(("0.0.0.0", port), H)
    return srv


if __name__ == "__main__":
    s = serve()
    print(f"serving on 0.0.0.0:{s.server_address[1]}  -> Browser tool: PORT {s.server_address[1]}, URL /")
    s.serve_forever()
