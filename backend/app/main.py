"""
VideoRAG — FastAPI Application Entry Point (Hybrid Architecture).

Initializes the FastAPI app, registers routers, configures middleware,
and mounts static file serving for extracted video clips.
"""

import sys
from pathlib import Path

# Ensure project root and backend dir are in sys.path
_current_file = Path(__file__).resolve()
_backend_dir = _current_file.parent.parent
_project_root = _backend_dir.parent

for _p in [str(_project_root), str(_backend_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api.routes import auth, upload, query, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event: dynamically initialize database tables on startup."""
    try:
        from database.connection import init_db
        init_db()
    except Exception as e:
        print(f"Warning: Could not initialize database on startup: {e}")
    yield


# ─── App Initialization ─────────────────────────────────────────────

app = FastAPI(
    title="VideoRAG API — Hybrid Architecture",
    lifespan=lifespan,
    description=(
        "Next-Gen Video Search & Generation — 3-Step Hybrid Pipeline.\n\n"
        "**Step 1**: Low-cost indexing (ASR + CV tags) on upload\n"
        "**Step 2**: Semantic retrieval + timestamp resolution on query\n"
        "**Step 3**: Targeted multimodal LLM analysis on the exact clip"
    ),
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS Middleware ─────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Static File Serving (for extracted clips) ──────────────────────

clips_dir = Path(settings.CLIP_OUTPUT_DIR)
clips_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static/clips", StaticFiles(directory=str(clips_dir)), name="clips")

# ─── Register Routers ───────────────────────────────────────────────

API_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=f"{API_PREFIX}/auth", tags=["Authentication"])
app.include_router(upload.router, prefix=f"{API_PREFIX}/upload", tags=["Upload"])
app.include_router(query.router, prefix=f"{API_PREFIX}/query", tags=["Query"])
app.include_router(chat.router, prefix=f"{API_PREFIX}/chat", tags=["Chat"])


# ─── Health Check ────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.2.0", "architecture": "hybrid-3-step"}
