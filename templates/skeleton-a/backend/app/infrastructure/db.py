"""DB engine/session, schema creation on empty DB, initial account seeding."""
import logging
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import Settings
from app.core.security import hash_password, new_password

log = logging.getLogger("app")


class Base(DeclarativeBase):
    pass


_engine = None
SessionLocal = sessionmaker(autoflush=False, expire_on_commit=False)


def init_engine(url: str):
    global _engine
    if url.startswith("sqlite:///"):
        path = url.replace("sqlite:///", "", 1)
        if path and path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
    args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    _engine = create_engine(url, connect_args=args, pool_pre_ping=True)
    SessionLocal.configure(bind=_engine)
    return _engine


def get_engine():
    return _engine


def init_db(settings: Settings) -> None:
    from app.infrastructure import models  # noqa: F401  (register tables)

    Base.metadata.create_all(_engine)
    _release_stale_jobs()
    _seed_users(settings)


def _release_stale_jobs() -> None:
    """A server restart kills running work: free the lock so the next request is not stuck at 409."""
    from app.infrastructure.models import Job

    with SessionLocal() as db:
        db.query(Job).filter(Job.status == "running").update({"status": "failed", "error": "서버 재시작으로 중단됨"})
        db.commit()


def _seed_users(settings: Settings) -> None:
    from app.infrastructure.models import User

    generated = []
    with SessionLocal() as db:
        for uid, role, pw in ((settings.admin_id, "admin", settings.admin_password),
                              (settings.user_id, "user", settings.user_password)):
            if db.get(User, uid):
                continue
            if not pw:
                pw = new_password()
                generated.append(f"{role}\t{uid}\t{pw}")
            db.add(User(id=uid, role=role, pw_hash=hash_password(pw)))
        db.commit()
    if generated:
        out = Path(settings.runtime_dir) / "initial-credentials.txt"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("role\tid\tpassword\n" + "\n".join(generated) + "\n", encoding="utf-8")
        os.chmod(out, 0o600)
        log.warning("초기 비밀번호가 환경변수에 없어 생성했습니다: %s 파일을 확인하세요.", out)
