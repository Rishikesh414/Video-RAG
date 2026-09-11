"""
Authentication service — JWT token creation, verification, and user management.
"""

from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.models.database import User


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its bcrypt hash."""
    try:
        pwd_bytes = plain_password.encode("utf-8")[:72]
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False


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


def get_user_by_email(email: str, db: Optional[Session] = None) -> Optional[User]:
    """
    Find a user by email address.
    """
    close_db = False
    if db is None:
        from database.connection import SessionLocal
        db = SessionLocal()
        close_db = True

    try:
        return db.query(User).filter(User.email == email.strip().lower()).first()
    finally:
        if close_db:
            db.close()


def authenticate_user(email: str, password: str, db: Optional[Session] = None) -> Optional[User]:
    """
    Authenticate a user by email and password.
    Returns User ORM object if valid, None otherwise.
    """
    close_db = False
    if db is None:
        from database.connection import SessionLocal
        db = SessionLocal()
        close_db = True

    try:
        user = db.query(User).filter(User.email == email.strip().lower()).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    finally:
        if close_db:
            db.close()


def create_user(request, db: Optional[Session] = None) -> Optional[User]:
    """
    Create a new user in the database.
    Returns the created User or None if email already exists.
    """
    close_db = False
    if db is None:
        from database.connection import SessionLocal
        db = SessionLocal()
        close_db = True

    try:
        clean_email = request.email.strip().lower()
        existing = db.query(User).filter(User.email == clean_email).first()
        if existing:
            return None

        hashed = hash_password(request.password)
        new_user = User(
            name=request.name.strip(),
            email=clean_email,
            hashed_password=hashed,
            role=getattr(request, "role", "student"),
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    finally:
        if close_db:
            db.close()
