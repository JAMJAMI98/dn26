"""Account and session persistence (server-side sessions with expiry)."""
from datetime import datetime, timedelta, timezone

from app.core.security import new_token, verify_password
from app.infrastructure.db import connect


def authenticate(user_id: str, password: str):
    with connect() as c:
        row = c.execute("SELECT id, role, pw_hash FROM users WHERE id = ?", (user_id,)).fetchone()
    return {"id": row["id"], "role": row["role"]} if row and verify_password(password, row["pw_hash"]) else None


def create_session(user: dict, ttl_min: int) -> dict:
    token = new_token()
    expires = (datetime.now(timezone.utc) + timedelta(minutes=ttl_min)).isoformat()
    with connect() as c:
        c.execute("INSERT INTO auth_sessions (token, user_id, expires_at) VALUES (?, ?, ?)", (token, user["id"], expires))
    return {"token": token, "expires_at": expires}


def user_for_token(token: str):
    with connect() as c:
        row = c.execute("SELECT u.id, u.role, s.expires_at FROM auth_sessions s JOIN users u ON u.id = s.user_id "
                        "WHERE s.token = ?", (token,)).fetchone()
    if not row or datetime.fromisoformat(row["expires_at"]) < datetime.now(timezone.utc):
        return None
    return {"id": row["id"], "role": row["role"]}


def delete_session(token: str) -> None:
    with connect() as c:
        c.execute("DELETE FROM auth_sessions WHERE token = ?", (token,))
