"""SQLite (standard library): connection per use, schema creation on empty DB, initial account seeding."""
import logging
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from app.core.config import Settings
from app.core.security import hash_password, new_password

log = logging.getLogger("app")
_db_path = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, role TEXT NOT NULL, pw_hash TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS auth_sessions (token TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id), expires_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, status TEXT NOT NULL,
  started_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')), finished_at TEXT, result TEXT, error TEXT);
"""


def init(path: str) -> None:
    global _db_path
    if path and path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    _db_path = path


@contextmanager
def connect():
    """`with connect() as c:` -> commit on success, rollback on error, always close."""
    conn = sqlite3.connect(_db_path, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def ping() -> bool:
    try:
        with connect() as c:
            c.execute("SELECT 1")
        return True
    except sqlite3.Error:
        return False


def init_db(settings: Settings) -> None:
    with connect() as c:
        c.executescript(SCHEMA)
        # a server restart kills running work: free the lock so the next request is not stuck at 409
        c.execute("UPDATE jobs SET status = 'failed', error = '서버 재시작으로 중단됨' WHERE status = 'running'")
    _seed_users(settings)


def _seed_users(settings: Settings) -> None:
    generated = []
    with connect() as c:
        for uid, role, pw in ((settings.admin_id, "admin", settings.admin_password),
                              (settings.user_id, "user", settings.user_password)):
            if c.execute("SELECT 1 FROM users WHERE id = ?", (uid,)).fetchone():
                continue
            if not pw:
                pw = new_password()
                generated.append(f"{role}\t{uid}\t{pw}")
            c.execute("INSERT INTO users (id, role, pw_hash) VALUES (?, ?, ?)", (uid, role, hash_password(pw)))
    if generated:
        out = Path(settings.runtime_dir) / "initial-credentials.txt"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("role\tid\tpassword\n" + "\n".join(generated) + "\n", encoding="utf-8")
        os.chmod(out, 0o600)
        log.warning("초기 비밀번호가 환경변수에 없어 생성했습니다: %s 파일을 확인하세요.", out)
