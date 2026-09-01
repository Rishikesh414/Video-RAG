"""
Chat routes — manage chat history for users.
"""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user

router = APIRouter()


@router.get("/history")
async def get_chat_history(current_user=Depends(get_current_user)):
    """
    Retrieve the chat history for the current user.
    Returns a list of past questions and answers.
    """
    # TODO: Query PostgreSQL for user's chat history
    return {"history": []}


@router.delete("/history")
async def delete_chat_history(current_user=Depends(get_current_user)):
    """
    Delete all chat history for the current user.
    """
    # TODO: Delete from PostgreSQL
    return {"message": "Chat history cleared"}
