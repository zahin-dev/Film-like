"""Authentication request and response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """Validated registration payload."""

    first_name: str = Field(min_length=1, max_length=60)
    last_name: str = Field(min_length=1, max_length=60)
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    age: int | None = Field(default=None, ge=1, le=120)

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, password: str) -> str:
        """Require a digit and a non-alphanumeric character."""
        if not any(character.isdigit() for character in password):
            raise ValueError("Password must contain at least one digit")
        if not any(not character.isalnum() for character in password):
            raise ValueError(
                "Password must contain at least one non-alphanumeric character"
            )
        return password


class UserLogin(BaseModel):
    """Validated login payload."""

    email: EmailStr
    password: str = Field(min_length=1, max_length=64)


class UserResponse(BaseModel):
    """Public user data returned by authentication endpoints."""

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
    """Authenticated user profile and signed access token."""

    user: UserResponse
    token: str
