"""
Query routes — Student endpoints for asking questions to the VideoRAG system.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.models.schemas import QueryRequest, QueryResponse
from app.services.query_service import process_query

router = APIRouter()


@router.post("/ask", response_model=QueryResponse)
async def ask_question(
    request: QueryRequest,
    current_user=Depends(get_current_user),
):
    """
    Submit a natural language question about lecture content.
    The VideoRAG pipeline retrieves relevant video segments,
    processes frames, and generates an evidence-based answer.
    """
    try:
        result = await process_query(request.question, current_user)
        return QueryResponse(
            answer=result["answer"],
            sources=result.get("sources", []),
            video_segment=result.get("video_segment"),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}",
        )


@router.get("/segment/{segment_id}")
async def get_video_segment(
    segment_id: str,
    current_user=Depends(get_current_user),
):
    """
    Retrieve a specific video segment by ID for playback.
    """
    # TODO: Look up segment in metadata store and return streaming URL
    return {"segment_id": segment_id, "url": "", "start_time": 0, "end_time": 0}
