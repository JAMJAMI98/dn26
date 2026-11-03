from datetime import datetime

from pydantic import BaseModel, Field


class LoginIn(BaseModel):
    id: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=256)


class LoginOut(BaseModel):
    token: str
    user_id: str
    role: str
    expires_at: datetime


class MeOut(BaseModel):
    user_id: str
    role: str


class JobOut(BaseModel):
    id: int
    kind: str
    status: str
    result: str | None = None
    error: str | None = None
