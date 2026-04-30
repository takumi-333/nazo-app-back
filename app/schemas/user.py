from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=8)
    email: str | None = Field(default=None)

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        # 英数字・アンダースコア・ハイフンのみ許可
        allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
        if not all(c in allowed for c in v):
            raise ValueError("username は英数字・アンダースコア・ハイフンのみ使用できます")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class UserPublic(BaseModel):
    id: UUID
    username: str
    avatar_url: str | None
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class MessageResponse(BaseModel):
    success: bool
    message: str = ""