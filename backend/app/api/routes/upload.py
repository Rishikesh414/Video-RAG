"""
Upload routes — Faculty endpoints for uploading lecture videos and PDF notes.
Dynamically saves and queries uploads in the PostgreSQL / SQLite database.

Processing pipeline runs in the background after upload.
Frontend can poll GET /upload/status/{video_id} for real-time progress.
"""

from pathlib import Path
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.models.database import Upload
from app.services.upload_service import (
    process_video_upload,
    process_pdf_upload,
    get_video_processing_status,
)
from database.connection import get_db

router = APIRouter()


@router.post("/video")
async def upload_video(
    file: UploadFile = File(...),
    module: str = Form("M1"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload a lecture video for background processing.

    The pipeline runs asynchronously:
      1. Whisper transcription (timestamped speech-to-text)
      2. Scene detection (PySceneDetect)
      3. OCR per scene keyframe (EasyOCR — slides, whiteboards)
      4. Visual description per scene (Gemini Flash VLM)
      5. YOLO visual tagging (object detection)
      6. Qdrant indexing (embeddings)

    Returns immediately with file_id. Poll GET /upload/status/{file_id}
    for real-time progress updates.

    Only accessible by faculty users.
    """
    if current_user.get("role") != "faculty":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only faculty members can upload videos",
        )

    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a video",
        )

    # Save file and launch background indexing
    result = await process_video_upload(file, current_user)
    file_id = result["file_id"]
    file_path = result.get("file_path", "")
    file_size = Path(file_path).stat().st_size if file_path and Path(file_path).exists() else 0

    # Dynamically record upload in DB (initial status = 'processing')
    upload_record = Upload(
        user_id=current_user["id"],
        filename=file.filename,
        file_type="video",
        file_path=str(file_path),
        module=module.upper(),
        file_size=file_size,
        status="processing",
    )
    db.add(upload_record)
    db.commit()
    db.refresh(upload_record)

    return {
        "message": "Video uploaded successfully. Processing started in background.",
        "file_id": file_id,
        "upload_id": upload_record.id,
        "filename": upload_record.filename,
        "module": upload_record.module,
        "status": "processing",
        "status_url": f"/api/v1/upload/status/{file_id}",
    }


@router.post("/pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    module: str = Form("M1"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload PDF notes to supplement the video knowledge base.
    Dynamically persists record in the uploads database table.
    Only accessible by faculty users.
    """
    if current_user.get("role") != "faculty":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only faculty members can upload PDFs",
        )

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a PDF",
        )

    result = await process_pdf_upload(file, current_user)
    file_path = result.get("file_path", "")
    file_size = Path(file_path).stat().st_size if file_path and Path(file_path).exists() else 0

    upload_record = Upload(
        user_id=current_user["id"],
        filename=file.filename,
        file_type="pdf",
        file_path=str(file_path),
        module=module.upper(),
        file_size=file_size,
        status="completed",
    )
    db.add(upload_record)
    db.commit()
    db.refresh(upload_record)

    return {
        "message": "PDF uploaded and indexed dynamically",
        "file_id": result["file_id"],
        "upload_id": upload_record.id,
        "filename": upload_record.filename,
        "module": upload_record.module,
    }


@router.get("/status/{video_id}")
async def get_processing_status(
    video_id: str,
    current_user=Depends(get_current_user),
):
    """
    Poll the real-time processing status of an uploaded video.

    Returns a JSON object with:
    - stage: Current pipeline stage (queued, transcription, ocr, done, failed, ...)
    - progress_pct: Integer 0-100
    - message: Human-readable status description
    - stats: Dict of indexing statistics so far
    - started_at / updated_at / completed_at: ISO timestamps

    Frontend should poll this every 2-3 seconds until stage == 'done' or 'failed'.
    """
    status_data = await get_video_processing_status(video_id)
    return status_data


@router.get("/list")
async def list_uploads(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Dynamically list all uploaded files from the database.
    """
    uploads = db.query(Upload).order_by(Upload.created_at.desc()).all()
    return {
        "uploads": [
            {
                "id": u.id,
                "filename": u.filename,
                "file_type": u.file_type,
                "file_path": u.file_path,
                "module": u.module,
                "file_size": u.file_size,
                "status": u.status,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in uploads
        ]
    }


@router.delete("/{upload_id}")
async def delete_upload(
    upload_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Dynamically delete an uploaded file record from the database.
    """
    if current_user.get("role") != "faculty":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only faculty members can delete uploads",
        )

    upload_record = db.query(Upload).filter(Upload.id == upload_id).first()
    if not upload_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found",
        )

    # Remove file from disk if present
    try:
        p = Path(upload_record.file_path)
        if p.exists():
            p.unlink()
    except Exception:
        pass

    db.delete(upload_record)
    db.commit()
    return {"message": "Upload deleted successfully", "id": upload_id}
