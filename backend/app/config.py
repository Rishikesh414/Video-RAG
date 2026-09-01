"""
VideoRAG — Application Configuration.

Loads environment variables and provides a typed settings object
for the entire backend application.
"""

from pathlib import Path
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
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "videorag"
    POSTGRES_USER: str = "videorag_user"
    POSTGRES_PASSWORD: str = "change-me"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # ── LLM ──────────────────────────────────
    LLM_PROVIDER: str = "llama"  # llama | openai | gemini
    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    LLAMA_MODEL_PATH: str = "./models/llama-3.1-8b-instruct"

    # ── Embeddings ───────────────────────────
    EMBEDDING_MODEL: str = "Qwen/Qwen3-Embedding-8B"
    SENTENCE_TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"

    # ── Whisper ──────────────────────────────
    WHISPER_MODEL: str = "large-v3"

    # ── FAISS ────────────────────────────────
    FAISS_INDEX_PATH: str = "./data/faiss_index"

    # ── Video Processing ─────────────────────
    MAX_KEYFRAMES: int = 32
    FRAME_EXTRACTION_FPS: int = 1

    # ── Data Paths ───────────────────────────
    VIDEO_UPLOAD_DIR: str = "./data/videos"
    FRAMES_DIR: str = "./data/frames"
    AUDIO_DIR: str = "./data/audio"
    TRANSCRIPTS_DIR: str = "./data/transcripts"
    OCR_OUTPUT_DIR: str = "./data/ocr_output"
    EMBEDDINGS_DIR: str = "./data/embeddings"
    METADATA_DIR: str = "./data/metadata"

    # ── JWT ───────────────────────────────────
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
