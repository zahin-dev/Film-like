"""
Dependencies

This module defines reusable FastAPI dependencies injected into
protected routes via Depends().

The get_current_user dependency enforces JWT authentication:
any route that declares it as a parameter will automatically
require a valid Bearer token in the Authorization header.

Dependencies defined here:
    - get_current_user: decode a JWT and return the authenticated user
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models.user import User
from app.repositories import user_repository
import jwt

# HTTPBearer extracts the token from the Authorization: Bearer <token> header.
# auto_error=True (default) returns 403 automatically if the header is absent.
bearer_scheme = HTTPBearer()

# Must match the algorithm used in auth_service.py when the token was signed.
_ALGORITHM = "HS256"


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency that authenticates a request via JWT.

    Decodes the Bearer token from the Authorization header, validates
    it, and returns the corresponding User instance. Raises 401 for
    any invalid or expired token so the error is consistent across
    all protected routes.

    Args:
        credentials (HTTPAuthorizationCredentials): Bearer token
            extracted from the Authorization header by HTTPBearer.
        db (Session): SQLAlchemy session injected by get_db().

    Returns:
        User: The authenticated user loaded from the database.

    Raises:
        HTTPException 401: If the token is expired, malformed,
            missing the sub claim, or the user no longer exists.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[_ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise jwt.InvalidTokenError
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user
