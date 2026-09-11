"""
Semantic Search — orchestrates query embedding + Qdrant retrieval.

Part of Step 2 (Retrieval). Takes a user question, embeds it, and
finds the most relevant metadata chunks from the vector store.
Returns ranked results with content, timestamps, and source video info.
"""

from typing import List, Dict

from pipeline.step2_retrieval.text_embedder import TextEmbedder
from pipeline.step2_retrieval.vector_store import VectorStore


class SemanticSearch:
    """
    Combines text embedding with Qdrant vector search to find the most
    relevant video segments for a given query.
    """

    def __init__(self, embedder: TextEmbedder, store: VectorStore):
        self.embedder = embedder
        self.store = store

    def search(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.0,
    ) -> List[Dict]:
        """
        Search for the most relevant content chunks.

        Args:
            query: Natural language question.
            top_k: Number of results to return.
            score_threshold: Minimum similarity score to include.

        Returns:
            Ranked list of dicts with 'score', 'content', 'start_time',
            'end_time', 'video_id', 'video_path'.
        """
        query_embedding = self.embedder.embed_text(query)
        raw_results = self.store.search(query_embedding, top_k=top_k)

        results = []
        for r in raw_results:
            if r["score"] >= score_threshold:
                meta = r["metadata"]
                results.append({
                    "score": r["score"],
                    "content": meta.get("content", ""),
                    "start_time": meta.get("start_time", 0),
                    "end_time": meta.get("end_time", 0),
                    "video_id": meta.get("video_id", ""),
                    "video_path": meta.get("video_path", ""),
                })

        return results

    def format_context(self, results: List[Dict]) -> str:
        """
        Format search results as context text for the timestamp resolver LLM.

        Args:
            results: Output from search().

        Returns:
            Formatted context string with timestamps and content.
        """
        parts = []
        for i, r in enumerate(results, 1):
            start = r["start_time"]
            end = r["end_time"]
            video = r.get("video_id", "unknown")
            content = r["content"]
            parts.append(
                f"[Result {i} | Video: {video} | {start:.1f}s – {end:.1f}s]\n{content}"
            )
        return "\n\n".join(parts)
