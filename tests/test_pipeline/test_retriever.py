"""
Tests for the FAISS retriever module.
"""

import pytest
import numpy as np


class TestFAISSStore:
    """Tests for pipeline.vectorstore.faiss_store."""

    def test_add_and_search(self):
        """Adding vectors and searching should return matching results."""
        from pipeline.vectorstore.faiss_store import FAISSStore

        store = FAISSStore(embedding_dim=4)

        embeddings = np.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
        ], dtype=np.float32)

        metadata = [
            {"content": "chunk_1", "source": "video_1.mp4"},
            {"content": "chunk_2", "source": "video_2.mp4"},
            {"content": "chunk_3", "source": "video_3.mp4"},
        ]

        store.add_embeddings(embeddings, metadata)
        assert store.total_vectors == 3

        query = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
        results = store.search(query, top_k=1)

        assert len(results) == 1
        assert results[0]["metadata"]["content"] == "chunk_1"

    def test_save_and_load(self, tmp_path):
        """Saving and loading the index should preserve data."""
        from pipeline.vectorstore.faiss_store import FAISSStore

        store = FAISSStore(embedding_dim=4)
        embeddings = np.random.rand(5, 4).astype(np.float32)
        metadata = [{"id": i} for i in range(5)]
        store.add_embeddings(embeddings, metadata)

        save_dir = str(tmp_path / "faiss_test")
        store.save(save_dir)

        loaded_store = FAISSStore()
        loaded_store.load(save_dir)

        assert loaded_store.total_vectors == 5
        assert len(loaded_store.metadata) == 5
