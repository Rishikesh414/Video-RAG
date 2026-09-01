"""
FAISS Store — manages the FAISS vector index for storing and
searching document/transcript embeddings.

Provides methods to build, save, load, and query the FAISS index
using cosine similarity (inner product on normalized vectors).
"""

import json
from pathlib import Path
from typing import List, Dict, Optional

import faiss
import numpy as np


class FAISSStore:
    """
    FAISS vector store for semantic search over video content embeddings.
    """

    def __init__(self, embedding_dim: int = 384):
        """
        Initialize the FAISS store.

        Args:
            embedding_dim: Dimension of the embedding vectors.
        """
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatIP(embedding_dim)  # Inner product (cosine on normalized)
        self.metadata: List[Dict] = []  # Parallel metadata for each vector

    def add_embeddings(
        self,
        embeddings: np.ndarray,
        metadata_list: List[Dict],
    ) -> None:
        """
        Add embeddings and their associated metadata to the index.

        Args:
            embeddings: numpy array of shape (n, embedding_dim), normalized.
            metadata_list: List of metadata dicts (one per embedding).
        """
        assert len(embeddings) == len(metadata_list), "Embeddings and metadata must match in length"
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype(np.float32))
        self.metadata.extend(metadata_list)

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
    ) -> List[Dict]:
        """
        Search the index for the most similar vectors.

        Args:
            query_embedding: Query vector of shape (embedding_dim,).
            top_k: Number of top results to return.

        Returns:
            List of dicts with 'score', 'metadata' for each result.
        """
        query = query_embedding.reshape(1, -1).astype(np.float32)
        faiss.normalize_L2(query)

        scores, indices = self.index.search(query, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            results.append({
                "score": float(score),
                "metadata": self.metadata[idx],
            })

        return results

    def save(self, directory: str) -> None:
        """
        Save the FAISS index and metadata to disk.

        Args:
            directory: Directory to save index.faiss and metadata.json.
        """
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(path / "index.faiss"))

        with open(path / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)

    def load(self, directory: str) -> None:
        """
        Load a FAISS index and metadata from disk.

        Args:
            directory: Directory containing index.faiss and metadata.json.
        """
        path = Path(directory)

        self.index = faiss.read_index(str(path / "index.faiss"))
        self.embedding_dim = self.index.d

        with open(path / "metadata.json", "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

    @property
    def total_vectors(self) -> int:
        """Return the total number of vectors in the index."""
        return self.index.ntotal
