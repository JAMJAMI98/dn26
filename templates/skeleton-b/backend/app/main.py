"""App assembly (standard library): settings, DB init, error format, security headers, routes, /health, frontend files.

`App.handle(...)` is the single entry used by both the HTTP server and the tests.
"""
from __future__ import annotations

import logging
import mimetypes
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from app.core import errors
from app.core.config import Settings, get_settings
from app.infrastructure import db
from app.presentation.http import Request, Response, Router, parse_query
from app.presentation.routes import auth, jobs

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("app")

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Content-Security-Policy": "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'",
}
TYPES = {".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8",
         ".html": "text/html; charset=utf-8", ".svg": "image/svg+xml", ".json": "application/json; charset=utf-8"}
MAX_BODY = 5 * 1024 * 1024


class App:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        db.init(self.settings.db_path)
        db.init_db(self.settings)
        self.router = Router()
        self.router.add("GET", "/health", self.health)
        auth.register(self.router, self.settings)
        jobs.register(self.router, self.settings)
        self.frontend = Path(self.settings.frontend_dir).resolve()

    def health(self, req):
        ok = db.ping()
        return Response(200 if ok else 503, {"status": "ok" if ok else "error", "db": ok})

    def handle(self, method: str, target: str, headers: dict | None = None, body: bytes = b"") -> Response:
        t0 = time.perf_counter()
        parts = urlsplit(target)
        req = Request(method.upper(), parts.path, parse_query(parts.query),
                      {k.lower(): v for k, v in (headers or {}).items()}, body)
        try:
            handler, params = self.router.match(req.method, req.path)
            if handler:
                req.params = params
                res = handler(req)
            elif req.path.startswith("/api/"):
                raise errors.AppError(404, "not_found", "없는 API입니다.")
            elif req.method in ("GET", "HEAD"):
                res = self.static(req.path)
            else:
                raise errors.AppError(405, "method_not_allowed", "허용되지 않는 요청 방식입니다.")
        except errors.AppError as e:
            res = Response(e.status, errors.body(e.code, e.message, e.details))
        except Exception:  # keep internals out of the API
            log.exception("unhandled error")
            res = Response(500, errors.body("internal_error", "서버 오류가 발생했습니다."))
        for k, v in SECURITY_HEADERS.items():
            res.headers.setdefault(k, v)
        log.info("%s %s %s %.0fms", req.method, req.path, res.status, (time.perf_counter() - t0) * 1000)
        return res

    def static(self, path: str) -> Response:
        """Serve frontend files; unknown paths fall back to index.html (client-side routes like /admin)."""
        rel = path.lstrip("/")
        target = (self.frontend / rel).resolve()
        hidden = any(p.startswith(".") for p in Path(rel).parts)
        if rel and not hidden and target.is_file() and self.frontend in target.parents:
            ctype = TYPES.get(target.suffix) or mimetypes.guess_type(target.name)[0] or "application/octet-stream"
            return Response(200, raw=target.read_bytes(), content_type=ctype, headers={"Cache-Control": "no-cache"})
        index = self.frontend / "index.html"
        if index.is_file():
            return Response(200, raw=index.read_bytes(), content_type=TYPES[".html"], headers={"Cache-Control": "no-cache"})
        return Response(200, {"message": "frontend not found (FRONTEND_DIR)"})


def make_handler(app: App):
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def _serve(self):
            length = int(self.headers.get("Content-Length") or 0)
            if length > MAX_BODY:
                res = Response(413, errors.body("too_large", "요청이 너무 큽니다."))
            else:
                res = app.handle(self.command, self.path, dict(self.headers.items()), self.rfile.read(length) if length else b"")
            self.send_response(res.status)
            for k, v in res.headers.items():
                self.send_header(k, v)
            self.send_header("Content-Length", str(len(res.body)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(res.body)

        do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = do_HEAD = _serve

        def log_message(self, fmt, *args):  # App.handle already logs one line per request
            pass

    return Handler


def serve() -> None:
    app = App()
    s = app.settings
    server = ThreadingHTTPServer((s.host, s.port), make_handler(app))
    log.info("listening on http://%s:%s", s.host, s.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
