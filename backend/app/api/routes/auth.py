"""
Authentication routes — login and registration endpoints.
"""

from fastapi import APIRouter, HTTPException, status

from app.models.schemas import LoginRequest, LoginResponse, RegisterRequest
from app.services.auth_service import authenticate_user, create_user, create_access_token

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate a user with email and password.
    Returns a JWT access token and user details.
    """
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user,
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """
    Register a new user (student or faculty).
    """
    user = create_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )
    return {"message": "User registered successfully", "user_id": user.id}
