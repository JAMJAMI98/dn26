"""Auth helpers: current user from `Authorization: Bearer <token>`, role guard decorator."""
from functools import wraps

from app.core.errors import AppError
from app.infrastructure.auth_repo import user_for_token


def bearer_token(req) -> str:
    auth = req.headers.get("authorization", "")
    if not auth.lower().startswith("bearer "):
        raise AppError(401, "unauthorized", "로그인이 필요합니다.")
    return auth.split(" ", 1)[1].strip()


def current_user(req) -> dict:
    user = user_for_token(bearer_token(req))
    if not user:
        raise AppError(401, "unauthorized", "로그인이 만료되었거나 올바르지 않습니다.")
    req.user = user
    return user


def login_required(fn):
    @wraps(fn)
    def wrapper(req):
        current_user(req)
        return fn(req)
    return wrapper


def require_role(*roles: str):
    def deco(fn):
        @wraps(fn)
        def wrapper(req):
            if current_user(req)["role"] not in roles:
                raise AppError(403, "forbidden", "이 기능을 사용할 권한이 없습니다.")
            return fn(req)
        return wrapper
    return deco
