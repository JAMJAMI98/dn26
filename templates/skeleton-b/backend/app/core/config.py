"""Settings from environment variables (.env at repo root or backend/). Standard library only. No secret values in code."""
import os
from dataclasses import dataclass, fields
from pathlib import Path


def _read_env_files() -> dict:
    values = {}
    for name in ("../.env", ".env"):
        p = Path(name)
        if not p.is_file():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            values.setdefault(k.strip().upper(), v.strip().strip('"').strip("'"))
    return values


@dataclass
class Settings:
    host: str = "0.0.0.0"
    port: int = 3000
    db_url: str = "sqlite:///./runtime/app.db"
    session_ttl_min: int = 480
    frontend_dir: str = "../frontend"
    runtime_dir: str = "./runtime"
    # initial accounts (roles: admin / user). Empty password -> generated at first start
    admin_id: str = "admin"
    admin_password: str = ""
    user_id: str = "user"
    user_password: str = ""

    @property
    def db_path(self) -> str:
        return self.db_url.replace("sqlite:///", "", 1)


def get_settings() -> Settings:
    """Environment variables win over .env files. Read on every call (tests change env before create_app)."""
    file_values = _read_env_files()
    kwargs = {}
    for f in fields(Settings):
        raw = os.environ.get(f.name.upper(), file_values.get(f.name.upper()))
        if raw is None:
            continue
        kwargs[f.name] = int(raw) if f.type in (int, "int") else raw
    return Settings(**kwargs)
