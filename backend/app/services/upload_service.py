"""
Upload service — handles file storage and triggers the VideoRAG processing pipeline.
"""

import uuid
from pathlib import Path

from fastapi import UploadFile

from app.config import settings


async def process_video_upload(file: UploadFile, current_user: dict) -> dict:
    """
    Save an uploaded video file to disk and queue it for pipeline processing.

    Steps:
    1. Generate a unique file ID
    2. Save the file to the video upload directory
    3. Trigger the VideoRAG pipeline (frame extraction, ASR, embedding, etc.)
    4. Store upload metadata in the database

    Returns:
        dict with file_id and status
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

    # TODO: Trigger async pipeline processing
    # TODO: Store upload record in PostgreSQL

    return {"file_id": file_id, "filename": file.filename, "status": "processing"}


async def process_pdf_upload(file: UploadFile, current_user: dict) -> dict:
    """
    Save an uploaded PDF file and index it into the vector store.

    Steps:
    1. Generate a unique file ID
    2. Save the PDF to disk
    3. Extract text, chunk, embed, and add to FAISS index
    4. Store upload metadata in the database

    Returns:
        dict with file_id and status
    """
    file_id = str(uuid.uuid4())
    upload_dir = Path(settings.VIDEO_UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / f"{file_id}.pdf"

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # TODO: Extract text from PDF, chunk, embed, and add to FAISS
    # TODO: Store upload record in PostgreSQL

    return {"file_id": file_id, "filename": file.filename, "status": "completed"}
