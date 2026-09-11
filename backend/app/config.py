"""
VideoRAG — Application Configuration (Hybrid Architecture).

Loads environment variables and provides a typed settings object.
Updated for the 3-step hybrid pipeline.
"""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ── General ──────────────────────────────
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-to-a-random-secret"

    # ── CORS ─────────────────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # ── Database ─────────────────────────────
    USE_SQLITE: bool = True
    SQLITE_DB_PATH: str = "./data/videorag.db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "videorag"
    POSTGRES_USER: str = "videorag_user"
    POSTGRES_PASSWORD: str = "change-me"
    CUSTOM_DATABASE_URL: Optional[str] = None

    @property
    def DATABASE_URL(self) -> str:
        if self.CUSTOM_DATABASE_URL:
            return self.CUSTOM_DATABASE_URL
        if self.USE_SQLITE:
            db_file = Path(self.SQLITE_DB_PATH).resolve()
            db_file.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite:///{db_file}"
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # ── Step 2: Standard LLM (cheap, for timestamp resolution) ───
    STANDARD_LLM_PROVIDER: str = "llama"  # llama | openai | gemini
    LLAMA_MODEL_PATH: str = "./models/llama-3.1-8b-instruct.gguf"

    # ── Step 3: Multimodal LLM (expensive, for clip analysis) ────
    MULTIMODAL_LLM_PROVIDER: str = "gemini"  # gemini | openai
    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""

    # ── Step 1: Visual Tagger ────────────────
    VISUAL_TAGGER_MODEL: str = "yolov8n.pt"

    # ── Embeddings ───────────────────────────
    EMBEDDING_MODEL: str = "Qwen/Qwen3-Embedding-8B"
    SENTENCE_TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"

    # ── Whisper ──────────────────────────────
    WHISPER_MODEL: str = "large-v3"

    # ── Qdrant Vector Store ──────────────────
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_URL: Optional[str] = None
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION: str = "videorag_chunks"
    QDRANT_PATH: Optional[str] = None

    # ── Clip Extraction ──────────────────────
    CLIP_OUTPUT_DIR: str = "./data/clips"
    CLIP_DURATION_SECONDS: int = 30  # Default clip window

    # ── Data Paths ───────────────────────────
    VIDEO_UPLOAD_DIR: str = "./data/videos"
    AUDIO_DIR: str = "./data/audio"
    TRANSCRIPTS_DIR: str = "./data/transcripts"
    VISUAL_TAGS_DIR: str = "./data/visual_tags"
    EMBEDDINGS_DIR: str = "./data/embeddings"
    METADATA_DIR: str = "./data/metadata"

    # ── JWT ───────────────────────────────────
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
