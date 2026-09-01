"""
Pydantic schemas — request/response models for API validation.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional


# ─── Auth Schemas ────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str  # "student" | "faculty"


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "student"  # "student" | "faculty"


# ─── Query Schemas ───────────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str
    module: Optional[str] = None  # e.g., "M1", "M2", "M3", "M4"


class VideoSegment(BaseModel):
    url: str
    title: str
    start_time: float = 0
    end_time: float = 0


class QueryResponse(BaseModel):
    answer: str
    sources: list[str] = []
    video_segment: Optional[VideoSegment] = None


# ─── Upload Schemas ──────────────────────────────────────────────────

class UploadResponse(BaseModel):
    file_id: str
    filename: str
    status: str = "processing"
