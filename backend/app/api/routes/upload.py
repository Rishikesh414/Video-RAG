"""
Upload routes — Faculty endpoints for uploading lecture videos and PDF notes.
"""

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status

from app.api.dependencies import get_current_user
from app.services.upload_service import process_video_upload, process_pdf_upload

router = APIRouter()


@router.post("/video")
async def upload_video(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    """
    Upload a lecture video for processing.
    The pipeline will extract frames, audio, transcripts, and build embeddings.
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

    result = await process_video_upload(file, current_user)
    return {"message": "Video uploaded and queued for processing", "file_id": result["file_id"]}


@router.post("/pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    """
    Upload PDF notes to supplement the video knowledge base.
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
    return {"message": "PDF uploaded and indexed", "file_id": result["file_id"]}


@router.get("/list")
async def list_uploads(current_user=Depends(get_current_user)):
    """
    List all uploaded files for the current user.
    """
    # TODO: Query database for user's uploads
    return {"uploads": []}
