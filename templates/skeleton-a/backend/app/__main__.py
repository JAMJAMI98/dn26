"""Run: cd backend && python -m app  (binds 0.0.0.0:PORT, default 3000)."""
import uvicorn

from app.core.config import get_settings


def main() -> None:
    s = get_settings()
    uvicorn.run("app.main:app", host=s.host, port=s.port)


if __name__ == "__main__":
    main()
