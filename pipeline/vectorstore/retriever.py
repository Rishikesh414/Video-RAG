"""
Retriever — high-level retrieval interface over the FAISS vector store.

Provides a clean API for the RAG chain to retrieve relevant content
chunks given a natural language query.
"""

from typing import List, Dict

import numpy as np

from pipeline.vectorstore.faiss_store import FAISSStore
from pipeline.embeddings.text_embedder import TextEmbedder


class VideoRetriever:
    """
    Retriever that combines text embedding with FAISS similarity search
    to find the most relevant video segments and transcript chunks.
    """

    def __init__(
        self,
        faiss_store: FAISSStore,
        text_embedder: TextEmbedder,
    ):
        """
        Initialize the retriever.

        Args:
            faiss_store: The FAISS vector store instance.
            text_embedder: The text embedding model instance.
        """
        self.store = faiss_store
        self.embedder = text_embedder

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.0,
    ) -> List[Dict]:
        """
        Retrieve the most relevant content for a query.

        Args:
            query: Natural language question.
            top_k: Number of results to return.
            score_threshold: Minimum similarity score to include.

        Returns:
            List of dicts with 'content', 'score', 'source', 'timestamp', etc.
        """
        # Embed the query
        query_embedding = self.embedder.embed_text(query)

        # Search FAISS
        results = self.store.search(query_embedding, top_k=top_k)

        # Filter by threshold
        filtered = [r for r in results if r["score"] >= score_threshold]

        return filtered

    def retrieve_with_context(
        self,
        query: str,
        top_k: int = 5,
    ) -> str:
        """
        Retrieve relevant chunks and format them as context for the LLM.

        Args:
            query: The user's question.
            top_k: Number of chunks to retrieve.

        Returns:
            Formatted context string for the RAG prompt.
        """
        results = self.retrieve(query, top_k=top_k)

        context_parts = []
        for i, result in enumerate(results, 1):
            meta = result["metadata"]
            source = meta.get("source", "Unknown")
            timestamp = meta.get("start_time", "")
            content = meta.get("content", "")

            header = f"[Source {i}: {source}"
            if timestamp:
                header += f" @ {timestamp}s"
            header += "]"

            context_parts.append(f"{header}\n{content}")

        return "\n\n".join(context_parts)
