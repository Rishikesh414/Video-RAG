"""
Text Embedder — generates semantic vector embeddings for text using
Qwen3-Embedding-8B or Sentence Transformers.

These embeddings are stored in FAISS for fast similarity search
during the retrieval phase of the RAG pipeline.
"""

from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer


class TextEmbedder:
    """
    Text embedding generator using Sentence Transformers.
    Supports Qwen3-Embedding-8B and other compatible models.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the text embedder.

        Args:
            model_name: HuggingFace model ID or local path.
                        Default is a lightweight model for development.
                        Use 'Qwen/Qwen3-Embedding-8B' for production.
        """
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate an embedding for a single text string.

        Args:
            text: The input text to embed.

        Returns:
            numpy array of shape (embedding_dim,).
        """
        return self.model.encode(text, normalize_embeddings=True)

    def embed_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for a batch of texts.

        Args:
            texts: List of input text strings.
            batch_size: Batch size for encoding.

        Returns:
            numpy array of shape (len(texts), embedding_dim).
        """
        return self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=True,
        )
