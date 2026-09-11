"""
Pydantic schemas — request/response models for the Hybrid VideoRAG API.

Response structure follows the 3-output design:
    1. Text answer (with confidence and reasoning)
    2. Video clip (URL, path, download info)
    3. Timestamp (start/end in source video)
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List


# ─── Auth Schemas ────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str  # "student" | "faculty"

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "student"  # "student" | "faculty"


# ─── Query Schemas (3-Output Hybrid Response) ───────────────────────

class QueryRequest(BaseModel):
    question: str
    module: Optional[str] = None  # e.g., "M1", "M2", "M3", "M4"


class AnswerInfo(BaseModel):
    """Output 1: Text response from the multimodal LLM."""
    text: str
    confidence: str = "unknown"  # high | medium | low
    reasoning: str = ""


class VideoClipInfo(BaseModel):
    """Output 2: The extracted video clip."""
    clip_id: str = ""
    clip_url: str = ""          # URL to stream/download the clip
    clip_filename: str = ""
    duration: float = 0         # Clip duration in seconds


class TimestampInfo(BaseModel):
    """Output 3: Timestamps in the source video."""
    start_time: float = 0
    end_time: float = 0
    formatted_start: str = ""   # e.g., "04:15"
    formatted_end: str = ""     # e.g., "04:45"
    source_video: str = ""
    video_id: str = ""


class QueryResponse(BaseModel):
    """
    Complete 3-part response from the hybrid VideoRAG pipeline.

    Contains:
    1. answer   — Text response with confidence
    2. video_clip — Extracted clip file info
    3. timestamp — Source video timing
    4. sources  — List of source video IDs used
    """
    answer: AnswerInfo
    video_clip: VideoClipInfo
    timestamp: TimestampInfo
    sources: List[str] = []


# ─── Upload Schemas ──────────────────────────────────────────────────

class UploadResponse(BaseModel):
    file_id: str
    filename: str
    status: str = "processing"


class IndexingResult(BaseModel):
    """Result of Step 1 indexing on upload."""
    video_id: str
    transcript_segments: int = 0
    visual_tags: int = 0
    scenes: int = 0
    chunks_indexed: int = 0
