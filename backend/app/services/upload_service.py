"""
Upload service — handles file storage and triggers Step 1 (Rich Indexing).

On video upload, the hybrid pipeline's Step 1 runs:
- Extracts audio → Whisper transcript (timestamped segments)
- Detects scene boundaries (PySceneDetect)
- Extracts OCR text per scene keyframe (EasyOCR)
- Generates visual descriptions per scene (Gemini Flash VLM)
- Runs YOLO visual tagger → timestamped object tags
- Builds enriched unified metadata and indexes into Qdrant

Processing status is tracked per video_id in JSON status files and
accessible via GET /api/v1/upload/status/{video_id}.
"""

import asyncio
import logging
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.config import settings
from pipeline.orchestrator import VideoRAGOrchestrator

logger = logging.getLogger(__name__)

# Lazy-loaded orchestrator singleton
_orchestrator = None


def _get_orchestrator() -> VideoRAGOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = VideoRAGOrchestrator(config=settings.model_dump())
    return _orchestrator


async def process_video_upload(file: UploadFile, current_user: dict) -> dict:
    """
    Save an uploaded video and run Step 1 (Rich Indexing) in the background.

    Steps:
    1. Save video to disk
    2. Launch Step 1 as an asyncio background task:
       - audio extraction → Whisper transcription
       - scene detection → OCR per keyframe → VLM description per keyframe
       - YOLO visual tagging
       - metadata build → Qdrant indexing
    3. Return immediately with file_id so the client can poll /status/{video_id}

    Returns:
        dict with file_id, filename, file_path, and initial status.
    """
    file_id = str(uuid.uuid4())
    upload_dir = Path(settings.VIDEO_UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Save file to disk
    file_ext = Path(file.filename).suffix or ".mp4"
    file_path = upload_dir / f"{file_id}{file_ext}"

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    logger.info(f"Video saved: {file_path} ({len(content):,} bytes) — launching pipeline...")

    # Launch the pipeline as an async background task
    # This allows the upload endpoint to return immediately
    extra = {
        "original_filename": file.filename,
        "uploaded_by": current_user.get("email", ""),
    }
    asyncio.create_task(
        _run_indexing_background(str(file_path), file_id, extra)
    )

    return {
        "file_id": file_id,
        "filename": file.filename,
        "file_path": str(file_path),
        "status": "queued",
        "message": "Video uploaded successfully. Processing started in the background.",
    }


async def _run_indexing_background(
    video_path: str,
    video_id: str,
    extra: dict,
) -> None:
    """
    Run the full Step 1 indexing pipeline as an async background task.
    Uses run_in_executor to avoid blocking the event loop during CPU-intensive work.
    """
    loop = asyncio.get_event_loop()
    orchestrator = _get_orchestrator()

    try:
        # Run the synchronous pipeline in a thread pool so it doesn't block FastAPI
        await loop.run_in_executor(
            None,
            lambda: orchestrator.index_video(
                video_path=video_path,
                video_id=video_id,
                extra=extra,
            )
        )
        logger.info(f"[{video_id[:8]}] Background indexing completed successfully")
    except Exception as e:
        logger.error(f"[{video_id[:8]}] Background indexing failed: {e}", exc_info=True)
        # tracker.mark_failed() is called inside orchestrator.index_video() on exception


async def get_video_processing_status(video_id: str) -> dict:
    """
    Get the current pipeline processing status for a video.

    Args:
        video_id: The video's unique ID (returned from upload endpoint).

    Returns:
        Status dict with stage, progress_pct, message, stats, and timestamps.
    """
    orchestrator = _get_orchestrator()
    return orchestrator.get_processing_status(video_id)


async def process_pdf_upload(file: UploadFile, current_user: dict) -> dict:
    """
    Save an uploaded PDF file and index it into the vector store.

    Returns:
        dict with file_id, file_path, and status.
    """
    file_id = str(uuid.uuid4())
    upload_dir = Path(settings.VIDEO_UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / f"{file_id}.pdf"

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # TODO: Extract text from PDF using PyMuPDF, chunk, embed, and add to Qdrant

    return {
        "file_id": file_id,
        "filename": file.filename,
        "file_path": str(file_path),
        "status": "completed",
    }
