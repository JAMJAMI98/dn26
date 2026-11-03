"""Account and session persistence (server-side sessions with expiry)."""
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.security import new_token, verify_password
from app.infrastructure.models import AuthSession, User


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def authenticate(db: Session, user_id: str, password: str) -> User | None:
    user = db.get(User, user_id)
    return user if user and verify_password(password, user.pw_hash) else None


def create_session(db: Session, user: User, ttl_min: int) -> AuthSession:
    s = AuthSession(token=new_token(), user_id=user.id,
                    expires_at=datetime.now(timezone.utc) + timedelta(minutes=ttl_min))
    db.add(s)
    db.commit()
    return s


def user_for_token(db: Session, token: str) -> User | None:
    s = db.get(AuthSession, token)
    if not s or _aware(s.expires_at) < datetime.now(timezone.utc):
        return None
    return db.get(User, s.user_id)


def delete_session(db: Session, token: str) -> None:
    s = db.get(AuthSession, token)
    if s:
        db.delete(s)
        db.commit()
