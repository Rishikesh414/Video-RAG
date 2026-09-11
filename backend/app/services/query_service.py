"""
Query service — orchestrates the hybrid VideoRAG pipeline to answer questions.

Flow:
    Step 2: Semantic search over text metadata → timestamp resolution
    Step 3: Clip extraction → multimodal LLM analysis → 3-part response
"""

from app.config import settings
from pipeline.orchestrator import VideoRAGOrchestrator


# Lazy-loaded orchestrator singleton
_orchestrator = None


def _get_orchestrator() -> VideoRAGOrchestrator:
    """Get or initialize the pipeline orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = VideoRAGOrchestrator(config=settings.model_dump())
    return _orchestrator


async def process_query(question: str, current_user: dict) -> dict:
    """
    Process a student's question through the hybrid pipeline (Steps 2 + 3).

    The pipeline:
    1. Embeds the question and searches Qdrant for relevant text metadata
    2. Uses a cheap LLM to pinpoint exact timestamps from the metadata
    3. Extracts a short video clip at those timestamps
    4. Sends the clip to a Multimodal LLM for deep visual analysis
    5. Returns: text answer + video clip + timestamps

    Args:
        question: The student's natural language question.
        current_user: The authenticated user's data.

    Returns:
        Dict with 'answer', 'video_clip', 'timestamp', 'sources'.
    """
    orchestrator = _get_orchestrator()
    result = orchestrator.query(question=question)
    return result
