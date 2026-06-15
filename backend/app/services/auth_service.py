"""
Authentication Service

This module implements the business logic for user authentication
in the Film-like application.

It orchestrates registration and login flows: input validation is
handled upstream by Pydantic schemas, and data persistence is
delegated to the user repository. This service is responsible for
the steps in between: duplicate detection, password hashing,
user construction, password verification, and JWT generation.

Functions:
    - register_user: handle the full user registration flow
    - login_user: handle the user login flow
"""

from sqlalchemy.orm import Session
from app.config import settings  # centralized environment configuration
from app.repositories import user_repository
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, AuthResponse
)
from app.models.user import User
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status

# SECRET_KEY is validated at startup by pydantic_settings — guaranteed non-empty
SECRET_KEY: str = settings.SECRET_KEY

# Signing algorithm used for all JWT tokens issued by this service
ALGORITHM = "HS256"

# Access token lifetime — short enough to limit the damage of a stolen token
TOKEN_EXPIRY_HOURS = 24


def register_user(db: Session, payload: UserCreate) -> AuthResponse:
    """
    Handle the full user registration flow.

    Orchestrates duplicate detection, password hashing, user creation,
    and JWT generation. Raises an HTTP exception if the email is already
    registered, so the exception propagates directly to the FastAPI route
    and is returned as a 409 response without any additional handling.

    Args:
        db (Session): SQLAlchemy database session, injected by FastAPI
            via the get_db() dependency.
        payload (UserCreate): Validated registration data. Password is
            received in plain text and hashed before storage.

    Returns:
        AuthResponse: The created user's profile wrapped with a JWT
            access token.

    Raises:
        HTTPException 409: If the email address is already registered.
    """
    if user_repository.get_by_email(db, payload.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    hashed_password = bcrypt.hashpw(
        payload.password.encode('utf-8'),
        bcrypt.gensalt()
    )

    username = payload.first_name + payload.last_name

    new_user = User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        username=username,
        email=payload.email,
        hashed_password=hashed_password.decode('utf-8'),
        age=payload.age
    )

    created_user = user_repository.create(db, new_user)

    return AuthResponse(
        user=UserResponse.model_validate(created_user),
        token=jwt.encode(
            {
                "sub": str(created_user.id),
                "exp": datetime.now(tz=timezone.utc) + timedelta(hours=TOKEN_EXPIRY_HOURS)
            },
            SECRET_KEY,
            ALGORITHM
        )
    )


def login_user(db: Session, payload: UserLogin) -> AuthResponse:
    """
    Handle the user login flow.

    Looks up the user by email, verifies the password against the stored
    bcrypt hash, and returns a JWT token on success. Both failure cases
    (unknown email and wrong password) return the same error message to
    prevent email enumeration attacks.

    Args:
        db (Session): SQLAlchemy database session, injected by FastAPI
            via the get_db() dependency.
        payload (UserLogin): Validated login data containing email
            and plain-text password.

    Returns:
        AuthResponse: The authenticated user's profile wrapped with a
            JWT access token.

    Raises:
        HTTPException 401: If the email is not found or the password
            does not match. Same message in both cases to prevent
            email enumeration.
    """
    existing_user = user_repository.get_by_email(db, payload.email)

    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not existing_user.verify_password(payload.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    return AuthResponse(
        user=UserResponse.model_validate(existing_user),
        token=jwt.encode(
            {
                "sub": str(existing_user.id),
                "exp": datetime.now(tz=timezone.utc) + timedelta(hours=TOKEN_EXPIRY_HOURS)
            },
            SECRET_KEY,
            ALGORITHM
        )
    )
