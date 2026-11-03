"""App assembly: settings check, DB init, error format, security headers, routers, /health, frontend serving."""
import logging
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import text

from app.core import errors
from app.core.config import get_settings
from app.infrastructure.db import get_engine, init_db, init_engine
from app.presentation.routes import auth, jobs

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("app")

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Content-Security-Policy": "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'",
}


def create_app() -> FastAPI:
    settings = get_settings()
    init_engine(settings.db_url)
    init_db(settings)

    app = FastAPI(title="service", version="0.1.0")
    errors.install(app)

    @app.middleware("http")
    async def headers_and_log(request: Request, call_next):
        t0 = time.perf_counter()
        response = await call_next(request)
        for k, v in SECURITY_HEADERS.items():
            response.headers.setdefault(k, v)
        log.info("%s %s %s %.0fms", request.method, request.url.path, response.status_code, (time.perf_counter() - t0) * 1000)
        return response

    @app.get("/health")
    def health():
        try:
            with get_engine().connect() as c:
                c.execute(text("SELECT 1"))
            return {"status": "ok", "db": True}
        except Exception:
            return JSONResponse({"status": "error", "db": False}, status_code=503)

    app.include_router(auth.router)
    app.include_router(jobs.router)

    dist = Path(settings.frontend_dist).resolve()

    @app.get("/{full_path:path}", include_in_schema=False)
    def frontend(full_path: str):
        if full_path.startswith("api/"):
            raise errors.AppError(404, "not_found", "없는 API입니다.")
        target = (dist / full_path).resolve()
        if full_path and target.is_file() and dist in target.parents:
            return FileResponse(target)
        index = dist / "index.html"
        if index.is_file():
            return FileResponse(index)
        return JSONResponse({"message": "frontend build not found. run: make build"}, status_code=200)

    return app


app = create_app()
