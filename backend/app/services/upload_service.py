"""
Upload service — handles file storage and triggers Step 1 (Indexing).

On video upload, the hybrid pipeline's Step 1 runs:
- Extracts audio → Whisper transcript
- Runs YOLO visual tagger → timestamped object tags
- Detects scene boundaries
- Builds unified metadata and indexes into Qdrant
"""

import uuid
from pathlib import Path

from fastapi import UploadFile

from app.config import settings
from pipeline.orchestrator import VideoRAGOrchestrator


# Lazy-loaded orchestrator singleton
_orchestrator = None


def _get_orchestrator() -> VideoRAGOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = VideoRAGOrchestrator(config=settings.model_dump())
    return _orchestrator


async def process_video_upload(file: UploadFile, current_user: dict) -> dict:
    """
    Save an uploaded video and run Step 1 (Low-Cost Indexing).

    Steps:
    1. Save video to disk
    2. Run Step 1: audio extraction → transcription → visual tagging → scene detection
    3. Build unified metadata and index into Qdrant

    Returns:
        dict with file_id, indexing stats, and status.
    """
    file_id = str(uuid.uuid4())
    upload_dir = Path(settings.VIDEO_UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Save file
    file_ext = Path(file.filename).suffix
    file_path = upload_dir / f"{file_id}{file_ext}"

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Run Step 1: Index the video
    orchestrator = _get_orchestrator()
    indexing_result = orchestrator.index_video(
        video_path=str(file_path),
        video_id=file_id,
        extra={
            "original_filename": file.filename,
            "uploaded_by": current_user.get("email", ""),
        },
    )

    return {
        "file_id": file_id,
        "filename": file.filename,
        "status": "indexed",
        "indexing": indexing_result,
    }


async def process_pdf_upload(file: UploadFile, current_user: dict) -> dict:
    """
    Save an uploaded PDF file and index it into the vector store.

    Returns:
        dict with file_id and status.
    """
    file_id = str(uuid.uuid4())
    upload_dir = Path(settings.VIDEO_UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / f"{file_id}.pdf"

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # TODO: Extract text from PDF, chunk, embed, and add to Qdrant

    return {"file_id": file_id, "filename": file.filename, "status": "completed"}
