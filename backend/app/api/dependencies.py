"""
Shared API dependencies — database sessions, auth checks, etc.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from database.connection import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Dependency that extracts and validates the current user from the JWT token.
    Raises 401 if the token is invalid or expired.
    """
    from app.services.auth_service import verify_token, get_user_by_email

    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_user_by_email(payload["email"], db=db)
    if user is not None:
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        }
    return payload
