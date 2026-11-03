"""Settings from environment variables (.env at repo root or backend/). No secret values in code."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    host: str = "0.0.0.0"
    port: int = 3000
    db_url: str = "sqlite:///./runtime/app.db"
    session_ttl_min: int = 480
    frontend_dist: str = "../frontend/dist"
    runtime_dir: str = "./runtime"

    # initial accounts (roles: admin / user). Empty password -> generated at first start
    admin_id: str = "admin"
    admin_password: str = ""
    user_id: str = "user"
    user_password: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
