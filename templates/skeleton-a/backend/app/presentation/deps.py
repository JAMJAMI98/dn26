"""Request dependencies: DB session, current user from `Authorization: Bearer <token>`, role guard."""
from collections.abc import Iterator

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.infrastructure.auth_repo import user_for_token
from app.infrastructure.db import SessionLocal
from app.infrastructure.models import User


def get_db() -> Iterator[Session]:
    with SessionLocal() as db:
        yield db


def bearer_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise AppError(401, "unauthorized", "로그인이 필요합니다.")
    return authorization.split(" ", 1)[1].strip()


def current_user(token: str = Depends(bearer_token), db: Session = Depends(get_db)) -> User:
    user = user_for_token(db, token)
    if not user:
        raise AppError(401, "unauthorized", "로그인이 만료되었거나 올바르지 않습니다.")
    return user


def require_role(*roles: str):
    def guard(user: User = Depends(current_user)) -> User:
        if user.role not in roles:
            raise AppError(403, "forbidden", "이 기능을 사용할 권한이 없습니다.")
        return user

    return guard
