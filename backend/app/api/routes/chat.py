"""
Chat routes — dynamically manage chat and Q&A history in the database.
"""

import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.models.database import ChatMessage
from database.connection import get_db

router = APIRouter()


@router.get("/history")
async def get_chat_history(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve the chat history dynamically from the database for the current user.
    Pairs up questions and answers for clean history display.
    """
    user_id = current_user.get("id") if isinstance(current_user, dict) else getattr(current_user, "id", None)
    if not user_id:
        return {"history": []}

    records = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    history = []
    current_q = None

    for msg in records:
        if msg.role == "user":
            current_q = {
                "id": msg.id,
                "question": msg.content,
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
            }
        elif msg.role == "assistant":
            sources = []
            if msg.sources:
                try:
                    sources = json.loads(msg.sources)
                except Exception:
                    sources = [msg.sources]

            timestamp = {}
            if msg.video_timestamp is not None:
                m = int(msg.video_timestamp // 60)
                s = int(msg.video_timestamp % 60)
                formatted = f"{m:02d}:{s:02d}"
                timestamp = {
                    "start_time": msg.video_timestamp,
                    "formatted_start": formatted,
                    "formatted_end": f"{m:02d}:{min(59, s + 30):02d}",
                }

            item = {
                "id": msg.id,
                "question": current_q.get("question", "") if current_q else "",
                "answer": {
                    "text": msg.content,
                    "confidence": msg.confidence or "high",
                },
                "sources": sources,
                "timestamp": timestamp,
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
            }
            history.append(item)
            current_q = None

    # If an unanswered question remains
    if current_q:
        history.append({
            "id": current_q["id"],
            "question": current_q["question"],
            "answer": {"text": "Awaiting response...", "confidence": "unknown"},
            "sources": [],
            "timestamp": {},
            "created_at": current_q["created_at"],
        })

    return {"history": list(reversed(history))}


@router.delete("/history")
async def delete_chat_history(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Dynamically delete all chat history records for the current user.
    """
    user_id = current_user.get("id") if isinstance(current_user, dict) else getattr(current_user, "id", None)
    if not user_id:
        return {"message": "No user session found"}

    db.query(ChatMessage).filter(ChatMessage.user_id == user_id).delete()
    db.commit()
    return {"message": "Chat history cleared successfully"}
