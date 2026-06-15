"""
Authentication Routes

This module defines the FastAPI router for authentication endpoints.
It handles HTTP concerns only - request reception, dependency injection,
and response forwarding. All business logic is delegated to auth_service.

Routes:
    - POST /auth/register: create a new user account
    - POST /auth/login: authenticate and receive a JWT token (coming soon)
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import (
    UserCreate, AuthResponse, UserLogin
    )
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
) -> AuthResponse:
    """
    Register a new user account.

    Receives and validates the registration payload via Pydantic,
    then delegates the full registration flow to the authentication
    service: duplicate detection, password hashing, user creation,
    and JWT generation.

    Args:
        user (UserCreate): Validated registration payload containing
            first_name, last_name, email, password, and optional age.
        db (Session): SQLAlchemy session injected by FastAPI via
            the get_db() dependency.

    Returns:
        AuthResponse: The created user's profile and a JWT access token.

    Raises:
        HTTPException 409: If the email address is already registered.
        HTTPException 422: If the request payload fails validation.
    """
    return auth_service.register_user(db, user)


@router.post("/login", status_code=status.HTTP_200_OK)
def login(
    payload: UserLogin,
    db: Session = Depends(get_db)
) -> AuthResponse:
    """
    Authenticate a user and return a JWT token.

    Verifies the email and password against the database.
    Returns the same error message for unknown email and wrong
    password to prevent email enumeration attacks.

    Args:
        payload (UserLogin): Validated login data containing
            email and plain-text password.
        db (Session): SQLAlchemy session injected by FastAPI
            via the get_db() dependency.

    Returns:
        AuthResponse: The authenticated user's profile and a
            JWT access token.

    Raises:
        HTTPException 401: If the email is not found or the
            password does not match.
        HTTPException 422: If the request payload fails validation.
    """
    return auth_service.login_user(db, payload)
