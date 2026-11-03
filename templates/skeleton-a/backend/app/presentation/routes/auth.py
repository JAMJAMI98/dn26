from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import AppError
from app.infrastructure import auth_repo
from app.infrastructure.models import User
from app.presentation.deps import bearer_token, current_user, get_db
from app.presentation.schemas import LoginIn, LoginOut, MeOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = auth_repo.authenticate(db, body.id, body.password)
    if not user:
        raise AppError(401, "invalid_credentials", "아이디 또는 비밀번호가 올바르지 않습니다.")
    s = auth_repo.create_session(db, user, get_settings().session_ttl_min)
    return LoginOut(token=s.token, user_id=user.id, role=user.role, expires_at=s.expires_at)


@router.post("/logout", status_code=204)
def logout(token: str = Depends(bearer_token), db: Session = Depends(get_db)):
    auth_repo.delete_session(db, token)


@router.get("/me", response_model=MeOut)
def me(user: User = Depends(current_user)):
    return MeOut(user_id=user.id, role=user.role)
