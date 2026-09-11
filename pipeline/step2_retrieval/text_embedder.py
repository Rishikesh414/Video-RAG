"""
Text Embedder — generates semantic vector embeddings for text using
Sentence Transformers (default) or Qwen3-Embedding-8B (production).

Part of Step 2 (Retrieval). Embeds both the metadata chunks (at index time)
and user queries (at query time) into the same vector space for Qdrant search.
"""

from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer


class TextEmbedder:
    """
    Text embedding generator using Sentence Transformers.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the text embedder.

        Args:
            model_name: HuggingFace model ID or local path.
                        Default is lightweight for development.
                        Use 'Qwen/Qwen3-Embedding-8B' for production.
        """
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

    def embed_text(self, text: str) -> np.ndarray:
        """Generate an embedding for a single text string."""
        return self.model.encode(text, normalize_embeddings=True)

    def embed_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Generate embeddings for a batch of texts."""
        return self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=True,
        )
