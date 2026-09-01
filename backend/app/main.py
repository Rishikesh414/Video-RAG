"""
VideoRAG — FastAPI Application Entry Point.

Initializes the FastAPI app, registers routers, and configures middleware.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.routes import auth, upload, query, chat

# ─── App Initialization ─────────────────────────────────────────────

app = FastAPI(
    title="VideoRAG API",
    description="Next-Gen Video Search & Generation — REST API",
    version="0.1.0",
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
    return {"status": "healthy", "version": "0.1.0"}
