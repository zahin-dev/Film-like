"""認証APIの入力・出力スキーマ。"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """検証済みのアカウント登録入力。"""

    first_name: str = Field(min_length=1, max_length=60)
    last_name: str = Field(min_length=1, max_length=60)
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    age: int | None = Field(default=None, ge=1, le=120)

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, password: str) -> str:
        """数字と記号をそれぞれ1文字以上必須にする。"""
        if not any(character.isdigit() for character in password):
            raise ValueError("パスワードには数字を1文字以上含めてください")
        if not any(not character.isalnum() for character in password):
            raise ValueError(
                "パスワードには記号を1文字以上含めてください"
            )
        return password


class UserLogin(BaseModel):
    """検証済みのログイン入力。"""

    email: EmailStr
    password: str = Field(min_length=1, max_length=64)


class UserResponse(BaseModel):
    """認証APIが返す公開ユーザー情報。"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    age: int | None = None
    created_at: datetime
    updated_at: datetime


class AuthResponse(BaseModel):
    """認証済みプロフィールと署名済みアクセストークン。"""

    user: UserResponse
    token: str
