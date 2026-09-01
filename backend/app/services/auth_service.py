"""
Authentication service — JWT token creation, verification, and user management.
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with the given payload.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token. Returns the payload or None if invalid.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if email is None:
            return None
        return {"email": email, "role": role}
    except JWTError:
        return None


def authenticate_user(email: str, password: str):
    """
    Authenticate a user by email and password.
    Returns user data if valid, None otherwise.
    """
    # TODO: Query user from PostgreSQL database
    # Placeholder — replace with actual DB lookup
    pass


def create_user(request):
    """
    Create a new user in the database.
    Returns the created user or None if email already exists.
    """
    # TODO: Insert user into PostgreSQL database
    # Placeholder — replace with actual DB insert
    pass
