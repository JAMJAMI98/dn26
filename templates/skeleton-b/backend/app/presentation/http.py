"""Tiny router on the standard library: Request, path params, JSON responses. Routes register handlers here."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from urllib.parse import parse_qs

from app.core.errors import AppError


@dataclass
class Request:
    method: str
    path: str
    query: dict
    headers: dict  # lower-case keys
    raw_body: bytes = b""
    params: dict = field(default_factory=dict)
    user: dict | None = None

    def json(self):
        if not self.raw_body:
            return {}
        try:
            return json.loads(self.raw_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise AppError(422, "invalid_input", "JSON 형식이 올바르지 않습니다.")

    def q(self, name: str, default=None):
        return self.query.get(name, [default])[0]


class Response:
    def __init__(self, status: int = 200, data=None, headers: dict | None = None, raw: bytes | None = None,
                 content_type: str = "application/json; charset=utf-8"):
        self.status, self.headers = status, dict(headers or {})
        if raw is not None:
            self.body = raw
        elif data is None or status == 204:
            self.body = b""
        else:
            self.body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        if self.body:
            self.headers.setdefault("Content-Type", content_type)


class Router:
    def __init__(self):
        self.routes = []  # (method, compiled regex, handler)

    def add(self, method: str, pattern: str, handler):
        """pattern like /api/jobs/{job_id:int} or /api/items/{name}"""
        def conv(m):
            name, typ = m.group(1), m.group(2)
            return rf"(?P<{name}>\d+)" if typ == "int" else rf"(?P<{name}>[^/]+)"
        rx = re.compile("^" + re.sub(r"\{(\w+)(?::(\w+))?\}", conv, pattern) + "$")
        self.routes.append((method.upper(), rx, handler, "int" in pattern))

    def route(self, method: str, pattern: str):
        def deco(fn):
            self.add(method, pattern, fn)
            return fn
        return deco

    def match(self, method: str, path: str):
        allowed = False
        for m, rx, handler, _ in self.routes:
            hit = rx.match(path)
            if hit:
                if m == method:
                    params = {k: int(v) if v.isdigit() else v for k, v in hit.groupdict().items()}
                    return handler, params
                allowed = True
        if allowed:
            raise AppError(405, "method_not_allowed", "허용되지 않는 요청 방식입니다.")
        return None, None


def parse_query(qs: str) -> dict:
    return parse_qs(qs, keep_blank_values=True)
